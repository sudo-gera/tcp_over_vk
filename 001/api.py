import urllib.parse
import aiohttp
import pprint
import asyncio
import json
import time
import logging
import typing

import object

class _API:
    def __init__(self, session: aiohttp.ClientSession, token: str):
        self.__session = session
        self.__token = token
        self.__wait_until = float('-inf')
        self.__lock = asyncio.Lock()

    async def __call__(self, path, *a, **args):
        async with self.__lock:
            # print(args, time.asctime(), id(self.__lock))
            await asyncio.sleep(self.__wait_until - time.monotonic())
            # print(args, time.asctime(), id(self.__lock))
            args = dict(access_token=self.__token, v='5.199') | args
            form = aiohttp.FormData(args)
            url = f'https://api.vk.com/method/{path[1:]}'
            async with self.__session.post(url, data=form) as resp:
                assert resp.status == 200
                result = object.build(await resp.json())
            self.__wait_until = time.monotonic() + 1
            if 'response' in result:
                return result.response
            logging.error(result.error)
            raise TabError(result.error)

class API:
    def __init__(self, session: aiohttp.ClientSession, token: str, _path: str = '', _api = None):
        self.__api = _API(session, token) if _api is None else _api
        self.__session = session
        self.__token = token
        self.__path = _path

    def __getattr__(self, name: str):
        name = ''.join([q.capitalize() for q in name.split('_')])
        name = name[0].lower() + name[1:]
        return API(self.__session, self.__token, self.__path + '.' + name, self.__api)

    async def __call__(self, *a, **args):
        if a and a[0]==[]:
            return await get_full_list(self, args)
        return await self.__api(self.__path, *a, **args)


async def get_full_list(api: API, args):
    res: list[typing.Any] = []
    count = None
    while count != len(res):
        args |= dict(offset=len(res))
        resp = await api(**args)
        res.extend(resp.items)
        count = resp.count
    resp.items = res
    return resp


