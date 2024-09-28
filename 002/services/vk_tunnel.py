from argparse import ArgumentParser
import detail.server
import asyncio
import detail.tunnel_manager
import services.base_service
from typing import Any, Literal
import detail

class VKTunnel(services.base_service.BaseService):
    def __init__(self, command: dict[str, Any]) -> None:
        self.executable : str = command['vk_tunnel']
        self.mode : Literal['server', 'client'] = command['mode']
        self.connections : int = command['connections']
        self.url : str | None = None
        self.process : asyncio.Task | None = None
        self.new_url_request : asyncio.Queue[None] = asyncio.Queue()
        self.work_request : asyncio.Queue[None] = asyncio.Queue()
        super().__init__()
    
    async def main(self):
        async with detail.server.server() as port:
            await asyncio.gather(
                self.tunnel_manager(port),

            )

    async def tunnel_manager(self, port):
        while 1:
            url, process = await detail.tunnel_manager.manage_process_until_url(self.executable, port)
            self.url = url
            self.tunnel = process
            for q in range(self.connections):
                await self.new_url_request.get()

    async def worker(self):
        while 1:
            url = self.url
            if url is None:
                await asyncio.sleep(1)
                continue
            else:
                async with socketio.AsyncSimpleClient() as sio:
                    














class vk_tunnel(services.base_service.start):
    @classmethod
    async def add_arguments(cls, parser: ArgumentParser) -> None:
        if cls is vk_tunnel:
            parser.add_argument('--vk-tunnel', help='path to vk-tunnel executable', default='vk-tunnel')
            parser.add_argument('--mode', choices=['server', 'client'], default='client', help="Client may temporary turn itself into server if nessesary. Default is client.")
            parser.add_argument('--connections', type=int, default=16, help="Websocket connections to deliver data.")
        return await super().add_arguments(parser)

    @classmethod
    async def exec_command(cls, command: dict[str, Any], stdout: services.base_service.StringIO, stderr: services.base_service.StringIO) -> int | None:
        vk = VKTunnel()
        

