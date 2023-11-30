import sys
import argparse
import asyncio
import traceback
import json
import io
import os
import logging
import functools

import stream
import get_file_prefix
import console_handler
import object
import router

async def connection(handler, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    async with stream.Stream(reader, writer) as sock:
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            data = await sock.read()
            data = json.loads(data)
            logging.info(repr(data))
            await handler.handle(object.build(data), stdout, stderr)
        except Exception:
            err = traceback.format_exc()
            logging.error(err)
            stderr.write(err)
        finally:
            stdout.seek(0)
            stderr.seek(0)
            msg = json.dumps([
                stdout.read(),
                stderr.read(),
            ])
            sock.write(msg.encode())
            await sock.drain()

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('group_id', type = int)
    args = parser.parse_args()
    tmp_file = get_file_prefix.tmp_file(args.group_id)
    logging.basicConfig(
        filename=tmp_file.log,
        level=LOGLEVEL,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
    with open(tmp_file.pid, 'w') as file:
        print(os.getpid(), file=file)
    handler = console_handler.console_handler(args.group_id)
    async with await asyncio.start_unix_server(functools.partial(connection, handler), tmp_file.sock) as server:
        server: asyncio.Server
        await handler.ainit()
        asyncio.create_task(router.vk_input_messages_handler(handler.group))
        try:
            await server.serve_forever()
        except asyncio.CancelledError:
            pass
        finally:
            server.close()
            await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
