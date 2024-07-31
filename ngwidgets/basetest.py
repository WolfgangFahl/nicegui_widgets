"""
Created on 2021-08-19

@author: wf
"""

import getpass
import os
import unittest

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


if __name__ == "__main__":
    unittest.main()
