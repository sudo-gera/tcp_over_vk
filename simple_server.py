from aiohttp import web
import socketio

sio = socketio.AsyncServer()

from vk_tunnel_server import VKTunnelApplication

app = VKTunnelApplication()
sio.attach(app)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def message(sid, data):
    print("message ", data)
    await sio.emit('message', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    web.run_app(app, port=8000)

