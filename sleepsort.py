"""Implementation of the sleepsort algorithm."""
import asyncio
import typing as t


async def _sort(lst: t.List[int]) -> t.List[int]:
    """Sleep sort algorithm."""
    result: t.List[int] = []
    futures: t.List[asyncio.Future[None]] = []

    min_elem = min(lst)
    sleep_coefficient = 0.001

    async def sort_elem(elem: int) -> None:
        """Sort the element."""
        await asyncio.sleep(sleep_coefficient * (elem - min_elem))
        result.append(elem)

    for elem in lst:
        futures.append(asyncio.ensure_future(sort_elem(elem)))

    await asyncio.gather(*futures)
    return result


def sleep_sort(lst: list[int]) -> list[int]:
    """Sort the list using the sleep sort algorithm."""
    return asyncio.run(_sort(lst))


def test(n: int) -> bool:
    """Test sleeps_sort on a presorted list."""
    lst = list(range(n, 0, -1))
    return sleep_sort(lst) == list(reversed(lst))


async def _min(lst: t.Iterable[int]) -> int:
    """Return the minimum element of a list."""
    queue: asyncio.Queue[int] = asyncio.Queue(1)
    tasks: t.List[asyncio.Task[None]] = []

    async def min_elem(elem: int) -> None:
        """Find the minimum element."""
        await asyncio.sleep(elem)
        await queue.put(elem)

    for elem in lst:
        tasks.append(asyncio.create_task(min_elem(elem)))

    result = await queue.get()
    for task in tasks:
        task.cancel()
    return result


def min_sleep(lst: t.Iterable[int]) -> int:
    """Return the minimum element of a list."""
    return asyncio.run(_min(lst))
