import socketio

class SingleConnection:
    def __init__(self, sio: socketio.AsyncClient | socketio.AsyncServer, sid: str) -> None:
        self.sio = sio
        self.sid = sid
    
    async def on_connect(self):
        ...

    async def on_message(self, data: bytes) -> None:
        ...

    async def on_disconnect(self) -> None:
        ...
