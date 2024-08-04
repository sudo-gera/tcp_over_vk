from __future__ import annotations
import asyncio
import secrets
import stream
import random
import weakref

# process

processes : dict[str|None, Process] = {}

class Process:
    def __new__(cls, id : str|None = None) -> Process:
        if id not in processes:
            self = super().__new__(cls)
            processes[id] = self
        self = processes[id]
        return self

    def __init__(self, id : str|bytes|bytearray|None = None) -> None:
        if isinstance(id, bytes | bytearray):
            id = id.decode()
        if not hasattr(self, 'id'):
            if id is None:
                self.generate_token()
            else:
                self.id = id
        self.check_token()
        self.remote = bool(id is not None)

    def generate_token(self):
        token = secrets.token_bytes(12)
        check = random.Random(token).randbytes(4)
        checked_token = check + token
        self.id = checked_token.hex() + '\n'

    def check_token(self):
        checked_token = bytes.fromhex(self.id)
        token = checked_token[:12]
        check1 = checked_token[12:]
        check2 = random.Random(token).randbytes(4)
        assert check1 == check2

    def __repr__(self) -> str:
        return self.__class__.__name__ + '(' + ', '.join([k + '=' + repr(v) for k,v in self.__dict__.items()]) + ')' + f' at {id(self)}'

    def __hash__(self) -> int:
        return hash(self.id)

# connections

connections : dict[frozenset[Process], None] = {}

@stream.streamify
async def accept_connection(sock: stream.Stream):
    sock.write(Process().id)
    remote = Process(await sock.readline())
    local = Process()
    connection_key =frozenset(local, remote)
    if connection_key not in connections:
        connections[connection_key] = Connection(remote=remote)


async def open_connection(remote_socket: tuple[str, int]):
    async with stream.Stream(await asyncio.open_connection(*remote_socket)) as sock:
        


class Connection:
    def __init__(self, connections_count: int, remote_socket : tuple[str, int]|None = None, remote_process: Process|None = None):
        self.remote_socket = remote_socket
        self.remote_process = remote_process
        self.outgoing_buffer = asyncio.Queue()
        self.connections : set[weakref.w] = set()
        self.connections_count = connections_count

    async def keep_alive(self):
        while 1:
            for connection_wr in [*self.connections]:
                if connections_ 






async def single_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):

class SingleConnection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer


    async def single_connection_reader():
        while 1:
            self.reader.re
#         asyncio.create_task(self.ai)

#     async def ainit(self, transport):
#         await transport.send(Process().id + '\n')

        

