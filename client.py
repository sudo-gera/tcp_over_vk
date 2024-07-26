# <<<<<<< HEAD
# =======
# <<<<<<< HEAD
# import asyncio

# _data=0

# class EchoClientProtocol(asyncio.Protocol):
#     def __init__(self, message, on_con_lost):
#         self.message = message
#         self.on_con_lost = on_con_lost

#     def connection_made(self, transport):
#         global _data
#         _data=self.message
#         transport.write(self.message.encode())
#         print('Data sent: {!r}'.format(self.message))

#     def data_received(self, data):
#         print('Data received: {!r}'.format(data.decode()))
#         assert data.decode()==_data

#     def connection_lost(self, exc):
#         print('The server closed the connection')
#         self.on_con_lost.set_result(True)


# async def main():
#     # Get a reference to the event loop as we plan to use
#     # low-level APIs.
#     loop = asyncio.get_running_loop()

#     on_con_lost = loop.create_future()
#     message = 'Hello World!'+str(hash('-'))

#     transport, protocol = await loop.create_connection(
#         lambda: EchoClientProtocol(message, on_con_lost),
#         '127.0.0.1', 8888)

#     # Wait until the protocol signals that the connection
#     # is lost and close the transport.
#     try:
#         await on_con_lost
#     finally:
#         transport.close()
# =======
# >>>>>>> 221e66b615c28ae6dc9dd846767b1c13d9ea0502
# import aiohttp
# import asyncio
# import time
# import json

# import random

# c=0

# <<<<<<< HEAD
# num=1
# =======
# num=100
# >>>>>>> 221e66b615c28ae6dc9dd846767b1c13d9ea0502

# def militime():
#     s=time.asctime().split()
#     s[3]+=str(time.time()%1)[1:5]
#     return ' '.join(s)

# async def counter():
#     oc=c
#     while c!=num:
#         await asyncio.sleep(0.01)
#         if c!=oc:
#             print(militime(),c)
#             oc=c
#             if c==num:
#                 break

# def randbytes(l):
#     return bytes([random.randint(32,126) for w in range(l)])

# rs={randbytes(65536) for w in range(num)}

# <<<<<<< HEAD
# # url='https://user225847803-kimyq256.wormhole.vk-apps.com/'
# =======
# >>>>>>> 221e66b615c28ae6dc9dd846767b1c13d9ea0502
# url='https://user225847803-2yl2j4hf.wormhole.vk-apps.com/'
# # url='http://localhost:7003/'

# async def f(session : aiohttp.ClientSession):
#     q=str(time.time())
#     async with session.post(url,params={'q':q},data=rs.pop()) as response:
#         html = await response.text()
#         global c
#         c+=1
#         # print("Body:", html[:15], "...")
    
# times=[]

# async def main():

#     # ct=asyncio.create_task(counter())
#     await asyncio.sleep(0.1)
#     print(militime())
#     times.append(time.time())
#     async with aiohttp.ClientSession() as session:
#         ts=[]
#         for w in range(num):
#             ts.append(f(session))
#         await asyncio.gather(*ts)
#     times.append(time.time())
#     print(militime())
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url+'time') as restimes:
#             times[1:1]=json.loads(await restimes.text())
#             # print(times)
#             print(times[1]-times[0])
#             print(times[3]-times[2])


# <<<<<<< HEAD
# =======
# >>>>>>> b735584cfc773161e853eaa65201f22ba0bc974c
# >>>>>>> 221e66b615c28ae6dc9dd846767b1c13d9ea0502


# asyncio.run(main())

# import asyncio
# from async_websocket_client.apps import AsyncWebSocketApp
# from async_websocket_client.dispatchers import BaseDispatcher
# class SomeDispatcher(BaseDispatcher):
#     async def on_connect(self):
#         return await self.ws.send('hello, server')

#     async def on_message(self, message: str):
#         return await self.ws.send(f'server, I received your message. len(message)=={len(message)}')

# client = AsyncWebSocketApp('ws://localhost:3002/', SomeDispatcher())

# asyncio.run(client.run()) # Run with asyncio

#!/usr/bin/env python

# import asyncio
# import websockets

# async def hello():
#     uri = "ws://localhost:3002"
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
#     name = "What's your name? "

#     await websocket.send(name)
#     print(f">>> {name}")

#     greeting = await websocket.recv()
#     print(f"<<< {greeting}")

# async def main():
#     async with websockets.serve(hello, "localhost", 3002):
#         await asyncio.Future()  # run forever

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import stream

async def sender(c):
    while 1:
        await asyncio.sleep(1)
        print('3002')
        c.write(b'3002')
        await c.drain()

async def main():
    async with stream.Stream(*await asyncio.open_connection('127.0.0.1', 3002)) as c:
        await asyncio.sleep(4)
        asyncio.create_task(sender(c))
        while data := await c.read(2**16):
            print(data)

asyncio.run(main())
