from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from urllib.request import urlopen
from ic import ic
import traceback
import server_example
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

import json

q=[Queue(),Queue()]

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        ic(self.path)
        n=int(self.path[1])
        ic(n)
        data=[]
        for w in range(2):
            try:
                while 1:
                    if data:
                        data.append(q[n].get_nowait())
                    else:
                        data.append(q[n].get(timeout=1))
            except Empty:
                pass
            if w==0:
                time.sleep(0.01)
        data=b''.join(data)
        ic(n,data)
        self.wfile.write(data)

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        ic(self.path)
        d_len=int(self.headers['Content-Length'])
        data=self.rfile.read(d_len)
        n=int(self.path[1])
        ic(n,data)
        q[1-n].put(data)
        self.wfile.write(b'ok')

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def setup(u=None):
    ic(u)
    if u==None:
        server = ThreadingSimpleServer(('0.0.0.0', 4444), Handler)
        server.serve_forever()

def recv_loop(q,u=None):
    n='0'
    if u==None:
        n='1'
        u='http://localhost:4444/'
    while 1:
        data=urlopen(u+n).read()
        ic(data)
        q.put(data)

def send_loop(q,u=None):
    buff=b''
    n='0'
    if u==None:
        n='1'
        u='http://localhost:4444/'
    while 1:
        data=[buff]
        buff=b''
        try:
            while 1:
                if data:
                    data.append(q.get_nowait())
                else:
                    data.append(q.get())
        except Empty:
            pass
        data=b''.join(data)
        if data:
            data,buff=data[:1024],data[1024:]
            ic(data)
            urlopen(u+n,data=data).read()








