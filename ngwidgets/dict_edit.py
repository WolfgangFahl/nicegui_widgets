"""
Created on 2023-06-22

@author: wf
"""
from typing import Any, Callable, Dict, Optional, Union
from dataclasses import dataclass, asdict, is_dataclass
from nicegui import ui
from nicegui.elements.input import Input
from nicegui.binding import bind_from


@dataclass
class FieldUiDef:
    """
    A generic user interface definition for a field.
    """

    field_name: str
    label: str
    size: int = 80
    validation: Optional[Callable[[Any], bool]] = None

    @staticmethod
    def from_field(
        field_name: str, label: Optional[str] = None, size: int = 80
    ) -> "FieldUiDef":
        """Automatically creates a FieldUiDef from a field name."""
        return FieldUiDef(field_name=field_name, label=label or field_name, size=size)


@dataclass
class FormUiDef:
    """
    A definition for the entire form's UI.
    """

    title: str
    ui_fields: Dict[str, FieldUiDef]

    @staticmethod
    def from_dataclass(data: dataclass, default_size: int = 80) -> "FormUiDef":
        """Automatically creates a FormUiDef from a dataclass."""
        fields = {
            field_name: FieldUiDef.from_field(field_name, size=default_size)
            for field_name in asdict(data).keys()
        }
        return FormUiDef(title=data.__class__.__name__, ui_fields=fields)

    @staticmethod
    def from_dict(dictionary: dict, default_size: int = 80) -> "FormUiDef":
        """Automatically creates a FormUiDef from a dictionary."""
        fields = {
            k: FieldUiDef.from_field(k, size=default_size) for k in dictionary.keys()
        }
        return FormUiDef(title="Dictionary Form", ui_fields=fields)


class DictEdit:
    """
    NiceGUI based user interface for dictionary or dataclass editing
    that can be customized for each field in a form.

    Attributes:
        d (Union[dict, dataclass]): The data to be edited, converted to a dict if a dataclass.
        form_ui_def (FormUiDef): The UI definition for the form (if any).
        card (ui.card): The card element containing the form.
        inputs (Dict[str, Input]): A dictionary mapping field names to input elements.
    """
    empty="❓"

    def __init__(self, d: Union[dict, dataclass], form_ui_def: Optional[FormUiDef] = None, customization: Optional[Dict[str, Dict[str, Any]]] = None):
        """
        Initialize the DictEdit instance with the given data and optional UI definition.

        Args:
            d (Union[dict, dataclass]): The dictionary or dataclass to be edited.
            form_ui_def (Optional[FormUiDef]): The UI definition for the form. If not provided,
                                               it will be generated automatically.
            customization (Optional[Dict[str, Dict[str, Any]]]): Customizations for the form fields.
        """
        self.d = asdict(d) if is_dataclass(d) else d
        self.form_ui_def = form_ui_def or (
            FormUiDef.from_dataclass(d)
            if is_dataclass(d)
            else FormUiDef.from_dict(self.d)
        )
        if customization:
            self.customize(customization)
        self.setup()

    def customize(self, customization: Dict[str, Dict[str, Any]]):
        """
        Customizes the UI fields based on the given customization dictionary.

        Args:
            customization (Dict[str, Dict[str, Any]]): A dictionary where each key corresponds to
                                                       a field name, and the value is another dictionary
                                                       specifying 'label', 'size', and optionally 'validation'.

        Example:
            customization = {
                'given_name': {'label': 'Given Name', 'size': 50},
                'family_name': {'label': 'Family Name', 'size': 50}
            }
        """
        for field_name, mods in customization.items():
            field_def = self.form_ui_def.ui_fields.get(field_name)
            if field_def:
                field_def.label = mods.get("label", field_def.label)
                field_def.size = mods.get("size", field_def.size)
                if "validation" in mods:
                    field_def.validation = mods["validation"]

    def setup(self):
        """Sets up the UI by creating a card and expansion for the form based on form_ui_def."""
        with ui.card() as self.card:
            with ui.expansion(text=self.form_ui_def.title, icon="house").classes(
                "w-full"
            ) as self.expansion:
                self.inputs = self._create_inputs()
            if 'ui_label' in self.d:
                bind_from(self.expansion._props, 'label', self.d, 'ui_label', 
                              backward=lambda x: f"{self.form_ui_def.title}: {x if x else DictEdit.empty}")


    def _create_inputs(self) -> Dict[str, Input]:
        """Creates input elements for the form based on the FormUiDef."""
        inputs = {}
        for field_def in self.form_ui_def.ui_fields.values():
            value = self.d.get(field_def.field_name)
            input_field = ui.input(label=field_def.label, value=value)
            input_field.bind_value(self.d, field_def.field_name).props(
                f"size={field_def.size}"
            )
            if field_def.validation:
                input_field.validation = {"Invalid input": field_def.validation}
            inputs[field_def.field_name] = input_field
        return inputs

    def add_on_change_handler(self, key: str, handler: Callable):
        """Adds an on_change event handler to the input corresponding to the given key."""
        if key in self.inputs:
            self.inputs[key].on_change(handler)
