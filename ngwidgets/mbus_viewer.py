"""
Created on 2025-01-22

@author: wf
"""

import json
import os
import re
from dataclasses import field
from typing import Dict

import meterbus
from nicegui import ui

from ngwidgets.widgets import Link
from ngwidgets.yamlable import lod_storable
from reportlab.lib.textsplit import dumbSplit


@lod_storable
class Manufacturer:
    """
    A manufacturer of M-Bus devices
    """

    name: str
    url: str
    country: str = "Germany"  # Most M-Bus manufacturers are German

    def as_html(self) -> str:
        return (
            Link.create(url=self.url, text=self.name, target="_blank")
            if self.url
            else self.name
        )


@lod_storable
class Device:
    """
    A device class for M-Bus devices storing manufacturer reference
    """
    mid: str  # manufacturer id reference
    model: str
    title: str = ""  # Optional full product title
    doc_url: str = ""  # Documentation URL
    # manufacturer: Manufacturer - set on relink

    def as_html(self) -> str:
        title = self.title if self.title else self.model
        device_link = Link.create(url=self.doc_url, text=title, target="_blank") if self.doc_url else title
        mfr_html = self.manufacturer.as_html() if hasattr(self, 'manufacturer') else self.mid
        return f"{mfr_html} → {device_link}"
    
@lod_storable
class MBusExample:
    """
    An M-Bus example storing device reference
    """
    did: str  # device id reference
    name: str
    title: str
    hex: str
    # device: Device - set on relink

    def as_html(self) -> str:
        device_html = self.device.as_html() if hasattr(self, 'device') else self.did
        example_text = f"{self.name}: {self.title}" if self.title else self.name
        return f"{device_html} → {example_text}"
    


@lod_storable
class MBusExamples:
    """
    Manages M-Bus devices and their examples with separate dictionaries for
    manufacturers, devices and examples
    """
    manufacturers: Dict[str, Manufacturer] = field(default_factory=dict)
    devices: Dict[str, Device] = field(default_factory=dict)
    examples: Dict[str, MBusExample] = field(default_factory=dict)

    @classmethod
    def get(cls, yaml_path: str = None) -> 'MBusExamples':
        """
        Load and dereference M-Bus examples from YAML
        
        Args:
            yaml_path: Path to YAML file (defaults to examples_path/mbus_examples.yaml)
            
        Returns:
            MBusExamples instance with dereferenced objects
        """
        if yaml_path is None:
            yaml_path = cls.examples_path() + "/mbus_examples.yaml"
            
        # Load raw YAML data
        mbus_examples = cls.load_from_yaml_file(yaml_path)
        mbus_examples.relink()
        return mbus_examples
        
    def relink(self):
        """
        Reestablish object references between manufacturers, devices and examples
        """
        # Dereference manufacturers in devices
        for device_id, device in self.devices.items():
            if device.mid in self.manufacturers:
                device.manufacturer = self.manufacturers[device.mid]
            else:
                raise KeyError(f"Manufacturer '{device.mid}' not found for device '{device_id}'")
                
        # Dereference devices in examples
        for example_id, example in self.examples.items():
            if example.did in self.devices:
                example.device = self.devices[example.did]
            else:
                raise KeyError(f"Device '{example.did}' not found for example '{example_id}'")


    @classmethod
    def examples_path(cls) -> str:
        # the root directory (default: examples)
        path = os.path.join(os.path.dirname(__file__), "../ngwidgets_examples")
        path = os.path.abspath(path)
        return path
    


class MBusParser:
    """
    parse MBus data
    """

    def __init__(self):
        # Define example messages
        self.examples = MBusExamples.get().examples

    def fromhex(self, x, base=16):
        """Convert hex string to integer"""
        return int(x, base)

    def get_frame_json(self, frame):
        """Fallback JSON generation if to_JSON not available"""
        if hasattr(frame, "to_JSON"):
            return frame.to_JSON()
        # Fallback to basic frame info
        data = {
            "header": {
                "start": frame.header.startField.parts[0],
                "length": len(frame.body.bodyHeader.ci_field.parts) + 2,
                "control": frame.header.cField.parts[0],
                "address": frame.header.aField.parts[0],
            },
            "body": {"ci_field": frame.body.bodyHeader.ci_field.parts[0]},
        }
        return json.dumps(data)

    def parse_mbus_frame(self, hex_data):
        """
        Parse M-Bus hex data and return mbus frame
        Returns tuple of (error_msg, mbus_frame)
        """
        frame = None
        error_msg = None
        try:
            # Allow flexible whitespace in input
            filtered_data = "".join(char for char in hex_data if char.isalnum())
            # Convert hex string to bytes
            data = list(map(self.fromhex, re.findall("..", filtered_data)))
            # Parse using meterbus
            frame = meterbus.load(data)
        except Exception as e:
            error_msg = f"Error parsing M-Bus data: {str(e)}"
        return error_msg, frame


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
        self.error_html = None

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
            with self.result_row:
                self.json_code.content = ""
                self.error_view.content = ""
                mbus_hex_str = self.hex_input.value
                error_msg, frame = self.parse_mbus_frame(mbus_hex_str)
                if error_msg:
                    self.error_view.content = f"{error_msg}"
                else:
                    json_str = self.get_frame_json(frame)
                    self.json_code.content = json_str
        except Exception as ex:
            self.solution.handle_exception(ex)

    def on_example_change(self):
        """Handle example selection change"""

        selected = self.example_select.value
        if selected in self.examples:
            example = self.examples[selected]
            self.hex_input.value = example.hex
            self.example_details.content = example.as_html()
            self.on_parse()

    def setup_ui(self):
        """Create the NiceGUI user interface"""
        ui.label("M-Bus Message Parser").classes("text-h4 q-mb-md")

        self.example_select = ui.select(
            label="Select Example",
            options=list(self.examples.keys()),
            on_change=self.on_example_change,
        ).classes("w-full q-mb-md")

        self.example_details = ui.html().classes("w-full mb-4")

        self.hex_input = self.createTextArea(
            label="Enter M-Bus hex message",
            placeholder="e.g. 68 4d 4d 68 08 00 72 26 54 83 22 77...",
            classes="h-32",
        )

        with ui.row() as self.button_row:
            ui.button("Parse Message", on_click=self.on_parse).classes("q-mt-md")
        with ui.row() as self.result_row:
            self.error_view = ui.html()
            self.json_code = ui.code(language="json").classes("w-full h-96 q-mt-md")
