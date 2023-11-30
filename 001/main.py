import asyncio

import parse_args
import client

async def main():
    args = await parse_args.process_args()
    await client.send(vars(args))

if __name__ == '__main__':
    asyncio.run(main())
