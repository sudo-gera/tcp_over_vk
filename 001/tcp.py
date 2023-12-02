import asyncio
import json
import functools
import base64
import itertools
import logging
import traceback
import typing

import stream
import send
import make_id
import object

servers = {}
connections: dict[int, typing.AsyncGenerator] = {}

async def connection(pair, forwarding, reader, writer, q = None, connection_id = None):
    try:
        connection_id = make_id.make_id() if connection_id is None else connection_id
        connections[connection_id] = connection_loop(pair, reader, writer)
        if q is not None:
            q.put_nowait(None)
        sock = await connections[connection_id].asend(None)
        for num in itertools.count():
            data = await sock.read(2**8)
            if not await send.data(pair,
                data = base64.b64encode(data).decode(),
                num = num,
                connection_id = connection_id,
                forwarding = forwarding,
            ):
                await connections[connection_id].aclose()
                break
            if not data:
                break
    except Exception:
        err = traceback.format_exc()
        logging.error(err)

async def connection_loop(pair, reader, writer):
    try:
        async with stream.Stream(reader, writer) as sock:
            waiting_for = 0
            messages = []
            while 1:
                message = yield sock
                messages.append(message)
                messages.sort(key = lambda message: message.num)
                while messages:
                    message = messages[0]
                    if message.num == waiting_for:
                        messages = messages[1:]
                        sock.write(base64.b64decode(message.data))
                        await sock.drain()
                        if not message.data:
                            messages.extend(range(512))
                            break
                        waiting_for += 1
                    else:
                        break
                if len(messages) > 256:
                    break
    except Exception:
        err = traceback.format_exc()
        logging.error(err)

async def on_remote_connection_event(pair, message):
    if message.connection_id not in connections:
        reader, writer = await asyncio.open_connection(message.forwarding[1].host, message.forwarding[1].port)
        q: asyncio.Queue[None] = asyncio.Queue()
        asyncio.create_task(connection(pair, message.forwarding, reader, writer, q, message.connection_id))
        await q.get()
    connection_gen = connections[message.connection_id]
    try:
        await connection_gen.asend(message)
    except StopAsyncIteration:
        pass

async def add(forwarding, stderr, pair):
    server = await asyncio.start_server(
        functools.partial(connection, pair, forwarding),
        forwarding[0].host,
        forwarding[0].port,
    )
    servers[json.dumps([forwarding, pair.connect_id])] = server
    asyncio.create_task(serve_forever(server, forwarding, pair))

async def serve_forever(server: asyncio.Server, forwarding, pair):
    async with server:
        try:
            await server.serve_forever()
        finally:
            server.close()
            await server.wait_closed()
            del servers[json.dumps([forwarding, pair.connect_id])]
            

def repr_forwarding(forwarding):
    return f'{forwarding[0].host}:{forwarding[0].port}:{forwarding[1].host}:{forwarding[1].port}'

async def remove(forwarding, stderr, pair):
    try:
        server = servers[json.dumps([forwarding, pair.connect_id])]
    except KeyError:
        print(f'No such forwarding: {repr_forwarding(forwarding)}', file=stderr)
        return
    server.close()
    await server.wait_closed()

async def print_all(stderr, pair):
    for forwarding in servers:
        forwarding = object.build(json.loads(forwarding))
        if forwarding[1] == pair.connect_id:
            print(repr_forwarding(forwarding[0]), file=stderr)
