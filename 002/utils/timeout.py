import asyncio
import traceback
import typing

T = typing.TypeVar('T')

async def run_with_timeout(coro: typing.Coroutine[typing.Any, typing.Any, T], timeout: float) -> T:
    task : asyncio.Task[T] = asyncio.create_task(coro)
    await asyncio.wait([task], timeout=timeout)
    if task.done():
        return task.result()
    task.cancel()
    raise asyncio.TimeoutError

async def get_with_timeout(queue: asyncio.Queue[T], timeout: float) -> T:
    return await run_with_timeout(queue.get(), timeout) 

async def _test() -> None:
    try:
        print('begin')
        await asyncio.sleep(1)
        print('end')
    finally:
        print(traceback.format_exc())

async def _main() -> None:
    await run_with_timeout(_test(), 1.5)
    await run_with_timeout(_test(), 0.5)

if __name__ == '__main__':
    asyncio.run(_main())