"""
Created on 2023-09-13

@author: wf
"""
from dataclasses import dataclass
from datetime import datetime

from fastapi.responses import Response
from nicegui import Client, app, run, ui

from ngwidgets.components_view import ComponentsView
from ngwidgets.dict_edit import DictEdit
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.lod_grid import GridConfig, ListOfDictsGrid
from ngwidgets.pdfviewer import pdfviewer
from ngwidgets.progress import NiceguiProgressbar
from ngwidgets.projects import Projects
from ngwidgets.projects_view import ProjectsView
from ngwidgets.tristate import Tristate
from ngwidgets.version import Version
from ngwidgets.webserver import WebserverConfig
from ngwidgets.widgets import HideShow, Lang


@dataclass
class Element:
    name: str
    wikidata_id: str
    atomic_number: int

    @property
    def ui_label(self) -> str:
        if self.name and self.atomic_number:
            return f"{self.name} ({self.atomic_number})"
        else:
            return DictEdit.empty


class NiceGuiWidgetsDemo(InputWebSolution):
    """
    Demonstration Solution
    """

    def __init__(self, webserver: "NiceGuiWebserver", client: Client):
        """
        Initialize the NiceGuiWidgetsDemoContext.

        Calls the constructor of the base class ClientWebContext to ensure proper initialization
        and then performs any additional setup specific to NiceGuiWidgetsDemoContext.

        Args:
            webserver (NiceGuiWebserver): The webserver instance associated with this context.
            client (Client): The client instance this context is associated with.
        """
        super().__init__(webserver, client)  # Call to the superclass constructor
        self.projects=self.webserver.projects

    async def load_pdf(self):
        self.pdf_viewer.load_pdf(self.pdf_url)

    #    slider = ui.slider(min=1, max=max_pages, value=1)  # PDF pages usually start from 1
    #    slider_label = ui.label().bind_text_from(slider, 'value')
    # def update_page(e):
    #    viewer.set_page(e.value)
    async def show_components(self, solution_id):
        def show():
            project = self.projects.get_project4_solution_id(solution_id)
            # Create a ComponentsView and display the components
            components_view = ComponentsView(self, self.projects, project)
            components_view.setup()

        await self.setup_content_div(show)

    async def show_solutions(self):
        def show():
            self.projects_view = ProjectsView(self)

        await self.setup_content_div(show)

    async def show_progress(self):
        def show():
            self.progress_bar = NiceguiProgressbar(
                total=100, desc="working", unit="step"
            )
            self.progress_bar.progress.visible = True

            def update_progress(step=1):
                # Update the progress
                self.progress_bar.update(step)
                # Reset the progress bar if it reaches the total
                if self.progress_bar.value >= self.progress_bar.total:
                    self.progress_bar.reset()

            def toggle_auto():
                if not hasattr(self, "auto_timer"):
                    self.auto_timer = ui.timer(
                        interval=0.3, callback=lambda: update_progress(), active=True
                    )
                else:
                    self.auto_timer.active = not self.auto_timer.active

            # Buttons for controlling the progress bar
            with ui.row():
                ui.button("--", on_click=lambda: update_progress(-1))
                ui.button("++", on_click=lambda: update_progress(1))
                ui.button("Auto", on_click=toggle_auto)

        await self.setup_content_div(show)

    async def show_color_schema(self):
        def show():
            self.config.color_schema.display()
            pass

        await self.setup_content_div(show)

    async def show_issue_1786(self):
        """
        https://github.com/zauberzeug/nicegui/discussions/1786
        """

        def foreground_no_slot(event):
            ui.notify(f"{event.sender.text} clicked")

        async def background_no_slot(event):
            await run.io_bound(foreground_no_slot, event)

        def foreground_with_slot(event):
            with self.button_row:
                ui.notify(f"{event.sender.text} clicked")

        async def background_with_slot(event):
            await run.io_bound(foreground_with_slot, event)

        def show():
            with ui.row() as self.button_row:
                ui.button("foreground no slot", on_click=foreground_no_slot)
                ui.button("background no slot", on_click=background_no_slot)
                ui.button("foreground with slot", on_click=foreground_with_slot)
                ui.button("background with slot", on_click=background_with_slot)

        await self.setup_content_div(show)

    async def show_langs(self):
        """
        show languages selection
        """

        def show():
            # Default language set to English
            default_lang = "en"

            # Get available languages
            languages = Lang.get_language_dict()
            with ui.card().style("width: 12%"):
                with ui.row():
                    ui.label("Lang code:")
                    # Create a label to display the chosen language with the default language
                    lang_label = ui.label(default_lang)
                with ui.row():
                    ui.label("Select:")
                    # Create a dropdown for language selection with the default language selected
                    # Bind the label text to the selection's value, so it updates automatically
                    ui.select(languages, value=default_lang).bind_value(
                        lang_label, "text"
                    )

        await self.setup_content_div(show)

    async def show_pdf_viewer(self):
        def show():
            self.pdf_viewer = pdfviewer(debug=self.args.debug).classes("w-full h-96")
            self.tool_button(tooltip="reload", icon="refresh", handler=self.load_pdf)

        await self.setup_content_div(show)

    async def show_grid(self):
        """
        show the lod grid
        """
        next_name = [
            0
        ]  # Wrap next_name in a list to make it mutable from the nested function
        self.names = [
            "Adam",
            "Brian",
            "Cindy",
            "Diana",
            "Evan",
            "Fiona",
            "George",
            "Hannah",
            "Ian",
            "Jack",
            "Kara",
            "Liam",
            "Mona",
            "Nora",
            "Oliver",
            "Pam",
            "Quincy",
            "Rachel",
            "Steve",
            "Tina",
            "Uma",
            "Victor",
            "Wendy",
            "Xavier",
            "Yvonne",
            "Zane",
            "Ashley",
            "Ben",
            "Charlotte",
            "Derek",  # Added more names for a total of 30
        ]

        def gen_name() -> str:
            """
            name generator
            """
            new_name = self.names[next_name[0]]
            next_name[0] += 1  # Increment the index
            if next_name[0] >= len(self.names):
                next_name[
                    0
                ] = 0  # Reset the index if it reaches the end of the names list
            return new_name

        lod = [
            {
                "name": "Alice",
                "age": 18,
                "parent": "David",
                "married": "2023-05-24",
                "weight": 96.48,
                "member": False,
            },
            {
                "name": "Bob",
                "age": 21,
                "parent": "Eve",
                "married": "2023-01-05",
                "weight": 87.85,
                "member": True,
            },
            {
                "name": "Carol",
                "age": 42,
                "parent": "Frank",
                "married": "2007-09-27",
                "weight": 51.81,
                "member": False,
            },
            {
                "name": "Dave",
                "age": 35,
                "parent": "Alice",
                "married": "2019-04-12",
                "weight": 72.28,
                "member": True,
            },
            {
                "name": "Ella",
                "age": 29,
                "parent": "Bob",
                "married": "2013-06-26",
                "weight": 58.09,
                "member": False,
            },
            {
                "name": "Frank",
                "age": 28,
                "parent": "Bob",
                "married": "2027-05-25",
                "weight": 81.32,
                "member": True,
            },
            {
                "name": "Grace",
                "age": 21,
                "parent": "Ella",
                "married": "2023-07-02",
                "weight": 95.36,
                "member": False,
            },
            {
                "name": "Hannah",
                "age": 49,
                "parent": "Frank",
                "married": "1994-01-14",
                "weight": 66.14,
                "member": True,
            },
            {
                "name": "Ian",
                "age": 43,
                "parent": "Bob",
                "married": "2015-05-15",
                "weight": 66.94,
                "member": False,
            },
            {
                "name": "Jill",
                "age": 22,
                "parent": "Carol",
                "married": "2019-06-05",
                "weight": 75.45,
                "member": False,
            },
            {
                "name": "Kevin",
                "age": 39,
                "parent": "Dave",
                "married": "2008-12-09",
                "weight": 95.58,
                "member": True,
            },
            {
                "name": "Liam",
                "age": 46,
                "parent": "Bob",
                "married": "2001-09-15",
                "weight": 86.69,
                "member": True,
            },
            {
                "name": "Mona",
                "age": 31,
                "parent": "Alice",
                "married": "2023-07-01",
                "weight": 88.72,
                "member": False,
            },
        ]

        def show():
            with ui.grid(columns=1) as self.grid_container:
                grid_config = GridConfig(
                    key_col="name",
                    keygen_callback=gen_name,  # Use name generator for new names
                    editable=True,
                    multiselect=True,
                    with_buttons=True,
                    debug=self.args.debug,
                )
                self.lod_grid = ListOfDictsGrid(lod=lod, config=grid_config)
                self.lod_grid.set_checkbox_selection("name")
                self.lod_grid.set_checkbox_renderer("member")

                # setup some grid event listeners
                # https://www.ag-grid.com/javascript-data-grid/grid-events/
                self.lod_grid.ag_grid.on("cellClicked", self.on_cell_clicked)
                self.lod_grid.ag_grid.on(
                    "cellDoubleClicked", self.on_cell_double_clicked
                )
                self.lod_grid.ag_grid.on("rowSelected", self.on_row_selected)
                self.lod_grid.ag_grid.on("selectionChanged", self.on_selection_changed)
                self.lod_grid.ag_grid.on("cellValueChanged", self.on_cell_value_changed)

        await self.setup_content_div(show)

    async def on_cell_clicked(self, event):
        await self.on_grid_event(event, "cellClicked")

    async def on_cell_double_clicked(self, event):
        await self.on_grid_event(event, "cellDoubleClicked")

    async def on_row_selected(self, event):
        await self.on_grid_event(event, "rowSelected")

    async def on_selection_changed(self, event):
        await self.on_grid_event(event, "selectionChanged")

    async def on_cell_value_changed(self, event):
        await self.on_grid_event(event, "cellValueChanged")

    async def on_grid_event(self, event, source):
        """
        React on ag_grid event
        See https://www.ag-grid.com/javascript-data-grid/grid-events/

        """
        args = event.args
        # Custom logic or message formatting can be based on the source
        if source in ["cellDoubleClicked", "cellClicked"]:
            msg = f"{source}: row:  {args['rowId']} column {args['colId']}"
        elif source == "cellValueChanged":
            msg = f"{source}: {args['oldValue']} → {args['newValue']} row:  {args['rowId']} column {args['colId']}"
        else:
            msg = f"grid event from {source}: {event.args}"
        # lambda event: ui.notify(f'selected row: {event.args["rowIndex"]}'))
        # lambda event: ui.notify(f'Cell value: {event.args["value"]}'))
        # self.on_property_grid_selection_change
        print(msg)

        ui.notify(msg)

    async def show_dictedit(self):
        """
        show the DictEdit examples
        """
        # Updated sample_dict with a datetime field for enrollment_date
        sample_dict = {
            "given_name": "Alice",
            "family_name": "Wonderland",
            "age": 30,
            "is_student": False,
            "enrollment_date": datetime.now(),  # Set default to current time
        }

        sample_element = Element("hydrogen", "Q556", 1)

        def show():
            customization = {
                "_form_": {"title": "Student", "icon": "person"},
                "given_name": {"label": "Given Name", "size": 50},
                "family_name": {"label": "Family Name", "size": 50},
                "enrollment_date": {
                    "label": "Enrollment Date",
                    "widget": "datetime",
                },  # Customization for datetime
            }
            with ui.grid(columns=3):
                self.dict_edit1 = DictEdit(sample_dict, customization=customization)
                self.dict_edit1.expansion.open()
                self.dict_edit2 = DictEdit(sample_element)
                self.dict_edit2.expansion.open()

        await self.setup_content_div(show)

    async def show_hide_show_demo(self):
        """
        Demonstrate the HideShow project.
        """

        def show():
            hide_show_section = HideShow(("Hide", "Show More"))
            with hide_show_section.content_div:
                ui.label(
                    "This is the hidden content. Click the button to hide/show this text."
                )

        await self.setup_content_div(show)

    async def show_tristate_demo(self):
        """
        Demonstrate the Tristate project.
        """

        def on_change():
            ui.notify(
                f"New State: {self.tristate.current_icon_index} ({self.tristate.utf8_icon})"
            )

        def update_icon_set_label(icon_set_name: str):
            # Update the label to show the icons of the new set
            self.icon_set_label.set_text(
                f'Icons in Set {icon_set_name}: {" ".join(Tristate.ICON_SETS[icon_set_name])}'
            )

        def on_icon_set_change(event):
            """
            react on change icon set
            """
            new_icon_set = event.value
            self.tristate.icon_set = Tristate.ICON_SETS[new_icon_set]
            self.tristate.current_icon_index = 0  # Reset to first icon of new set
            self.tristate.update_props()
            update_icon_set_label(new_icon_set)

        def show():
            ui.label("Tristate Demo:")
            # Initialize Tristate component with the default icon set
            default_icon_set_name = "marks"

            # Label to display the icons in the current set
            self.icon_set_label = ui.label()
            update_icon_set_label(default_icon_set_name)

            # Dropdown for selecting the icon set
            icon_set_names = list(Tristate.ICON_SETS.keys())
            self.add_select(
                "Choose Icon Set", icon_set_names, on_change=on_icon_set_change
            )

            ui.label("Click to try:")
            self.tristate = Tristate(
                icon_set_name=default_icon_set_name, on_change=on_change
            )

        await self.setup_content_div(show)

    async def home(self):
        """
        provide the main content page
        """

        def setup_home():
            # Define the links and labels in a dictionary
            links = {
                "nicegui solutions bazaar": "/solutions",
                "ColorSchema": "/color_schema",
                "DictEdit": "/dictedit",
                "HideShow Demo": "/hideshow",
                "Lang": "/langs",
                "ListOfDictsGrid": "/grid",
                "Tristate Demo": "/tristate",
                "pdfviewer": "/pdfviewer",
                "Progressbar": "/progress",
            }

            # Generate the HTML using the dictionary
            html_content = "<ul>"
            for label, link in links.items():
                html_content += f'<li><a href="{link}">{label}</a></li>'
            html_content += "</ul>"

            # html_content now contains the HTML code to render the list of links
            ui.html(html_content)

        await self.setup_content_div(setup_home)


class NiceGuiWidgetsDemoWebserver(InputWebserver):
    """
    webserver to demonstrate ngwidgets capabilities
    """

    @classmethod
    def get_config(cls) -> WebserverConfig:
        copy_right = "(c)2023-2024 Wolfgang Fahl"
        config = WebserverConfig(
            short_name="ngdemo",
            timeout=6.0,
            copy_right=copy_right,
            version=Version(),
            default_port=9856,
        )
        server_config = WebserverConfig.get(config)
        server_config.solution_class = NiceGuiWidgetsDemo
        return server_config

    def __init__(self):
        """
        Constructor
        """
        InputWebserver.__init__(self, config=NiceGuiWidgetsDemoWebserver.get_config())
        # pdf_url = "https://www.africau.edu/images/default/sample.pdf"
        self.pdf_url = "https://raw.githubusercontent.com/mozilla/pdf.js/ba2edeae/web/compressed.tracemonkey-pldi-09.pdf"
        self.projects = Projects(topic="nicegui")
        self.projects.load()
        pass

        @app.get("/solutions.yaml")
        def get_solutions_yaml():
            yaml_data = self.projects.to_yaml()
            return Response(content=yaml_data, media_type="text/yaml")

        @ui.page("/solutions")
        async def show_solutions(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_solutions)

        @ui.page("/components/{solution_id}")
        async def show_components(solution_id: str, client: Client):
            return await self.page(
                client, NiceGuiWidgetsDemo.show_components, solution_id
            )

        @ui.page("/progress")
        async def show_progress(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_progress)

        @ui.page("/langs")
        async def show_langs(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_langs)

        @ui.page("/color_schema")
        async def show_color_schema(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_color_schema)

        @ui.page("/dictedit")
        async def show_dictedit(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_dictedit)

        @ui.page("/grid")
        async def show_grid(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_grid)

        @ui.page("/hideshow")
        async def show_hide_show(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_hide_show_demo)

        @ui.page("/tristate")
        async def show_tristate_demo(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_tristate_demo)

        @ui.page("/pdfviewer")
        async def show_pdf_viewer(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_pdf_viewer)

        @ui.page("/issue1786")
        async def show_issue_1786(client: Client):
            return await self.page(client, NiceGuiWidgetsDemo.show_issue_1786)
