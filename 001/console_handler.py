import traceback
import aiohttp
import logging
import asyncio
import pprint

import api
import storage
import local_file
import object
import remote_file
import router
import tcp
import send

class console_handler():
    def __init__(self, group_id):
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
                self.group = object.Object(
                    remote_storage = remote_storage,
                    API = API,
                    group_id = self.group_id,
                )
                yield

    async def handle(self, args, stdout, stderr):
        try:
            if isinstance(args.connect_id, int):
                args.connect_id = abs(args.connect_id)
                chat = await send.reach(self.group, args.connect_id)
                if chat.code in [0]:
                    if args.L is not None:
                        for forwarding in args.L:
                            res = await tcp.event(
                                object.Object(
                                    command = 'bind',
                                    forwarding = forwarding,
                                )
                            )
                            print(res.log, file = stderr)
                    if args.l is not None:
                        for forwarding in args.l:
                            await tcp.event(
                                object.Object(
                                    command = 'del',
                                    forwarding = forwarding,
                                )
                            )
                            print(res.log, file = stderr)
                    if args.R is not None:
                        for forwarding in args.R:
                            res = await send.call(self.group, args.connect_id, object.Object(
                                command = 'bind',
                                forwarding = forwarding,
                            ))
                            print(res.log, file = stderr)
                    if args.r is not None:
                        for forwarding in args.r:
                            res = await send.call(self.group, args.connect_id, object.Object(
                                command = 'del',
                                forwarding = forwarding,
                            ))
                            print(res.log, file = stderr)
                    if args.meta is not None:
                        res = await send.call(self.group, args.connect_id, object.Object(
                            command = 'meta',
                            value = args.meta,
                        ))
                        print(res.log, file = stderr)
                    # await asyncio.sleep(4)
                    # await send.send(self.group, args.connect_id, object.Object(
                    #     command = 'args',
                    #     args = args,
                    # ))
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
        except Exception:
            print(traceback.format_exc(), file=stderr)

