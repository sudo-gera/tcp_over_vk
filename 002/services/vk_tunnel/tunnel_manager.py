from __future__ import annotations
import asyncio
import asyncio.subprocess
import contextlib
import re

import utils.timeout as timeout

@contextlib.asynccontextmanager
async def process_closer(process: asyncio.subprocess.Process):
    try:
        yield process
    finally:
        while process.returncode is None:
            try:
                process_kill()
            except NameError:
                process_kill = process.kill
                process.terminate()
            try:
                await timeout.run_with_timeout(process.wait(), 4)
            except TimeoutError:
                pass

async def manage_process_once(executable: str, url_fut: asyncio.Future[str], port: int) -> None:
    try:
        process = await asyncio.create_subprocess_exec(executable, '--timeout=999999999', f'--port={port}', stdout=asyncio.subprocess.PIPE)
        async with process_closer(process):
            data = b''
            while (new_chunk := await process.stdout.read(2**16)):
                if url_fut.done():
                    continue # read whole stdout so process would not be blocked
                data += new_chunk
                urls : list[bytes] = re.findall(r'://\S+\.vk-apps\.com\b'.encode(), data)
                if urls:
                    url_fut.set_result(urls[0].decode())
                    data = None
    finally:
        if not url_fut.done():
            url_fut.set_exception(TabError)

class process_manager:
    def __init__(self):
        self.process_task : asyncio.Task | None = None
        self.worker_task : asyncio.Task | None = None

    async def worker(self):
        ...

    async def __ainit__(self):
        self.worker_task = asyncio.create_task(self.worker())

    async def __aexit__(self, *a, **s):
        self.worker_task.cancel()
        try:
            await self.worker_task
        except asyncio.CancelledError:
            pass

import socketio

class ClientWorker:
    def __init__(self, connection: Connection, url: str):
        self.connection = connection
        self.sio = socketio.AsyncClient()
        self.url = url
        self.sio.event(self.connect)
        self.sio.event(self.connect_error)
        self.sio.event(self.message)
        self.sio.event(self.disconnect)

    def connect(self):
        pass
    
    def connect_error(self):
        pass
    
    def message(self, data):
        pass
    
    def disconnect(self):
        pass

    async def main(self):
        while 1:
            await self.sio.connect(self.url)


class Connection:
    ...




# async def manage_process_until_url(executable: str, port: int) -> tuple[str, asyncio.Task[None]]:
#     while True:
#         url_fut : asyncio.Future[str] = asyncio.Future()
#         process = asyncio.create_task(manage_process_once(executable, url_fut, port))
#         with contextlib.suppress(Cancelle)
#         try:
#             url = await url_fut
#             return url, process
#         except TabError:
#             await asyncio.sleep(4)


    






