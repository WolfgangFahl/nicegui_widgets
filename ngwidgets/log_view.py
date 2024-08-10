"""
Created on 2023-11-15

A custom logging handler that emits messages to a NiceGUI log element and
handles errors by printing to stderr and invoking a custom error handler.

@author: wf
"""

import logging
import sys
from nicegui import ui


class LogElementHandler(logging.Handler):
    """
    A logging handler that emits messages to a NiceGUI log element.

    Attributes:
        solution: An object that handles exceptions, expected to have a handle_exception method.
        element (ui.log): The NiceGUI log element where messages are pushed.
        level (int): The logging level for this handler.
    """

    def __init__(self, solution, element: ui.log, level: int = logging.NOTSET) -> None:
        """
        Initialize the LogElementHandler.

        Args:
            solution: The solution object that handles exceptions.
            element (ui.log): The NiceGUI log element to which messages will be emitted.
            level (int): The logging level for this handler. Default is logging.NOTSET.
        """
        self.solution = solution
        self.element = element
        super().__init__(level)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a record to the NiceGUI log element.

        This method formats the log record and pushes it to the NiceGUI log element.
        If an error occurs during this process, the error is handled by handleError.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        try:
            msg = self.format(record)
            self.element.push(msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            self.handleError(ex, record)

    def handleError(self, ex: Exception, record: logging.LogRecord) -> None:
        """
        Handle errors that occur during the emit process.

        This method prints the error message to stderr and invokes the solution's
        handle_exception method.

        Args:
            ex (Exception): The exception that occurred during the emit process.
            record (logging.LogRecord): The log record that was being processed when the error occurred.
        """
        err_msg = f"Error: {str(ex)} | Log Record: {str(record)}"
        print(err_msg, file=sys.stderr)
        
