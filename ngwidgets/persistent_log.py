"""
Created on 2024-10-04

@author: wf
"""

import logging
from collections import Counter
from dataclasses import field
from datetime import datetime
from typing import List, Optional, Tuple

from lodstorage.yamlable import lod_storable

# ANSI colors
BLUE = "\033[0;34m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
END_COLOR = "\033[0m"


@lod_storable
class LogEntry:
    """
    Represents a log entry with a message, kind, and log level name.
    """

    msg: str
    kind: str
    level_name: str
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@lod_storable
class Log:
    """
    Wrapper for persistent logging.
    """

    entries: List[LogEntry] = field(default_factory=list)

    def color_msg(self, color, msg):
        """Display a colored message"""
        print(f"{color}{msg}{END_COLOR}")

    def __post_init__(self):
        """
        Initializes the log with level mappings and updates the level counts.
        """
        self.do_log = True
        self.do_print = False
        self.levels = {"❌": logging.ERROR, "⚠️": logging.WARNING, "✅": logging.INFO}
        self.level_names = {
            logging.ERROR: "error",
            logging.WARNING: "warn",
            logging.INFO: "info",
        }
        self.update_level_counts()

    def clear(self):
        """
        Clears all log entries.
        """
        self.entries = []
        self.update_level_counts()

    def update_level_counts(self):
        """
        Updates the counts for each log level based on the existing entries.
        """
        self.level_counts = {"error": Counter(), "warn": Counter(), "info": Counter()}
        for entry in self.entries:
            counter = self.get_counter(entry.level_name)
            if counter is not None:
                counter[entry.kind] += 1

    def get_counter(self, level: str) -> Counter:
        """
        Returns the counter for the specified log level.
        """
        return self.level_counts.get(level)

    def get_level_summary(self, level: str, limit: int = 7) -> Tuple[int, str]:
        """
        Get a summary of the most common counts for the specified log level.

        Args:
            level (str): The log level name ('error', 'warn', 'info').
            limit (int): The maximum number of most common entries to include in the summary (default is 7).

        Returns:
            Tuple[int, str]: A tuple containing the count of log entries and a summary message.
        """
        counter = self.get_counter(level)
        if counter:
            count = sum(counter.values())
            most_common_entries = dict(
                counter.most_common(limit)
            )  # Get the top 'limit' entries
            summary_msg = f"{level.capitalize()} entries: {most_common_entries}"
            return count, summary_msg
        return 0, f"No entries found for level: {level}"

    def log(self, icon: str, kind: str, msg: str):
        """
        Log a message with the specified icon and kind.

        Args:
            icon (str): The icon representing the log level ('❌', '⚠️', '✅').
            kind (str): The category or type of the log message.
            msg (str): The log message to record.
        """
        level = self.levels.get(icon, logging.INFO)
        level_name = self.level_names[level]
        icon_msg = f"{icon}:{msg}"
        log_entry = LogEntry(msg=icon_msg, level_name=level_name, kind=kind)
        self.entries.append(log_entry)

        # Update level counts
        self.level_counts[level_name][kind] += 1

        if self.do_log:
            logging.log(level, icon_msg)
        if self.do_print:
            print(icon_msg)
