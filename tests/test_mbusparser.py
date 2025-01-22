"""
Created on 2025-01-17

@author: wf
"""
import json
from ngwidgets.basetest import Basetest
from ngwidgets.mbus_viewer import MBusParser,MBusExample

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
        for name, example in MBusExample.get().items():
            if not example.hex:
                if self.debug:
                    print(f"{example.name}: ⚪ no hex data")
                continue

            error_msg, frame = mbus_parser.parse_mbus_frame(example.hex)
            if self.debug:
                marker = "✗" if error_msg else "✓"
                print(f"{example.name} {marker}")
                if error_msg:
                    print(f"  {error_msg}")
                else:
                    json_str = mbus_parser.get_frame_json(frame)
                    json_data = json.loads(json_str)
                    print(json.dumps(json_data, indent=2))

            if example.hex:  # only assert for examples with hex data
                self.assertIsNone(error_msg, f"Failed to parse {example.name}")
                self.assertIsInstance(json_data, dict)
