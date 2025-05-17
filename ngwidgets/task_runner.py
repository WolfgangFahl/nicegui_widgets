"""
Created on 2025-03-09

@author: wf
"""

from nicegui import background_tasks, ui


class TaskRunner:
    """
    A wrapper to run a single task in background.

    This class provides functionality to execute asynchronous tasks while
    ensuring only one task runs at a time. It includes timeout functionality
    to automatically cancel long-running tasks.
    """

    def __init__(self, timeout: float = 20):
        """
        Initialize a TaskRunner instance.

        Args:
            timeout (float, optional): Maximum time in seconds to allow a task to run
                before cancellation. Defaults to 20 seconds.
        """
        self.task = None
        self.timeout = timeout  # seconds

    def cancel_running(self):
        """
        Cancel the currently running task if one exists.
        """
        if self.task:
            self.task.cancel()

    def run(self, func):
        """
        Run a function as a background task, canceling any previously running task.

        Args:
            func: An async function to be executed in the background.
                Should be passed without calling it (no parentheses).

        Note:
            The function will be automatically cancelled after the timeout period.
        """
        # Cancel any running task
        self.cancel_running()

        # Set timeout
        ui.timer(self.timeout, lambda: self.cancel_running(), once=True)

        # Run new task in background
        self.task = background_tasks.create(func())
