from __future__ import annotations
import argparse
import asyncio
import aiohttp
import time
import json
# import pickle
import aiohttp.web
import base64
from ic import ic
import sys
import urllib.request
import functools
import traceback
import weakref

if len(sys.argv)==2:
    http_listen=('0.0.0.0:'+sys.argv[1]).split(':')[-2:]
    http_connect=None
    tcp_listen=None
    tcp_connect=None
elif len(sys.argv)==3:
    http_listen=None
    http_connect=sys.argv[2]
    tcp_connect=(':'+sys.argv[1]).split(':')[-4:]
    tcp_listen,tcp_connect=tcp_connect[:2],tcp_connect[2:]
else:
    print(f'''to start server: {sys.argv[0]} [http-listen-host:]http-listen-port''')
    print(f'''to start client: {sys.argv[0]} [tcp-listen-host:]tcp-listen-port:tcp-remote-host:tcp-remote-port http(s)://-started-url''')
    exit(1)

connections:dict[str,connection]={}
conn_lock=asyncio.Lock()

conn_time=6*3600
live_time=600

async def async_later(coro,time):
    await asyncio.sleep(time)
    await coro

def later(coro,time):
    asyncio.create_task(async_later(coro,time))    

def err(q):
    self=0
    async def e(r):
        try:
            r= await r
            return r
        except Exception:
            ic(q)
            ic(traceback.format_exc())
            if self is not None:
                self.remove()
    @functools.wraps(q)
    def w(*a,**s):
        nonlocal self
        if a and type(a[0])==connection:
            self=a[0]
        elif a and type(a[0]) in [connection.h2t_c, connection.t2h_c]:
            try:
                self=a[0].conn
            except Exception:
                self=None
        else:
            self=None
        try:
            r=q(*a,**s)
            if asyncio.iscoroutine(r):
                return e(r)
            return r
        except Exception:
            ic(q)
            ic(traceback.format_exc())
            if self is not None:
                self.remove()
    return w


class DataQueue:
    def __init__(self):
        self.queue=asyncio.Queue()
        self.len=0
        self.lock=asyncio.Lock()
    def put(self,val:bytes):
        ic(val)
        assert type(val) in [bytes, bytearray]
        self.queue.put_nowait(val)
        self.len+=len(val)
    def get(self):
        data=[]
        try:
            while 1:
                chunk=self.queue.get_nowait()
                self.len-=len(chunk)
                data.append(chunk)
        except asyncio.QueueEmpty:
            pass
        ic(data)
        data=b''.join(data)
        return data
    def __len__(self):
        return self.len
    async def get_wait(self):
        async with self.lock:
            ic('start waiting...')
            data=await self.queue.get()
            self.len-=len(data)
            ic('stop waiting...', data)
            g=self.get()
            data+=g
            return data

events = DataQueue()

async def run_with_timeout(coro,timeout):
    task = asyncio.create_task(coro)
    await asyncio.wait([task], timeout=timeout)
    return task.result()

class connection(asyncio.Protocol):
    class t2h_c:
        @err
        def __init__(self,conn:connection):
            self.conn:connection=conn
            self.conn.last=time.time()
            self.loop=asyncio.create_task(self.session_loop())
            self.queue=DataQueue()
            self.num=0
        @err
        async def session_loop(self):
            if http_connect:
                async with aiohttp.ClientSession(trust_env=True) as session:
                    while self.conn is not None and self.conn.work:
                        data=await self.what_to_send()
                        if self.conn is None:
                            return
                        async with session.post(f'''{http_connect}/{self.conn.name}/{self.conn.forward_to}''', data=data, ssl=False) as resp:
                            pass
        @err
        def update_reading(self):
            if len(self.queue)<4096:
                self.conn.transport.resume_reading()
            else:
                self.conn.transport.pause_reading()
        @err
        async def what_to_send(self):
            try:
                data = await run_with_timeout(self.queue.get_wait(), 16)
                ic(data)
                # async with asyncio.timeout(2):
                #     data=await self.queue.get_wait()
                ic(len(data))
                self.update_reading()
            except (asyncio.CancelledError,asyncio.InvalidStateError):
                data=b''
            return ic(data+events.get())
        @err
        def event(self,ev,data=None):
            if self.conn is None:
                return
            d=dict(
                to=self.conn.forward_to,
                type=ev,
                name=self.conn.name,
            )
            self.conn.last=time.time()
            if ev!='new':
                num=self.num
                self.num+=1
                d['num']=num
            if ev=='got':
                d['data']=base64.b64encode(data).decode()
            d=json.dumps(d)+'^'
            d=d.encode()
            if ev=='got':
                self.queue.put(d)
                self.update_reading()
            else:
                events.put(d)
            if ev=='del':
                later(self.conn.async_local_remove(),4)
        @err
        def remove(self):
            self.conn=None
            self.loop.cancel()

    class h2t_c:
        @err
        def __init__(self,conn):
            self.conn:connection=conn
            self.conn.last=time.time()
            self.loop=asyncio.create_task(self.session_loop())
            self.num=0
            self.buff=[]
        @err
        async def session_loop(self):
            if http_connect:
                async with aiohttp.ClientSession(trust_env=True) as session:
                        while self.conn is not None and self.conn.work:
                            try:
                                async with session.get(f'''{http_connect}/{self.conn.name}/{self.conn.forward_to}''', ssl=False) as resp:
                                    data=await resp.read()
                                    await self.received(data)
                            except asyncio.exceptions.TimeoutError:
                                pass
                            except aiohttp.client_exceptions.ServerDisconnectedError:
                                exit()
        @err
        async def received(self,all_data):
            for data in all_data.split(b'^')[:-1]:
                if not data and self.conn is not None:
                    self.conn.local_remove()
                    break
                ic(len(data))
                data=json.loads(data)
                conn=await get_connection(data['name'],data['to'])
                if conn:
                    assert conn.name==data['name']
                    await conn.h2t.event(data)
        @err
        async def event(self,data):
            if not self.conn.work:
                return
            self.conn.last=time.time()
            if data['type']=='new':
                return
            self.buff.append((data['num'],data))
            self.buff.sort()
            for num,ev in self.buff:
                if num!=self.num:
                    break
                self.num+=1
                if ev['type']=='got':
                    while self.conn.transport is None:
                        await asyncio.sleep(0.01)
                        if self.conn is None:
                            return
                    self.conn.transport.write(base64.b64decode(ev['data']))
                if ev['type']=='eof':
                    while self.conn.transport is None:
                        await asyncio.sleep(0.01)
                    self.conn.transport.write_eof()
                if ev['type']=='del':
                    self.conn.local_remove()
            self.buff=[q for q in self.buff if q[0]>=self.num]
            if len(self.buff)>1024:
                self.conn.remove()
        @err
        def remove(self):
            self.conn=None
            self.loop.cancel()

    @err
    def connection_made(self, transport: asyncio.Transport) -> None:
        self.transport=transport
        self.t2h.event('new')
    @err
    def data_received(self, data: bytes) -> None:
        self.t2h.event('got',data)
    @err
    def eof_received(self) -> None:
        self.t2h.event('eof')
    @err
    def connection_lost(self, exc: Exception | None) -> None:
        self.t2h.event('del')
        

    @err
    def __init__(self,name=None,forward_to=None):
        super().__init__()
        if name is None:
            name=time.time()
        if forward_to is None:
            forward_to=':'.join(tcp_connect)
        connections[name]=self
        self.forward_to=forward_to
        # ic(forward_to)
        self.name=name
        self.work=1
        self.transport:asyncio.Transport=None

        self.t2h=self.t2h_c(self)
        self.h2t=self.h2t_c(self)

    @err
    async def connect(self):
        assert http_listen is not None
        loop = asyncio.get_running_loop()
        await loop.create_connection(
            lambda: self,
            *self.forward_to.split(':'))
    
    @err
    def remove(self):
        if self.work:
            self.connection_lost(None)
    
    @err
    def local_remove(self):
        if self.work:
            self.work=0
            self.t2h.remove()
            self.h2t.remove()
            if self.transport is not None:
                self.transport.close()
                self.transport=None
        # ic(self.name, connections)
        if self.name in connections:
            connections[self.name]=None

    @err
    async def async_local_remove(self):
        self.local_remove()

@err
async def get_connection(name,forward_to)->connection:
    try:
        name=float(name)
    except:
        return None
    t=time.time()
    global connections
    connections={q:w for q,w in connections.items() if w is not None or q+conn_time>t}
    for _name in connections:
        if connections[_name] is not None:
            if connections[_name].last+live_time<time.time():
                connections[_name].remove()
    if name in connections:
        return connections[name]
    if time.time()>name+conn_time:
        return None
    connections[name]=connection(name,forward_to)
    await connections[name].connect()
    return connections[name]


@err
async def recv(req):
    name=req.match_info['name']
    forward_to=req.match_info['forward_to']
    conn=await get_connection(name,forward_to)
    if conn is None:
        return aiohttp.web.Response(text='^')
    try:
        data=await req.read()
    except Exception:
        data=b''
    await conn.h2t.received(data)
    return aiohttp.web.Response(text=bin(len(data))[2:])

@err
async def send(req):
    name=req.match_info['name']
    forward_to=req.match_info['forward_to']
    conn=await get_connection(name,forward_to)
    if conn is None:
        return aiohttp.web.Response(text='^')
    data=await conn.t2h.what_to_send()
    return aiohttp.web.Response(body=data)

@err
async def get_time(req):
    return aiohttp.web.Response(text=str(time.time()))

if http_listen:
    app = aiohttp.web.Application()
    app.add_routes([
        aiohttp.web.get('/', get_time),
        aiohttp.web.post('/{name}/{forward_to}', recv),
        aiohttp.web.get('/{name}/{forward_to}', send),
    ])
    aiohttp.web.run_app(app, host=http_listen[0], port=http_listen[1])
if http_connect:
    # http_client_name=urllib.request.urlopen(http_connect).read()
    @err
    async def main():
        loop = asyncio.get_running_loop()
        server = await loop.create_server(
            connection,
            *tcp_listen)
        async with server:
            await server.serve_forever()
        await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
