import asyncio
import websockets

import stream

import sys

if len(sys.argv)==3:
    http_listen=None
    http_connect=sys.argv[2]
    tcp_connect=(':'+sys.argv[1]).split(':')[-4:]
    tcp_listen,tcp_connect=tcp_connect[:2],tcp_connect[2:]
    tcp_listen[1] = int(tcp_listen[1])
else:
    print(f'''to start client: {sys.argv[0]} [tcp-listen-host:]tcp-listen-port:tcp-remote-host:tcp-remote-port ws(s)://-started-url''')
    exit(1)

async def connection(reader, writer):
    async with stream.Stream(reader, writer) as sock:
        async with websockets.connect(http_connect, ssl=False) as websocket:
            await websocket.send(':'.join(tcp_connect))
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
                        data = b''
                    sock.write(data)
                    await sock.drain()
            await asyncio.gather(a(), s())


async def main():
    async with await asyncio.start_server(connection, *tcp_listen) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
