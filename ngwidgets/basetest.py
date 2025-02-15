"""
Created on 2021-08-19

@author: wf
"""

import getpass
import os
import threading
import unittest
from functools import wraps

from ngwidgets.profiler import Profiler


class Basetest(unittest.TestCase):
    """
    base test case
    """

    def setUp(self, debug=False, profile=True):
        """
        setUp test environment
        """
        unittest.TestCase.setUp(self)
        self.debug = debug
        self.profile = profile
        msg = f"test {self._testMethodName}, debug={self.debug}"
        self.profiler = Profiler(msg, profile=self.profile)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.profiler.time()

    @staticmethod
    def inPublicCI():
        """
        are we running in a public Continuous Integration Environment?
        """
        publicCI = getpass.getuser() in ["travis", "runner"]
        jenkins = "JENKINS_HOME" in os.environ
        return publicCI or jenkins

    @staticmethod
    def isUser(name: str):
        """Checks if the system has the given name"""
        return getpass.getuser() == name

    @staticmethod
    def timeout(seconds):
        """
        Decorator to enforce a timeout on test methods.

        params:
          1: seconds: Timeout in seconds
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = [None]
                exception = [None]

                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=target)
                thread.start()
                thread.join(seconds)

                if thread.is_alive():
                    raise TimeoutError(f"Test timed out after {seconds} seconds")

                if exception[0] is not None:
                    raise exception[0]

                return result[0]

            return wrapper

        return decorator


if __name__ == "__main__":
    unittest.main()
