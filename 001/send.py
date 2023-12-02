import json
import base64
import pprint
import asyncio
import time
import secrets
import fractions
import logging
import aiohttp

import object
import timeout
import make_id

async def reach(pair):
    res = await call(pair, command = 'ping')
    if isinstance(res, dict):
        return object.Object(
            code = 0,
        )
    if res is ...:
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


async def send(pair, message = {}, **args):
    message = object.destroy(message) | args
    message = json.dumps(message).encode()
    message = ''.join([f'{q:08b}' for q in message])
    ...
    message = base64.b16encode(message).decode()
    route = pair.group.remote_storage.route[pair.connect_id](default = None)
    if route is None:
        return False
    if 1 or len(message) < 8192:
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
    # else:
    #     url = (await pair.group.API.docs.get_messages_upload_server(peer_id = route)).upload_url
    #     session: aiohttp.ClientSession
    #     session = pair.group.session
    #     filename = f'{make_id.make_id()}.txt'
    #     with aiohttp.MultipartWriter('form-data') as writer:
    #         part = writer.append(message)
    #         part.set_content_disposition('form-data', filename=filename, name='file')
    #         async with session.post(url, data = writer) as resp:
    #             assert resp.status == 200
    #             res = object.build(await resp.json())
    #     file = await pair.group.API.docs.save(file = res.file, title = filename)
    #     print(file)
    #     message = f'@club{pair.connect_id}'
    #     await pair.group.API.messages.send(
    #         random_id = 0,
    #         peer_id = route,
    #         message = message,
    #         attachment = f'doc{file.doc.owner_id}_{file.doc.id}'
    #     )
    #     return True
            


        
        

callers = {}
async def call(pair, message = {}, **args):
    message = object.destroy(message) | args
    caller_id = make_id.make_id()
    q: asyncio.Queue[dict] = asyncio.Queue()
    callers[caller_id] = q
    try:
        if await send(pair, data = message, command = 'ping', caller_id = caller_id):
            try:
                a = await timeout.get_with_timeout(q, 8)
                return a
            except TimeoutError:
                return ...
    finally:
        del callers[caller_id]

async def data(pair, message = {}, **args):
    message = object.destroy(message) | args
    return await send(pair, command = 'data', data = object.Object(
        command = 'tcp',
        data = message
    ))
