"""
Created on 2023-06-22

@author: wf
"""
from nicegui import ui
from dataclasses import dataclass, asdict, is_dataclass
from typing import Any, Callable, Dict, List, Union
from nicegui.binding import bind_from


@dataclass
class FieldUiDef:
    """
    A generic user interface definition for a field.
    """
    field_name: str
    label: str
    size: int = 80

    @staticmethod
    def from_field(name: str, default_size: int = 80) -> "FieldUiDef":
        """Automatically creates a FieldUiDef from a field name."""
        return FieldUiDef(field_name=name,label=name, size=default_size)


@dataclass
class FormUiDef:
    """
    A definition for the entire form's UI.
    """

    title: str
    ui_fields: List[FieldUiDef]

    @staticmethod
    def from_dataclass(data: dataclass, default_size: int = 80) -> "FormUiDef":
        """Automatically creates a FormUiDef from a dataclass."""
        fields = [
            FieldUiDef.from_field(field_name, default_size)
            for field_name in asdict(data).keys()
        ]
        return FormUiDef(title=data.__class__.__name__, ui_fields=fields)

    @staticmethod
    def from_dict(dictionary: dict, default_size: int = 80) -> "FormUiDef":
        """Automatically creates a FormUiDef from a dictionary."""
        fields = [FieldUiDef.from_field(k, default_size) for k in dictionary.keys()]
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

    def __init__(
        self,
        d: Union[dict, dataclass],
        form_ui_def: FormUiDef = None,
        customization: Dict[str, Dict[str, Any]] = None,
    ):
        """
        Initialize the DictEdit instance.

        Args:
            d (Union[dict, dataclass]): The dictionary or dataclass to be edited.
            form_ui_def (FormUiDef): Optional UI definition for the form.
        """
        self.d = (
            asdict(d) if is_dataclass(d) else d
        )  # Convert dataclass to dict if needed
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
        for field_def in self.form_ui_def.ui_fields:
            # get the field modification for this field (if any)
            field_mod = customization.get(field_def.label,None)
            if field_mod:
                field_def.label = field_mod.get("label", field_def.label)
                field_def.size = field_mod.get("size", field_def.size)
                if "validation" in field_mod:
                    field_def.validation = field_mod["validation"]

    def setup(self):
        """
        setup the UI
        """
        with ui.card() as self.card:
            with ui.expansion(text=self.form_ui_def.title, icon="house").classes(
                "w-full"
            ) as self.expansion:
                self.inputs = self._create_inputs()
                # Bind the label of the expansion to the 'name' field of the data if available
                if "ui_label" in self.d:
                    bind_from(
                        self.expansion._props,
                        "label",
                        self.d,
                        "name",
                        backward=lambda x: f"{self.form_ui_def.title}: {x}",
                    )

    def _create_inputs(self):
        """Creates inputs for the form based on the FormUiDef."""
        inputs = {}
        for field_def in self.form_ui_def.ui_fields:
            value = self.d.get(field_def.label)
            input_field = (
                ui.input(label=field_def.label, value=value)
                .bind_value(self.d, field_def.label)
                .props(f"size={field_def.size}")
            )
            inputs[field_def.label] = input_field
        return inputs

    def add_on_change_handler(self, key: str, handler: Callable):
        """
        Adds an on_change event handler to the input corresponding to the given key.

        Args:
            key (str): The key of the dictionary entry.
            handler (Callable): The event handler function to be added.
        """
        if key in self.inputs:
            self.inputs[key].on_change(handler)
