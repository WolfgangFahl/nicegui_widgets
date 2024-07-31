"""
Created on 2022-11-18

@author: wf
"""

import time


class Profiler:
    """
    simple profiler
    """

    def __init__(self, msg, profile=True, with_start: bool = True):
        """
        construct me with the given msg and profile active flag

        Args:
            msg(str): the message to show if profiling is active
            profile(bool): True if messages should be shown
        """
        self.msg = msg
        self.profile = profile
        if with_start:
            self.start()

    def start(self):
        """
        start profiling
        """
        self.starttime = time.time()
        if self.profile:
            print(f"Starting {self.msg} ...")

    def time(self, extraMsg=""):
        """
        time the action and print if profile is active
        """
        elapsed = time.time() - self.starttime
        if self.profile:
            print(f"{self.msg}{extraMsg} took {elapsed:5.1f} s")
        return elapsed
