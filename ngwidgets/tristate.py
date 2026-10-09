"""
tristate.py
-----------
Created on 2023-12-10

@author: WF
@author: OpenAI Assistant (ChatGPT Version 4)

This module provides a Tristate class for use in NiceGUI applications,
creating a tri-state toggle input that cycles through predefined icon sets.

The implementation is inspired by examples and discussions from:
- NiceGUI Custom Vue Component example: https://github.com/zauberzeug/nicegui/tree/main/examples/custom_vue_component
- JSFiddle by WF: https://jsfiddle.net/wf_bitplan_com/941std72/8/
- Stack Overflow answer by WF: https://stackoverflow.com/a/27617418/1497139


Prompts for Reproducing this Code:
1. "Create a Python class Tristate in a module tristate for a NiceGUI component that serves as a tri-state toggle input."
2. "Implement icon cycling within the Python class to handle state changes without relying on JavaScript logic."
3. "Utilize Unicode icon sets within the Python class for the visual representation of each state."
4. "Ensure the Python class handles the reactivity and updates the Vue component's props when the state changes."
5. "Apply google style doc-strings and type hints for better code clarity and leverage black and isort for code formatting and import sorting."
6. "Provide comprehensive documentation within the Python class to explain the functionality and usage of each method and property."
7. "add proper authorship and iso-date of creation information in the module header"
8. "add a prompts for reproducing this code in the header comment section that will allow any proper LLM  to reproduce this code"
9. "Introduce an `update` method invocation within the state change logic to trigger a re-render of the component in NiceGUI.
10. "add links to https://github.com/zauberzeug/nicegui/tree/main/examples/custom_vue_component, https://jsfiddle.net/wf_bitplan_com/941std72/8/ and https://stackoverflow.com/a/27617418/1497139 for proper reference"
11. "Include the following Unicode icon sets in the Tristate component for NiceGUI:
'arrows' with Left Arrow ('←'), Up-Down Arrow ('↕️'), and Right Arrow ('→');
'ballot' with Ballot Box ('☐'), Ballot Box with Check ('☑️'), and Ballot Box with X ('☒️');
'check' with Checkbox ('☐'), Question Mark ('❔'), and Checkmark ('✔️');
'circles' with Circle ('⭘'), Bullseye ('🎯'), and Fisheye ('🔘');
'electrical' with Plug ('🔌'), Battery Half ('🔋'), and Lightning ('⚡');
'faces' with Sad Face ('☹️'), Neutral Face ('😐'), and Happy Face ('☺️');
'hands' with Thumbs Down ('👎'), Hand ('✋'), and Thumbs Up ('👍');
'hearts' with Empty Heart ('♡'), Half Heart ('❤️'), and Full Heart ('❤️');
'locks' with Unlocked ('🔓'), Locked with Pen ('🔏'), and Locked ('🔒');
'marks' with Question Mark ('❓'), Check Mark ('✅'), and Cross Mark ('❌');
'moons' with New Moon ('🌑'), Half Moon ('🌓'), and Full Moon ('🌕');
'musical_notes' with Single Note ('♪'), Double Note ('♫'), and Multiple Notes ('🎶');
'stars' with Empty Star ('☆'), Half Star ('★'), and Full Star ('★');
'traffic_lights' with Red ('🔴'), Yellow ('🟡'), and Green ('🟢');
'weather' with Cloud ('☁️'), Sun ('☀️'), and Thunderstorm ('⛈️')."

"""

from typing import Callable, Optional

from nicegui.element import Element

# Ensure imports are sorted according to isort compatibility
# Apply black coding style for formatting


class Tristate(Element, component="tristate.js"):
    """
    A Tristate toggle component for NiceGUI.

    Attributes:
        icon_set (str): The name of the icon set to use.
        current_icon_index (int): The index of the current icon in the set.
        style (str): CSS styling for the input element.
    """

    ICON_SETS = {
        "arrows": ["←", "↕️", "→"],  # Left Arrow, Up-Down Arrow, Right Arrow
        "ballot": [
            "☐",
            "☑️",
            "☒️",
        ],  # Ballot Box, Ballot Box with Check, Ballot Box with X
        "check": ["☐", "❔", "✔️"],  # Checkbox, Question Mark, Checkmark
        "circles": ["⭘", "🎯", "🔘"],  # Circle, Bullseye, Fisheye
        "electrical": ["🔌", "🔋", "⚡"],  # Plug, Battery Half, Lightning
        "faces": ["☹️", "😐", "☺️"],  # Sad Face, Neutral Face, Happy Face
        "hands": ["👎", "✋", "👍"],  # Thumbs Down, Hand, Thumbs Up
        "hearts": ["♡", "❤️", "❤️"],  # Empty Heart, Half Heart, Full Heart
        "locks": ["🔓", "🔏", "🔒"],  # Unlocked, Locked with Pen, Locked
        "marks": ["❓", "✅", "❌"],  # Question, Check, Cross
        "moons": ["🌑", "🌓", "🌕"],  # New Moon, Half Moon, Full Moon
        "musical_notes": ["♪", "♫", "🎶"],  # Single Note, Double Note, Multiple Notes
        "stars": ["☆", "★", "★"],  # Empty Star, Half Star, Full Star
        "traffic_lights": ["🔴", "🟡", "🟢"],  # Red, Yellow, Green
        "weather": ["☁️", "☀️", "⛈️"],  # Cloud, Sun, Thunderstorm
    }

    def __init__(
        self,
        icon_set_name: str = "marks",
        style: str = "border: none;",
        on_change: Optional[Callable] = None,
    ) -> None:
        """
        Initializes the Tristate component.

        Args:
            icon_set_name (str): The name of the icon set to use. Default is 'marks'.
            style (str): CSS styling for the input element. Default is 'border: none;'.
            on_change (Optional[Callable]): Callback function for state changes.
        """
        super().__init__()
        self.icon_set_name = icon_set_name
        self.icon_set = Tristate.ICON_SETS[icon_set_name]
        self.current_icon_index = 0
        # the style string goes to the input element of the component;
        # self.style is the Style object of the element in nicegui 3
        self.input_style = style
        self.style(style)
        self.user_on_change = on_change
        self.on("change", self.on_change)

        self.update_props()

    def on_change(self, _=None) -> None:
        """Handles the change event, cycles the icon, and calls user-defined callback if any."""
        self.cycle_icon()
        if self.user_on_change is not None:
            self.user_on_change()

    def cycle_icon(self, _=None) -> None:
        """Cycles through the icons in the set and updates the component."""
        self.current_icon_index = (self.current_icon_index + 1) % len(self.icon_set)
        self.update_props()

    def update_props(self) -> None:
        """Updates the component properties with the current icon and style."""
        self.utf8_icon = self.icon_set[self.current_icon_index]
        self._props["value"] = self.utf8_icon
        self._props["style"] = self.input_style
        self.update()

    # Additional methods as needed
