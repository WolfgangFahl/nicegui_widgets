"""
Created on 2023-06-22

@author: wf
"""

from dataclasses import asdict, dataclass, field, fields, is_dataclass
from datetime import date, datetime
from typing import Any, Callable, Dict, Optional, Union

from nicegui import ui
from nicegui.binding import bind_from
from nicegui.elements.input import Input


@dataclass
class FieldUiDef:
    """
    A generic user interface definition for a field.
    """

    field_name: str
    label: str
    size: int = 80
    field_type: Optional[type] = None
    validation: Optional[Callable[[Any], bool]] = None

    @staticmethod
    def from_field(field) -> "FieldUiDef":
        """Automatically creates a FieldUiDef from a dataclass field"""
        return FieldUiDef(
            field_name=field.name, label=field.name, field_type=field.type
        )

    @staticmethod
    def from_key_value(key: str, value) -> "FieldUiDef":
        """Automatically create a FieldUiDef from a key,value pair"""
        # Choose a default type for None values, e.g., str
        field_type = type(value) if value is not None else str
        return FieldUiDef(field_name=key, label=key, field_type=field_type)


@dataclass
class FormUiDef:
    """
    A definition for the entire form's UI.
    """

    title: str
    icon: Optional[str] = "house"
    ui_fields: Dict[str, FieldUiDef] = field(default_factory=dict)

    @staticmethod
    def from_dataclass(data: dataclass) -> "FormUiDef":
        """Automatically creates a FormUiDef from a dataclass."""
        ui_fields = {}
        for field in fields(data):
            ui_fields[field.name] = FieldUiDef.from_field(field)
        return FormUiDef(title=data.__class__.__name__, ui_fields=ui_fields)

    @staticmethod
    def from_dict(dictionary: dict) -> "FormUiDef":
        """Automatically creates a FormUiDef from a dictionary."""
        ui_fields = {
            key: FieldUiDef.from_key_value(key, value)
            for key, value in dictionary.items()
        }
        return FormUiDef(title="Dictionary Form", ui_fields=ui_fields)


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

    empty = "❓"

    def __init__(
        self,
        data_to_edit: Union[dict, dataclass],
        form_ui_def: Optional[FormUiDef] = None,
        customization: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """
        Initialize the DictEdit instance with the given data and optional UI definition.

        Args:
            data_to_edit (Union[dict, dataclass]): The dictionary or dataclass to be edited.
            form_ui_def (Optional[FormUiDef]): The UI definition for the form. If not provided,
                                               it will be generated automatically.
            customization (Optional[Dict[str, Dict[str, Any]]]): Customizations for the form fields.
        """
        self.data_to_edit = data_to_edit
        self.d = asdict(data_to_edit) if is_dataclass(data_to_edit) else data_to_edit
        self.form_ui_def = form_ui_def or (
            FormUiDef.from_dataclass(data_to_edit)
            if is_dataclass(data_to_edit)
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
        if "_form_" in customization:
            form_mod = customization["_form_"]
            self.form_ui_def.title = form_mod.get("title", self.form_ui_def.title)
            self.form_ui_def.icon = form_mod.get("icon", self.form_ui_def.icon)
        for field_name, mods in customization.items():
            field_def = self.form_ui_def.ui_fields.get(field_name, None)
            if field_def:
                field_def.label = mods.get("label", field_def.label)
                field_def.size = mods.get("size", field_def.size)
                if "validation" in mods:
                    field_def.validation = mods["validation"]

    def setup(self):
        """Sets up the UI by creating a card and expansion for the form based on form_ui_def."""
        with ui.card() as self.card:
            with ui.expansion(
                text=self.form_ui_def.title, icon=self.form_ui_def.icon
            ).classes("w-full") as self.expansion:
                self.inputs = self._create_inputs()
            if is_dataclass(self.data_to_edit) and hasattr(
                self.data_to_edit, "ui_label"
            ):
                bind_from(
                    self.expansion._props,
                    "label",
                    self.data_to_edit,
                    "ui_label",
                    backward=lambda x: f"{self.form_ui_def.title}: {x if x else DictEdit.empty}",
                )

    def open(self):
        """
        show the details of the dict edit
        """
        self.expansion.open()

    def close(self):
        """
        hide the details of the dict edit
        """
        self.expansion.close()

    def _create_inputs(self) -> Dict[str, Input]:
        """Creates input elements for the form based on the FormUiDef."""
        inputs = {}
        for field_def in self.form_ui_def.ui_fields.values():
            value = self.d.get(field_def.field_name)
            if field_def.field_type is str:
                input_field = ui.input(label=field_def.label, value=value).props(
                    f"size={field_def.size}"
                )  # Text input for strings
            elif field_def.field_type in [int, float]:
                input_field = ui.number(
                    label=field_def.label, value=value
                )  # Number input for ints and floats
            elif field_def.field_type is bool:
                input_field = ui.checkbox(
                    field_def.label, value=value
                )  # Checkbox for booleans
            elif field_def.field_type in [datetime, date]:
                with ui.input("Date") as input_field:
                    with input_field.add_slot("append"):
                        ui.icon("edit_calendar").on(
                            "click", lambda: menu.open()
                        ).classes("cursor-pointer")
                    with ui.menu() as menu:
                        ui.date().bind_value(input_field)
            else:
                input_field = ui.input(
                    label=field_def.label, value=value
                )  # Default to text input

            input_field.bind_value(self.d, field_def.field_name)
            if field_def.validation:
                input_field.validation = {"Invalid input": field_def.validation}
            inputs[field_def.field_name] = input_field
        return inputs

    def add_on_change_handler(self, key: str, handler: Callable):
        """Adds an on_change event handler to the input corresponding to the given key."""
        if key in self.inputs:
            self.inputs[key].on_change(handler)
