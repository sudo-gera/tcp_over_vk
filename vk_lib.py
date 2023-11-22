import urllib.parse
import aiohttp
import pprint
import asyncio
import json

import storage

class Object(dict):  # allow a.name instead of a['name'] for JSON types
    def __init__(self, *a, **s):
        super().__init__(*a, **s)
        self.__dict__ = self

    @staticmethod
    def __convert(obj, build, Obj):
        if isinstance(obj, dict):
            return Obj({q: build(w) for q,w in obj.items()})
        if isinstance(obj, list):
            return [build(w) for w in obj]
        return obj

    @staticmethod
    def _build(obj):
        return Object.__convert(obj, Object._build, Object)

    @staticmethod
    def _destroy(obj):
        return Object.__convert(obj, Object._destroy, lambda x:x)

    
        
class API:
    def __init__(self, session: aiohttp.ClientSession, token: str, path: str = ''):
        self.__session = session
        self.__token = token
        self.__path = path

    def __getattr__(self, name: str):
        name = ''.join([q.capitalize() for q in name.split('_')])
        name = name[0].lower() + name[1:]
        return API(self.__session, self.__token, self.__path + '.' + name)

    async def __call__(self, Object_build=Object.build, **args):
        args = dict(access_token=self.__token, v='5.154') | args
        form = aiohttp.FormData(args)
        url = f'https://api.vk.com/method/{self.__path[1:]}'
        async with self.__session.post(url, data=form) as resp:
            assert resp.status == 200
            result = await resp.json()
        if {*result} == {'response'}:
            return Object_build(result)['response']
        pprint.pprint(result)
        raise Exception

    def __bool__(self):
        return True

