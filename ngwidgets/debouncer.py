"""
Debouncing module for managing rapid
function calls and providing UI feedback.
Created on 2024-06-08
"""

import asyncio
from typing import Any, Callable, Optional

from nicegui import background_tasks, run, ui


class Debouncer:
    """A class to manage debouncing of function calls.

    This class allows for debouncing function calls which can be either CPU-bound or I/O-bound.
    It includes optional callbacks that execute at the start and completion of the debounced function.
    """

    def __init__(
        self,
        delay: float = 0.330,
        debounce_cpu_bound: bool = False,
        debounce_task_name: str = "Debounce Task",
        debug: bool = False,
    ):
        """
        Initialize the Debouncer with a specific delay.

        Args:
            delay (float): The debouncing delay in seconds. Default is 0.330 seconds.
            debounce_cpu_bound (bool): If True, use CPU-bound execution; otherwise use I/O-bound execution.
            debounce_task_name (str): The name to use for the task.
            debug(bool): if True show debug info
        """
        self.delay = delay
        self.counter = 0
        self.debounce_cpu_bound = debounce_cpu_bound
        self.debounce_task_name = debounce_task_name
        self.debug = debug
        self.task: Optional[asyncio.Task] = None

    def log(self, call_type: str, func, *args, **kwargs):
        """
        log the call
        """
        if self.debug:
            print(f"calling {call_type} #{self.counter}. time")
            print("function:", func.__name__)
            print("args:", args, kwargs)

    async def debounce(
        self,
        func: Callable,
        *args,
        on_start: Optional[Callable[[], Any]] = None,
        on_done: Optional[Callable[[], Any]] = None,
        **kwargs,
    ):
        """
        Debounce the given function call, using either CPU-bound or I/O-bound execution based on the flag.
        Optional callbacks can be specified for execution at the start and end of the function.

        Args:
            func (Callable): The function to be debounced.
            on_start (Optional[Callable[[], Any]]): Function to call just before the delay starts.
            on_done (Optional[Callable[[], Any]]): Function to call after the function execution completes.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.
        """
        self.counter += 1
        # abort any running task
        if self.task and not self.task.done():
            self.task.cancel()

        async def task_func():
            if on_start:
                on_start()
            # debounce by waiting
            if self.counter > 1:
                await asyncio.sleep(self.delay)
            try:
                if asyncio.iscoroutinefunction(func):
                    self.log("coroutine", func, *args, **kwargs)
                    await func(*args, **kwargs)
                elif self.debounce_cpu_bound:
                    self.log("cpu_bound", func, *args, **kwargs)
                    await run.cpu_bound(func, *args, **kwargs)
                else:
                    self.log("io_bound", func, *args, **kwargs)
                    await run.io_bound(func, *args, **kwargs)
            except Exception as e:
                print(f"Error during task execution: {e}")
            finally:
                if on_done:
                    on_done()

        self.task = background_tasks.create(task_func(), name=self.debounce_task_name)


class DebouncerUI:
    """A class to manage UI feedback for debouncing, using a specific UI container."""

    def __init__(
        self,
        parent,
        delay: float = 0.330,
        debounce_cpu_bound: bool = False,
        debounce_task_name: str = "Debounce Task",
        debug: bool = False,
    ):
        """
        Initialize the Debouncer UI within a specified parent container.

        Args:
            parent: The container in which the UI feedback should be managed.
            delay (float): The debouncing delay in seconds.
            debounce_cpu_bound (bool): If True, use CPU-bound execution; otherwise use I/O-bound execution.
            debounce_task_name (str): The name to use for the task.
            debug(bool): if True show debug info
        """
        self.parent = parent
        self.debouncer = Debouncer(
            delay=delay,
            debounce_cpu_bound=debounce_cpu_bound,
            debounce_task_name=debounce_task_name,
            debug=debug,
        )
        self.spinner = None

    def debounce(
        self,
        func: Callable,
        *args,
        on_start: Optional[Callable[[], Any]] = None,
        on_done: Optional[Callable[[], Any]] = None,
        **kwargs,
    ):
        """
        Debounce the given function call, managing UI feedback appropriately.

        Args:
            func (Callable): The function to be debounced.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.
        """

        def ui_on_start():
            """
            Default on start behavior is to add a spinner.
            """
            with self.parent:
                if not self.spinner:
                    self.spinner = ui.spinner()
            if on_start:
                on_start()

        def ui_on_done():
            """
            Default behavior is to remove the spinner.
            """
            if on_done:
                on_done()
            if self.spinner:
                try:
                    self.spinner.delete()
                except Exception as _ex:
                    pass
                self.spinner = None

        debounce_result = self.debouncer.debounce(
            func, *args, on_start=ui_on_start, on_done=ui_on_done, **kwargs
        )
        return debounce_result
