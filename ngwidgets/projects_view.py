"""
Created on 2023-15-12


This module, developed as part of the ngwidgets package under the instruction of WF, provides
classes for displaying software projects in a NiceGUI application. It defines the
`ProjectView` class for rendering a single project and the `ProjectsView` class for
managing a collection of `ProjectView` instances in a searchable and sortable card layout.

see https://github.com/WolfgangFahl/nicegui_widgets/issues/50

The implementation is inspired by a Streamlit application, as analyzed from a provided screenshot,
which includes UI elements such as a date picker widget, package metadata display, and installation
command. These will be recreated using NiceGUI's elements such as `ui.date_picker()`, `ui.label()`,
`ui.link()`, `ui.card()`, `ui.text()`, and `ui.input()` for a similar user experience.

For details on the original Streamlit implementation, refer to:
https://raw.githubusercontent.com/jrieke/projects-hub/main/streamlit_app.py

Prompts for LLM:
- Incorporate the Project and Projects classes from ngwidgets into NiceGUI.
- Implement the setup method for ProjectView to render project details in a UI card.
- Implement the setup method for ProjectsView to manage a searchable and sortable display of projects.
- Adapt the webserver class from ngwidgets to use ProjectsView for displaying projects.

Main author: OpenAI's language model (instructed by WF)
"""

import math
from datetime import datetime, timedelta

from nicegui import run, ui

from ngwidgets.progress import NiceguiProgressbar
from ngwidgets.projects import Project, Projects
from ngwidgets.widgets import Link


class ProjectView:
    """
    display a single project
    """

    def __init__(self, project: Project):
        self.project = project

    def setup(self, container) -> ui.card:
        """
        setup a card for my project
        """
        with container:
            self.card = ui.card()
            with self.card:
                with ui.row().classes("flex w-full items-center"):
                    # Title
                    title = f"{self.project.name}"
                    if self.project.version:
                        title = f"{title} - {self.project.version}"
                    ui.label(title).classes("text-2xl")
                    if self.project.stars:
                        # Flexible space to push stars to the right
                        ui.label("").classes("flex-grow")
                        star_rating = math.ceil(math.log10(self.project.stars + 0.5))
                        star_rating = min(star_rating, 5)
                        github_stars = f"{'⭐'*star_rating}️ {self.project.stars}"
                        ui.label(github_stars).classes("text-xl ml-auto")
                columns = 4 if self.project.components_url else 3
                self.card_grid = ui.grid(columns=columns)
                with self.card_grid:
                    if self.project.pypi:
                        pypi_icon = "<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/PyPI_logo.svg/64px-PyPI_logo.svg.png' alt='pypi' title='pypi'/>"
                        pypi_link = Link.create(
                            self.project.pypi, f"{pypi_icon}{self.project.package}"
                        )
                        html_markup = pypi_link
                        self.pypi_html = ui.html(html_markup)
                    if self.project.github:
                        github_icon = "<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Octicons-mark-github.svg/32px-Octicons-mark-github.svg.png' alt='github' title='github'/>"
                        github_name = self.project.github_repo_name
                        github_html_markup = f"{github_icon}{github_name}"
                        github_link = Link.create(
                            self.project.github, github_html_markup
                        )
                        html_markup = f"{github_link}"
                        self.github_html = ui.html(html_markup)
                        html_markup = ""
                        if self.project.github_author:
                            author = self.project.github_author
                            author_url = f"https://github.com/{author}"
                            if self.project.avatar:
                                avatar_icon = f"<img src='{self.project.avatar}' alt='{author}' title='{author}' style='width: 40px; height: 40px; border-radius: 50%;'/>"
                            else:
                                avatar_icon = author
                            author_link = Link.create(
                                author_url, f"{avatar_icon}{author}"
                            )
                            html_markup = f"{author_link}"
                        self.project_html = ui.html(html_markup)
                        # components (if any)
                        html_markup = ""
                        if self.project.components_url:
                            components = self.project.get_components()
                            components_count = len(
                                components.components
                            )  # Assuming get_components returns a list
                            components_icon = "<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Octicons-puzzle.svg/32px-Octicons-puzzle.svg.png' alt='components' title='components'/>"
                            components_restful_url = (
                                f"/components/{self.project.solution_id}"
                            )
                            components_link = Link.create(
                                components_restful_url, components_icon
                            )
                            html_markup += f" {components_link} {components_count}"
                            self.components_html = ui.html(html_markup)
                html_markup = ""
                if self.project.pypi:
                    if self.project.pypi_description:
                        html_markup = f"""<strong>{self.project.package}</strong>:
            <span>{self.project.pypi_description}</span>"""
                    inst_html = f"<pre>{self.project.install_instructions}</pre>"
                    html_markup = f"{html_markup}\n{inst_html}"

                self.desc_html = ui.html(html_markup)
            return self.card


class ProjectsView:
    """
    display the available projects as rows and columns
    sorted by user preference (default: stars) and allows to search/filter
    """

    def __init__(self, webserver: "InputWebserver", projects: Projects = None):
        """Initialize the ProjectsView with an optional collection of Projects.

        Args:
            webserver (InputWebserver): The webserver that serves the projects.
            projects (Projects): The collection of software projects. If None, projects are loaded from storage.
        """
        self.webserver = webserver
        if projects is None:
            projects = Projects(topic="nicegui")
            projects.load()
        self.projects = projects
        self.sorting = "stars"  # Set the default sorting method to "Stars"
        self.cards_container = None
        self.setup()

    def setup(self):
        """Set up the UI elements to render the collection of projects as a searchable and sortable card layout in NiceGUI."""
        with ui.row():
            self.last_update_label = ui.label()
            self.update_button = ui.button("Update", on_click=self.update_projects)
            self.update_last_update_label()
            self.progress_bar = NiceguiProgressbar(
                total=100, desc="updating projects", unit="projects"
            )

        with ui.row():
            # Filter input for searching projects
            self.filter_input = ui.input(
                placeholder="Search projects...", on_change=self.update_view
            )
        # Radio buttons for sorting
        sort_options = {
            "stars": "Stars",
            "name": "Name",
            "component_count": "Component Count",
            "github_owner": "Owner",
        }
        with ui.row():
            ui.label("Sort by:")
            self.sort_radio_group = (
                ui.radio(options=sort_options, on_change=self.update_view)
                .props("inline")
                .bind_value(self, "sorting")
            )

        # Project cards container
        self.cards_container = ui.grid(columns=4)
        self.views = {}
        # Initially display all projects
        self.update_view()

    def update_view(self):
        """Update the view to render the filtered and sorted projects."""
        if not self.cards_container:
            return
        search_term = self.filter_input.value.lower()
        if search_term:
            filtered_projects = [
                comp
                for comp in self.projects.projects
                if search_term in comp.name.lower()
            ]
        else:
            # Include all projects if search term is empty
            filtered_projects = self.projects.projects

        # Clear the current cards container
        self.cards_container.clear()
        if self.sorting:
            sorted_projects = self.projects.sort_projects(
                filtered_projects, self.sorting
            )
        else:
            sorted_projects = filtered_projects
        # Create a card for each project
        for project in sorted_projects:
            cv = ProjectView(project)
            self.views[project.name] = cv
            cv.setup(self.cards_container)

    async def update_projects(self, p):
        """
        update the projects
        """
        # avoid multiple background runs
        self.update_button.disable()
        ui.notify("Updating projects ... this might take a few seconds")

        await run.io_bound(self.projects.update, progress_bar=self.progress_bar)
        await run.io_bound(self.projects.save)

        # Notify the user after completion (optional)
        ui.notify("Projects updated successfully.")
        self.update_last_update_label()

    def update_last_update_label(self):
        """Update the label showing the last update time."""
        min_to_wait = 60  # Set the waiting time in minutes
        if self.projects.last_update_time:
            last_update_str = self.projects.last_update_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.last_update_label.set_text(f"Last Update: {last_update_str}")
            # Enable or disable the refresh button based on the GitHub API limits
            elapsed = datetime.now() - self.projects.last_update_time
            if elapsed < timedelta(minutes=min_to_wait):  # 60 calls per day?
                self.update_button.disable()
                # Calculate remaining minutes until the next update is possible
                remaining_time = timedelta(minutes=min_to_wait) - elapsed
                # Round up to the nearest whole minute
                minutes_until_next_update = math.ceil(
                    remaining_time.total_seconds() / 60
                )

                # Update the tooltip with the remaining minutes
                self.update_button.tooltip(
                    f"{minutes_until_next_update} min until enabled"
                )

            else:
                self.update_button.enable()
                self.update_button.tooltip("updating might take a few seconds")
        else:
            self.last_update_label.set_text("Last Update: Not yet updated")
