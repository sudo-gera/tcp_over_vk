import asyncio
<<<<<<< HEAD
import time
import random


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        asyncio.create_task(self.dr(data))

    async def dr(self,data):
        print(id(self),id(self.transport))
        message = data.decode()
        print('Data received: {!r}'.format(message))

        await asyncio.sleep(random.random())

        print('Send: {!r}'.format(message))
        self.transport.write(data)

        print('Close the client socket')
        self.transport.close()


async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '127.0.0.1', 8888)

    async with server:
        await server.serve_forever()


asyncio.run(main())
=======
import asyncio.locks
from aiohttp import web
import time
import random
import json

c=0
num=1

def militime():
    s=time.asctime().split()
    s[3]+=str(time.time()%1)[1:5]
    return ' '.join(s)

def randbytes(l):
    return bytes([random.randint(32,126) for w in range(l)])

async def counter():
    oc=c
    while 1:
        await asyncio.sleep(0.01)
        if c!=oc:
            print(militime(),c)
            oc=c

rs={randbytes(65536) for w in range(num)}

cv=asyncio.locks.Condition()

times=[]

async def hello(request):
    async with cv:
        global c
        c+=1
        # print(c)
        print('\r           \r',c,end='\r')
        if c==num:
            times.append(time.time())
            print(militime())
            await asyncio.sleep(1)
            print(militime())
            times.append(time.time())
            cv.notify_all()
        else:
            await cv.wait()
            pass
    return web.Response(text=rs.pop().decode())

async def timesync(request):
    return web.Response(text=json.dumps(times))


app = web.Application()
app.add_routes([web.get('/', hello),web.get('/time', timesync),
                web.post('/', hello)])

web.run_app(app, port=7003)

>>>>>>> b735584cfc773161e853eaa65201f22ba0bc974c
