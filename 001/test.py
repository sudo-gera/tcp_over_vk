import asyncio
import aiohttp
import pprint
import random
import difflib
import time

import storage
import local_file
import api
import object
import router
import remote_file

async def main():
    # local_storage = storage.Storage(local_file.file())
    async with aiohttp.ClientSession(trust_env=True) as session:
        # group_id = local_storage.default_group_id()
        group_ids = [223648671, 223648680]
        group_storage = storage.Storage(local_file.file(group_ids[0]))
        token = group_storage.token()
        API = api.API(session, token)
        a = await API.wall.create_comment(owner_id = -group_ids[1], post_id = 1, message = f'{time.asctime()}', from_group = group_ids[0])
        pprint.pprint(object.destroy(a))


if __name__ == '__main__':
    asyncio.run(main())
