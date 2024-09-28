import asyncio
import socketio

sio = socketio.AsyncClient(ssl_verify=False)

@sio.event
async def connect():
    print('connection established')

@sio.event
async def message(data):
    print('message received with ', data)

@sio.event
async def disconnect():
    print('disconnected from server')

async def sender():
    while 1:
        await asyncio.sleep(1)
        await sio.send('123')

async def main():
    await sio.connect('https://user225847803-yybmoqi2.wormhole.vk-apps.com/', transports=['websocket'])
    asyncio.create_task(sender())
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
