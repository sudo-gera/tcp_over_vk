import asyncio
import aiohttp
import pprint
import random
import difflib
import time
import itertools
import functools
import sys
import difflib
import traceback


import storage
import local_file
import api
import make_id
import object
# import router
import remote_file

def polyhash(text):
    res = 9
    for c in text:
        res += ord(c)
        res *= 257
        res %= 10**8
    res = f'{res:08}'.replace('0','1')
    return res

q = asyncio.Queue()

async def vk_input_messages_handler(group):
    while True:
        result = await group.API.groups.get_long_poll_server(group_id=group.group_id)
        key, server, ts = result.key, result.server, result.ts
        while True:
            async with group.session.get(f'{server}?act=a_check&key={key}&ts={ts}&wait=25') as resp:
                assert resp.status == 200
                res = object.build(await resp.json())
            if 'updates' not in res:
                break
            ts, updates = res.ts, res.updates
            for update in updates:
                if update.type == 'message_new':
                    message = update.object.message
                    text = message.text
                    q.put_nowait(text)

async def main():
    try:
        for c in itertools.count():
            unilen = c
            [chr(c), None][1]
    except Exception:
        pass
    # local_storage = storage.Storage(local_file.file())
    async with aiohttp.ClientSession(trust_env=True) as session:
        # group_id = local_storage.default_group_id()
        # group_ids = [223648671, 223648680]

        group_ids = [218701793, 218708263][::-1]
        for group_id in group_ids:
            group_storage = storage.Storage(local_file.file(group_id))
            token = group_storage.token()
            API = api.API(session, token)
            remote_storage = storage.Storage(await remote_file.file(API))
            group = object.Object(
                session = session,
                group_id = group_id,
                API = API,
                remote_storage = remote_storage,
            )
        
            # if group_id == group_ids[0]:
            #     asyncio.create_task(vk_input_messages_handler(group))
            #     continue

            for connect_id in group_ids:
                if connect_id != group_id:
                    break
            route = remote_storage.route[connect_id]()
            pair = object.Object(
                connect_id = connect_id,
                group = group,
            )
        # for q in range(99):
        #     try:
        #         url = (await pair.group.API.docs.get_messages_upload_server(peer_id = 2000000000 + q)).upload_url
        #         session: aiohttp.ClientSession
        #         session = pair.group.session
        #         filename = f'{make_id.make_id()}.txt'
        #         with aiohttp.MultipartWriter('form-data') as writer:
        #             part = writer.append(b'hello')
        #             part.set_content_disposition('form-data', filename = filename, name = 'file')
        #             async with session.post(url, data = writer) as resp:
        #                 assert resp.status == 200
        #                 res = object.build(await resp.json())
        #         file = await pair.group.API.docs.save(file = res.file, title = filename)
        #         print(file.doc.url)
        #         message = f'@club{pair.connect_id}'
        #         await pair.group.API.messages.send(
        #             random_id = 0,
        #             peer_id = route,
        #             message = message,
        #             attachment = f'doc{file.doc.owner_id}_{file.doc.id}'
        #         )
        #     except Exception:
        #         print(traceback.format_exc())
        # print(await pair.group.API.docs.search(q='llll'))

        # a = await API.wall.create_comment(owner_id = -group_ids[1], post_id = 1, message = f'{time.asctime()}', from_group = group_ids[0])
        # pprint.pprint(object.destroy(a))
        # with aiohttp.MultipartWriter('form-data') as writer:
        #     part = writer.append(b'hello')
        #     part.set_content_disposition('form-data', filename='file.txt', name='file')
        #     async with session.post('http://localhost:9999', data = writer) as resp:
        #         pass
        # @functools.lru_cache(1)
        # def count_by_key(key):
        #     try:
        #         count = 0
        #         while 1:
        #             value = yield
        #             count += 1
        #             yield
        #     finally:
        #         print(f'{key:5} from {value - count + 1} to {value} len {count}')
        # message = ''.join([chr(c) for c in range(12832, 12832+9000)])
        # async def check(message):
        #     while 1:
        #         encodable = []
        #         for c in message:
        #             try:
        #                 c.encode()
        #                 encodable.append(True)
        #             except Exception:
        #                 encodable.append(False)
        #         if not any(encodable):
        #             return 2
        #         if not all(encodable):
        #             return 1
        #         try:
        #             await API.messages.send(random_id = 0, peer_id = remote_storage.route[group_ids[0]](), message = message)
        #         except TabError as e:
        #             if e.msg.error_code == 100:
        #                 return 2
        #             if e.msg.error_code == 914:
        #                 return 1
        #             await asyncio.sleep(60)
        #             continue
        #         qmes = await q.get()
        #         # print(message)
        #         res = int(message != qmes)
        #         return res if len(message) > 2 else res * 2

        # _begin = 65534
        # _end = 67582 #unilen
        # small_len = _end - _begin

        # wr_cnt = 0
        # async def test(begin, end):
        #     if end - begin <= 2048:
        #         message = [chr(c) for c in range(begin, end)]
        #         message = ''.join([q+q for q in message])
        #         res = await check(message)
        #         print(begin, end, res)
        #         if res != 1:
        #             print(f'{round(end/unilen,8):0.8f}', file=sys.stderr)
        #             nonlocal wr_cnt
        #             wr_cnt +=1
        #             if wr_cnt > 4:
        #                 sys.stdout.flush()
        #                 wr_cnt = 0
        #             return
        #     center = (begin + end)//2
        #     await test(begin, center)
        #     await test(center, end)

        # await test(_begin, _end)

        # message = ''.join([random.choice('\x00_') for c in range(4096 - 8)])
        # print(await check(message))

        # async def long_check(message, unitest, depth = 0):
        #     print(message)
        #     res = await check(message)
        #     print(res)
        #     if res == 0:
        #         return 0
        #     left = message[::2]
        #     left += left
        #     await long_check(left, unitest)
        #     right = message[1::2]
        #     right += right
        #     await long_check(right, unitest)
            

        # unitest = [1] * unilen
        # for line in open('unitest.txt'):
        #     begin, end, val = map(int, line.split())
        #     if val != 1:
        #         for c in range(begin, end+1):
        #             unitest[c] = val

        # message = []
        # for c in range(unilen):
        #     if unitest[c] == 0:
        #         message.append(chr(c))
        #     # if len(message) == 32:
        #         print(await check(''.join(message*4096)), c)
        #         message.clear()

        # s = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890йцукенгшщзхъфывапролджэёячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЁЯЧСМИТЬБЮ'
        # print(len(s))
        # print(await check(s*32))

        # print(unitest.count(0))

        # for c in range(unilen):
        #     counter = count_by_key(unitest[c])
        #     counter.send(None)
        #     counter.send(c)



if __name__ == '__main__':
    asyncio.run(main())
