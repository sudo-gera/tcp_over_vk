from __future__ import annotations
from io import StringIO
from commands.global_command import GlobalCommand
from abc import ABC, abstractmethod
import asyncio
import traceback
from typing import *
import utils
import utils.get_subclasses
import secrets

class BaseService(ABC):
    def __init__(self) -> None:
        services.add(self)
        self.service_id = secrets.token_hex(4)
        self.main_task = asyncio.create_task(self.main_restarter())
        self.status : Literal['active', 'failed', 'exited'] = 'active'
        self.exc : str | None = None

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, value: object) -> bool:
        return self is value

    async def main_restarter(self) -> None:
        while 1:
            try:
                self.status = 'active'
                self.exc = None
                await self.main()
                self.status = 'exited'
            except Exception:
                self.status = 'failed'
                self.exc = traceback.format_exc()
            await asyncio.sleep(1)

    @abstractmethod
    async def main(self) -> None:
        ...

services : set[BaseService] = set()

class start(GlobalCommand):
    pass

class stop(GlobalCommand):
    pass

class restart(GlobalCommand):
    pass

class list(GlobalCommand):
    @classmethod
    async def exec_command(cls, command: dict[str, Any], stdout: StringIO, stderr: StringIO) -> int | None:
        for service in services:
            print(f'{service.service_id}\t{service.__class__.__name__}\t{service.status}')
        return await super().exec_command(command, stdout, stderr)

class list_exc(GlobalCommand):
    @classmethod
    async def exec_command(cls, command: dict[str, Any], stdout: StringIO, stderr: StringIO) -> int | None:
        for service in services:
            print(f'{service.service_id}\t{service.__class__.__name__}\t{service.status}')
            if service.exc is not None:
                lines = service.exc.splitlines(keepends=True)
                lines = [service.service_id + line for line in lines]
                exc = ''.join(lines)
                print(exc)
        return await super().exec_command(command, stdout, stderr)

