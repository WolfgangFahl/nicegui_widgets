"""
Created on 2023-15-12


This module, developed as part of the ngwidgets package under the instruction of WF, provides
classes for displaying software components in a NiceGUI application. It defines the
`ComponentView` class for rendering a single component and the `ComponentsView` class for
managing a collection of `ComponentView` instances in a searchable and sortable card layout.

see https://github.com/WolfgangFahl/nicegui_widgets/issues/50

The implementation is inspired by a Streamlit application, as analyzed from a provided screenshot,
which includes UI elements such as a date picker widget, package metadata display, and installation
command. These will be recreated using NiceGUI's elements such as `ui.date_picker()`, `ui.label()`,
`ui.link()`, `ui.card()`, `ui.text()`, and `ui.input()` for a similar user experience.

For details on the original Streamlit implementation, refer to:
https://raw.githubusercontent.com/jrieke/components-hub/main/streamlit_app.py

Prompts for LLM:
- Incorporate the Component and Components classes from ngwidgets into NiceGUI.
- Implement the setup method for ComponentView to render component details in a UI card.
- Implement the setup method for ComponentsView to manage a searchable and sortable display of components.
- Adapt the webserver class from ngwidgets to use ComponentsView for displaying components.

Main author: OpenAI's language model (instructed by WF)
"""

from typing import List
from nicegui import ui
from ngwidgets.nicegui_component import Component, Components  # Replace with the actual import path

class ComponentView:
    def __init__(self, component: Component):
        self.component = component

    def setup(self,container) -> ui.card:
        """
        setup a card 
        """
        with container:
            self.card=ui.card()
            with self.card:
                ui.label(f'{self.component.name} - {self.component.version}')
                if self.component.stars is not None:
                    ui.label(f'⭐️ Stars: {self.component.stars}')
                ui.label(f'Package: {self.component.package}')
                ui.label(f'GitHub: {self.component.github}')
                ui.link('PyPI', self.component.pypi)
                ui.label('Description:')
                ui.textarea(self.component.pypi_description)
                ui.button('Copy Install Command', on_click=lambda: self.copy_to_clipboard(self.component.install_instructions))
            return self.card
class ComponentsView:
    """
    display the available components as rows and columns
    sorted by user preference (default: stars) and allows to search/filter
    """
    def __init__(self, webserver: 'InputWebserver', components: Components = None):
        """Initialize the ComponentsView with an optional collection of Components.

        Args:
            webserver (InputWebserver): The webserver that serves the components.
            components (Components): The collection of software components. If None, components are loaded from storage.
        """        
        self.webserver = webserver
        if components is None:
            components = Components(topic="nicegui")
            components.load()
        self.components = components
        self.setup()

    def setup(self):
        """Set up the UI elements to render the collection of components as a searchable and sortable card layout in NiceGUI."""
        # Filter input for searching components
        self.filter_input = ui.input(placeholder='Search components...',on_change=self.update_view)
    
        # Component cards container
        self.cards_container = ui.grid()
        self.views={}
        # Initially display all components
        self.update_view()
    
    def update_view(self):
        """Update the view to render the filtered and sorted components."""
        search_term = self.filter_input.value.lower()
        if search_term:
            filtered_components = [comp for comp in self.components.components if search_term in comp.name.lower()]
        else:
            # Include all components if search term is empty
            filtered_components = self.components.components

        # Clear the current cards container
        self.cards_container.clear()
    
        # Sort the components by stars (descending order) as an example
        sorted_components = sorted(filtered_components, key=lambda c: c.stars if c.stars else 0, reverse=True)
    
        # Create a card for each component
        for component in sorted_components:
            cv=ComponentView(component)
            self.views[component.name]=cv
            cv.setup(self.cards_container)
           
