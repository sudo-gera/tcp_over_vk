from time import sleep,time
from pathlib import Path
from json import loads,dumps
from urllib.request import urlopen
from pprint import pprint
from urllib.parse import quote_plus
import requests
import json
import threading
import queue
import random
import os
import io
import base64
import pathlib
import sys
try:
    # exec(open('/Users/gera/c/h.py'))
    from icecream import ic
except Exception:
    ic=lambda a=None:a

def items(q):
    if type(q) == type(dict()):
        if set(q.keys()) == set(['count', 'items']):
            return items(q['items'])
        else:
            for w in q:
                q[w] = items(q[w])
            return q
    elif type(q) == type(list()):
        return [items(w) for w in q]
    else:
        return q

def api_f(token,path,data=''):
    if path and path[-1] not in '&?':
        if '?' in path:
            path+='&'
        else:
            path+='?'
    sleep(1/6)
    data=data.encode()
    ret=loads(urlopen('https://api.vk.com/method/'+path+'v=5.131&access_token='+token,data=data).read().decode())
    try:
        if 'error' in ret.keys():
            print(path.split('?')[0],ret['error']['error_msg'],ret['error']['error_code'])
    except:
        pprint(ret)
    try:
        return items(ret['response'])
    except:
        pass


class Api:
    def __init__(self,token,s='',group_id=None):
        self._s=s
        self._t=token
        self._g=group_id
    def __getattr__(self,n):
        return Api(self._t,self._s+'.'*(not not self._s)+n)
    # def group_id(self):
    #     if self._g is None:
    #         self._g=self.messages.getConversations()['items'][0]['conversation']['chat_settings']['owner_id']
    #     return self._g
    def __call__(self,**d):
        s=self._s+'?'
        d=[w+'='+quote_plus(str(d[w])) for w in d]
        d='&'.join(d)
        return api_f(self._t,s+d)

def recv_loop(api,group_id):
    long_poll=None
    while 1:
        if long_poll is None:
            long_poll=api.groups.getLongPollServer(group_id=group_id)
            ts=long_poll['ts']

        poll=json.loads(urlopen(f"{long_poll['server']}?act=a_check&key={long_poll['key']}&ts={ts}&wait=25").read().decode())

        if 'failed' in poll:
            if poll['failed']==1:
                ts=poll['ts']
                continue
            else:
                long_poll=None
                continue

        upd=poll['updates']
        ts=poll['ts']
        for w in upd:
            if w['type']=='message_new':
                data=w['object']['message']['text']
                data=base64.b64decode(data.encode())
                yield data


def send_loop(api,group_id):
    a=[]
    while 1:
        yield a
        data=a.pop()
        if 0 and 0<len(data)<2048:
            data=base64.b64encode(data).decode()
            api.messages.send(peer_id=peer_id,message=data,random_id=random.randint(0,2**32-1))
        else:
            name = str(time()) + '.txt'
            url=api.docs.getWallUploadServer(group_id=peer_id)['upload_url']
            r = requests.post(
                url,
                files={
                    'file': (
                        name,
                        io.BytesIO(data)
                    )
                }
            ).json()
            doc = api.docs.save(file=r['file'],title=name)['doc']
            api.messages.send(peer_id=peer_id,random_id=random.randint(0,2**32-1),attachment=f'''doc{doc['owner_id']}_{doc['id']}''')




home=str(pathlib.Path.home())+'/'
tokens=json.loads(open(home+'.IPoVKtoken').read())
token=list(tokens.keys())['rem' in sys.argv]
api=Api(token)
group_id=tokens[token]

data=bytes([random.randint(0,255) for w in range(1024)])

peer_id=2000000001


def post_data(data):
    ic(data)
    name = str(time()) + '.txt'
    ic(name)
    url=api.docs.getWallUploadServer(group_id=tokens[token])
    ic(url)
    url=url['upload_url']
    ic(url)
    file={'file': (name,io.BytesIO(data))}
    ic(file)
    r = requests.post(url,files=file).json()
    ic(r)
    doc = api.docs.save(file=r['file'],title=name)
    ic(doc)
    doc=doc['doc']['url']
    return doc

# print(post_data(data))

# name = str(time()) + '.txt'
# url=api.docs.getMessagesUploadServer(type='doc',peer_id=peer_id)['upload_url']
# r = requests.post(
#     url,
#     files={
#         'file': (
#             name,
#             io.BytesIO(data)
#         )
#     }
# ).json()
# doc = api.docs.save(file=r['file'],title=name)['doc']
# api.messages.send(peer_id=peer_id,random_id=random.randint(0,2**32-1),attachment=f'''doc{doc['owner_id']}_{doc['id']}''')

# print(post_data(b'hello world'))


# import vk_api

# vk_session = vk_api.VkApi(token=[*tokens][0])

# vk = vk_session.get_api()

# ic(vk_api.VkUpload(vk).document_message(doc=io.BytesIO(b'123'),title='test.txt',peer_id=peer_id))



# name = str(time()) + '.txt'
# url=api.docs.getWallUploadServer(group_id=group_id)['upload_url']
# r = requests.post(url,files={'file': (name,io.BytesIO(data))}).json()
# doc = api.docs.save(file=r['file'],title=name)['doc']
# api.messages.send(peer_id=peer_id,random_id=random.randint(0,2**32-1),attachment=f'''doc{doc['owner_id']}_{doc['id']}''')

# def run():
#     while 1:
#         sleep(1)
#         print(time())

# t=threading.Thread(target=run)
# t.start()

# sleep(4)
# ic(input())

