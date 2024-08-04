import asyncio
import argparse
import re
import traceback
import sys

from forwarding_parser import ColonSeparatedSocketSequence

import js_common

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', required=True, type=ColonSeparatedSocketSequence(1))
    parser.add_argument('-L', required=True, type=ColonSeparatedSocketSequence(2), help='local tcp forwarding')
    parser.add_argument('-R', required=True, type=ColonSeparatedSocketSequence(2), help='remote tcp forwarding')
    parser.add_argument('-U', required=True, type=ColonSeparatedSocketSequence(2), help='local udp forwarding')
    parser.add_argument('-V', required=True, type=ColonSeparatedSocketSequence(2), help='remote udp forwarding')
    args = parser.parse_args()

    connection = js_common.Connection(remote_socket=args.connect)

    




if __name__ == '__main__':
    asyncio.run(main())
    


