async def client():
    async with socketio.AsyncSimpleClient() as sio:
        @sio.event