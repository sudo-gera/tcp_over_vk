import json
import base64
import pprint
import asyncio
import time
import secrets
import fractions
import logging

import object
import timeout

async def reach(group, connect_id):
    res = await call(group, connect_id, command = 'ping')
    if isinstance(res, dict):
        return object.Object(
            code = 0,
        )
    if res is ...:
        route = group.remote_storage.route[connect_id]()
        if group.remote_storage.pending[route](default = None) == connect_id:
            try:
                members = await group.API.messages.get_conversation_members([], peer_id = route)
                for member in members.items:
                    if member.member_id == -connect_id:
                        # await remove_pending(group, route, connect_id)
                        break
                else:
                    raise TabError
            except TabError:
                name = f'{group.group_id} <--> {connect_id}'
                link = (await group.API.messages.get_invite_link(peer_id = route, reset = 0)).link
                return object.Object(
                    code = 2,
                    link = link,
                    name = name,
                )
        return object.Object(
            code = 1,
        )
    name = f'{group.group_id} <--> {connect_id}'
    new_chat = (await group.API.messages.create_chat(title=name)).chat_id
    new_chat += 2000000000
    async with group.remote_storage as safe_storage:
        safe_storage.pending[new_chat] = connect_id
        safe_storage.route[connect_id] = new_chat
    link = (await group.API.messages.get_invite_link(peer_id = new_chat, reset = 0)).link
    return object.Object(
        code = 3,
        link = link,
        name = name,
    )


async def send(group, connect_id, message = {}, **args):
    message = object.destroy(message) | args
    message = json.dumps(message).encode()
    message = base64.b16encode(message).decode()
    message = f'@club{connect_id} {message}'
    route = group.remote_storage.route[connect_id](default = None)
    if route is None:
        return False
    try:
        await group.API.messages.send(
            random_id = 0,
            peer_id = route,
            message = message,
        )
        return True
    except TabError:
        return False
    
callers = {}
async def call(group, connect_id, message = {}, **args):
    message = object.destroy(message) | args
    caller_id = secrets.randbelow(2**64) + time.time_ns() * 2**64
    q = asyncio.Queue()
    callers[caller_id] = q
    try:
        if await send(group, connect_id, data = message, command = 'ping', caller_id = caller_id):
            try:
                a = await timeout.get_with_timeout(q, 8)
                return a
            except TimeoutError:
                return ...
    finally:
        del callers[caller_id]
