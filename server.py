# import asyncio
# <<<<<<< HEAD
# =======
# <<<<<<< HEAD
# import time
# import random


# class EchoServerProtocol(asyncio.Protocol):
#     def connection_made(self, transport):
#         peername = transport.get_extra_info('peername')
#         print('Connection from {}'.format(peername))
#         self.transport = transport

#     def data_received(self, data):
#         asyncio.create_task(self.dr(data))

#     async def dr(self,data):
#         print(id(self),id(self.transport))
#         message = data.decode()
#         print('Data received: {!r}'.format(message))

#         await asyncio.sleep(random.random())

#         print('Send: {!r}'.format(message))
#         self.transport.write(data)

#         print('Close the client socket')
#         self.transport.close()


# async def main():
#     # Get a reference to the event loop as we plan to use
#     # low-level APIs.
#     loop = asyncio.get_running_loop()

#     server = await loop.create_server(
#         lambda: EchoServerProtocol(),
#         '127.0.0.1', 8888)

#     async with server:
#         await server.serve_forever()


# asyncio.run(main())
# =======
# >>>>>>> 221e66b615c28ae6dc9dd846767b1c13d9ea0502
# import asyncio.locks
# from aiohttp import web
# import time
# import random
# import json

# c=0
# <<<<<<< HEAD
# num=100
# =======
# num=1
# >>>>>>> 221e66b615c28ae6dc9dd846767b1c13d9ea0502

# def militime():
#     s=time.asctime().split()
#     s[3]+=str(time.time()%1)[1:5]
#     return ' '.join(s)

# def randbytes(l):
#     return bytes([random.randint(32,126) for w in range(l)])

# async def counter():
#     oc=c
#     while 1:
#         await asyncio.sleep(0.01)
#         if c!=oc:
#             print(militime(),c)
#             oc=c

# rs={randbytes(65536) for w in range(num)}

# cv=asyncio.locks.Condition()

# times=[]

# async def hello(request):
#     async with cv:
#         global c
#         c+=1
#         # print(c)
#         print('\r           \r',c,end='\r')
#         if c==num:
#             times.append(time.time())
#             print(militime())
#             await asyncio.sleep(1)
#             print(militime())
#             times.append(time.time())
#             cv.notify_all()
#         else:
#             await cv.wait()
#             pass
#     return web.Response(text=rs.pop().decode())

# async def timesync(request):
#     return web.Response(text=json.dumps(times))


# app = web.Application()
# app.add_routes([web.get('/', hello),web.get('/time', timesync),
#                 web.post('/', hello)])

# web.run_app(app, port=7003)

# <<<<<<< HEAD
# =======
# >>>>>>> b735584cfc773161e853eaa65201f22ba0bc974c
# >>>>>>> 221e66b615c28ae6dc9dd846767b1c13d9ea0502

# import asyncio
# from async_websocket_client.apps import AsyncWebSocketApp
# from async_websocket_client.dispatchers import BaseDispatcher
# class SomeDispatcher(BaseDispatcher):
#     async def on_connect(self):
#         return await self.ws.send('hello, server')

#     async def on_message(self, message: str):
#         return await self.ws.send(f'server, I received your message. len(message)=={len(message)}')

# client = AsyncWebSocketApp('ws://localhost:3001/', SomeDispatcher())

# asyncio.run(client.run()) # Run with asyncio


#!/usr/bin/env python

# import asyncio
# import websockets

# async def hello():
#     uri = "ws://localhost:3001"
#     async with websockets.connect(uri) as websocket:
#         name = '123'

#         await websocket.send(name)
#         print(f">>> {name}")

#         greeting = await websocket.recv()
#         print(f"<<< {greeting}")

# if __name__ == "__main__":
#     asyncio.run(hello())

#!/usr/bin/env python

# import asyncio
# import websockets

# async def hello(websocket):
#     print('start')
#     name = await websocket.recv()
#     print(f"<<< {name}")

#     greeting = f"Hello {name}!"

#     await websocket.send(greeting)
#     print(f">>> {greeting}")

# async def main():
#     async with websockets.serve(hello, "localhost", 3001):
#         await asyncio.Future()  # run forever

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio

import stream

# async def copy(reader: stream.Stream, writer: stream.Stream):
#     while data:=await reader.read():
#         writer.write(data)
#         await writer.drain()

# async def connection(s_reader, s_writer):
#     async with stream.Stream(s_reader, s_writer) as s:
#             await asyncio.gather(
#                 copy(s, c),
#                 copy(c, s),
#             )

async def sender(c):
    while 1:
        await asyncio.sleep(1)
        print('3001')
        c.write(b'3001')
        await c.drain()

async def main():
    async with stream.Stream(*await asyncio.open_connection('127.0.0.1', 3001)) as c:
        await asyncio.sleep(4)
        asyncio.create_task(sender(c))
        while data := await c.read(2**16):
            print(data)

asyncio.run(main())

