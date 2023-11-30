import aiohttp

import group_api

def route(session: aiohttp.ClientSession, api: group_api.API):
    ...

import aiohttp
import asyncio
import pprint

import group_api
import object

async def get_route(api: group_api.API, peer_id: str|int):
    if not api.storage.channel_by_id[peer_id]:
        ...
        a = await api.api.messages.get_conversations(count=100)
        pprint.pprint(object.destroy(a))
        # api.storage.channel_by_id[peer_id]
    return api.storage.channel_by_id[peer_id]()
    
async def main():
    async with aiohttp.ClientSession() as session:
        api = await group_api.API(session, group_id=218700852)
        await get_route(api, 0)

if __name__ == '__main__':
    asyncio.run(main())
