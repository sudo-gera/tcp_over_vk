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

    pipe=[*os.pipe(),*os.pipe()]

    fcntl.fcntl(pipe[0], fcntl.F_SETFL, os.O_NONBLOCK);

    peer_id=2000000001
    group_id=tokens[token]
    if not os.fork():
        time.sleep(1/2)
        q=queue.Queue()
        s=queue.Queue()
        pipe=pipe[1]
        api=vk.Api(token)
        def run(q,pipe,s):
            tmp=b''
            while s.empty():
                n=os.write(pipe,tmp)
                ic(n)
                tmp=tmp[n:]
                tmp+=q.get()
        t=threading.Thread(target=run,args=(q,pipe,s))
        t.start()
        try:
            vk.recv_loop(api,q,group_id)
        except KeyboardInterrupt:
            s.put(0)
            q.put(b'')
            t.join()
            print()

    elif not os.fork():
        time.sleep(1/2)
        api=vk.Api(token)
        pipe=pipe[2]
        q=queue.Queue()
        s=queue.Queue()
        def run(q,pipe,s):
            tmp=b''
            while s.empty():
                q.put(tmp)
                tmp=os.read(pipe,relay.buffer_size)
                ic(len(tmp))
        t=threading.Thread(target=run,args=(q,pipe,s))
        t.start()
        try:
            vk.send_loop(api,q,group_id,peer_id)
        except KeyboardInterrupt:
            s.put(0)
            q.put(b'')
            t.join()
            print()
    else:
        pipe=[pipe[0],pipe[3]]
        s=relay.Server()
        s.forward_to = ('localhost',9090)
        # s.forward_to = ('192.168.238.111',8080)
        s.add_pipe(pipe)
        if list(tokens).index(token):
            s.create_server('',8080)
        try:
            s.main_loop()
        except KeyboardInterrupt:
            print()







