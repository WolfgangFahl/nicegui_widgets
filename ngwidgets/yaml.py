"""
Created on 2023-12-08

@author: wf, ChatGPT

Prompts for the development of the 'Yaml' class within the 'yaml' module:
1. Develop a Python class named 'Yaml' in a module called 'yaml'. This class should focus on converting dataclass instances to YAML format, specifically for use in object-oriented programming.
2. Implement methods in the 'Yaml' class for formatting multi-line string attributes using YAML block scalar style and excluding attributes with None values from the YAML output.
3. Add a method to handle multi-line strings in the 'Yaml' class, ensuring they are formatted as block scalars in the YAML output.
4. Include functionality to recursively remove None values from dataclass instances before conversion in the 'Yaml' class.
5. The 'Yaml' class should only process dataclass instances, with error handling to raise a ValueError for non-dataclass objects.
6. Write a comprehensive test suite for the 'Yaml' class within the context of the 'ngwidgets.basetest' framework. The tests should verify correct block scalar formatting, omission of None values, and general accuracy of the YAML conversion.
7. Emphasize the use of Google-style docstrings, comprehensive comments, and type hints throughout the 'Yaml' class and its test suite.
8. Adhere strictly to the provided instructions, and if there are any assumptions or uncertainties, seek clarification before proceeding.

"""

from dataclasses import asdict, is_dataclass
from typing import Any

import yaml


class Yaml:
    """
    A YAML handler class for converting dataclass objects to YAML format.
    """

    def __init__(self):
        """
        Initializes the Yaml handler, setting up custom representers.
        """
        self.dumper = yaml.Dumper
        self.dumper.ignore_aliases = lambda *args: True
        self.dumper.add_representer(type(None), self.represent_none)
        self.dumper.add_representer(str, self.represent_literal)

    def represent_none(self, _, __) -> yaml.Node:
        """
        Custom representer for ignoring None values in the YAML output.
        """
        return self.dumper.represent_scalar("tag:yaml.org,2002:null", "")

    def represent_literal(self, dumper: yaml.Dumper, data: str) -> yaml.Node:
        """
        Custom representer for block scalar style for strings.
        """
        if "\n" in data:
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    def to_yaml(self, obj: Any) -> str:
        """
        Converts a dataclass object to a YAML string, omitting None values and using block scalar style for strings.

        Args:
            obj (Any): The dataclass object to convert to YAML.

        Returns:
            str: The YAML string representation of the dataclass object.

        Raises:
            ValueError: If the provided object is not a dataclass instance.
        """
        if not is_dataclass(obj):
            raise ValueError("Provided object must be a dataclass instance.")

        obj_dict = asdict(obj)
        clean_dict = self.remove_nones(obj_dict)
        yaml_str = yaml.dump(
            clean_dict,
            Dumper=self.dumper,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        return yaml_str

    def remove_nones(self, value: Any) -> Any:
        """
        Recursively removes keys with None values from a dictionary or list.

        Args:
            value (Any): The input value (dictionary, list, or other).

        Returns:
            Any: The cleaned value with no None values.
        """
        if isinstance(value, dict):
            return {k: self.remove_nones(v) for k, v in value.items() if v is not None}
        elif isinstance(value, list):
            return [self.remove_nones(v) for v in value]
        return value


# Example usage:
# Assuming 'competence_tree' is an instance of a dataclass
# yaml_handler = Yaml()
# yaml_representation = yaml_handler.to_yaml(competence_tree)
# print(yaml_representation)
