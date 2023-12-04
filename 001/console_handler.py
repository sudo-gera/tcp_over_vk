import traceback
import aiohttp
import logging
import asyncio
import pprint
import dataclasses
import typing

import api
import storage
import local_file
import object
import remote_file
# import router
import local
import remote

@dataclasses.dataclass
class current_group:
    session: aiohttp.ClientSession
    API: api.API
    remote_storage: storage.Storage
    group_id: int

@dataclasses.dataclass
class current_pair:
    connect_id: int
    group: current_group

class console_handler():
    def __init__(self, group_id: int):
        self.group_id = group_id
        self.resources = self.resource_manager()
    
    async def ainit(self):
        await self.resources.asend(None)

    async def resource_manager(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            group_storage = storage.Storage(local_file.file(self.group_id))
            API = api.API(session, group_storage.token())
            async with await remote_file.file(API) as rem_file:
                remote_storage = storage.Storage(rem_file)
                self.group = current_group(
                    session = session,
                    remote_storage = remote_storage,
                    API = API,
                    group_id = self.group_id,
                )
                yield self

    async def __aenter__(self):
        return await anext(self.resources, 0)
    
    async def __aexit__(self, *a):
        return await anext(self.resources, 0)

    async def handle(self, args, stdout, stderr):
        try:
            args.connect_id = abs(args.connect_id)
            pair = current_pair(
                connect_id = args.connect_id,
                group = self.group,
            )
            chat = await remote.reach(pair)
            if chat.code in [0]:
                handlers: dict[str,tuple[typing.Callable, str]] = {
                    'L': (local, 'bind'),
                    'R': (remote, 'bind'),
                    'l': (local, 'del'),
                    'r': (remote, 'del'),
                }
                for arg in handlers:
                    if getattr(args, arg) is not None:
                        for forwarding in getattr(args, arg):
                            try:
                                await handlers[arg][0].call(
                                    pair, stdout, stderr,
                                    event = handlers[arg][1],
                                    forwarding = forwarding,
                                )
                            except TabError:
                                print('Cannot send', file=stderr)
                            except TimeoutError:
                                print('Timed out', file=stderr)
                # if args.meta is not None:
                #     res = await send.call(pair, object.Object(
                #         command = 'meta',
                #         value = args.meta,
                #     ))
                #     print(res.log, file = stderr)
            if chat.code in [1,2]:
                print(f'No response from remote device.', file=stderr)
                print(f'Is server running?', file=stderr)
                print(f'You can run `python3 main.py -g {args.connect_id}` on remote machine.', file=stderr)
                print(f'It will check server and start it, if nessesary.', file=stderr)
            if chat.code in [2]:
                print(file=stderr)
                print(f'Or maybe you have not completed these steps:', file=stderr)
                print(file=stderr)
            if chat.code in [2,3]:
                print(f'1. Open this link of the chat: {chat.link}', file=stderr)
                print(f'2. Join the chat "{chat.name}"', file=stderr)
                print(f'3. Open this link of the remote group https://vk.com/club{args.connect_id}', file=stderr)
                print(f'4. Invite this group to this chat', file=stderr)
                print(f'5. Run this command again', file=stderr)
            if args.list:
                print('Local forwardings:', file=stdout)
                await local.call(pair, stdout, stderr, event = 'list')
                print('Remote forwardings:', file=stdout)
                await remote.call(pair, stdout, stderr, event = 'list')

        except Exception:
            print(traceback.format_exc(), file=stderr)

