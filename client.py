import aiohttp
import asyncio
import time
import json

import random

c=0

num=100

def militime():
    s=time.asctime().split()
    s[3]+=str(time.time()%1)[1:5]
    return ' '.join(s)

async def counter():
    oc=c
    while c!=num:
        await asyncio.sleep(0.01)
        if c!=oc:
            print(militime(),c)
            oc=c
            if c==num:
                break

def randbytes(l):
    return bytes([random.randint(32,126) for w in range(l)])

rs={randbytes(65536) for w in range(num)}

url='https://user225847803-2yl2j4hf.wormhole.vk-apps.com/'
# url='http://localhost:7003/'

async def f(session : aiohttp.ClientSession):
    q=str(time.time())
    async with session.post(url,params={'q':q},data=rs.pop()) as response:
        html = await response.text()
        global c
        c+=1
        # print("Body:", html[:15], "...")
    
times=[]

async def main():

    # ct=asyncio.create_task(counter())
    await asyncio.sleep(0.1)
    print(militime())
    times.append(time.time())
    async with aiohttp.ClientSession() as session:
        ts=[]
        for w in range(num):
            ts.append(f(session))
        await asyncio.gather(*ts)
    times.append(time.time())
    print(militime())
    async with aiohttp.ClientSession() as session:
        async with session.get(url+'time') as restimes:
            times[1:1]=json.loads(await restimes.text())
            # print(times)
            print(times[1]-times[0])
            print(times[3]-times[2])




asyncio.run(main())
