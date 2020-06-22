from functools import wraps
from types import coroutine
import itertools
import heapq


# Borrowing the coroutine style from curio
# https://github.com/dabeaz/curio/blob/master/curio/traps.py
@coroutine
def _kernel_trap(*args):
    result = yield args
    if isinstance(result, BaseException):
        raise result
    else:
        return result


trap_handlers = []


def trap(func):
    trap_id = len(trap_handlers)
    trap_handlers.append(None)

    @wraps(func)
    async def wrapped(*args):
        return await _kernel_trap(trap_id, args)

    def connect_handler(handler_func):
        # ensure same signature as func
        trap_handlers[trap_id] = handler_func

    wrapped.handler = connect_handler

    return wrapped


@trap
async def sleep(delay):
    pass


@trap
async def clock():
    pass


class Task():
    _last_id = 1

    def __init__(self, coro):
        self.id = Task._last_id
        Task._last_id += 1
        self._trap_result = None
        self.coro = coro
        self.send = self.coro.send


async def main():
    print('executing main')
    print('clock', await clock())
    await sleep(2)
    print('slept for two seconds')
    print('clock', await clock())
    return "main result"


def make_kernel():
    current_task = None
    current_time = 0.0
    task_id = itertools.count()
    task_queue = []
    # task_queue = [(current_time, next(task_id), current_task)]

    @sleep.handler
    def trap_sleep(delay):
        nonlocal current_time, current_task
        # Advances time, reschedules the next task
        current_time, _, current_task = heapq.heappushpop(
            task_queue,
            (current_time + delay, next(task_id), current_task)
        )

    @clock.handler
    def trap_clock():
        return current_time

    while task_queue:
        # Time handling
        heapq.heappop(task_queue)

    def kernel(coro):
        current_task = Task(coro)

        while current_task:
            try:
                trap_id, args = current_task.send(current_task._trap_result)
            except StopIteration as e:
                print("DONE")
                # send result to parent

                return e.value
                break

            current_task._trap_result = trap_handlers[trap_id](*args)

    return kernel


kernel = make_kernel()


if __name__ == "__main__":
    kernel(main())
