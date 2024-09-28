from __future__ import annotations
from argparse import ArgumentParser
from typing import Coroutine
import commands.base_command
from typing import Any
import utils.await_if_necessary
import utils.forwarding_parser

class GlobalCommand(commands.base_command.BaseCommand):
    @classmethod
    async def add_arguments(cls, parser: ArgumentParser) -> None:
        if cls is GlobalCommand:
            parser.add_argument('--commands-connect', required=True, type=utils.forwarding_parser.ColonSeparatedSocketSequence(1))
        return await utils.await_if_necessary.await_if_necessary(super().add_arguments(parser))

