"""
Created on 2023-12-16

@author: wf
"""

from nicegui import ui

from ngwidgets.components import Component, Components
from ngwidgets.projects import Project, Projects
from ngwidgets.projects_view import ProjectView
from ngwidgets.widgets import Link


class ComponentsView:
    """
    Display a collection of components in a grid layout
    """

    def __init__(
        self, webserver: "InputWebserver", projects: Projects, project: Project
    ):
        self.webserver = webserver
        self.projects = projects
        self.project = project
        self.components = project.get_components(projects.default_directory)
        self.displayed_components = []
        self.container = None
        self.slider = None
        self.page_size = 8

    def setup(self):
        """
        Set up the UI elements to render the collection of components
        as a grid layout with four columns.
        """
        self.project_container = ui.grid(columns=4)
        self.project_view = ProjectView(self.project)
        self.project_view.setup(self.project_container)
        if self.components:
            self.slider = ui.slider(
                min=1,
                max=len(self.components.components) // self.page_size + 1,
                step=1,
                value=1,
                on_change=self.update_display,
            )
            self.container = ui.grid(columns=4)
        self.update_display()

    def update_display(self, *_args):
        """
        Update the displayed components based on the slider's position
        """
        if not self.components:
            return
        start_index = (self.slider.value - 1) * self.page_size
        end_index = start_index + self.page_size
        displayed_components = self.components.components[start_index:end_index]

        # Clear existing components in the container
        self.container.clear()

        # Add new components to the container
        with self.container:
            for component in displayed_components:
                cv = ComponentView(self.project, component)
                cv.setup(self.container)


class ComponentView:
    """
    Display a single component
    """

    def __init__(self, project: Project, component: Component):
        self.project = project
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
                    html_markup = ""
                    delim = ""
                    if self.component.demo_url:
                        link = Link.create(self.component.demo_url, "demo")
                        html_markup += link
                        delim = " "
                    if self.component.source:
                        url = self.project.components_url.replace(
                            "/.components.yaml", self.component.source
                        )
                        link = Link.create(url, self.component.name)
                        html_markup += delim + link
                        delim = " "
                    if self.component.issue:
                        url = f"{self.project.github}/issues/{self.component.issue}"
                        link = Link.create(url, f"#{self.component.issue}")
                        html_markup += delim + link
                        delim = " "
                    ui.html(html_markup)
                    if self.component.demo_image_url:
                        ui.image(self.component.demo_image_url)
                    if self.component.description:
                        ui.label(self.component.description)
