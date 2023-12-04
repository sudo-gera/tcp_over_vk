import json
import base64
import pprint
import asyncio
import time
import secrets
import fractions
import logging
import aiohttp
import functools
import io

import object
import timeout
import make_id
import base128
import event_handler

@event_handler.handle('ping')
async def on_ping(pair, event, stdout, stderr):
    return {}

async def reach(pair):
    try:
        res = await call(pair, io.StringIO(), io.StringIO(), event = 'ping')
        return object.Object(
            code = 0,
        )
    except TimeoutError:
        route = pair.group.remote_storage.route[pair.connect_id]()
        if pair.group.remote_storage.pending[route](default = None) == pair.connect_id:
            try:
                members = await pair.group.API.messages.get_conversation_members([], peer_id = route)
                for member in members.items:
                    if member.member_id == -pair.connect_id:
                        # await remove_pending(group, route, connect_id)
                        break
                else:
                    raise TabError
            except TabError:
                name = f'{pair.group.group_id} <--> {pair.connect_id}'
                link = (await pair.group.API.messages.get_invite_link(peer_id = route, reset = 0)).link
                return object.Object(
                    code = 2,
                    link = link,
                    name = name,
                )
        return object.Object(
            code = 1,
        )
    except TabError:
        # assert False
        route = pair.group.remote_storage.route[pair.connect_id](default = None)
        if route is not None:
            if pair.group.remote_storage.pending[route]:
                async with pair.group.remote_storage as safe_storage:
                    del safe_storage.pending[route]
        name = f'{pair.group.group_id} <--> {pair.connect_id}'
        new_chat = (await pair.group.API.messages.create_chat(title=name)).chat_id
        new_chat += 2000000000
        async with pair.group.remote_storage as safe_storage:
            safe_storage.pending[new_chat] = pair.connect_id
            safe_storage.route[pair.connect_id] = new_chat
        link = (await pair.group.API.messages.get_invite_link(peer_id = new_chat, reset = 0)).link
        return object.Object(
            code = 3,
            link = link,
            name = name,
        )

until_ping = 0
send_lock = asyncio.Lock()

async def send(pair, message = {}, **args):
    message = object.destroy(message) | args
    binary = None
    if 'binary' in message:
        # async with send_lock:
        #     global until_ping
        #     if until_ping == 0:
        #         await call(pair, io.StringIO(), io.StringIO(), event = 'ping')
        #         until_ping += 16
        #     else:
        #         until_ping -= 1
        binary = message['binary']
        del message['binary']
    message = json.dumps(message).encode()
    if binary is not None:
        message += b'\0' + binary
    route = pair.group.remote_storage.route[pair.connect_id](default = None)
    if route is None:
        return False
    if 1:
        message = base128.encode(message)
        message = f'@club{pair.connect_id} {message}'
        try:
            await pair.group.API.messages.send(
                random_id = 0,
                peer_id = route,
                message = message,
            )
            return True
        except TabError:
            return False
    else:
        print(await pair.group.API.groups.get_token_permissions())
        url = (await pair.group.API.docs.get_upload_server()).upload_url
        session: aiohttp.ClientSession
        session = pair.group.session
        filename = f'{make_id.make_id()}.txt'
        with aiohttp.MultipartWriter('form-data') as writer:
            part = writer.append(message)
            part.set_content_disposition('form-data', filename = filename, name = 'file')
            async with session.post(url, data = writer) as resp:
                assert resp.status == 200
                res = object.build(await resp.json())
        file = await pair.group.API.docs.save(file = res.file, title = filename)
        print(file)
        message = f'@club{pair.connect_id}'
        await pair.group.API.messages.send(
            random_id = 0,
            peer_id = route,
            message = message,
            attachment = f'doc{file.doc.owner_id}_{file.doc.id}'
        )
        return True
            
async def on_return(q, stdout, stderr, pair, event):
    stdout.write(event.stdout)
    stderr.write(event.stderr)
    q.put_nowait(event.value)

async def call(pair, stdout, stderr, message = {}, **args):
    link = make_id.make_id()
    q: asyncio.Queue[dict] = asyncio.Queue()
    event_handler.event_handlers[link] = functools.partial(on_return, q, stdout, stderr)
    args['link'] = link
    try:
        if not await send(pair, message, **args):
            raise TabError
        a = await timeout.get_with_timeout(q, 8)
        return a
    finally:
        del event_handler.event_handlers[link]
        

# callers = {}
# async def call(pair, message = {}, **args):
#     message = object.destroy(message) | args
#     caller_id = make_id.make_id()
#     q: asyncio.Queue[dict] = asyncio.Queue()
#     callers[caller_id] = q
#     try:
#         if await send(pair, data = message, command = 'ping', caller_id = caller_id):
#             try:
#                 a = await timeout.get_with_timeout(q, 8)
#                 return a
#             except TimeoutError:
#                 return ...
#     finally:
#         del callers[caller_id]

# async def data(pair, message = {}, **args):
#     message = object.destroy(message) | args
#     return await send(pair, command = 'data', data = object.Object(
#         command = 'tcp',
#         data = message
#     ))
