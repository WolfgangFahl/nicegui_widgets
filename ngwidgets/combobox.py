"""
Created on 2024-07-04


@author: wf
"""
from typing import Dict, List

from nicegui import (
    ui,
)  # Ensures all necessary UI components, including select, are imported


class ComboBox:
    """
    A ComboBox class that encapsulates a UI selection control which allows both drop-down and free-form text input,
    suitable for dynamic user interfaces.

    Attributes:
        label_base (str): The base text for the combobox label.
        options (List[str] or Dict[str, str]): The current list of options available in the combobox.
        select (ui.Select): The UI component instance, allowing for both selection and direct input.
    """

    def __init__(self, 
        label: str, 
        options: List[str] or Dict[str, str],
        width_chars:int=40,
        **kwargs):
        self.label_base = label
        self.width_chars=width_chars
        self.options = sorted(options) if isinstance(options, list) and all(options) else options
        self.select = None
        self.kwargs = kwargs
        self.setup_ui()

    def setup_ui(self):
        """Initializes the UI component for the combobox with optional text input capability."""
        self.select = ui.select(
            label=f"{self.label_base} ({len(self.options)})",
            options=self.options,
            with_input=True,  # Allows users to either select from the dropdown or enter custom text.
            **self.kwargs  # Pass all additional keyword arguments to the select component.
        )
        self.select.style(f'width: {self.width_chars}ch')  # 

        
    def update_options(self, new_options: List[str] or Dict[str, str], limit: int = None, options_count: int = None):
        """Updates the options available in the combobox and refreshes the label, applying a limit to the number of items displayed if specified,
        and showing total available options if different from displayed due to the limit.
    
        Args:
            new_options (List[str] or Dict[str, str]): The new options to update in the combobox.
            limit (int, optional): Maximum number of options to display. If None, all options are displayed.
            options_count (int, optional): The total count of available options, relevant only if a limit is set.
        """
        # Sort new_options if it is a list and all elements are non-None, otherwise use as is
        if isinstance(new_options, list) and all(new_options):
            new_options = sorted(new_options)
    
        # Apply limit if specified
        if limit is not None and isinstance(new_options, list) and len(new_options) > limit:
            new_options = new_options[:limit]
            # Use options_count to show how many are available in total
            total_options = options_count if options_count is not None else len(new_options)
            label_text = f"{self.label_base} ({len(new_options)}/{total_options})"
        else:
            label_text = f"{self.label_base} ({len(new_options)})"
    
        self.options = new_options
        self.select.options = self.options
        self.select._props['label'] = label_text = label_text
    
        # Explicitly update the UI to reflect changes
        self.select.update()


