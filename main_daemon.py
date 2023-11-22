import asyncio
import argparse
import sys
import file_storage
import aiohttp

async def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('group_id')
§    args = parser.parse_args(argv[1:])
    group_id = args.group_id
    storage = file_storage.Storage(group_id=group_id)
    async with aiohttp.ClientSession(trust_env=True) as session:
        ...

if __name__ == '__main__':
    asyncio.run(main(sys.argv))

