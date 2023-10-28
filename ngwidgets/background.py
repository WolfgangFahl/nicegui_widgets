"""
Created on 2023-09-12

@author: wf
"""
from nicegui import core,Client
import asyncio
import concurrent.futures
import signal
from typing import Callable, Any, Union

class BackgroundTaskHandler:
    """
    A class to handle background tasks, especially those that are CPU-intensive 
    or blocking and thus need to be executed outside the main event loop.
    
    Attributes:
        process_pool_executor (concurrent.futures.ProcessPoolExecutor): Executor to 
            run blocking functions in separate processes.
            
      Usage:
    
        task_handler = BackgroundTaskHandler()
        
        future, result_coro = task_handler.execute_in_background(some_blocking_function, arg1, arg2)
        
        # If needed, to cancel:
        future.cancel()
        
        # When you want the result:
        result = await result_coro()
    """

    def __init__(self):
        """Initializes the background task handler."""
        self.process_pool_executor = concurrent.futures.ProcessPoolExecutor()
        signal.signal(signal.SIGINT, self.handle_sigint)

    def execute_in_background(self, 
                              blocking_function: Callable[..., Any], 
                              *args: Any, 
                              use_process_pool: bool = False,
                              **kwargs: Any) -> (concurrent.futures.Future, Callable[[], Any]):
        """
        Executes a function in the background.
    
        Args:
            blocking_function (Callable[..., Any]): The function to execute.
            *args (Any): Positional arguments to pass to the function.
            use_process_pool (bool, optional): Whether to use a process pool executor. 
                Defaults to False, which means a thread executor will be used.
            **kwargs (Any): Keyword arguments to pass to the function.
    
        Returns:
            concurrent.futures.Future: The future representing the background task.
            Callable[[], Any]: A coroutine to get the result.
        """
        loop = asyncio.get_running_loop()
    
        # The lambda here ensures that both args and kwargs are passed to blocking_function
        func_with_args = lambda: blocking_function(*args, **kwargs)
    
        if use_process_pool:
            future = loop.run_in_executor(self.process_pool_executor, func_with_args)
        else:
            future = loop.run_in_executor(None, func_with_args)
    
        async def get_result():
            return await future
    
        return future, get_result

    async def disconnect(self) -> None:
        """Disconnect all clients from current running server."""
        for client_id in Client.instances:
            await core.sio.disconnect(client_id)

    def handle_sigint(self, signum: signal.Signals, frame: Union[None, Any]) -> None:
        """
        Handles the SIGINT (Ctrl+C) signal to gracefully disconnect and clean up.

        Args:
            signum (signal.Signals): The signal number.
            frame (Union[None, Any]): The interrupted stack frame.
        """
        asyncio.create_task(self.disconnect())
        signal.signal(signal.SIGINT, signal.default_int_handler)

    async def cleanup(self) -> None:
        """
        Cleans up resources and disconnects tasks. This method should be 
        called before the application exits.
        """
        await self.disconnect()
        self.process_pool_executor.shutdown()
