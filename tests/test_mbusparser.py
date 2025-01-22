"""
Created on 2025-01-17

@author: wf
"""

import json

from ngwidgets.basetest import Basetest
from ngwidgets.mbus_viewer import MBusExamples, MBusParser, Manufacturer, Device, MBusExample


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
        for name, example in MBusExamples.get().items():
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
        
    def test_create_mbus_examples(self):
        """
        Create MBus examples structure with manufacturers, devices, examples dictionaries
        """
        # Create manufacturers dict
        manufacturers = {
            "allmess": Manufacturer(
                name="Allmess",
                url="https://www.allmess.de",
                country="Germany"
            )
        }
        
        # Create devices dict with manufacturer references
        devices = {
            "cf_echo_ii": Device(
                mid="allmess",  # Reference to manufacturer by id
                model="CF Echo II",
                doc_url="https://www.allmess.de/fileadmin/multimedia/alle_Dateien/MA/MA_BA_12088-AC%20CF%20Echo%20II%20D%20TS1021_KL.pdf"
            ),
            "ultramaxx": Device(
                mid="allmess",  # Reference to manufacturer by id
                model="UltraMaXX",
                title="Integral-MK UltraMaXX",
                doc_url="https://www.allmess.de/fileadmin/multimedia/alle_Dateien/DB/DB_P0012%20UltraMaXX_TS0219.pdf"
            )
        }
        
        # Create examples dict with device references
        examples = {
            "cf_echo_basic": MBusExample(
                did="cf_echo_ii",  # Reference to device by id
                name="Basic Reading",
                title="Standard M-Bus reading",
                hex="684d4d680800722654832277040904360000000c78265483220406493500000c14490508000b2d0000000b3b0000000a5a18060a5e89020b61883200046d0d0c2c310227c80309fd0e2209fd0f470f00008d16"
            ),
            "cf_echo_init": MBusExample(
                did="cf_echo_ii",  # Reference to device by id
                name="CF Echo II init write",
                title="CF Echo II init",
                hex="6803036873fea61716"
            ),
            "ultramaxx_init": MBusExample(
                did="ultramaxx",  # Reference to device by id
                name="CFUM init",
                title="CFUM init",
                hex="6803036853fea6f716"
            )
        }
        
        # Create MBusExamples instance with all three dicts
        mbus_examples = MBusExamples(
            manufacturers=manufacturers,
            devices=devices,
            examples=examples
        )
        
        # Save to YAML file
        yaml_path = "/tmp/mbus_examples.yaml"
        mbus_examples.save_to_yaml_file(yaml_path)
        if self.debug:
            print(f"Created YAML file at {yaml_path}")
        
        # Verify we can read it back
        loaded_examples = MBusExamples.load_from_yaml_file(yaml_path)
        loaded_examples.relink()
        self.assertEqual(len(loaded_examples.manufacturers), len(manufacturers))
        self.assertEqual(len(loaded_examples.devices), len(devices))
        self.assertEqual(len(loaded_examples.examples), len(examples))
        
        # Test dereferencing
        for device in loaded_examples.devices.values():
            self.assertIsInstance(device.manufacturer, Manufacturer)
        
        for example in loaded_examples.examples.values():
            self.assertIsInstance(example.device, Device)
            self.assertIsInstance(example.device.manufacturer, Manufacturer)