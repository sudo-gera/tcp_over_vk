import asyncio
import json
import sys
import os
import traceback
import io

import stream
import user

async def connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    async with stream.Stream(reader, writer) as sock:
        buffer = io.StringIO()
        try:
            data = await sock.read()
            data = json.loads(data)
            await user.user(data, buffer)
        except Exception:
            sock.write(traceback.format_exc().encode())
            await sock.drain()
        finally:
            buffer.seek(0)
            sock.write(buffer.read().encode())
            await sock.drain()
            

if sys.platform == 'darwin':
    TMP_DIR = '/private/tmp/'
elif os.getcwd().startswith('/data/data/com.termux'):
    TMP_DIR = '/data/data/com.termux/files/usr/var/run'
else:
    TMP_DIR = '/tmp/'

FILE_PREFIX = os.path.join(TMP_DIR, f'tcp_over_vk_{os.getuid()}_')

SOCK_PATH = FILE_PREFIX + 'sock.sock'

PID_PATH = FILE_PREFIX + 'pid.pid'

async def main():
    with open(PID_PATH, 'w') as file:
        file.write(f'{os.getpid()}\n')
    async with await asyncio.start_unix_server(connection, SOCK_PATH) as server:
        server: asyncio.Server
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            pass
        finally:
            server.close()
            await server.wait_closed()
    
if __name__ == '__main__':
    asyncio.run(main())



