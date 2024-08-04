import asyncio
import argparse
import re
import traceback
import sys

from forwarding_parser import ColonSeparatedSocketSequence

import js_common

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--listen', required=True, type=ColonSeparatedSocketSequence(1))
    args = parser.parse_args()

    server = asyncio.start_server(js_common.SingleConnection, **args.listen[0])

    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())

