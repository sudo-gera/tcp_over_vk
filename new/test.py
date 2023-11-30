import aiohttp
import asyncio
import pprint
import time
import itertools

import group_api
import object

async def main():
    async with aiohttp.ClientSession(trust_env=1) as session:
        api = await group_api.API(session, group_id=218700852)
        # print(await api.api.storage.set(key=1, value=2, user_id=225847803))
        # for c in itertools.count():
        #     await asyncio.sleep(1)
        #     message_id = await api.api.messages.send(peer_id=2000000001, random_id=0, message=f'{time.asctime()}')
        #     print(message_id)
        #     try:
        #         print(await api.api.messages.send_reaction(peer_id=2000000001, cmid=11, reaction_id=1))
        #     except Exception:
        #         pass
            # await api.api.messages.edit(peer_id=2000000001, random_id=0, message=f'{time.asctime()}', message_id=message_id)
            # await api.api.messages.edit(peer_id=2000000001, random_id=0, message=f'{time.asctime()}', message_id=16058)
        # res = await api.api.groups.get_long_poll_server(group_id=api.group.id)
        # key, server, ts = res.key, res.server, res.ts
        # while 1:
        #     async with session.get(f'{server}?act=a_check&key={key}&ts={ts}&wait=1') as resp:
        #         res = object.build(await resp.json())
        #         ts, updates = res.ts, res.updates
        #         for update in updates:
        #             pprint.pprint(object.destroy(update))

if __name__ == '__main__':
    asyncio.run(main())

