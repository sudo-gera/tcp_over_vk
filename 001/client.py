import json
import os
import asyncio
import sys
import logging
import traceback

import stream
import get_file_prefix


async def send(args):
    tmp_file = get_file_prefix.tmp_file(args['g'])
    while True:
        try:
            async with stream.Stream(*await asyncio.open_unix_connection(tmp_file.sock)) as sock:
                sock.write(json.dumps(args).encode())
                sock.write_eof()
                await sock.drain()
                stdout_buffer, stderr_buffer = json.loads((await sock.read()).decode())
                sys.stdout.write(stdout_buffer)
                sys.stderr.write(stderr_buffer)
            break
        except (ConnectionRefusedError, FileNotFoundError):
            logging.info('Server is not running, starting...')
            path = os.path.join(
                os.path.abspath(
                    os.path.dirname(__file__)
                ),
                'server.py'
            )
            await asyncio.create_subprocess_exec(sys.executable, path, str(args['g']))
            await asyncio.sleep(1)
