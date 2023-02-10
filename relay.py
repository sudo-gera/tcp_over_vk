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

    def main_loop(self):
        ss = select.select
        while 1:
            time.sleep(delay)
            input_ready, output_ready, except_ready = ss(self.input.keys(), [], [])
            for s in input_ready:
                try:
                    if not self.input[s]['on_event'](s):
                        break
                except Exception:
                    ic(traceback.format_exc())

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

    def pipe_send(self,message):
        message = json.dumps(message)
        message = message.encode()
        assert b'^' not in message
        # ic(message[:32],message[-32:],bytes_hash(message))
        message+=b'^'
        ic(len(message))
        # ic(len(message),message[:32],message[-32:])
        os.write(self.pipe[1],message)

    def on_accept(self,server):
        client, client_addr = server.accept()
        print (client_addr, "has connected")
        client_id = int(time.time()*2**128)
        self.client_by_id[client_id]=client
        self.input[client]={
            'on_event': self.on_event,
            'id': client_id,
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
        print (n, "has disconnected")
        client_id=self.input[client]['id']
        self.pipe_send({
            'event': 'del',
            'id': client_id,
        })
        client.close()
        del self.input[client]
        del self.client_by_id[client_id]

    def on_recv(self,client,data):
        data=base64.b64encode(data).decode()
        client_id=self.input[client]['id']
        self.pipe_send({
            'event': 'got',
            'id': client_id,
            'data': data
        })

    def on_pipe(self,pipe):
        _s=len(self.pipe_buffer)
        try:
            self.pipe_buffer+=os.read(pipe,pipe_buffer_size)
        except BlockingIOError:
            pass
        # ic(len(self.pipe_buffer),self.pipe_buffer[:32],self.pipe_buffer[-32:])
        ic(len(self.pipe_buffer)-_s)
        [*data, self.pipe_buffer]=self.pipe_buffer.split(b'^')
        for w in data:
            # ic(w[:32],w[-32:],bytes_hash(w))
            w=json.loads(w.decode())
            if w['event']=='new':
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(self.forward_to)
                client_id = w['id']
                self.client_by_id[client_id]=client
                self.input[client]={
                    'id': client_id,
                    'on_event': self.on_event,
                }
            if w['event']=='got':
                try:
                    client=self.client_by_id[w['id']]
                    data=w['data']
                    data=data.encode()
                    data=base64.b64decode(data)
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

