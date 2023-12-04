import asyncio
import json
import functools
import base64
import itertools
import logging
import traceback
import typing
import io
import collections

import stream
import remote
import make_id
import object
import event_handler

servers = {}
connections: dict[int, tuple[asyncio.Task, typing.AsyncGenerator]] = {}
dead = collections.deque()


async def connection(pair, forwarding, reader, writer, q = None, connection_id = None):
    try:
        connection_id = make_id.make_id() if connection_id is None else connection_id
        connections[connection_id] = (
            asyncio.current_task(),
            connection_loop(pair, reader, writer, connection_id)
        )
        if q is not None:
            q.put_nowait(None)
        sock = await connections[connection_id][1].asend(None)
        for num in itertools.count():
            data = await sock.read(2**11)
            if not await remote.send(pair,
                binary = data,
                num = num,
                connection_id = connection_id,
                forwarding = forwarding,
                event = 'tcp',
            ):
                await connections[connection_id][1].aclose()
                break
            if not data:
                break
    except Exception:
        err = traceback.format_exc()
        logging.error(err)

async def connection_loop(pair, reader, writer, connection_id):
    exc = None
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
                        # sock.write(base64.b64decode(message.data))
                        sock.write(message.binary)
                        await sock.drain()
                        if not message.binary:
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
    except asyncio.CancelledError as _exc:
        exc = _exc
    dead.append(connection_id)
    if len(dead) > 4096:
        dead.popleft()
    connections[connection_id][0].cancel()
    del connections[connection_id]
    if exc is not None:
        raise exc

@event_handler.handle('kill')
async def on_kill(pair, message):
    if message.connection_id in connections:
        await connections[message.connection_id].aclose()

@event_handler.handle('tcp')
async def on_remote_connection_event(pair, message):
    if message.connection_id in dead:
        await remote.send(pair, event='kill', connection_id = message.connection_id)
        return
    if message.connection_id not in connections:
        reader, writer = await asyncio.open_connection(message.forwarding[1].host, message.forwarding[1].port)
        q: asyncio.Queue[None] = asyncio.Queue()
        asyncio.create_task(connection(pair, message.forwarding, reader, writer, q, message.connection_id))
        await q.get()
    connection_gen = connections[message.connection_id]
    try:
        # asyncio.create_task(connection_gen[1].asend(message))
        await connection_gen[1].asend(message)
    except StopAsyncIteration:
        pass
    return True

@event_handler.handle('bind')
async def on_bind(pair, stdout, stderr, message):
    server = await asyncio.start_server(
        functools.partial(connection, pair, message.forwarding),
        message.forwarding[0].host,
        message.forwarding[0].port,
    )
    servers[json.dumps([message.forwarding, pair.connect_id])] = server
    asyncio.create_task(serve_forever(server, message.forwarding, pair))

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

@event_handler.handle('del')
async def on_del(pair, stdout, stderr, message):
    try:
        server = servers[json.dumps([message.forwarding, pair.connect_id])]
    except KeyError:
        print(f'No such forwarding: {repr_forwarding(message.forwarding)}', file=stderr)
        return
    server.close()
    await server.wait_closed()

@event_handler.handle('list')
async def on_list(pair, stdout, stderr, message):
    for forwarding in servers:
        forwarding = object.build(json.loads(forwarding))
        if forwarding[1] == pair.connect_id:
            print(repr_forwarding(forwarding[0]), file=stdout)
