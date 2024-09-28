import utils.import_all
import asyncio
import utils.await_if_necessary
import utils.forwarding_parser
import argparse
import utils.get_subclasses
import utils.stream
import json
import commands.global_command
import utils
import sys

async def main() -> int|None:
    parser = argparse.ArgumentParser()
    await utils.await_if_necessary.await_if_necessary(commands.global_command.GlobalCommand.add_arguments(parser))
    # parser.add_argument('--commands-connect', required=True, type=utils.forwarding_parser.ColonSeparatedSocketSequence(1))
    # group = parser.add_subparsers(required=True)
    # command_classes = utils.get_subclasses.get_subclasses(commands.command.Command)
    # assert len(set(map(attrgetter('__name__'), command_classes))) == len(command_classes)
    # for command_class in command_classes:
    #     command_parser = group.add_parser(command_class.__name__)
    #     command_parser.add_argument('--____command_name____', dest='command_name', default=command_class.__name__, required=False)
    #     await utils.await_if_necessary.await_if_necessary(command_class.add_arguments(command_parser))
    args = parser.parse_args()
    print(args)
    commands_connect : tuple[str, int] = args.commands_connect[0]
    if not commands_connect[0]:
        commands_connect = ('127.0.0.1', commands_connect[1])
    async with utils.stream.Stream(await asyncio.open_connection(*commands_connect)) as stream:
        stream.write(json.dumps(vars(args)).encode())
        stream.write_eof()
        await stream.drain()
        out = json.loads((await stream.read()).decode())
        sys.stdout.write(out['stdout'])
        sys.stderr.write(out['stderr'])
        code = out['code']
        assert isinstance(code, int|None)
        if isinstance(code, int):
            return code
        if code is None:
            return code
        assert False

if __name__ == '__main__':
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        pass
