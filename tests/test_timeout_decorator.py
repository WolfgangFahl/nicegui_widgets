"""
Created on 2025-02-15

@author: wf
"""

import time

from ngwidgets.basetest import Basetest


class TestTimeoutDecorator(Basetest):
    """
    Test the TimeoutDecorator functionality
    """

    def setUp(self, debug=True, profile=True):
        """
        Setup the test environment
        """
        Basetest.setUp(self, debug, profile)

    def test_timeout_exceeded(self):
        """
        Test that the timeout decorator raises an error when time limit is exceeded
        """
        with self.assertRaises(TimeoutError):

            @Basetest.timeout(0.2)
            def long_function():
                time.sleep(0.5)

            long_function()

    def test_timeout_not_exceeded(self):
        """
        Test that the timeout decorator does not raise an error if function completes in time
        """

        @Basetest.timeout(2)
        def quick_function():
            return "Success"

        result = quick_function()
        self.assertEqual(result, "Success")
