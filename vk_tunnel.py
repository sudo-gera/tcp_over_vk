import asyncio
import asyncio.subprocess
import contextlib
import re

import timeout

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
    
async def manage_process_once(executable: str, url_fut: asyncio.Future[str]):
    process = await asyncio.create_subprocess_exec(executable, stdout=asyncio.subprocess.PIPE)
    async with process_closer(process):
        data = b''
        while (new_chunk := await process.stdout.read(2**16)):
            print(new_chunk)
            if url_fut.done():
                continue # read whole stdout so process would not be blocked
            data += new_chunk
            urls : list[bytes] = re.findall(r'://\S+\.vk-apps\.com\b'.encode(), data)
            if urls:
                url_fut.set_result(urls[0].decode())
                data = None

class server:
    def __init__(self, executable: str):
        self.executable = executable
        self.url : str

    async def __aenter__(self):
        has_url_fut = asyncio.Future()
        self.manager = asyncio.create_task(self.manage(has_url_fut))
        await has_url_fut

    async def __aexit__(self, *a):
        self.manager.cancel()
        await self.manager

    async def manage(self, has_url_fut: asyncio.Future[None]):
        while 1:
            url_fut = asyncio.Future()
            process_manager = asyncio.create_task(manage_process_once(self.executable, url_fut))
            try:
                self.url = await url_fut
                await process_manager
            finally:
                process_manager.cancel()
                await process_manager

async def main():
    url_fut = asyncio.Future()
    m = asyncio.create_task(manage_process_once('vk-tunnel', url_fut))
    print(await url_fut)
    await m


if __name__ == '__main__':
    asyncio.run(main())
