"""
Created on 2023-11-15

A custom logging handler that emits messages to a NiceGUI log element and
a standard logger.

@author: wf
"""

import logging
import sys
import time
from typing import List, TextIO

from nicegui import ui


class LogView:
    """
    Handle logging by delegating to a ui.log
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
        max_lines: int = 100,
        classes: str = "w-full",
        level: int = logging.NOTSET,
        log_stream: TextIO = sys.stderr,
        with_sleep: float = None,
    ):
        self.level = level
        self.with_sleep = with_sleep
        self.loggers: List[logging.Logger] = []
        self.ui_log = ui.log(max_lines=max_lines).classes(classes)
        self.handler = UiLogHandler(self, level)
        self.fallback_handler = logging.StreamHandler(log_stream)
        self.fallback_handler.setLevel(logging.DEBUG)

    def on_fail(self, ex: Exception):
        self.ui_log = None
        self.handler.ui_log = None
        self.fallback_handler.emit(
            f"ui.log failure: {str(ex)} - switching off ui log ..."
        )

    def clear(self):
        """
        clear my ui_log
        """
        if self.ui_log is not None:
            try:
                self.ui_log.clear()
            except Exception as ex:
                self.on_fail(ex)

    def iconize(self, msg: str, level: int) -> str:
        level_icon = self.LOG_LEVEL_ICONS.get(level, "")
        if not msg.startswith(level_icon):
            msg = f"{level_icon}:{msg}"
        return msg

    def push(self, msg: str, level: int = None):
        """
        Push a message to the UI log.

        Args:
            msg (str): The message to push to the log.
        """
        if level is None:
            level = self.level
        msg = self.iconize(msg, level)
        if self.ui_log is None:
            self.fallback_handler.emit(
                logging.makeLogRecord({"msg": msg, "levelno": self.level})
            )
        else:
            try:
                self.ui_log.push(msg)
                if self.with_sleep:
                    time.sleep(self.with_sleep)
            except Exception as ex:
                self.on_fail(ex)

    def setLevel(self, level: int):
        """
        Set the logging level for this handler and all associated loggers.

        Args:
            level (int): The logging level to set.
        """
        self.level = level
        self.handler.setLevel(level)
        self.fallback_handler.setLevel(level)
        for logger in self.loggers:
            logger.setLevel(level)

    def addAsHandler(self, logger: logging.Logger):
        """
        Add this LogView as a handler to the given logger.

        Args:
            logger (logging.Logger): The logger to add this handler to.
        """
        if logger in self.loggers:
            return
        if self.handler not in logger.handlers:
            if self.handler.addAsHandler(logger):
                self.loggers.append(logger)


class UiLogHandler(logging.Handler):
    """
    A logging handler that emits messages to a NiceGUI log element.
    Uses a fallback logger to make sure messages do not get lost when the log element is not available
    """

    def __init__(
        self,
        log_view: LogView,
        level: int = logging.NOTSET,
    ):
        """
        Constructor

        Args:
            log_view (LogView): the LogView which encapsultes the ui.log in which messages will be emitted.
            level (int): The logging level for this handler. Default is logging.NOTSET.
        """
        super().__init__(level)
        self.log_view = log_view

    def addAsHandler(self, logger: logging.Logger) -> bool:
        """
        Add this handler to the given logger if it's not already added.

        Args:
            logger (logging.Logger): The logger to add this handler to.

        Returns:
            bool: True if the handler was added, False if it was already present.
        """
        if self not in logger.handlers:
            logger.addHandler(self)
            # see https://nicegui.io/documentation/log#attach_to_a_logger
            ui.context.client.on_disconnect(lambda: logger.removeHandler(self))
            return True
        else:
            return False

    def emit(self, record: logging.LogRecord):
        """
        Emit a record to the NiceGUI log element
        and a fallback standard logging.

        Args:
            record (logging.LogRecord): The log record to be emitted.
        """
        try:
            formatted_msg = self.format(record)
            self.log_view.push(formatted_msg, record.levelno)
        except Exception as ex:
            self.log_view.on_fail(ex)

    def setLevel(self, level):
        """
        Set the logging level of this handler.

        Args:
            level (int): The logging level to set.
        """
        super().setLevel(level)
