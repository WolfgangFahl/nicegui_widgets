"""
Created on 2023-06-22

@author: wf
"""
from nicegui import ui


class DictEdit:
    """
    nicegui based user interface for dictionary editing
    """

    def __init__(self, d, default_size: int = 80):
        """
        Constructor.

        Args:
            d (dict): The dictionary to be edited.
        """
        self.d = d
        self.inputs = {}

        if d:
            for k in d.keys():
                # Create an input field and bind it to the dictionary value
                input_field = (
                    ui.input(label=k, value=d[k])
                    .bind_value(d, k)
                    .props(f"size={default_size}")
                )
                self.inputs[k] = input_field

    def add_on_change_handler(self, key: str, handler):
        """
        Adds an on_change event handler to the input corresponding to the given key.

        Args:
            key (str): The key of the dictionary entry.
            handler (callable): The event handler function to be added.
        """
        if key in self.inputs:
            self.inputs[key].on_change(handler)
