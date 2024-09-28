from asyncio import BaseTransport
from aiohttp import web
from multidict import CIMultiDict
from typing import *
from aiohttp.web_response import StreamResponse
from aiohttp.http_writer import StreamWriter
from aiohttp.web_server import Server

def cast_to_subclass(target: Any, wrapper: type):
    assert issubclass(wrapper, type(target))
    target.__class__ = wrapper
    assert isinstance(target, wrapper)
    return target

allowed_input_headers = [b'host', b'connection', b'upgrade', b'sec-websocket-key', b'sec-websocket-version']
allowed_output_headers = ['upgrade', 'connection', 'sec-websocket-accept']

class StreamWriterWrapper(StreamWriter):
    async def write_headers(self, status_line: str, headers: CIMultiDict[str]) -> None:
        headers = {
            k:v
            for k,v in headers.items()
            if k.lower() in allowed_output_headers
        }
        return await super().write_headers(status_line, headers)

class RequestHandlerWrapper(web.RequestHandler):
    def connection_made(self, transport: BaseTransport) -> None:
        self.vk_buffer = b''
        return super().connection_made(transport)

    def data_received(self, data: bytes) -> None:
        if self.vk_buffer is None:
            return super().data_received(data)
        self.vk_buffer += data
        if b'\r\n\r\n' not in self.vk_buffer:
            return
        self.vk_buffer, data = self.vk_buffer.split(b'\r\n\r\n', 1)
        headers = self.vk_buffer.split(b'\r\n')
        headers = [
            header
            for i,header in enumerate(headers)
            if i==0 or header.split(b':')[0].lower() in allowed_input_headers
        ]
        data = b'\r\n'.join(headers) + b'\r\n\r\n' + data
        self.vk_buffer = None
        return super().data_received(data)

class ServerWrapper(Server):
    def __call__(self) -> web.RequestHandler:
        return RequestHandlerWrapper(self, loop=self._loop, **self._kwargs)

class VKTunnelApplication(web.Application):
    async def _handle(self, request: web.Request) -> StreamResponse:
        cast_to_subclass(request._payload_writer, StreamWriterWrapper)
        return await super()._handle(request)

    def _make_handler(self, *a, **k) -> web.Server:
        return cast_to_subclass(super()._make_handler(*a, **k), ServerWrapper)
