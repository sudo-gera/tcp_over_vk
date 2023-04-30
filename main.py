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
# import tg
# import direct
import time
import functools
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
    # tg_tokens=json.loads(open(home+'.IPoTGtoken').read())
    # tokens=json.loads(open(home+'.IPoTGtoken').read())
    
    token=list(tokens.keys())['rem' not in sys.argv]
    # tg_token=list(tg_tokens.keys())['rem' not in sys.argv]

    # pipe=[os.pipe(),os.pipe(),os.pipe(),os.pipe()]
    pipes=[os.pipe(),os.pipe()]

    if 'rem' in sys.argv:
        u=None
    else:
        # u='http://localhost:4444/'
        # u='http://172.30.1.136:4444'
        u='https://user225847803-lsh3jbwp.wormhole.vk-apps.com/'

    threading.Thread(target=lambda:direct.setup(u)).start()

    # port=4032
    if not os.fork():
        time.sleep(1/2)
        q=queue.Queue()
        s=queue.Queue()
        pipe=pipes[0][1]
        # api=vk.Api(token)
        # api.group_id=tokens[token]
        # tg_api=tg.Api(tg_token)
        # api=tg.Api(token)
        def run(q,pipe):
            tmp=b''
            while 1:
                n=os.write(pipe,tmp)
                # ic(n)
                tmp=tmp[n:]
                tmp+=q.get()
        t=threading.Thread(target=run,args=(q,pipe))
        t.start()
        # threading.Thread(target=functools.partial(direct.recv_loop,q,port+([*tokens].index(token)))).start()
        # threading.Thread(target=functools.partial(vk.recv_loop,api,q,group_id)).start()
        # threading.Thread(target=functools.partial(tg.recv_loop,api,q)).start()
        # vk.recv_loop(api,q)
        try:
            # tg.recv_loop(api,q)
            # vk.recv_loop(api,q,tg_api)
            vk.recv_loop(api,q)
            # direct.recv_loop(q,port+([*tokens].index(token)))
            # direct.recv_loop(q,u)
        except KeyboardInterrupt:
            pass
        # try:
        #     # vk.recv_loop(api,q,group_id)
        #     direct.recv_loop(q,port+([*tokens].index(token)))
        # except KeyboardInterrupt:
        #     t.join()
        #     print()

    elif not os.fork():
        time.sleep(1/2)
        q=queue.Queue()
        e=queue.Queue()
        s=queue.Queue()
        pipe=pipes[1][0]
        # api=vk.Api(token)
        # api.group_id=tokens[token]
        # tg_api=tg.Api(tg_token)
        # api=tg.Api(token)
        def run(q,e,pipe):
            tmp=b''
            while 1:
                q.put(tmp)
                tmp=os.read(pipe,relay.pipe_buffer_size)
                # ic(len(tmp))
        t=threading.Thread(target=run,args=(q,e,pipe))
        t.start()
        # threading.Thread(target=functools.partial(direct.send_loop,e,port+1-([*tokens].index(token)))).start()
        # threading.Thread(target=functools.partial(vk.send_loop,api,q,group_id,peer_id)).start()
        # threading.Thread(target=functools.partial(tg.send_loop,api,q)).start()
        # threading.Thread(target=functools.partial(tg.run_server,api,q)).start()
        # vk.send_loop(api,q)
        try:
            # tg.run_server(api,q)
            # vk.send_loop(api,q,tg_api)
            vk.send_loop(api,q)
            # direct.send_loop(q,port+1-([*tokens].index(token)))
            # direct.send_loop(q,u)
        except KeyboardInterrupt:
            pass
        # try:
        #     direct.send_loop(q,port+1-([*tokens].index(token)))
        #     # vk.send_loop(api,q,group_id,peer_id)
        # except KeyboardInterrupt:
        #     t.join()
        #     print()

    # elif not os.fork():
    #     time.sleep(1/2)
    #     api=vk.Api(token)
    #     pipe=pipe[2]
    #     q=queue.Queue()
    #     e=queue.Queue()
    #     s=queue.Queue()
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
        # s.forward_to = ('192.168.49.1',8080)
        # s.forward_to = ('192.168.238.111',8080)
        s.add_pipe(pipe)
        if list(tokens).index(token):
            # ic(os.getpid())
            s.create_server('',8082)
        try:
            s.main_loop()
        except KeyboardInterrupt:
            print()







