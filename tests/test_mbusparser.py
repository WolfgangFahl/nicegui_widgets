"""
Created on 2025-01-17

@author: wf
"""
import json
from ngwidgets.basetest import Basetest
from ngwidgets.mbus_viewer import MBusParser

class TestMBusParser(Basetest):
    """
    test MBusParser
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def test_mbus_parser(self):
        """
        Test examples from MBusParser class
        """
        mbus_parser = MBusParser()
        for name, hex_data in mbus_parser.examples.items():
            error_msg,json_str = mbus_parser.parse_mbus_data(hex_data)
            if self.debug:
                marker="✗" if error_msg else "✓"
                print(f"{name}{marker}")
                if error_msg:
                    print(error_msg)
                else:
                    json_data=json.loads(json_str)
                    print(json.dumps(json_data,indent=2))

            self.assertIsNone(error_msg, f"Failed to parse {name}")
            self.assertIsInstance(json_data, dict)
