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


class TaskRunner:
    """
    A robust background task runner that supports:
    - Explicit async, blocking, or async-wrapped-blocking modes
    - Enforces correct usage
    - Supports progress bar feedback
    - Enforces timeouts and cancellation
    - Returns task references for external cancellation
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
        """🆕 Cancel currently running task and record timing"""
        if self.task and not self.task.done():
            try:
                self.task.cancel()
                self.log.log("🔄", "cancel", f'Cancelled task "{self.task_name}"')
            except Exception as ex:
                self.log.log("⚠️", "cancel_error", f"Error cancelling task: {ex}")

        if self.progress:
            self.progress.reset()

        # 🆕 Record stop time when cancelled (instead of resetting timing)
        if self.start_time and not self.stop_time:
            self.stop_time = time.time()

    def is_running(self) -> bool:
        """Check if task is currently running"""
        running = self.task and not self.task.done()
        return running

    def run(self, func: Callable, *args, **kwargs):
        """
        Automatically detect function type and run appropriately.

        Args:
            func: async or sync function
            *args, **kwargs: arguments to pass to func

        Returns:
            asyncio.Task: The created background task
        """
        if inspect.iscoroutinefunction(func):
            return self.run_async(func, *args, **kwargs)
        else:
            return self.run_blocking(func, *args, **kwargs)

    def run_blocking(
        self,
        blocking_func: Callable,
        *args,
        on_result: Optional[Callable] = None,
        **kwargs,
    ):
        """
        Run a blocking (sync) function via asyncio.to_thread.

        Args:
            blocking_func: a regular function doing I/O or CPU-heavy work
            on_result: called with the return value of blocking_func when given
            *args, **kwargs: arguments to pass to blocking_func

        Returns:
            asyncio.Task: The created background task
        """
        if inspect.iscoroutinefunction(blocking_func) or inspect.iscoroutine(
            blocking_func
        ):
            raise TypeError("run_blocking expects a sync function, not async.")
        self.set_name(blocking_func)

        async def wrapper():
            # Use nicegui managed threads
            result = await run.io_bound(blocking_func, *args, **kwargs)
            if on_result:
                on_result(result)

        return self._start(wrapper)

    def run_async_wrapping_blocking(
        self,
        coro_func: Callable[[], asyncio.Future],
        on_result: Optional[Callable] = None,
    ):
        """
        Run an async function that internally handles blocking with to_thread.

        Args:
            coro_func: async function doing await to_thread(blocking_func)
            on_result: called with the return value of coro_func when given

        Returns:
            asyncio.Task: The created background task
        """
        if not inspect.iscoroutinefunction(coro_func):
            raise TypeError(
                "run_async_wrapping_blocking expects an async def function."
            )
        self.set_name(coro_func)
        return self._start(coro_func)

    def run_async(self, coro_func: Callable[..., asyncio.Future], *args, **kwargs):
        """
        Run a pure async function in the background.

        Args:
            coro_func: a non-blocking async function
            *args, **kwargs: arguments to pass to coro_func

        Returns:
            asyncio.Task: The created background task
        """
        if not inspect.iscoroutinefunction(coro_func):
            raise TypeError("run_async expects an async def function (not called yet).")
        self.set_name(coro_func)
        return self._start(coro_func, *args, **kwargs)

    def _start(
        self,
        coro_func: Callable[..., asyncio.Future],
        *args,
        on_result: Optional[Callable] = None,
        **kwargs,
    ):
        """
        🆕 Internal method to start a task with proper error handling and timing.

        Returns:
            asyncio.Task: The created background task
        """
        self.cancel_running()
        self.start_time = time.time()
        self.stop_time = None  # 🆕 Reset stop time on new task

        async def wrapped():
            try:
                if self.progress:
                    self.progress.reset()
                    self.progress.set_description("Working...")
                result = await asyncio.wait_for(
                    coro_func(*args, **kwargs), timeout=self.timeout
                )
                if on_result:
                    on_result(result)
            except asyncio.TimeoutError:
                self.log.log(
                    "❌", "timeout",
                    f'Task "{self.task_name}" exceeded {self.timeout}s timeout — possible blocking code?'
                )
            except asyncio.CancelledError:
                self.log.log("⚠️", "cancelled", f'Task "{self.task_name}" was cancelled.')
                raise  # 🆕 Re-raise to properly propagate cancellation
            except Exception as ex:
                self.log.log("❌", "exception", f'Task "{self.task_name}": {str(ex)}')
                raise  # 🆕 Re-raise to allow caller to handle
            finally:
                if self.progress:
                    self.progress.update_value(self.progress.total)
                self.stop_time = time.time()

        self.task = background_tasks.create(wrapped())
        return self.task  # 🆕 Return task reference for external cancellation