import json
import base64
import pprint
import asyncio
import time
import secrets
import fractions
import logging
import traceback

import object
import timeout
import send
import event

assert False

async def add_to_list(location, value):
    values = location(default = [])
    if value not in values:
        values.append(value)
        async with location as safe_location:
            safe_location(values)

async def remove_pending(group, peer_id, group_id):
    group_id = abs(group_id)
    if group.remote_storage.pending[peer_id](default = None) == group_id:
        async with group.remote_storage as safe_storage:
            del safe_storage.pending[peer_id]

async def process_pending_user(group, user_id, peer_id):
    if group.remote_storage.pending[peer_id]:
        await group.API.messages.send(
            peer_id = peer_id, random_id = 0,
            message = f"Welcome @id{user_id}!\n"
                f"It is time to invite @club{group.remote_storage.pending[peer_id]()} here to complete a connection!")

async def on_message_from_group(group, message):
    assert message.from_id < 0
    await remove_pending(group, message.peer_id, -message.from_id)
    text = message.text.split(' ', 1)
    if len(text) != 2:
        return
    if not (text[0] == '@all' or text[0].startswith(f'[club{group.group_id}|')):
        return
    if group.remote_storage.route[-message.from_id](default = None) != message.peer_id:
        async with group.remote_storage as safe_storage:
            safe_storage.route[-message.from_id] = message.peer_id
    text = text[1]
    data = object.build(json.loads(base64.b16decode(text)))
    await on_decoded_message_from_group(group, data, message)

async def on_decoded_message_from_group(group, data, message):
    await remove_pending(group, message.peer_id, -message.from_id)
    pair = object.Object(
        group = group,
        connect_id = -message.from_id,
    )
    if data.command == 'ping':
        data.data = await event.event(pair, data.data)
        await send.send(pair, data, command = 'pong')
    if data.command == 'pong':
        if data.caller_id in send.callers:
            send.callers[data.caller_id].put_nowait(data.data)
    if data.command == 'join':
        await send.send(pair, data, command = 'greet')
    if data.command == 'greet':
        pass
    if data.command == 'args':
        pprint.pprint(object.destroy(data))
    if data.command == 'data':
        await event.event(pair, data.data)

async def on_message_event(group, message):
    try:
        if 'action' in message and message.action.type.startswith('chat_invite_user'):
            if 'member_id' in message.action and -group.group_id != message.action.member_id < 0 :
                message.from_id = message.action.member_id
                await on_decoded_message_from_group(group, object.Object(
                    command = 'join'
                ), message)
                return
            else:
                await process_pending_user(group, getattr(message.action, 'member_id', message.from_id), message.peer_id)
        if message.from_id < 0:
            await on_message_from_group(group, message)
    except Exception:
        err = traceback.format_exc()
        logging.error(err)

async def vk_input_messages_handler(group):
    while True:
        try:
            result = await group.API.groups.get_long_poll_server(group_id=group.group_id)
            key, server, ts = result.key, result.server, result.ts
            while True:
                async with group.session.get(f'{server}?act=a_check&key={key}&ts={ts}&wait=25') as resp:
                    assert resp.status == 200
                    res = object.build(await resp.json())
                if 'updates' not in res:
                    break
                ts, updates = res.ts, res.updates
                for update in updates:
                    if update.type == 'message_new':
                        message = update.object.message
                        # pprint.pprint(object.destroy(message))
                        for attachment in message.attachments:
                            url = attachment[attachment.type].url
                            async with group.API.session.get(url) as resp:
                                assert resp.status == 200
                                message += ' '
                                message += resp.read().decode()
                        # print(message)
                        asyncio.create_task(on_message_event(group, message))
                        # await on_message_event(group, message)
                        # pprint.pprint(group.remote_storage._Storage__file.db)
        except Exception:
            err = traceback.format_exc()
            logging.error(err)
            await asyncio.sleep(1)