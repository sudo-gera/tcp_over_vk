#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# modifed by sudo-gera
# Distributed over IDC(I Don't Care) license
import socket
import select
import time
import sys
import re
import os
import base64
import json
import traceback
from ic import ic

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 4096
pipe_buffer_size=65536
delay = 0.0001
# forward_to = ('localhost',9090)
# forward_to = ('192.168.238.111',8080)

def bytes_hash(b):
    r=0
    for w in b:
        r*=127
        r+=w
        r&=2**64-1
    return r

class Server:

    def create_server(self, host, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(200)
        self.input[server]={
            'on_event': self.on_accept,
        }
        
    def __init__(self):
        self.input={}
        self.pipe_buffer=b''
        self.client_by_id={}

    def check(self):
        if 0:
            # ic(self.client_by_id)
            # ic(self.input)
            for client_id in self.client_by_id:
                assert self.client_by_id[client_id] in self.input
                assert self.input[self.client_by_id[client_id]]['id']==client_id
            for client in self.input:
                if 'id' in self.input[client]:
                    assert self.input[client]['id'] in self.client_by_id
                    assert self.client_by_id[self.input[client]['id']]==client

    def main_loop(self):
        ss = select.select
        while 1:
            time.sleep(delay)
            input_ready, output_ready, except_ready = ss(self.input.keys(), [], [])
            for s in input_ready:
                self.check()
                try:
                    if not self.input[s]['on_event'](s):
                        break
                except Exception:
                    ic(traceback.format_exc())
                self.check()

    def on_event(self,client):
        try:
            data = client.recv(buffer_size)
        except ConnectionResetError:
            data = ''
        if not data:
            self.on_close(client)
        else:
            self.on_recv(client,data)
            return 1

    def on_accept(self,server):
        client, client_addr = server.accept()
        # print (client_addr, "has connected")
        client_id = round(time.time()*10**6)%(256**6//4)*4
        self.client_by_id[client_id]=client
        self.input[client]={
            'on_event': self.on_event,
            'id': client_id,
            'buffer': {},
            'recv_count': 0,
            'send_count': 0,
        }
        self.pipe_send({
            'event': 'new',
            'id': client_id,
        })

    def add_pipe(self,pipe):
        self.pipe=pipe
        self.input[pipe[0]]={
            'on_event': self.on_pipe,
        }

    def on_close(self,client):
        try:
            n=client.getpeername()
        except OSError:
            n='(undefined)'
        # print (n, "has disconnected")
        client_id=self.input[client]['id']
        self.pipe_send({
            'event': 'del',
            'id': client_id,
        })
        client.close()
        del self.input[client]
        del self.client_by_id[client_id]

    def on_recv(self,client,data):
        data=data
        client_id=self.input[client]['id']
        num=self.input[client]['recv_count']
        self.input[client]['recv_count']=num+1
        self.pipe_send({
            'event': 'got',
            'id': client_id,
            'data': data,
            'num': num,
        })

    def pipe_send(self,w):
        # ic(w)
        assert type(w)==dict
        assert set(w.keys()) in [{'event','id'},{'event','id','data'}]
        assert w['event'] in 'new del got'.split()
        assert (w['event'] == 'got')==('data' in w)
        assert w['id']%4==0
        assert w['id']//256**6==0
        data=[None,'new','got','del'].index(w['event'])
        data+=w['id']
        data=data.to_bytes(6,'little')
        if 'data' in w:
            ll=256**4
            if len(w['data'])>=ll:
                tmp=w['data']
                w['data']=tmp[:ll]
                self.pipe_send(w)
                w['data']=tmp[ll:]
                self.pipe_send(w)
                return
            data+=len(w['data']).to_bytes(4,'little')
            data+=w['data']
        w=data
        # ic(w)
        os.write(self.pipe[1],w)

    def on_pipe(self,pipe):
        _s=len(self.pipe_buffer)
        try:
            self.pipe_buffer+=os.read(pipe,pipe_buffer_size)
        except BlockingIOError:
            pass
        data=[]
        b=self.pipe_buffer
        # ic(b)
        while 1:
            if len(b)<6:
                break
            pref=int.from_bytes(b[:6],'little')
            tmp={
                'event':[None,'new','got','del'][pref%4],
                'id':pref//4*4,
            }
            if pref%2:
                data.append(tmp)
                b=b[6:]
            else:
                l=int.from_bytes(b[6:10],'little')
                if len(b)<10 or len(b)<l+10:
                    break
                tmp['data']=b[10:10+l]
                data.append(tmp)
                b=b[10+l:]
        self.pipe_buffer=b
        # ic(b,data)
        for w in data:
            # ic(w)
            self.pipe_got(w)

    def pipe_got(self,w):
        if w['event']=='new':
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(self.forward_to)
            client_id = w['id']
            self.client_by_id[client_id]=client
            self.input[client]={
                'id': client_id,
                'on_event': self.on_event,
                'buffer': {},
                'recv_count': 0,
                'send_count': 0,
            }
        if w['event']=='got':
            try:
                client=self.client_by_id[w['id']]
                data=w['data']
                client.send(data)
            except KeyError:
                pass
        if w['event']=='del':
            try:
                client=self.client_by_id[w['id']]
                client.close()
                del self.input[client]
                del self.client_by_id[w['id']]
            except KeyError:
                pass


# if __name__ == '__main__':
#     pipe=[*os.pipe(),*os.pipe()]
#     if not os.fork():
#         pipe=[pipe[2],pipe[1]]
#         s=Server()
#         s.add_pipe(pipe)
#         try:
#             s.main_loop()
#         except KeyboardInterrupt:
#             print()
#     else:
#         pipe=[pipe[0],pipe[3]]
#         s=Server()
#         s.add_pipe(pipe)
#         s.create_server('',8080)
#         try:
#             s.main_loop()
#         except KeyboardInterrupt:
#             print()

