import asyncio
import traceback
import logging
import json
import io

import base128
import object
import remote
import event_handler
import local

@event_handler.handle('join')
async def on_join(pair, event):
    await remote.send(pair, event='greet')

@event_handler.handle('greet')
async def on_greet(pair, event):
    pass

async def on_message_event(group, message):
    try:
        for attachment in message.attachments:
            url = attachment[attachment.type].url
            async with group.session.get(url) as resp:
                assert resp.status == 200
                message.text += ' '
                message.text += resp.read().decode()

        if 'action' in message and message.action.type.startswith('chat_invite_user'):
            if 'member_id' in message.action and -group.group_id != message.action.member_id < 0 :
                message.from_id = message.action.member_id
                event = object.Object(event = 'join')
            else:
                user_id = getattr(message.action, 'member_id', message.from_id)
                if group.remote_storage.pending[message.peer_id]:
                    await group.API.messages.send(
                        peer_id = message.peer_id, random_id = 0,
                        message = f"Welcome @id{user_id}!\n"
                            f"It is time to invite @club{group.remote_storage.pending[message.peer_id]()} here to complete a connection!")
                return

        if message.from_id > 0:
            return
        if message.text:
            assert message.from_id < 0
            if group.remote_storage.pending[message.peer_id](default = None) == -message.from_id:
                async with group.remote_storage as safe_storage:
                    del safe_storage.pending[message.peer_id]
            text = message.text.split(' ', 1)
            if len(text) != 2:
                return
            if not (text[0] == '@all' or text[0].startswith(f'[club{group.group_id}|')):
                return
            if group.remote_storage.route[-message.from_id](default = None) != message.peer_id:
                async with group.remote_storage as safe_storage:
                    safe_storage.route[-message.from_id] = message.peer_id
            text = text[1]
            text = base128.decode(text)
            binary = None
            if b'\0' in text:
                text, binary = text.split(b'\0', 1)
            event = object.build(json.loads(text))
            if binary is not None:
                event.binary = binary

        pair = object.Object(
            group = group,
            connect_id = -message.from_id
        )
        await local.send(pair, event)

    except Exception:
        err = traceback.format_exc()
        logging.error(err)

async def handling_vk_events_loop(group):
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
                        asyncio.create_task(on_message_event(group, message))
        except Exception:
            err = traceback.format_exc()
            logging.error(err)
            await asyncio.sleep(1)


