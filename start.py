import asyncio
import json
import sys
import os.path
import aiohttp
import pprint

import vk_messages
import storage
import daemon
import stream

async def main():
    group_id = int(sys.argv[1])
    async with aiohttp.ClientSession(trust_env=True) as session:
        while not await vk_messages.check_token(session, group_id):
            print('Привет! Для работы tcp_over_vk нужен токен.')
            token = input('Вставь токен сюда: ')
            await vk_messages.set_token(token, group_id)
    asyncio.create_task(vk_messages.recv_loop(lambda x:pprint.pprint(x), group_id))
    await asyncio.sleep(4)
    await vk_messages.sendto(0,0)
    await asyncio.sleep(4)

    # while True:
    #     try:
    #         async with stream.Stream(*await asyncio.open_unix_connection(daemon.SOCK_PATH)) as sock:
    #             sock.write(json.dumps(sys.argv).encode())
    #             await sock.drain()
    #             sock.write_eof()
    #             await sock.drain()
    #             print((await sock.read()).decode(), end='')
    #         break
    #     except (ConnectionRefusedError, FileNotFoundError):
    #         path = os.path.join(
    #             os.path.abspath(
    #                 os.path.dirname(__file__)
    #             ),
    #             'daemon.py'
    #         )
    #         await asyncio.create_subprocess_exec(sys.executable, path)
    #         await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
