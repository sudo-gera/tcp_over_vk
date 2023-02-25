from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
from ic import ic
import json
import pathlib
from pprint import pprint
import time
import requests
import io
import queue
import sys
import base64
import traceback
import gzip
from urllib.parse import quote_plus

home=str(pathlib.Path.home())+'/'
tokens=json.loads(open(home+'.IPoTGtoken').read())


def api_f(token,path,data='',url=0,ins=''):
    if path and path[-1] not in '&?':
        if '?' in path:
            path+='&'
        else:
            path+='?'
    time.sleep(1/2)
    data=data.encode()
    ret=f'''https://api.telegram.org/{ins}bot{token}/{path}'''
    if url:
        return ret
    ret=json.loads(urlopen(ret,data=data).read().decode())
    try:
        if ret['ok']==False:
            print(path.split('?')[0],ret['description'],ret['error_code'])
    except Exception:
        pprint(ret)
    try:
        return ret['result']
    except Exception:
        pprint(ret)


class Api:
    def __init__(self,token,s=''):
        self._s=s
        self._t=token
    def __getattr__(self,n):
        return Api(self._t,self._s+'.'*(not not self._s)+n)
    def __call__(self,**d):
        s=self._s+'?'
        d=[w+'='+quote_plus(str(d[w])) for w in d]
        d='&'.join(d)
        return api_f(self._t,s+d)
    def _url(self,**d):
        s=self._s+'?'
        d=[w+'='+quote_plus(str(d[w])) for w in d]
        d='&'.join(d)
        return api_f(self._t,s+d,url=1)
    def _file(self,**d):
        s=self._s+'?'
        d=[w+'='+quote_plus(str(d[w])) for w in d]
        d='&'.join(d)
        return api_f(self._t,s+d,url=1,ins='file/')




def recv_loop(api,q):
    bot_id=api.getMe()['id']
    ic(bot_id)
    update_id=-1
    a=api.getUpdates(offset=update_id,timeout=1)
    update_id=max([w['update_id'] for w in a])+1 if a else update_id
    while 1:
        a=api.getUpdates(offset=update_id,timeout=25)
        update_id=max([w['update_id'] for w in a])+1 if a else update_id
        for a in a:
            r=a['message']
            y=r
            r=r['text'].split('_')
            if len(r)<3 or r[0] in sys.argv:
                continue
            elif r[1]=='file':
                # r=api.getFile(file_id=y['document']['file_id'])
                # data=urlopen(api.__getattr__(y['file_path'])._file()).read()
                data=urlopen(base64.b64decode(r[2].encode()).decode()).read()
                data=gzip.decompress(data)
                # ic(data)
                q.put(data)
            elif r[1]=='text':
                r=r[2]
                t=base64.b64decode(r.encode())
                # ic(t)
                q.put(t)
            # if 'reply_to_message' not in r:
            #     continue
            # r=r['reply_to_message']
            # if r['from']['id']!=bot_id:
            #     if 'text' in r:
            #         t=base64.b64decode(r['text'].encode())
            #         ic(len(t))
            #         q.put(t)
            #     else:
            #         r=api.getFile(file_id=r['document']['file_id'])
            #         data=urlopen(api.__getattr__(r['file_path'])._file()).read()
            #         data=gzip.decompress(data)
            #         q.put(data)



# def send_loop(api,q):
#     buff=b''
#     chat_id=-1001851792503
#     while 1:
#         data=[buff]
#         buff=b''
#         try:
#             while 1:
#                 data.append(q.get_nowait())
#         except Exception:
#             pass
#         data=b''.join(data)
#         if not data:
#             buff=q.get()
#             continue
#         ic(len(data))
#         try:
#             if len(data)<0:
#                 api.sendMessage(chat_id=chat_id,text=base64.b64encode(data).decode(),reply_markup=json.dumps(dict(force_reply=True)))
#             else:
#                 data, buff = data[:2*10**7], buff+data[2*10**7:]

#                 _data=gzip.compress(data,9)
#                 name = f'''{len(data)}_{time.time()}.txt'''

#                 files=[
#                     ['document',[name,_data]]
#                 ]

#                 r = requests.post(api.sendDocument._url(chat_id=chat_id,reply_markup=json.dumps(dict(force_reply=True))), files=files).json()['result']
#         except Exception:
#             buff+=data
#             ic(traceback.format_exc())
#             time.sleep(1/2)

_q_=[]


_buff_=b''

_api_=0


class MyServer(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        global _buff_
        data=[_buff_,_q_.get()]
        # self._q_[1].put(base64.b64decde(self.path[1:].encode()))
        try:
            while 1:
                data.append(_q_.get_nowait())
        except queue.Empty:
            pass
        data=b''.join(data)
        l=1024
        if not data:
            return
        if len(data)<l:
            data,_buff_=data[:l],data[l:]
            # ic(data)
            self.wfile.write(sys.argv[1].encode()+b'_text_'+base64.b64encode(data))
        else:
            ll=1024**2*16
            data,_buff_=data[:ll],data[ll:]
            # ic(data)

            api=_api_

            _data=gzip.compress(data,9)
            name = f'''{len(data)}_{time.time()}.txt'''

            files=[
                ['document',[name,_data]]
            ]

            chat_id=-1001851792503

            r = requests.post(api.sendDocument._url(chat_id=chat_id), files=files).json()['result']


            r=api.getFile(file_id=r['document']['file_id'])
            # ic(r)
            r=api.__getattr__(r['file_path'])._file().encode()
            r=sys.argv[1].encode()+b'_file_'+base64.b64encode(r)
            self.wfile.write(r)



    def log_message(self, *a):
        return

def run_server(api,q):
    hostName = "0.0.0.0"
    hostPort = 8084 + ('rem' in sys.argv)

    myServer = HTTPServer((hostName, hostPort), MyServer)

    global _q_,_api_
    _q_=q
    _api_=api

    try:
        myServer.serve_forever()
    except:
        pass
    myServer.server_close()




if __name__=='__main__':

    api=Api([*tokens][0])


    # update_id=-1
    # while 1:
    #     a=api.getUpdates(offset=update_id,timeout=25)
    #     update_id=max([w['update_id'] for w in a])+1 if a else update_id
    #     for a in a:
    #         pprint(a)


            # data=b'123'
            # name = f'''{len(data)}_{time.time()}.txt'''

            # files=[
            #     ['document',[name,data]]
            # ]

            # r = requests.post(api.sendDocument._url(chat_id=user_id), files=files).json()['result']

            # pprint(api.sendMessage(chat_id=user_id,text=a['message']['text'],reply_markup=json.dumps(dict(force_reply=True,input_field_placeholder='456'))))
            # pprint(api.sendMessage(chat_id=user_id,text='123',reply_markup=json.dumps(dict(one_time_keyboard=True,keyboard=[[dict(text='qwe')]]))))
    # t=0
    # while 1:
    #     t=time.time()
    #     time.sleep(max(t+1-time.time(),0))

    pprint(api.getMe())

    # pprint(api.sendMessage(chat_id=-1001851792503,text=time.asctime(),reply_markup=json.dumps(dict(force_reply=True))))






