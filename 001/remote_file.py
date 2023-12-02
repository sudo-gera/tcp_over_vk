import asyncio
import logging
import itertools
import json
import base64
import time
import itertools
import typing

import api

async def store_db(api, db):
    text = json.dumps(db)
    text = base64.b16encode(text.encode()).decode()
    chunk_len = 4096
    for user_id in itertools.count(1):
        part, text = text[:chunk_len], text[chunk_len:]
        await api.storage.set(key='data', value=part, user_id=user_id)
        if not part:
            break

async def load_db(api):
    text = ''
    for user_id in itertools.count(1):
        part = await api.storage.get(key='data', user_id=user_id)
        part = part[0].value
        text += part
        if not part:
            break

    text = base64.b16decode(text).decode()
    return json.loads(text)


class file:
    API: api.API
    synced: bool
    db: dict[str, typing.Any]
    async def __new__(self, API: api.API):
        self = super().__new__(self)
        self.API = API
        self.synced = True
        try:
            # await store_db(self.api, {})
            self.db = await load_db(self.API)
        except Exception:
            self.db = {}
        return self

    def __getitem__(self, key: str):
        return self.db[key]
    
    def __setitem__(self, key: str, value: typing.Any):
        self.db[key] = value
        self.synced = False

    def __delitem__(self, key: str):
        del self.db[key]
        self.synced = False
    
    def __contains__(self, key: str):
        return key in self.db

    async def sync(self):
        await store_db(self.API, self.db)
        self.synced = True

    async def __call__(self):
        if not self.synced:
            await self.sync()

    def __del__(self):
        if not self.synced:
            logging.critical('database is not synced, all changes are lost!')
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        await self()
    
