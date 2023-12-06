"""
Created on 2023-06-22

@author: wf
"""
from nicegui import ui
class DictEdit:
    """
    nicegui based user interface for dictionary editing
    
    """
    
    def __init__(self, d, default_size:int=80):
        """
        Constructor.

        Args:
            d (dict): The dictionary to be edited.
        """
        self.d = d
        self.inputs = {}

        if d:
            for k in d.keys():
                value = d[k]
                # Create an input field for each key in the dictionary
                self.inputs[k] = ui.input(label=k, value=str(value), on_change=self.on_input_change).props(f"size={default_size}")

    def on_input_change(self, event):
        """
        Handle input change events.

        Args:
            event: The event object containing the changed data.
        """
        key = event.source.label
        new_value = event.value
        self.d[key] = new_value
        # Optionally, update the input field's value
        self.inputs[key].value = new_value
            
    
        
        
