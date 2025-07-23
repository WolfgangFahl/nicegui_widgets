"""
Created on 2025-03-09

@author: wf
"""

import asyncio
import inspect
import time
from typing import Callable, Optional

from basemkit.persistent_log import Log
from ngwidgets.progress import Progressbar
from nicegui import background_tasks
from nicegui import run

# optional generic Progressbar tqdm or nicegui.ui
class TaskRunner:
    """
    A robust background task runner that supports:
    - Explicit async, blocking, or async-wrapped-blocking modes
    - Enforces correct usage
    - Supports progress bar feedback
    - Enforces timeouts and cancellation
    """

    def __init__(self, timeout: float = 20.0, progress: Optional[Progressbar] = None):
        self.task = None
        self.timeout = timeout
        self.progress = progress
        self.log = Log()
        self.start_time = None
        self.stop_time = None
        self.task_name = "?"

    def set_name(self, func: Callable):
        """Set task name from function"""
        self.task_name = getattr(func, '__name__', '?')

    def get_status(self) -> str:
        """Get formatted status string with timing information"""
        if not self.start_time:
            status = 'Ready'
        else:
            elapsed = self.get_elapsed_time()
            start_str = time.strftime('%H:%M:%S', time.localtime(self.start_time))

            if self.is_running():
                status = f'Running "{self.task_name}" for {elapsed:.1f}s since {start_str}'
            elif self.stop_time:
                stop_str = time.strftime('%H:%M:%S', time.localtime(self.stop_time))
                status = f'Completed "{self.task_name}" in {elapsed:.1f}s ({start_str}-{stop_str})'
            else:
                status = f'Interrupted "{self.task_name}" after {elapsed:.1f}s from {start_str}'

        return status

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds since task started"""
        elapsed = 0.0
        if self.start_time:
            if self.is_running():
                elapsed = time.time() - self.start_time
            elif self.stop_time:
                elapsed = self.stop_time - self.start_time
        return elapsed

    def cancel_running(self):
        if self.task and not self.task.done():
            self.task.cancel()
        if self.progress:
            self.progress.reset()
        # Reset timing when cancelled
        self.start_time = None
        self.stop_time = None

    def is_running(self) -> bool:
        running = self.task and not self.task.done()
        return running

    def run(self, func: Callable, *args, **kwargs):
        """
        Automatically detect function type and run appropriately.

        Args:
            func: async or sync function
            *args, **kwargs: arguments to pass to func
        """
        if inspect.iscoroutinefunction(func):
            self.run_async(func, *args, **kwargs)
        else:
            self.run_blocking(func, *args, **kwargs)

    def run_blocking(self, blocking_func: Callable, *args, **kwargs):
        """
        Run a blocking (sync) function via asyncio.to_thread.

        Args:
            blocking_func: a regular function doing I/O or CPU-heavy work
            *args, **kwargs: arguments to pass to blocking_func
        """
        if inspect.iscoroutinefunction(blocking_func) or inspect.iscoroutine(
            blocking_func
        ):
            raise TypeError("run_blocking expects a sync function, not async.")
        self.set_name(blocking_func)
        async def wrapper():
            # this would be the native asyncio call
            # await asyncio.to_thread(blocking_func, *args, **kwargs)
            # we use nicegui managed threads
            await run.io_bound(blocking_func, *args, **kwargs)

        self._start(wrapper)

    def run_async_wrapping_blocking(self, coro_func: Callable[[], asyncio.Future]):
        """
        Run an async function that internally handles blocking with to_thread.

        Args:
            coro_func: async function doing await to_thread(blocking_func)
        """
        if not inspect.iscoroutinefunction(coro_func):
            raise TypeError(
                "run_async_wrapping_blocking expects an async def function."
            )
        self.set_name(coro_func)
        self._start(coro_func)

    def run_async(self, coro_func: Callable[..., asyncio.Future], *args, **kwargs):
        """
        Run a pure async function in the background.

        Args:
            coro_func: a non-blocking async function
            *args, **kwargs: arguments to pass to coro_func
        """
        if not inspect.iscoroutinefunction(coro_func):
            raise TypeError("run_async expects an async def function (not called yet).")
        self.set_name(coro_func)
        self._start(coro_func, *args, **kwargs)

    def _start(self, coro_func: Callable[..., asyncio.Future], *args, **kwargs):
        self.cancel_running()
        self.start_time = time.time()

        async def wrapped():
            try:
                if self.progress:
                    self.progress.reset()
                    self.progress.set_description("Working...")
                await asyncio.wait_for(coro_func(*args, **kwargs), timeout=self.timeout)
            except asyncio.TimeoutError:
                self.log.log(
                    "❌", "timeout", "Task exceeded timeout — possible blocking code?"
                )
            except asyncio.CancelledError:
                self.log.log("⚠️", "cancelled", "Task was cancelled.")
            except Exception as ex:
                self.log.log("❌", "exception", str(ex))
            finally:
                if self.progress:
                    self.progress.update_value(self.progress.total)
                self.stop_time = time.time()

        self.task = background_tasks.create(wrapped())
