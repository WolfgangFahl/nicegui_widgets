"""
Created on 2025-03-09

@author: wf
"""

import asyncio
import inspect
from typing import Callable, Optional

from nicegui import background_tasks
from basemkit.persistent_log import Log

# optional generic Progressbar tqdm or nicegui.ui
from ngwidgets.progress import Progressbar


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

    def cancel_running(self):
        if self.task and not self.task.done():
            self.task.cancel()
            if self.progress:
                self.progress.reset()

    def is_running(self) -> bool:
        running = self.task and not self.task.done()
        return running

    def run_async(self, coro_func: Callable[[], asyncio.Future]):
        """
        Run a pure async function in the background.

        Args:
            coro_func: a non-blocking async function
        """
        if not inspect.iscoroutinefunction(coro_func):
            raise TypeError("run_async expects an async def function (not called yet).")
        self._start(coro_func)

    def run_blocking(self, blocking_func: Callable[[], any]):
        """
        Run a blocking (sync) function via asyncio.to_thread.

        Args:
            blocking_func: a regular function doing I/O or CPU-heavy work
        """
        if inspect.iscoroutinefunction(blocking_func) or inspect.iscoroutine(
            blocking_func
        ):
            raise TypeError("run_blocking expects a sync function, not async.")

        async def wrapper():
            await asyncio.to_thread(blocking_func)

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
        self._start(coro_func)

    def _start(self, coro_func: Callable[[], asyncio.Future]):
        self.cancel_running()

        async def wrapped():
            try:
                if self.progress:
                    self.progress.reset()
                    self.progress.set_description("Working...")
                await asyncio.wait_for(coro_func(), timeout=self.timeout)
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

        self.task = background_tasks.create(wrapped())
