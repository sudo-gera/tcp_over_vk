import asyncio
import traceback
import logging
import io
import shlex

import send
import object

listeners = []

async def smart_event(message, stderr):
    print('smart_event', file=stderr)
    print(message, file = stderr)
    if message.command == 'meta':
        await asyncio.create_subprocess_exec(*shlex.split(message.value))

    # if message.command == 'bing':
    # if message.command == 'del':
    #     ...
    # if message.command == 'list':
    #     ...

async def event(message):
    if message.command == 'ping':
        return message
    else:
        stderr = io.StringIO()
        try:
            await smart_event(message, stderr)
        except Exception:
            err = traceback.format_exc()
            logging.debug(err)
            stderr.write(err) 
        finally:
            stderr.seek(0)
            return object.Object(log = stderr.read())
