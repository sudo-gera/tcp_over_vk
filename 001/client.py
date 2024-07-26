import json
import os
import asyncio
import sys
import logging
import traceback

import stream
import get_file_prefix

async def send(args, tmp_file):
    async with stream.Stream(*await asyncio.open_unix_connection(tmp_file.sock)) as sock:
        sock.write(json.dumps(args).encode())
        sock.write_eof()
        await sock.drain()
        stdout_buffer, stderr_buffer = json.loads((await sock.read()).decode())
        sys.stdout.write(stdout_buffer)
        sys.stderr.write(stderr_buffer)
    
async def start_server(args):
    logging.info('Server is not running, starting...')
    path = os.path.join(
        os.path.abspath(
            os.path.dirname(__file__)
        ),
        'server.py'
    )
    await asyncio.create_subprocess_exec(sys.executable, path, str(args['g']))

async def start_and_send(args):
    tmp_file = get_file_prefix.tmp_file(args['g'])
    # while True:
    try:
        await send(args, tmp_file)
    except (ConnectionRefusedError, FileNotFoundError, BrokenPipeError):
        await asyncio.sleep(1)
        try:
            await send(args, tmp_file)
        except (ConnectionRefusedError, FileNotFoundError, BrokenPipeError):
            await start_server(args)
            await asyncio.sleep(1)
            await send(args, tmp_file)
