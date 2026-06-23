import asyncio
import threading
from typing import Coroutine, TypeVar, List, Any
from typing import Optional


class ThreadedEventLoop:
    """ Provides a thread-safe lazy-initialized asyncio event loop. """
    _loop: Optional[asyncio.AbstractEventLoop] = None
    _loop_lock = threading.Lock()
    _thread: Optional[threading.Thread] = None

    def _start_thread(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._thread_loop)
        self._thread.daemon = True
        self._thread.name = "Zaber Motion Library Event Loop"
        self._thread.start()

    def _thread_loop(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def get_loop(self) -> asyncio.AbstractEventLoop:
        with self._loop_lock:
            if self._loop is None:
                self._start_thread()
            assert self._loop is not None
            return self._loop


event_loop = ThreadedEventLoop()

TReturn = TypeVar('TReturn')


async def gather_all(*coro: Coroutine[Any, Any, TReturn]) -> List[TReturn]:
    """ Run all coroutines in parallel. """
    return await asyncio.gather(*coro)


def wait_all(*coro: Coroutine[Any, Any, TReturn]) -> List[TReturn]:
    """ Run all coroutines in parallel in thread pool executor and wait for them to finish. """
    future = asyncio.run_coroutine_threadsafe(gather_all(*coro), event_loop.get_loop())
    return future.result()
