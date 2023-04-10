import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)
    print('\x1b[A\x1b[80C'+f"printed at {time.strftime('%X')}")

async def main():
    print(f"started at {time.strftime('%X')}")

    t1= asyncio.create_task(say_after(1, 'hello'))
    t2= asyncio.create_task(say_after(2, 'world'))
    await t1
    await t2

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())
