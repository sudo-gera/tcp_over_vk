import logging
import traceback
import io

import event_handler
import remote
import object

async def call(pair, stdout, stderr, message = {}, **args):
    message = object.destroy(message) | args
    logging.info(message)
    message = object.build(message)
    return await event_handler.event_handlers[message.event](pair, stdout, stderr, message)

async def send(pair, message = {}, **args):
    message = object.destroy(message) | args
    message = object.build(message)
    # print(message)
    if message.event in event_handler.event_handlers:
        if 'link' in message: # received call over vk
            stdout = io.StringIO()
            stderr = io.StringIO()
            value = None
            try:
                value = await call(pair, stdout, stderr, message)
            except Exception:
                err = traceback.format_exc()
                logging.error(err)
                stderr.write(err)
            finally:
                stdout.seek(0)
                stderr.seek(0)
                await remote.send(
                    pair,
                    event = message.link,
                    stdout = stdout.read(),
                    stderr = stderr.read(),
                    value = value,
                )
        else:
            await event_handler.event_handlers[message.event](pair, message)
    else:
        logging.error(f'No handler for event {message.event!r}.')

