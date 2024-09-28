from aiohttp import web
import socketio
from vk_tunnel_server import VKTunnelApplication

from contextlib import asynccontextmanager
import random

from websocket_connection import WebsocketConnection

connections : dict[str, WebsocketConnection] = {}

@asynccontextmanager
async def server():
    port = random.randint(1025, 65535)

    sio = socketio.AsyncServer()
    app = VKTunnelApplication()
    sio.attach(app)

    @sio.event
    async def connect(sid: str, environ: object):
        connections[sid] = WebsocketConnection(sio, sid)
        await connections[sid].on_connect()

    @sio.event
    async def message(sid, data):
        await connections[sid].on_message(data)

    @sio.event
    async def disconnect(sid):
        await connections[sid].on_disconnect()

    runner = web.AppRunner(app)
    try:
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', port)
        await site.start()
        yield port
    finally:
        await runner.cleanup()

