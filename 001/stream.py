from __future__ import annotations
import asyncio

class Stream(asyncio.StreamReader, asyncio.StreamWriter):
    def __init__(self, reader, writer):
        self.__reader = reader
        self.__writer = writer

    def __dir__(self):
        return dir(self.__reader) + dir(self.__writer)

    def __getattribute__(self, name:str):
        if name.startswith(f'_Stream_'):
            return super().__getattribute__(name)
        a = [w for w in [self.__reader, self.__writer] if name in dir(w)]
        assert len(a) == 1, name
        return getattr(a[0], name)

    def __repr__(self):
        return repr((self.__reader, self.__writer))

    async def __aenter__(self) -> Stream:
        return self

    async def __aexit__(self, *a):
        await self.drain()
        if self.can_write_eof():
            self.write_eof()
        self.close()
        await self.wait_closed()

    def __del__(self):
        pass
