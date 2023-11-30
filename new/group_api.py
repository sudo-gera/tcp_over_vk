import storage
import aiohttp
import asyncio

import api
import storage
import object

class API:
    storage: storage.Storage
    api: api.API
    group: dict

    async def __new__(cls, session: aiohttp.ClientSession, *, group_id: int|str|None = None, token: str|None = None):
        self = super().__new__(cls)
        assert (token is None) ^ (group_id is None)
        if group_id is not None:
            self.storage = storage.Storage(group_id)
            self.group = object.build(self.storage.group())
            self.api = api.API(session, self.storage.token())
        if token is not None:
            self.api = api.API(session, token)
            assert (await self.api.groups.get_token_permissions()).mask & 4096
            self.group = (await self.api.groups.get_by_id()).groups[0]
            group_id = self.group.id
            self.storage = storage.Storage(group_id)
            self.storage.token(token)
            self.storage.group(self.group)
        return self

