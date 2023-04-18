import aiohttp
import asyncio
from ic import ic

def polyhash(q):
    import pickle
    d=pickle.dumps(q)
    r=0
    for w in d:
        r*=257
        r+=w
        r&=0xFFFFFFFFFFFFFFFF
    r%=10**6
    return r

q=[Queue(),Queue()]
buff=b''
m_len=256**3

async def get(request):
    n=int(request.match_info.get('id','*'))
    # ic(n)
    global buff
    data=buff
    buff=b''
    f=[0,0]
    for w in f:
        if w:
            time.sleep(0.01)
        while 1:
            if data:
                try:
                    data+=q[n].get_nowait()
                except Empty:
                    break
            else:
                try:
                    data+=q[n].get(timeout=30)
                except Empty:
                    f=[]
                    break
    data,buff=data[:m_len],data[m_len:]
    ic(n,len(data),polyhash(data))



    global c
    c+=1
    print('\r           \r',c,end='\r')
    return web.Response(text=randbytes(65).decode())

app = web.Application()
app.add_routes([
    web.get('/{id}', hello),
    web.post('/{id}', hello)
])



