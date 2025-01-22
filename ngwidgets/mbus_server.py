#!/usr/bin/env python
"""
Created on 2025-01-22

@author: wf
"""
import argparse
from nicegui import ui
import meterbus
import re
import json

class MBusParser:
    def __init__(self):
        self.hex_input = None
        self.result_area = None

    def fromhex(self, x, base=16):
        """Convert hex string to integer"""
        return int(x, base)

    def parse_mbus_data(self, hex_data):
        """
        Parse M-Bus hex data and return JSON result
        Returns tuple of (success, result)
        where result is either JSON data or error message
        """
        try:
            # Remove any whitespace from input
            filtered_data = "".join(hex_data.split())

            # Convert hex string to bytes
            data = list(map(self.fromhex, re.findall("..", filtered_data)))

            # Parse using meterbus
            frame = meterbus.load(data)
            json_data = frame.to_JSON()

            # Pretty print the JSON for display
            parsed = json.loads(json_data)
            return True, json.dumps(parsed, indent=2)
        except Exception as e:
            return False, f"Error parsing M-Bus data: {str(e)}"

    def createTextArea(self, label, readonly=False, placeholder=None):
        """Create a standardized textarea with common styling"""
        textarea = ui.textarea(
            label=label,
            placeholder=placeholder
        ).classes("w-full").props('input-class=h-64').props('clearable')
        textarea.enabled=not readonly
        return textarea

    def on_parse(self):
        """Handle parse button click"""
        success, result = self.parse_mbus_data(self.hex_input.value)
        self.result_area.value = result

    def create_ui(self):
        """Create the NiceGUI user interface"""
        # Add a title
        ui.label("M-Bus Message Parser").classes("text-h4 q-mb-md")

        # Create text areas using the common function
        self.hex_input = self.createTextArea(
            label="Enter M-Bus hex message",
            placeholder="e.g. 684d4d680800722654832277..."
        )

        self.result_area = self.createTextArea(
            label="Parsed Result",
            readonly=True
        )

        # Add a parse button
        ui.button("Parse Message", on_click=self.on_parse).classes("q-mt-md")

        # Add example message
        ui.button(
            "Load Example",
            on_click=lambda: self.hex_input.set_value(
                "684d4d680800722654832277040904360000000c78265483220406493500000c14490508000b2d0000000b3b0000000a5a18060a5e89020b61883200046d0d0c2c310227c80309fd0e2209fd0f470f00008d16"
            )
        ).classes("q-mt-md q-ml-sm")

def main():
    """Entry point for M-Bus Parser"""
    parser = argparse.ArgumentParser(description="M-Bus Message Parser Web Interface")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )

    args = parser.parse_args()

    # Create parser instance and UI
    mbus_parser = MBusParser()
    mbus_parser.create_ui()

    # Start the server
    ui.run(
        host=args.host,
        port=args.port,
        title="M-Bus Parser",
        dark=None,  # Use system preference for dark/light mode
        show=True
    )

# Call main directly without a guard
# for proper nicegui startup
main()