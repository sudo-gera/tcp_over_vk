from urllib.request import urlopen
from ic import ic
import json
import pathlib
from pprint import pprint
import time
import requests
import io
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




api=Api(tokens[0])

a=api.getUpdates(limit=1)
user_id=a[0]['message']['chat']['id']


data=b'123'
name = f'''{len(data)}_{time.time()}.txt'''

files=[
    ['document',[name,data]]
]

r = requests.post(api.sendDocument._url(chat_id=user_id), files=files).json()['result']
ic(r)
file_id=r['document']['file_id']
ic(file_id)
f=api.getFile(file_id=file_id)
ic(f)
ic(api.__getattr__(f['file_path'])._file())












