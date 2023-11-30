import urllib.parse
import aiohttp
import pprint
import asyncio
import json
import time
import logging

import object

class API:
    def __init__(self, session: aiohttp.ClientSession, token: str, _path: str = ''):
        self.__session = session
        self.__token = token
        self.__path = _path
        self.__wait_until = float('-inf')

    def __getattr__(self, name: str):
        name = ''.join([q.capitalize() for q in name.split('_')])
        name = name[0].lower() + name[1:]
        return API(self.__session, self.__token, self.__path + '.' + name)

    async def __call__(self, *a, **args):
        if a and a[0]==[]:
            return await get_full_list(self, args)
        args = dict(access_token=self.__token, v='5.199') | args
        form = aiohttp.FormData(args)
        url = f'https://api.vk.com/method/{self.__path[1:]}'
        await asyncio.sleep(max(self.__wait_until - time.time(), 0))
        async with self.__session.post(url, data=form) as resp:
            assert resp.status == 200
            result = object.build(await resp.json())
        self.__wait_until = time.monotonic() + 0.05
        if 'response' in result:
            return result.response
        logging.debug(result.error)
        raise TabError(result.error)

async def get_full_list(api: API, args):
    res = []
    count = None
    while count != len(res):
        args |= dict(offset=len(res))
        resp = await api(**args)
        res.extend(resp.items)
        count = resp.count
    resp.items = res
    return resp


