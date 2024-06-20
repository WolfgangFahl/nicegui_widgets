"""
Debouncing module for managing rapid function calls and providing UI feedback.
Created on 2024-06-08
@author: wf
"""

from nicegui import ui, run, background_tasks
import asyncio
from typing import Callable, Optional

from nicegui import ui, run, background_tasks
import asyncio
from typing import Callable, Optional, Any

class Debouncer:
    """A class to manage debouncing of function calls.
    
    This class allows for debouncing function calls which can be either CPU-bound or I/O-bound.
    It includes optional callbacks that execute at the start and completion of the debounced function.
    """
    
    def __init__(self, delay: float = 0.330):
        """
        Initialize the Debouncer with a specific delay.

        Args:
            delay (float): The debouncing delay in seconds. Default is 330 milliseconds.
        """
        self.delay = delay
        self.task: Optional[asyncio.Task] = None

    async def debounce(self, func: Callable, on_start: Callable[[], Any] = None, on_done: Callable[[], Any] = None,
                       debounce_cpu_bound: bool = False, debounce_task_name: str = 'Debounce Task',
                       *args, **kwargs):
        """
        Debounce the given function call, using either CPU-bound or I/O-bound execution based on the flag.
        Optional callbacks can be specified for execution at the start and end of the function.

        Args:
            func (Callable): The function to be debounced.
            on_start (Callable[[], Any], optional): Function to call just before the delay starts.
            on_done (Callable[[], Any], optional): Function to call after the function execution completes.
            debounce_cpu_bound (bool): If True, use CPU-bound execution; otherwise use I/O-bound execution.
            debounce_task_name (str): The name to use for the task.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.
        """
        if self.task:
            self.task.cancel()

        async def task_func():
            if on_start:
                on_start()
            await asyncio.sleep(self.delay)
            try:
                if asyncio.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                elif debounce_cpu_bound:
                    await run.cpu_bound(func, *args, **kwargs)
                else:
                    await run.io_bound(func, *args, **kwargs)
            finally:
                if on_done:
                    on_done()

        self.task = background_tasks.create(task_func(), name=debounce_task_name)

class DebouncerUI:
    """A class to manage UI feedback for debouncing, using a specific UI container."""
    
    def __init__(self, parent, delay: float = 0.330):
        """
        Initialize the Debouncer UI within a specified parent container.

        Args:
            parent: The container in which the UI feedback should be managed.
            delay (float): The debouncing delay in seconds.
        """
        self.parent = parent
        self.debouncer = Debouncer(delay)

    async def debounce(self, func: Callable, 
                       debounce_cpu_bound: bool = False, 
                       debounce_task_name: str = 'Debounce Task',
                       *args, **kwargs):
        """
        Debounce the given function call, managing UI feedback appropriately.

        Args:
            func (Callable): The function to be debounced.
            debounce_cpu_bound (bool): If True, use CPU-bound execution; otherwise use I/O-bound execution.
            debounce_task_name (str): The name to use for the task.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.
        """
        def on_start():
            with self.parent:
                self.spinner = ui.spinner()

        def on_done():
            self.parent.clear()

        await self.debouncer.debounce(func, 
            on_start=on_start, 
            on_done=on_done,                          
            debounce_cpu_bound=debounce_cpu_bound,
            debounce_task_name=debounce_task_name, 
            *args, 
            **kwargs)

