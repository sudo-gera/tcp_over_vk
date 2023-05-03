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

if len(sys.argv)!=3:
    print(f'''to start server: {sys.argv[0]} [tcp-connect-host:]tcp-connect-port [http-listen-host:]http-listen-port''')
    print(f'''to start client: {sys.argv[0]} [tcp-listen-host:]tcp-listen-port http(s)://-started-url''')
    exit(1)

if sys.argv[2].startswith('http'):
    tcp_listen=(':'+sys.argv[1]).split(':')[-2:]
    tcp_connect=None
    http_listen=None
    http_connect=sys.argv[2]
else:
    tcp_listen=None
    tcp_connect=(':'+sys.argv[1]).split(':')[-2:]
    http_listen=('0.0.0.0:'+sys.argv[2]).split(':')[-2:]
    http_connect=None

connections:dict[str,connection]={}
conn_lock=asyncio.Lock()

conn_time=6*3600

async def async_later(coro,time):
    await asyncio.sleep(time)
    await coro

def later(coro,time):
    asyncio.create_task(async_later(coro,time))    

def mem(q):
    async def e(r):
        try:
            return await r
        except MemoryError:
            ic(traceback.format_exc())
            q.__self__.send_remove()
    @functools.wraps(q)
    def w(*a,**s):
        try:
            r=q(*a,**s)
            if asyncio.iscoroutine(r):
                return e(r)
            return r
        except MemoryError:
            ic(traceback.format_exc())
            q.__self__.send_remove()
    return w


class connection(asyncio.Protocol):
    def __init__(self,name=None,):
        super().__init__()
        if name is None:
            name=str(time.time())
        connections[name]=self
        self.lock=asyncio.Lock()
        self.name=name
        self.h2t=asyncio.Queue()
        self.t2h=asyncio.Queue()
        self.send_num=0
        self.recv_num=0
        self.work=1
        self.dlen=0
        self.hlen=0
        self.tlen=0
        self.recv_buff=[]
        self.poll=asyncio.create_task(self.recv())
        self.push=asyncio.create_task(self.send())
        self.dget=asyncio.create_task(self.enum_get())
    @mem
    async def connect(self):
        loop = asyncio.get_running_loop()
        #ic(tcp_connect)
        await loop.create_connection(
            lambda: self,
            *tcp_connect)
    @mem
    def recv_data(self,data):
        if not data.endswith(b'^'):
            return
        ic(len(data),connections_len())
        self.dlen+=len(data)
        for d in data.split(b'^')[:-1]:
            if d:
                self.h2t_put(d)
            else:
                self.remove()
    @mem
    async def send_data(self):
        data=await self.t2h.get()
        self.tlen-=len(data)
        if self.tlen<=4096:
            self.transport.resume_reading()
        data+=b'^'
        await asyncio.sleep(0.03)
        try:
            while self.work:
                tmp=self.t2h.get_nowait()
                self.tlen-=len(tmp)
                if self.tlen<=4096:
                    self.transport.resume_reading()
                data+=tmp+b'^'
        except asyncio.QueueEmpty:
            pass
        except MemoryError:
            del data
            self.send_remove()
        self.dlen+=len(data)
        ic(len(data),connections_len())
        return data
    @mem
    async def recv(self):
        if http_connect:
            async with aiohttp.ClientSession(trust_env=True) as session:
                try:
                    while self.work:
                        try:
                            async with session.get(f'''{http_connect}/{self.name}''') as resp:
                                data=await resp.read()
                                self.recv_data(data)
                        except asyncio.exceptions.TimeoutError:
                            ic()
                            pass
                        except aiohttp.client_exceptions.ServerDisconnectedError:
                            exit()
                except MemoryError:
                    self.send_remove()
    @mem
    async def send(self):
        if http_connect:
            async with aiohttp.ClientSession(trust_env=True) as session:
                while self.work:
                    data=await self.send_data()
                  # ic(self.name,data)
                    async with session.post(f'''{http_connect}/{self.name}''', data=data) as resp:
                        pass
    @mem
    def t2h_put(self,data):
        if 'data' in data:
            data['data']=base64.b64encode(data['data']).decode()
        data=json.dumps(data).encode()
        self.tlen+=len(data)
        if self.tlen>4096:
            self.transport.pause_reading()
        asyncio.create_task(self.async_put(self.t2h,data))
    @mem
    async def async_put(self,q,data):
        try:
            await q.put(data)
        except MemoryError:
            self.send_remove()      
    @mem
    def h2t_put(self,data):
        l=len(data)
        self.hlen+=l
        data=data.decode()
        data=json.loads(data)
        if 'data' in data:
            data['data']=base64.b64decode(data['data'])
        data['l']=l
        asyncio.create_task(self.async_put(self.h2t,data))
    @mem
    def later(self,d,t):
        num=self.send_num
        self.send_num=num+1
        # ic(self.name,data,num)
        later(self.enum_put({
            'num': num,
        }|d),t)
    @mem
    def connection_made(self, transport: asyncio.Transport) -> None:
      # ic(self.name)
        self.transport=transport
        if http_connect:
            self.t2h_put({
                'event': 'new',
            })
    @mem
    def data_received(self, data: bytes) -> None:
      # ic()
        self.later(({
            'event':'got',
            'data':data,
        }),min(0.1,self.dlen//1638400))
    @mem
    def eof_received(self) -> None:
      # ic()
        self.later(({
            'event':'eof',
        }),4)
    @mem
    def connection_lost(self, exc: Exception | None) -> None:
      # ic()
        self.later(({
            'event':'del',
        }),4)
        self.remove()
    @mem
    async def enum_put(self, data: dict) -> None:
        self.t2h_put(data)
    @mem
    async def async_remove(self):
        self.transport.close()
        self.work=0
        async with conn_lock:
            if self.name in connections:
                connections[self.name]=None
        later(self.remove_later(),16)
    @mem
    def remove(self):
        asyncio.create_task(self.async_remove())
    @mem
    def send_remove(self):
        self.later(({
            'event':'del',
        }),4)
        self.remove()
    @mem
    async def remove_later(self):
        self.dget.cancel()
        self.push.cancel()
        self.poll.cancel()
    @mem
    async def enum_get(self):
        while self.work:
            ev=await self.h2t.get()
            self.hlen-=ev['l']
          # ic(ev)
            if ev['event']=='new':
                pass
            else:
                num=ev['num']
              # ic(ev,num,self.recv_buff,self.recv_num)
                self.recv_buff.append((num,ev))
                self.recv_buff.sort()
                for num,ev in self.recv_buff:
                    if num==self.recv_num:
                        self.recv_num=num+1
                      # ic(num,ev)
                        if ev['event']=='got':
                            self.transport.write(ev['data'])
                        if ev['event']=='eof':
                            self.transport.write_eof()
                        if ev['event']=='del':
                            self.remove()
                    else:
                      # ic(num,ev)
                        break
                if len(self.recv_buff)>1024:
                    self.send_remove()
                self.recv_buff=[(num,ev) for num,ev in self.recv_buff if num>=self.recv_num]

def connections_len():
    return len([w for q,w in connections.items() if w is not None])

async def get_connection(name):
    async with conn_lock:
        try:
            name=float(name)
        except:
            return None
        t=time.time()
        global connections
        connections={q:w for q,w in connections.items() if w is not None or q+conn_time>t}
        if name in connections:
            return connections[name]
        if time.time()-conn_time>name:
            return None
        connections[name]=connection(name)
        await connections[name].connect()
        return connections[name]


async def recv(req):
    name=req.match_info['name']
    conn=await get_connection(name)
    if conn is None:
        return aiohttp.web.Response(text='^')
    data=await req.read()
    conn.recv_data(data)
    return aiohttp.web.Response(text=bin(len(data))[2:])

async def send(req):
    name=req.match_info['name']
    conn=await get_connection(name)
    if conn is None:
        return aiohttp.web.Response(text='^')
    data=await conn.send_data()
    return aiohttp.web.Response(body=data)

async def get_time(req):
    return aiohttp.web.Response(text=str(time.time()))

if http_listen:
    app = aiohttp.web.Application()
    app.add_routes([
        aiohttp.web.get('/', get_time),
        aiohttp.web.post('/{name}', recv),
        aiohttp.web.get('/{name}', send),
    ])
    aiohttp.web.run_app(app, host=http_listen[0], port=http_listen[1])
if http_connect:
    # http_client_name=urllib.request.urlopen(http_connect).read()
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
