import pathlib
import relay
import vk
import sys
import os
import random
import base64
import json
import fcntl
import io
import re
import direct
import time
import queue
import requests
import threading
import multiprocessing
from urllib.request import urlopen
from ic import ic
import multiprocessing

if __name__ == '__main__':
    home=str(pathlib.Path.home())+'/'
    tokens=json.loads(open(home+'.IPoVKtoken').read())
    
    token=list(tokens.keys())['rem' not in sys.argv]

    # pipe=[os.pipe(),os.pipe(),os.pipe(),os.pipe()]
    pipes=[os.pipe(),os.pipe()]


    peer_id=2000000001
    group_id=tokens[token]
    if not os.fork():
        time.sleep(1/2)
        q=queue.Queue()
        s=queue.Queue()
        pipe=pipes[0][1]
        api=vk.Api(token)
        def run(q,pipe):
            tmp=b''
            while 1:
                n=os.write(pipe,tmp)
                # ic(n)
                tmp=tmp[n:]
                tmp+=q.get()
        t=threading.Thread(target=run,args=(q,pipe))
        t.start()
        try:
            vk.recv_loop(api,q,group_id)
        except KeyboardInterrupt:
            t.join()
            print()

    if not os.fork():
        time.sleep(1/2)
        q=queue.Queue()
        s=queue.Queue()
        pipe=pipes[1][0]
        api=vk.Api(token)
        def run(q,pipe):
            tmp=b''
            while 1:
                q.put(tmp)
                tmp=os.read(pipe,relay.pipe_buffer_size)
                # ic(len(tmp))
        t=threading.Thread(target=run,args=(q,pipe))
        t.start()
        try:
            vk.send_loop(api,q,group_id,peer_id)
        except KeyboardInterrupt:
            t.join()
            print()

    # elif not os.fork():
    #     time.sleep(1/2)
    #     api=vk.Api(token)
    #     pipe=pipe[2]
    #     q=queue.Queue()
    #     e=queue.Queue()
    #     s=queue.Queue()
    #     def run(q,e,pipe,s):
    #         # pipe_buffer=b''
    #         # t=time.time()
    #         # l=0
    #         # tt=time.time()
    #         # while s.empty():
    #         #     try:
    #         #         pipe_buffer+=os.read(pipe,relay.buffer_size)
    #         #     except BlockingIOError:
    #         #         pass
    #         #     ic(len(pipe_buffer),pipe_buffer[:32],pipe_buffer[-32:])
    #         #     [*data, pipe_buffer]=pipe_buffer.split(b'^')
    #         #     count={}
    #         #     for w in data:
    #         #         time.sleep(time.time()-t+1/8)
    #         #         t=time.time()
    #         #         ic(w[:32],w[-32:],relay.bytes_hash(w))
    #         #         bw=w
    #         #         w=json.loads(w.decode())
    #         #         p=e
    #         #         if w['type']=='new':
    #         #             if w['id'] not in count:
    #         #                 count[w['id']]=0
    #         #         if w['type']=='got':
    #         #             if count[w['id']]>1024:
    #         #                 p=q
    #         #             count[w['id']]+=len(w['data'])
    #         #         if w['type']=='del':
    #         #             if w['id'] in count:
    #         #                 del count[w['id']]
    #         #         if p==e:
    #         #             if l>1024:
    #         #                 p=q
    #         #             l+=len(bw)
    #         #             if time.time()-tt>1:
    #         #                 l=0
    #         #         p.put(bw)
    #         tmp=b''
    #         while s.empty():
    #             q.put(tmp)
    #             tmp=os.read(pipe,relay.buffer_size)
    #             ic(len(tmp))
    #     t=threading.Thread(target=run,args=(q,e,pipe,s))
    #     t.start()
    #     def loop(f,a):
    #         try:
    #             f(*a)
    #         except KeyboardInterrupt:
    #             pass
    #     y=threading.Thread(target=loop,args=(vk.send_loop,(api,q,group_id,peer_id)))
    #     y.start()    
    #     u=threading.Thread(target=loop,args=(direct.send_loop,(e)))
    #     u.start()    
    # if not os.fork():
    #     pipe=[pipe[3][0],pipe[0][1]]
    #     while 1:
    #         os.write(pipe[1],os.read(pipe[0],65536))
    #         time.sleep(2)
    # if not os.fork():
    #     pipe=[pipe[1][0],pipe[2][1]]
    #     while 1:
    #         os.write(pipe[1],os.read(pipe[0],65536))
    #         time.sleep(2)
    # if not os.fork():
    #     pipe=[pipe[2][0],pipe[3][1]]
    #     fcntl.fcntl(pipe[0], fcntl.F_SETFL, os.O_NONBLOCK);
    #     s=relay.Server()
    #     s.forward_to = ('127.0.0.1',9090)
    #     s.add_pipe(pipe)
    #     if not list(tokens).index(token):
    #         s.create_server('',8081)
    #     try:
    #         s.main_loop()
    #     except KeyboardInterrupt:
    #         print()
    else:
        pipe=[pipes[0][0],pipes[1][1]]
        fcntl.fcntl(pipe[0], fcntl.F_SETFL, os.O_NONBLOCK);
        s=relay.Server()
        s.forward_to = ('127.0.0.1',9090)
        s.add_pipe(pipe)
        if list(tokens).index(token):
            s.create_server('',8081)
        try:
            s.main_loop()
        except KeyboardInterrupt:
            print()







