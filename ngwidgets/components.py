"""
Created on 2023-12-16

This module, developed under the instruction of WF, provides classes for managing and 
interacting with UI components. It includes the `Component` data class for representing 
individual UI components and the `Components` class for handling a collection of these 
components, with functionality to load and save them in YAML format. These classes are 
intended to facilitate the management of UI components in various applications.

Prompts for LLM: 
- Create Python classes Component and Components for managing UI components, including loading and saving functionality.
- Develop a data class in Python to represent a UI component with the attributes:
    name (str): The name of the component.
    url (str): A URL to the component's code.
    video_url (str): A URL to a video demonstration of the component.
    additional attributes as necessary.
- Implement methods in Components to load and save a collection of Component instances from/to a YAML file.
- The classes should allow easy management and retrieval of UI components for various applications.

Main author: OpenAI's language model (instructed by WF)
"""
from ngwidgets.yamable import YamlAble
from dataclasses import asdict, dataclass
from typing import List,Optional

@dataclass
class Component:
    name: str
    video_url: Optional[str] = None
    issue: Optional[str] = None
    fixed: Optional[str] = None
    # Additional fields can be added here

class Components(YamlAble['Components']):
    """
    Components
    """
    components: List[Component]

    def __init__(self, components: List[Component] = None):
        if components is None:
            self.components = []
        else:
            self.components = components

    @classmethod
    def from_dict(cls, data: dict) -> 'Components':
        components = [Component(**item) for item in data['components']]
        return cls(components)

    def to_dict(self) -> dict:
        return {'components': [asdict(component) for component in self.components]}