import urllib.parse
import aiohttp
import pprint
import asyncio
import json

import object

class API:
    def __init__(self, session: aiohttp.ClientSession, token: str, _path: str = ''):
        self.__session = session
        self.__token = token
        self.__path = _path

    def __getattr__(self, name: str):
        name = ''.join([q.capitalize() for q in name.split('_')])
        name = name[0].lower() + name[1:]
        return API(self.__session, self.__token, self.__path + '.' + name)

    async def __call__(self, **args):
        args = dict(access_token=self.__token, v='5.199') | args
        form = aiohttp.FormData(args)
        url = f'https://api.vk.com/method/{self.__path[1:]}'
        async with self.__session.post(url, data=form) as resp:
            assert resp.status == 200
            result = await resp.json()
        if {*result} == {'response'}:
            return object.build(result).response
        pprint.pprint(result)
        raise Exception
