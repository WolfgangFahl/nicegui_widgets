"""
Created on 2023-12-16

This components module has the classes Component and Components
for managing components of an online software components bazaar
It was created for nicegui components but may be adapted to other
context by modifying the topic,

Prompts for LLM: 
- Create Python classes Component and Components for managing UI components, including loading and saving functionality.
- Develop a data class in Python to represent a UI component with the attributes:
    name: The title or identifier of the component.
    source: A web link directing to where the component's code can be found.
    demo_url: A web link to an image or video showing the component in action.
    doc_url: A web link to any documentation or detailed information about the component.
    issue: Reference to any known issues or bugs related to the component, typically tracked on platforms like GitHub.
    fixed: Date marking when any known issues or bugs with the component were resolved.
- Implement methods in Components to load and save a collection of Component instances from/to a YAML file.

Main author: OpenAI's language model (instructed by WF)
"""

from dataclasses import dataclass, field
from typing import List, Optional

from ngwidgets.yamlable import lod_storable


@lod_storable
class Component:
    """
    Represents a single component with its associated metadata.

    Attributes:
        name (str): The name of the component.
        description(str): a multiline description of the component
        source (Optional[str]): The source code URL of the component, if available.
        demo_url (Optional[str]): The URL of an online demo of the component, if available.
        demo_image_url (Optional[str]): The URL of a picture and/or video demonstrating the component, if available.
        doc_url (Optional[str]): The URL of the documentation for the component, if available.
        issue (Optional[str]): The identifier for any related issue (github), if applicable.
        fixed (Optional[str]): The date on which any related issue was fixed, if applicable.
    """

    name: str
    description: Optional[str] = None
    source: Optional[str] = None
    demo_url: Optional[str] = None
    demo_image_url: Optional[str] = None
    doc_url: Optional[str] = None
    issue: Optional[int] = None
    fixed: Optional[str] = None


@lod_storable
class Components:
    """
    Components
    """

    version: Optional[str] = None
    components: List[Component] = field(default_factory=list)
