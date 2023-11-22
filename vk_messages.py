import urllib.parse
import aiohttp
import pprint
import asyncio
import json

import storage
import vk_lib


async def check_token(session,group_id):
    token = storage.storage[group_id].token
    if isinstance(token, storage.Storage):
        return
    api = API(session, token)
    perms = await api.groups.get_token_permissions()
    if {'name': 'messages', 'setting': 4096} not in perms.permissions:
        del storage.storage[group_id].token
        return
    gid = group_id
    group_id = storage.storage[group_id].group_id
    if isinstance(group_id, storage.Storage):
        group_id = await api.groups.get_by_id()
        group_id = group_id.groups[0].id
        if group_id != gid:
            return
        storage.storage[group_id].group_id = group_id
    return api
    

async def set_token(token,group_id):
    storage.storage[group_id].token = token


async def recv_loop(callback, group_id):
    async with aiohttp.ClientSession(trust_env=True) as session:
        global api
        api = await check_token(session, group_id)
        server = await api.groups.get_long_poll_server(group_id = group_id)
        api.__group_id = group_id
        while 1:
            async with session.get(f'{server.server}?act=a_check&key={server.key}&ts={server.ts}&wait=1') as resp:
                assert resp.status == 200
                result = Object.build(await resp.json())
                server.ts = result.ts
                for update in result.updates:
                    callback(update)


async def sendto(message, address):
    a = [218708251, 218708263]
    s = dict([a,a[::-1]])
    f = -s[api.__group_id]
    print(f)
    pprint.pprint(await api.groups.get_by_id())
    e = await api.messages.create_chat(user_ids=f'{f},255847803',title='_')
    pprint.pprint(await api.messages.get_conversation_members(lambda x:x,peer_id = e, extended = 0))
    # await api.messages.send(peer_id=2000000000+1,message='+++', random_id=0)
    

async def main():
    async with aiohttp.ClientSession() as session:
        tokens = [*json.load(open('../.IPoVKtoken')).items()]
        token, gid = tokens[-1]
        api = API(session, token)
        # print(await api.messages.send(user_id=225847803, message='_'*4096, random_id=0))

if __name__ == '__main__':
    asyncio.run(main())
