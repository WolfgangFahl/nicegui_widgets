"""
Created on 18.05.2025

@author: wf
"""

import requests

from ngwidgets.live_test import LiveWebTest, LiveCmd
#from ngwidgets.basetest import Basetest

#class TestLiveTest(Basetest):
class TestLiveTest(LiveWebTest):
    """
    test a live test Environment
    """

    def setUp(self, debug=False, profile=True):
        LiveWebTest.setUp(self, debug=debug, profile=profile)

    def test_via_cmd_line(self):
        """
        this is not a true test but a debug tool
        to check the LiveWebServer/LiveWebSolution/LiveCmd combo is working
        """
        return
        cmd = LiveCmd()
        args=["-d","-s"]
        _exit_code = cmd.cmd_main(args)

    def test_basic_json(self):
        """Test a basic JSON response"""
        # Set the handler for this test
        self.set_test_handler(lambda: {"status": "ok", "message": "Basic test passed"})

        # Make the request
        test_url=self.get_test_url()
        response = requests.get(test_url)

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["message"], "Basic test passed")

    def test_complex_json(self):
        """Test a more complex JSON structure"""
        # Set the handler with nested data
        self.set_test_handler(
            lambda: {
                "status": "ok",
                "data": {
                    "numbers": [1, 2, 3, 4, 5],
                    "nested": {"a": 1, "b": "text", "c": True},
                    "items": [
                        {"id": 1, "name": "Item 1"},
                        {"id": 2, "name": "Item 2"},
                        {"id": 3, "name": "Item 3"},
                    ],
                },
            }
        )

        # Make the request
        response = requests.get(f"{self.base_url}/test")

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(len(data["data"]["numbers"]), 5)
        self.assertEqual(data["data"]["nested"]["b"], "text")
        self.assertEqual(len(data["data"]["items"]), 3)
        self.assertEqual(data["data"]["items"][1]["name"], "Item 2")

    def test_error_response(self):
        """Test error response handling"""
        # Set a handler that returns an error response
        self.set_test_handler(
            lambda: {"status": "error", "error": "Not found", "code": 404}
        )

        # Make the request
        response = requests.get(f"{self.base_url}/test")

        # The HTTP status should still be 200 since we're just testing JSON content
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["error"], "Not found")
        self.assertEqual(data["code"], 404)
