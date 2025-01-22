"""
Created on 2025-01-22

@author: wf
"""
import re
import json
import meterbus
from nicegui import ui

class MBusParser:
    """
    parse MBus data
    """
    def __init__(self):
        # Define example messages
        self.examples = {
            "Basic Reading": "684d4d680800722654832277040904360000000c78265483220406493500000c14490508000b2d0000000b3b0000000a5a18060a5e89020b61883200046d0d0c2c310227c80309fd0e2209fd0f470f00008d16",
            "CF Echo II": "68 03 03 68  73 fe a6 17  16"
        }

    def fromhex(self, x, base=16):
        """Convert hex string to integer"""
        return int(x, base)

    def get_frame_json(self, frame):
        """Fallback JSON generation if to_JSON not available"""
        if hasattr(frame, 'to_JSON'):
            return frame.to_JSON()
        # Fallback to basic frame info
        data = {
            "header": {
                "start": frame.header.startField.parts[0],
                "length": len(frame.body.bodyHeader.ci_field.parts) + 2,
                "control": frame.header.cField.parts[0],
                "address": frame.header.aField.parts[0]
            },
            "body": {
                "ci_field": frame.body.bodyHeader.ci_field.parts[0]
            }
        }
        return json.dumps(data)

    def parse_mbus_data(self, hex_data):
        """
        Parse M-Bus hex data and return JSON result
        Returns tuple of (error_msg, json_str)
        """
        json_str = None
        error_msg = None
        try:
            # Allow flexible whitespace in input
            filtered_data = "".join(char for char in hex_data if char.isalnum())
            # Convert hex string to bytes
            data = list(map(self.fromhex, re.findall("..", filtered_data)))
            # Parse using meterbus
            frame = meterbus.load(data)
            json_str = self.get_frame_json(frame)
        except Exception as e:
            error_msg = f"Error parsing M-Bus data: {str(e)}"
        return error_msg, json_str

class MBusViewer(MBusParser):
    """
    Meterbus message viewer with JSON editor support
    """
    def __init__(self, solution=None):
        super().__init__()
        self.solution = solution
        self.hex_input = None
        self.json_code = None
        self.example_select = None
        self.error_label = None

    def createTextArea(self, label, placeholder=None, classes: str = "h-64"):
        """Create a standardized textarea with common styling"""
        textarea = (
            ui.textarea(label=label, placeholder=placeholder)
            .classes("w-full")
            .props(f"input-class={classes}")
            .props("clearable")
        )
        return textarea

    def on_parse(self):
        """Handle parse button click"""
        try:
            error_msg, json_str = self.parse_mbus_data(self.hex_input.value)
            if error_msg:
                self.error_label.text = error_msg
                self.error_label.classes("text-red-500")
            else:
                self.json_code.content=json_str
        except Exception as ex:
            self.solution.handle_exception(ex)

    def on_example_change(self):
        """Handle example selection change"""
        selected = self.example_select.value
        if selected in self.examples:
            self.hex_input.value = self.examples[selected]
            self.on_parse()

    def setup_ui(self):
        """Create the NiceGUI user interface"""
        ui.label("M-Bus Message Parser").classes("text-h4 q-mb-md")

        self.error_label = ui.label().classes("text-red-500 hidden")

        self.example_select = ui.select(
            label="Select Example",
            options=list(self.examples.keys()),
            on_change=self.on_example_change,
        ).classes("w-full q-mb-md")

        self.hex_input = self.createTextArea(
            label="Enter M-Bus hex message",
            placeholder="e.g. 68 4d 4d 68 08 00 72 26 54 83 22 77...",
            classes="h-32",
        )

        with ui.row() as self.button_row:
            ui.button("Parse Message", on_click=self.on_parse).classes("q-mt-md")

        self.json_code = ui.code(language='json').classes("w-full h-96 q-mt-md")