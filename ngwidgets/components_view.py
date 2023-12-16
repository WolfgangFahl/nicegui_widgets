"""
Created on 2023-12-16

@author: wf
"""
from ngwidgets.projects import Project, Projects
from ngwidgets.components import Component, Components
from nicegui import ui

class ComponentsView:
    """
    Display a collection of components in a grid layout
    """

    def __init__(self, webserver: "InputWebserver",projects:Projects,project: Project):
        self.webserver = webserver
        self.projects = projects
        self.project  = project
        self.components = project.get_components(projects.default_directory)

    def setup(self):
        """
        Set up the UI elements to render the collection of components
        as a grid layout with four columns.
        """
        with ui.grid(columns=4) as container:
            # Create a card for each component
            for component in self.components.components:
                cv = ComponentView(component)
                cv.setup(container)
                
class ComponentView:
    """
    Display a single component
    """

    def __init__(self, component: Component):
        self.component = component
        
    def setup(self, container) -> ui.card:
        """
        Setup a card for the component
        """
        with container:
            self.card = ui.card()
            with self.card:
                with ui.row().classes("flex w-full items-center"):
                    # Title
                    title = f"{self.component.name}"
                    ui.label(title).classes("text-2xl")