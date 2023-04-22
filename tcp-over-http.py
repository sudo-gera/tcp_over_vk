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
        self.recv_buff=[]
        self.poll=asyncio.create_task(self.recv())
        self.push=asyncio.create_task(self.send())
        self.dget=asyncio.create_task(self.enum_get())
    async def connect(self):
        loop = asyncio.get_running_loop()
        #ic(tcp_connect)
        await loop.create_connection(
            lambda: self,
            *tcp_connect)
    def recv_data(self,data):
        if not data.endswith(b'^'):
            print(data)
            print('wrong server response')
            exit(1)
        ic(len(data),connections_len())
        for d in data.split(b'^')[:-1]:
            if d:
                self.h2t_put(d)
            else:
                asyncio.create_task(self.remove())
    async def send_data(self):
        data=await self.t2h.get()+b'^'
        await asyncio.sleep(0.03)
        try:
            while self.work:
                data+=self.t2h.get_nowait()+b'^'
        except asyncio.QueueEmpty:
            pass
        ic(len(data),connections_len())
        return data
    async def recv(self):
        if http_connect:
            async with aiohttp.ClientSession(trust_env=True) as session:
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
    async def send(self):
        if http_connect:
            async with aiohttp.ClientSession(trust_env=True) as session:
                while self.work:
                    data=await self.send_data()
                  # ic(self.name,data)
                    async with session.post(f'''{http_connect}/{self.name}''', data=data) as resp:
                        pass
    def t2h_put(self,data):
        if 'data' in data:
            data['data']=base64.b64encode(data['data']).decode()
        data=json.dumps(data).encode()
        asyncio.create_task(self.t2h.put(data))
    def h2t_put(self,data):
        data=json.loads(data.decode())
        if 'data' in data:
            data['data']=base64.b64decode(data['data'])
        asyncio.create_task(self.h2t.put(data))
    def connection_made(self, transport: asyncio.Transport) -> None:
      # ic(self.name)
        self.transport=transport
        if http_connect:
            self.t2h_put({
                'event': 'new',
            })
    def data_received(self, data: bytes) -> None:
      # ic()
        asyncio.create_task(self.enum_put({
            'event':'got',
            'data':data,
        }))
    async def later(self,coro,t):
        await asyncio.sleep(t)
        await coro
    def eof_received(self) -> None:
      # ic()
        asyncio.create_task(self.later(self.enum_put({
            'event':'eof',
        }),4))
    def connection_lost(self, exc: Exception | None) -> None:
      # ic()
        asyncio.create_task(self.later(self.enum_put({
            'event':'del',
        }),4))
        asyncio.create_task(self.remove())
    async def enum_put(self, data: dict) -> None:
        async with self.lock:
            num=self.send_num
            self.send_num=num+1
          # ic(self.name,data,num)
            self.t2h_put({
                'num': num,
            }|data)
    async def remove(self):
        self.transport.close()
        self.work=0
        async with conn_lock:
            if self.name in connections:
                connections[self.name]=None
        asyncio.create_task(self.later(self.remove_later(),16))
    async def remove_later(self):
        self.dget.cancel()
        self.push.cancel()
        self.poll.cancel()
    async def enum_get(self):
        while self.work:
            ev=await self.h2t.get()
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
                            await self.remove()
                            # asyncio.create_task(self.later(self.remove(),16))
                    else:
                      # ic(num,ev)
                        break
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
