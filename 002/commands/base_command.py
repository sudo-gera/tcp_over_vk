from argparse import ArgumentParser
from io import StringIO
from typing import Any
import utils
import utils.await_if_necessary
import utils.get_subclasses
from operator import attrgetter

class BaseCommand:
    @classmethod
    async def add_arguments(cls, parser: ArgumentParser) -> None:
        command_classes = cls.__subclasses__()
        group = parser.add_subparsers(required=bool(command_classes))
        assert len(set(map(attrgetter('__name__'), command_classes))) == len(command_classes)
        for command_class in command_classes:
            command_parser = group.add_parser(command_class.__name__)
            command_parser.add_argument('--_ '+cls.__name__, default=command_class.__name__, required=False, help="For internal use ony. Don't provide manually.")
            await utils.await_if_necessary.await_if_necessary(command_class.add_arguments(command_parser))

    @classmethod
    async def exec_command(cls, command: dict[str, Any], stdout: StringIO, stderr: StringIO) -> int | None:
        command_classes = cls.__subclasses__()
        assert len(set(map(attrgetter('__name__'), command_classes))) == len(command_classes)
        user_command_name = command.get('_ '+cls.__name__, None)
        if user_command_name is None:
            print(f'Error: command {cls.__name__!r} must have {cls.exec_command.__name__!r} method or subcommands.', file=stderr)
            return None
        for command_class in command_classes:
            if command_class.__name__ == user_command_name:
                return await utils.await_if_necessary.await_if_necessary(command_class.exec_command(command, stdout, stderr))
        else:
            print(f'Error: value {user_command_name!r} is invalid argument for after value {cls.__name__!r}.', file=stderr)
            return None
