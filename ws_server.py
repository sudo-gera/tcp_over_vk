import asyncio
import websockets

import sys

import stream

if len(sys.argv)==2:
    http_listen=('0.0.0.0:'+sys.argv[1]).split(':')[-2:]
    http_listen[1] = int(http_listen[1])
else:
    print(f'''to start server: {sys.argv[0]} [http-listen-host:]http-listen-port''')
    exit(1)

async def connection(websocket: websockets.WebSocketServerProtocol):
    print('new connection_')
    tcp_connect = (await websocket.recv()).split(':')
    print(tcp_connect)
    tcp_connect[1] = int(tcp_connect[1])
    async with stream.Stream(*await asyncio.open_connection(*tcp_connect)) as sock:
        print('new connection')
        async def a():
            data=...
            while data:
                data = await sock.read(2**16)
                await websocket.send(data)
        async def s():
            data=...
            while data:
                try:
                    data = await websocket.recv()
                except websockets.ConnectionClosed:
                    data = ''
                sock.write(data)
                await sock.drain()
        await asyncio.gather(a(), s())


        

async def main():
    async with websockets.serve(connection, *http_listen):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
