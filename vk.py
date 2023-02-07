from time import sleep,time
from pathlib import Path
from json import loads,dumps
from urllib.request import urlopen
from pprint import pprint
from urllib.parse import quote_plus
import requests
import json
import random
import os
import io
import re
import gzip
import base64
import traceback
from ic import ic

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
    sleep(1/2)
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

def recv_loop(api,q,group_id):
    long_poll=None
    while 1:
        try:
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
                    data=gzip.decompress(data)
                    for w in w['object']['message']['attachments']:
                        if w['type']=='doc':
                            tmp=urlopen(w['doc']['url']).read()
                            tmp=gzip.decompress(tmp)
                            data+=tmp
                    ic(len(data))
                    q.put(data)
        except Exception:
            ic(traceback.format_exc())
            sleep(1/2)


def send_loop(api,q,group_id,peer_id):
    buff=b''
    while 1:
        data=[buff]
        buff=b''
        try:
            while 1:
                data.append(q.get_nowait())
        except Exception:
            pass
        data=b''.join(data)
        ic(len(data))
        if not data:
            buff=q.get()
            continue
        data=gzip.compress(data,compresslevel=9)
        try:
            if len(data)<2048:
                _data=base64.b64encode(data).decode()
                api.messages.send(peer_id=peer_id,message=_data,random_id=random.randint(0,2**32-1))
            else:
                data, buff = data[:123456789], buff+data[123456789:]
                name = f'''{len(data)}_{time()}.txt'''
                url=api.docs.getWallUploadServer(group_id=group_id)['upload_url']
                r = requests.post(url,files={'file': (name,io.BytesIO(data))}).json()
                doc = api.docs.save(file=r['file'],title=name)['doc']
                api.messages.send(peer_id=peer_id,random_id=random.randint(0,2**32-1),attachment=f'''doc{doc['owner_id']}_{doc['id']}''')
        except Exception:
            data=gzip.decompress(data)
            buff+=data
            ic(traceback.format_exc())
            sleep(1/2)







# api=Api(tokens[0])


# def main_loop(token,group_id):
    

# group_id=218700852
# long_poll=None
# try:
#     while 1:
#         if long_poll is None:
#             long_poll=api.groups.getLongPollServer(group_id=group_id)
#             ts=long_poll['ts']

#         poll=json.loads(urlopen(f"{long_poll['server']}?act=a_check&key={long_poll['key']}&ts={ts}&wait=25").read().decode())

#         if 'failed' in poll:
#             if poll['failed']==1:
#                 ts=poll['ts']
#                 continue
#             else:
#                 long_poll=None
#                 continue

#         upd=poll['updates']
#         ts=poll['ts']
#         for w in upd:
#             ic(w)
# except KeyboardInterrupt:
#     print()

# token = tokens[0]



