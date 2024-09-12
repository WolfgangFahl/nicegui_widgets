"""
Created on 2024-09-11

see https://github.com/zauberzeug/nicegui/blob/main/tests/README.md

@author: wf
"""

from nicegui import ui
from nicegui.testing import Screen


def test_hello_world(screen: Screen):
    ui.label("Hello, world")

    screen.open("/")
    screen.should_contain("Hello, world")
