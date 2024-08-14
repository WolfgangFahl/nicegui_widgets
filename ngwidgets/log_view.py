"""
Created on 2023-11-15

A custom logging handler that emits messages to a NiceGUI log element and
a standard logger.

@author: wf
"""

import logging
import sys
from typing import List, TextIO
from nicegui import ui

class LogView:
    """
    Handle logging by delegating to a ui.log
    """

    def __init__(
        self,
        max_lines: int = 100,
        classes: str = "w-full",
        level: int = logging.NOTSET,
        log_stream: TextIO = sys.stderr,
    ):
        self.loggers: List[logging.Logger] = []
        self.ui_log = ui.log(max_lines=max_lines).classes(classes)
        self.handler = UiLogHandler(self.ui_log, level, log_stream)

    def push(self, msg: str):
        self.ui_log.push(msg)

    def setLevel(self, level: int):
        self.handler.setLevel(level)
        for logger in self.loggers:
            logger.setLevel(level)

    def addAsHandler(self, logger: logging.Logger):
        if logger in self.loggers:
            return
        self.loggers.append(logger)
        if self.handler not in logger.handlers:
            self.handler.addAsHandler(logger)

class UiLogHandler(logging.Handler):
    """
    A logging handler that emits messages to a NiceGUI log element.
    Uses a fallback logger to make sure messages do not get lost when the log element is not available
    """

    LOG_LEVEL_ICONS = {
        logging.DEBUG: "🐞",
        logging.INFO: "ℹ️",
        logging.WARNING: "⚠️",
        logging.ERROR: "❌",
        logging.CRITICAL: "🔥",
    }

    def __init__(
        self,
        ui_log: ui.log,
        level: int = logging.NOTSET,
        log_stream: TextIO = sys.stderr,
    ):
        """
        Constructor

        Args:
            ui_log (ui.log): The NiceGUI log element to which messages will be emitted.
            level (int): The logging level for this handler. Default is logging.NOTSET.
            log_stream (TextIO): The stream to use for fallback logging. Default is sys.stderr.
        """
        super().__init__(level)
        self.ui_log = ui_log
        self.fallback_handler = logging.StreamHandler(log_stream)
        self.fallback_handler.setLevel(logging.DEBUG)

    def addAsHandler(self, logger: logging.Logger):
        """
        add me as a handler to the given logger

        Args:
            logger (logging.Logger): the source logger

        """
        if self not in logger.handlers:
            logger.addHandler(self)

    def emit(self, record: logging.LogRecord):
        """
        Emit a record to the NiceGUI log element
        and a fallback standard logging.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        level_icon = self.LOG_LEVEL_ICONS.get(record.levelno, "")
        if record.msg:
            record.msg = f"{level_icon}:{record.msg}"
        self.fallback_handler.emit(record)
        formatted_msg = self.format(record)

        if self.ui_log is not None:
            try:
                self.ui_log.push(formatted_msg)
            except Exception as ex:
                self.fallback_handler.handleError(record)
                self.fallback_handler.emit(f"ui.log failure: {str(ex)} - switching off ui log ...")
                self.ui_log=None
                pass

    def setLevel(self, level):
        """
        Set the logging level of this handler.

        Args:
            level (int): The logging level to set.
        """
        super().setLevel(level)
