import asyncio
import traceback
import logging
import io
import shlex

import send
import object
import tcp

# listeners = []

async def smart_event(pair, message, stderr):
    if message.command != 'tcp':
        logging.info([message, pair.connect_id])
    if message.command == 'meta':
        print('got meta')
    #     await asyncio.create_subprocess_exec(*shlex.split(message.value))
    if message.command == 'bind':
        await tcp.add(message.forwarding, stderr, pair)
    if message.command == 'del':
        await tcp.remove(message.forwarding, stderr, pair)
    if message.command == 'list':
        await tcp.print_all(stderr, pair)
    if message.command == 'tcp':
        await tcp.on_remote_connection_event(pair, message.data)

async def event(pair, message):
    if message.command == 'ping':
        return message
    else:
        stderr = io.StringIO()
        try:
            await smart_event(pair, message, stderr)
        except Exception:
            err = traceback.format_exc()
            logging.debug(err)
            stderr.write(err) 
        finally:
            stderr.seek(0)
            return object.Object(log = stderr.read())
