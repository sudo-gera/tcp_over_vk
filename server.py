import asyncio
import asyncio.locks
from aiohttp import web
import time
import random
import json

c=0
num=100

def militime():
    s=time.asctime().split()
    s[3]+=str(time.time()%1)[1:5]
    return ' '.join(s)

def randbytes(l):
    return bytes([random.randint(32,126) for w in range(l)])

async def counter():
    oc=c
    while 1:
        await asyncio.sleep(0.01)
        if c!=oc:
            print(militime(),c)
            oc=c

rs={randbytes(65536) for w in range(num)}

cv=asyncio.locks.Condition()

times=[]

async def hello(request):
    async with cv:
        global c
        c+=1
        # print(c)
        print('\r           \r',c,end='\r')
        if c==num:
            times.append(time.time())
            print(militime())
            await asyncio.sleep(1)
            print(militime())
            times.append(time.time())
            cv.notify_all()
        else:
            await cv.wait()
            pass
    return web.Response(text=rs.pop().decode())

async def timesync(request):
    return web.Response(text=json.dumps(times))


app = web.Application()
app.add_routes([web.get('/', hello),web.get('/time', timesync),
                web.post('/', hello)])

web.run_app(app, port=7003)

