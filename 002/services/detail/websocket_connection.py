from weakref import WeakValueDictionary

import socketio
import time

class WebsocketConnection:
    def __init__(self, sio : socketio.AsyncClient | socketio.AsyncServer, sid: str) -> None:
        self.sio = sio
        self.sid = sid
        self.last_received_ping = time.time_ns()

    async def on_connect(self):
        ...

    async def on_message(self, data: bytes):
        ...

    async def on_disconnect(self):
        ...

    async def pinger(self):
        while 1:
            t = self.small_time()
            self.sio.send(t.to_bytes(2, 'big'))
            await asyncio.sleep()

    def small_time(self):
        return (time.time_ns() >> 27) & ((1 << 16) - 2)

import socketio

