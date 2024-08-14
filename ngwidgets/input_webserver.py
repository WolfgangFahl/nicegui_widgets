"""
Created on 2023-09-12

@author: wf
"""

import os

from nicegui import Client, ui

from ngwidgets.local_filepicker import LocalFilePicker
from ngwidgets.log_view import LogView
from ngwidgets.webserver import NiceGuiWebserver, WebserverConfig, WebSolution
from ngwidgets.widgets import About


class InputWebserver(NiceGuiWebserver):
    """
    a webserver around a single input file of given filetypes
    """

    def __init__(self, config: WebserverConfig = None):
        """
        constructor
        """
        NiceGuiWebserver.__init__(self, config=config)

        @ui.page("/")
        async def home_page(client: Client):
            return await self.page(client, InputWebSolution.home)

        @ui.page("/settings")
        async def settings_page(client: Client):
            return await self.page(client, InputWebSolution.settings)

        @ui.page("/about")
        async def about_page(client: Client):
            return await self.page(client, InputWebSolution.about)

    def configure_run(self):
        """
        override the run configuration
        """
        NiceGuiWebserver.configure_run(self)
        args = self.args
        self.is_local = args.local
        if hasattr(args, "root_path"):
            self.root_path = os.path.abspath(args.root_path)
        else:
            self.root_path = None


class InputWebSolution(WebSolution):
    """
    A WebSolution that is focused on handling a single input.

    Attributes:
        is_local (bool): Indicates if the input source is local or remote.
        input (str): The input data or path to be processed.
    """

    def __init__(self, webserver: NiceGuiWebserver, client: Client):
        """
        Initializes the InputWebSolution instance with the webserver and client.

        Args:
            webserver (NiceGuiWebserver): The webserver instance this solution is part of.
            client (Client): The client interacting with this solution.
        """
        super().__init__(webserver, client)
        self.debug = webserver.debug
        self.root_path = None
        self.is_local = False
        self.input = ""
        self.render_on_load = False

    def input_changed(self, cargs):
        """
        react on changed input
        """
        self.input = cargs.value
        pass

    def read_input(self, input_str: str):
        """Reads the given input and handles any exceptions.

        Args:
            input_str (str): The input string representing a URL or local file.
        """
        try:
            ui.notify(f"reading {input_str}")
            if self.log_view:
                self.log_view.clear()
            self.error_msg = None
        except BaseException as e:
            self.handle_exception(e, self.do_trace)

    async def read_and_optionally_render(self, input_str, with_render: bool = False):
        """
        Reads the given input and optionally renders the given input

        Args:
            input_str (str): The input string representing a URL or local file.
            with_render(bool): if True also render
        """
        self.input_input.set_value(input_str)
        self.read_input(input_str)
        if with_render or self.args.render_on_load:
            await self.render(None)

    async def reload_file(self):
        """
        reload the input file
        """
        input_str = self.input
        if not input_str:
            return
        if os.path.exists(input_str):
            input_str = os.path.abspath(input_str)
        allowed = self.is_local
        if not self.is_local:
            for allowed_url in self.allowed_urls:
                if input_str.startswith(allowed_url):
                    allowed = True
        if not allowed:
            ui.notify("only white listed URLs and Path inputs are allowed")
        else:
            await self.read_and_optionally_render(self.input, with_render=True)

    async def open_file(self) -> None:
        """
        Opens a Local filer picker dialog and reads the
        selected input file."""
        if self.is_local:
            pick_list = await LocalFilePicker("~", multiple=False)
            if pick_list and len(pick_list) > 0:
                input_file = pick_list[0]
                with_render = self.render_on_load
                await self.read_and_optionally_render(
                    input_file, with_render=with_render
                )

    pass

    async def home(self):
        """
        provide the main content page

        """
        await self.setup_content_div(setup_content=None)

    async def about(self):
        """
        show about
        """
        await self.setup_content_div(self.setup_about)

    def setup_about(self):
        """
        display an About
        """
        self.about_div = About(self.config.version)

    async def setup_footer(
        self,
        with_log: bool = True,
        handle_logging: bool = True,
        max_lines: int = 20,
        log_classes: str = "w-full h-40",
    ):
        """
        setup a footer with an optional log view
        """
        if with_log:
            self.log_view = LogView(max_lines=max_lines, classes=log_classes)
            if handle_logging:
                self.log_view.addAsHandler(self.logger)
        else:
            self.log_view = None
        await super().setup_footer()
        if self.args.input:
            # await client.connected()
            with_render = self.render_on_load
            await self.read_and_optionally_render(
                self.args.input, with_render=with_render
            )

    async def settings(self):
        """
        Generates the settings page
        """

        def show():
            with ui.row():
                ui.checkbox("debug", value=self.webserver.debug).bind_value(
                    self.webserver, "debug"
                )
                ui.checkbox(
                    "debug with trace", value=self.webserver.do_trace
                ).bind_value(self.webserver, "do_trace")
                ui.checkbox("render on load", value=self.render_on_load).bind_value(
                    self, "render_on_load"
                )
            self.configure_settings()

        await self.setup_content_div(show)

    def configure_settings(self):
        """
        Configures settings specific to this web solution.
        This method is intended to be overridden by subclasses to provide custom settings behavior.
        The base method does nothing and can be extended in subclasses.
        """

    def configure_menu(self):
        """
        Configures the menu items specific to this web solution.
        This method is intended to be overridden by subclasses to provide custom menu behavior.
        The base method does nothing and can be extended in subclasses.
        """
        pass

    def prepare_ui(self):
        """
        handle the command line arguments
        """
        WebSolution.prepare_ui(self)
        args = self.webserver.args
        self.input = args.input
        self.root_path = self.webserver.root_path
        self.is_local = args.local
        self.render_on_load = args.render_on_load
