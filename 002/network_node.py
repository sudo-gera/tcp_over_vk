import utils.import_all
import asyncio
import commands.global_command
import utils.await_if_necessary
import utils.forwarding_parser
import argparse
import utils.get_subclasses
import utils.stream
import json
import io
import traceback

@utils.stream.streamify
async def on_connect(stream: utils.stream.Stream) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code : int|None = 1
    try:
        command = json.loads((await stream.read()).decode())
        code = await commands.global_command.GlobalCommand.exec_command(command, stdout, stderr)
        # command_classes = utils.get_subclasses.get_subclasses(commands.command.Command)
        # assert len(set(map(attrgetter('__name__'), command_classes))) == len(command_classes)
        # for command_class in command_classes:
            # if command_class.__name__ == command['command_name']:
                # code = await utils.await_if_necessary.await_if_necessary(command_class.exec_command(command, stdout, stderr))
                # break
        # else:
            # print('Error: command not found.', file=stderr)
    except Exception:
        stderr.write(traceback.format_exc())
    finally:
        stream.write(json.dumps(dict(
            stdout=stdout.getvalue(),
            stderr=stderr.getvalue(),
            code=code,
        )).encode())
        try:
            await stream.drain()
        except Exception:
            pass


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--commands-listen', required=True, type=utils.forwarding_parser.ColonSeparatedSocketSequence(1))
    args = parser.parse_args()
    commands_listen : tuple[str, int] = args.commands_listen[0]
    if not commands_listen[0]:
        commands_listen = ('127.0.0.1', commands_listen[1])
    async with await asyncio.start_server(on_connect, *commands_listen) as server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        pass
