import argparse
import asyncio
import aiohttp
import time
import json
# import pickle
import aiohttp.web
import base64
from ic import ic

def parse_args() -> list[None | tuple[str, int]]:
    p = argparse.ArgumentParser()
    p.add_argument('--tcp-listen')
    p.add_argument('--tcp-connect')
    p.add_argument('--http-listen')
    p.add_argument('--http-connect')
    p = vars(p.parse_args())
    return [
        None if w is None else
        (
            w[:-1] if w.endswith('/') else w
        )if q=='http_connect' else(
            tuple([
                int(r)
                if e else r
            for e, r in enumerate((':'+w).split(':')[-2:])])
        )
    for q, w in p.items()]


tcp_listen,\
    tcp_connect,\
    http_listen,\
    http_connect = parse_args()

connections={}

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
        self.poll=asyncio.create_task(self.send())
        self.dget=asyncio.create_task(self.enum_get())
    async def connect(self):
        loop = asyncio.get_running_loop()
        await loop.create_connection(
            lambda: self,
            *tcp_connect)
    async def recv(self):
        if http_connect:
            async with aiohttp.ClientSession(trust_env=True) as session:
                while self.work:
                    try:
                        async with session.get(f'''{http_connect}/{self.name}''') as resp:
                            data=await resp.read()
                            ic(len(data))
                            ic(self.name,data)
                            self.h2t_put(data)
                    except asyncio.exceptions.TimeoutError:
                        pass
                    except aiohttp.client_exceptions.ServerDisconnectedError:
                        exit()
    async def send(self):
        if http_connect:
            async with aiohttp.ClientSession(trust_env=True) as session:
                while self.work:
                    data=await self.t2h.get()
                    ic(self.name,data)
                    ic(len(data))
                    async with session.post(f'''{http_connect}/{self.name}''', data=data) as resp:
                        pass
    def t2h_put(self,data):
        if 'data' in data:
            data['data']=base64.b64encode(data['data']).decode()
        data=json.dumps(data)
        asyncio.create_task(self.t2h.put(data))
    def h2t_put(self,data):
        data=json.loads(data)
        if 'data' in data:
            data['data']=base64.b64decode(data['data'])
        asyncio.create_task(self.h2t.put(data))
    def connection_made(self, transport: asyncio.Transport) -> None:
        ic(self.name)
        self.transport=transport
        if http_connect:
            self.t2h_put({
                'event': 'new',
            })
    def data_received(self, data: bytes) -> None:
        ic()
        asyncio.create_task(self.enum_put({
            'event':'got',
            'data':data,
        }))
    def eof_received(self) -> None:
        ic()
        asyncio.create_task(self.enum_put({
            'event':'eof',
        }))
    def connection_lost(self, exc: Exception | None) -> None:
        ic()
        asyncio.create_task(self.enum_put({
            'event':'del',
        }))
        self.transport.close()
        self.work=0
    async def enum_put(self, data: dict) -> None:
        async with self.lock:
            num=self.send_num
            self.send_num=num+1
            ic(self.name,data,num)
            self.t2h_put({
                'num': num,
            }|data)
    async def enum_get(self):
        while self.work:
            ev=await self.h2t.get()
            ic(ev)
            if ev['event']=='new':
                pass
            else:
                num=ev['num']
                ic(ev,num,self.recv_buff,self.recv_num)
                self.recv_buff.append((num,ev))
                self.recv_buff.sort()
                for num,ev in self.recv_buff:
                    if num==self.recv_num:
                        self.recv_num=num+1
                        ic(num,ev)
                        if ev['event']=='got':
                            self.transport.write(ev['data'])
                        if ev['event']=='eof':
                            self.transport.write_eof()
                        if ev['event']=='del':
                            self.transport.close()
                            self.work=0
                    else:
                        ic(num,ev)
                        break
                self.recv_buff=[(num,ev) for num,ev in self.recv_buff if num>=self.recv_num]


async def recv(req):
    name=req.match_info['name']
    if name not in connections:
        connections[name]=connection(name)
        await connections[name].connect()
    data=await req.read()
    ic(len(data))
    ic(name,data)
    connections[name].h2t_put(data)
    return aiohttp.web.Response(text=bin(len(data))[2:])

async def send(req):
    name=req.match_info['name']
    if name not in connections:
        connections[name]=connection(name)
        await connections[name].connect()
    data=await connections[name].t2h.get()
    ic(len(data))
    ic(name,data)
    return aiohttp.web.Response(body=data)

if http_listen:
    app = aiohttp.web.Application()
    app.add_routes([
        aiohttp.web.post('/{name}', recv),
        aiohttp.web.get('/{name}', send),
    ])
    aiohttp.web.run_app(app, host=http_listen[0], port=http_listen[1])
if http_connect:
    async def main():
        loop = asyncio.get_running_loop()
        server = await loop.create_server(
            connection,
            *tcp_listen)
        async with server:
            await server.serve_forever()
        await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
    asyncio.run(main())
