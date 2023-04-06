from http.server import BaseHTTPRequestHandler, HTTPServer
import time
# from urllib.request import urlopen
from ic import ic
import traceback
import server_example
from traceback import format_exc

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

# def send_loop(q,port):
#     while 1:
#         try:
#             data=q.get()
#             ic(type(data))
#             ic(data)
#             ic(port)
#             time.sleep(1)
#             if data:
#                 urlopen(f'''http://localhost:{port}''',data=data).read()
#         except Exception:
#             print(traceback.format_exc())


# def recv_loop(q,port):
#     hostName = "0.0.0.0"
#     hostPort = port

#     class MyServer(BaseHTTPRequestHandler):
#         def do_POST(self):
#             ic()
#             self.send_response(200)
#             self.send_header("Content-type", "text/html; charset=utf-8")
#             self.end_headers()
#             lenn=int(self.headers['Content-Length'])
#             data=self.rfile.read(lenn)
#             ic(data)
#             q.put(data)

#     myServer = HTTPServer((hostName, hostPort), MyServer)
#     print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

#     try:
#         myServer.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     myServer.server_close()
#     print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading

from queue import Queue,Empty

import subprocess

import json

import base64

q=[Queue(),Queue()]
buff=b''
m_len=256**3

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        ic(self.path)
        n=int(self.path[1])
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
        # ic(n,data)
        self.wfile.write(data)

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        ic(self.path)
        d_len=int(self.headers['Content-Length'])
        data=self.rfile.read(d_len)
        n=int(self.path[1])
        # ic(n,data)
        ic(n,len(data),polyhash(data))
        q[1-n].put(data)
        self.wfile.write(str(len(data).bit_length()).encode())

    def log_message(*args):
        pass

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def setup(u=None):
    ic(u)
    if u==None:
        server = ThreadingSimpleServer(('0.0.0.0', 4444), Handler)
        try:
            server.serve_forever()
        except:
            pass

def _urlopen(u,data=None):
    # a=subprocess.run(['curl','-s','--noproxy','*',u]+([] if data==None else ['-d',data]),stdout=subprocess.PIPE)
    # if a.returncode:
    #     time.sleep(1)
    # return a.stdout
    from urllib.request import urlopen
    try:
        a=urlopen(u,data).read()
        return a
    except Exception:
        print(format_exc())
        time.sleep(1)




def recv_loop(q,u=None):
    n='0'
    if u==None:
        n='1'
        u='http://localhost:4444/'
    while 1:
        try:
            data=_urlopen(u+n)
            if data:
                ic(len(data),polyhash(data))
                data=base64.b64decode(data)
                # ic(data)
                q.put(data)
        except Exception:
            print(format_exc())


def send_loop(q,u=None):
    buff=b''
    n='0'
    if u==None:
        n='1'
        u='http://localhost:4444/'
    while 1:
        try:
            data=buff
            buff=b''
            for w in range(2):
                if w:
                    time.sleep(0.01)
                try:
                    while 1:
                        if data:
                            data+=q.get_nowait()
                        else:
                            data+=q.get()
                except Empty:
                    pass
            if data:
                data,buff=data[:m_len],data[m_len:]
                # ic(data)
                data=base64.b64encode(data)
                ic(len(data),polyhash(data))
                _urlopen(u+n,data=data)
        except Exception:
            print(format_exc())








