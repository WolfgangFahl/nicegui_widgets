"""
Created on 2023-09-12

@author: wf
"""
import os
import logging
from ngwidgets.webserver import NiceGuiWebserver, WebserverConfig
from ngwidgets.local_filepicker import LocalFilePicker
from ngwidgets.widgets import About
from nicegui import ui, Client
from ngwidgets.log_view import LogElementHandler


class InputWebserver(NiceGuiWebserver):
    """
    a webserver around a single input file of given filetypes
    """

    def __init__(self, config: WebserverConfig = None):
        """
        constructor
        """
        NiceGuiWebserver.__init__(self, config=config)
        self.is_local = False
        self.input = ""
        self.logger = logging.getLogger()

        @ui.page("/")
        async def home(client: Client):
            return await self.home(client)

        @ui.page("/settings")
        async def settings():
            return await self.settings()

        @ui.page("/about")
        async def about():
            return await self.about()

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
        if with_render:
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

    async def home(self, _client: Client):
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
            self.log_view = ui.log(max_lines=max_lines).classes(log_classes)
            if handle_logging:
                self.log_view_handler = LogElementHandler(self.log_view)
                self.logger.addHandler(self.log_view_handler)
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
        self.setup_menu()
        ui.checkbox("debug", value=self.debug).bind_value(self, "debug")
        ui.checkbox("debug with trace", value=True).bind_value(self, "do_trace")
        ui.checkbox("render on load", value=self.render_on_load).bind_value(
            self, "render_on_load"
        )
        self.configure_settings()
        await self.setup_footer()

    def configure_settings(self):
        """
        overrideable settings configuration
        """
        pass

    def configure_menu(self):
        """
        overrideable menu configuration
        """

    def configure_run(self):
        """
        overrideable configuration
        """
        pass

    def run(self, args):
        """
        Runs the UI of the web server.

        Args:
            args (list): The command line arguments.
        """
        self.input = args.input
        self.is_local = args.local
        if hasattr(args, "root_path"):
            self.root_path = os.path.abspath(args.root_path)
        else:
            self.root_path = None
        self.render_on_load = args.render_on_load
        super().run(args)
