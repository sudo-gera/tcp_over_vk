import asyncio
import sys
import argparse

async def user(argv, out):
    print('hello', file=out)

if __name__ == '__main__':
    asyncio.run(user(sys.argv, sys.stdout))

