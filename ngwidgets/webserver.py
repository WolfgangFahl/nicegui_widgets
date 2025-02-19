"""
Created on 2023-09-10

@author: wf
"""

import asyncio
import logging
import os
import sys
import traceback
import urllib.request
import uuid
from dataclasses import field
from typing import Any, Callable, Dict, List, Optional, Union

from nicegui import Client, core, ui

from ngwidgets.color_schema import ColorSchema
from ngwidgets.version import Version
from ngwidgets.yamlable import lod_storable


@lod_storable
class WebserverConfig:
    """
    configuration of a webserver
    """

    # the short name to be used e.g. for determining the default storage_path
    short_name: str

    # set your copyright string here
    copy_right: Optional[str] = ""
    default_port: int = 9860
    version: Optional[Version] = None
    color_schema: ColorSchema = field(default_factory=ColorSchema.indigo)
    fastapi_docs: Optional[bool] = True
    detailed_menu: bool = True
    timeout: Optional[float] = None
    storage_secret: Optional[str] = None
    storage_path: Optional[str] = None
    config_path: Optional[str] = None

    def __post_init__(self):
        """
        make sure the necessary fields exist
        """
        self.config_path = self.base_path
        self.storage_path = self.storage_path or os.path.join(self.base_path, "storage")
        self.storage_secret = self.storage_secret or str(uuid.uuid4())
        self.timeout = self.timeout if self.timeout is not None else 3.0

    @property
    def yaml_path(self) -> str:
        return os.path.join(self.config_path, f"{self.short_name}_config.yaml")

    @property
    def base_path(self) -> str:
        base_path = self.config_path or os.path.join(
            os.path.expanduser("~"), ".solutions", self.short_name
        )
        return base_path

    @classmethod
    def get(cls, config: "WebserverConfig") -> "WebserverConfig":
        """
        Retrieves or initializes a WebserverConfig instance based on the provided 'config' parameter.
        This method ensures that essential properties like 'storage_secret', 'config_path', and 'storage_path'
        are set in the 'config' object. If a configuration file already exists at the 'yaml_path', it's loaded,
        and its values are used to update the provided 'config'. However, certain key properties like 'version',
        'short_name', and 'default_port' can still be overridden by the provided 'config' if they are set.

        If the configuration file does not exist, this method will create the necessary directories and save
        the provided 'config' as the initial configuration to the 'yaml_path', which is derived from 'config_path'
        and 'short_name' and typically located under the user's home directory in the '.solutions' folder.

        Args:
            config (WebserverConfig): The configuration object with preferred or default settings.

        Returns:
            WebserverConfig: The configuration loaded from the YAML file, or the provided 'config'
                             if the YAML file does not exist.
        """
        if os.path.exists(config.yaml_path):
            # Load the existing config
            server_config = cls.load_from_yaml_file(config.yaml_path)
            if config.version:
                server_config.version = config.version
            if config.copy_right:
                server_config.copy_right = config.copy_right
            if config.default_port != 9680:
                server_config.default_port = config.default_port
            if config.short_name != server_config.short_name:
                _msg = f"config short_name mismatch {config.short_name}!={server_config.short_name}"
                pass
            server_config.short_name = config.short_name
        else:
            # Create the directories to make sure they  exist
            os.makedirs(config.config_path, exist_ok=True)
            os.makedirs(config.storage_path, exist_ok=True)

            # Use the provided default_config as the initial configuration
            server_config = config
            server_config.save_to_yaml_file(config.yaml_path)

        return server_config


class NiceGuiWebserver(object):
    """
    a basic NiceGuiWebserver
    """

    def __init__(self, config: WebserverConfig = None):
        """
        Constructor
        """
        self.debug = False
        self.logger = logging.getLogger()
        self.do_trace = True
        if config is None:
            config = WebserverConfig()
        self.config = config
        self.app = core.app

    async def page(self, client: Client, wanted_action: Callable, *args, **kwargs):
        """
        Handle a page request for a specific client. This method ensures that a specific type of WebSolution
        (or its subclass) is created for each client and used throughout the client's interaction.

        Args:
            client (Client): The client making the request.
            wanted_action(Callable): The function of the solution to perform. Might be overriden so we check the solution_instance
            *args, **kwargs: Additional arguments to pass to the action.

        Returns:
            The result of the action performed.
        """
        solution_class = self.config.solution_class
        if not solution_class:
            raise TypeError("no solution_class configured")

        action_result=await self.execute_action(client,
            solution_class,
            wanted_action,
            *args,
            **kwargs)
        return action_result

    async def execute_action(self, client: Client, solution_class, wanted_action: Callable, *args, **kwargs):
        """
        Execute the specified action on the solution instance.

        Args:
            client (Client): The client making the request.
            solution_class: The solution class to create an instance for to execute the action on.
            wanted_action(Callable): The function to perform.
            args, *kwargs: Additional arguments to pass to the action.

        Returns:
            The result of the action performed.
        """
        solution_instance = solution_class(self, client)

        # Check if the solution_instance is an instance of solution_class or its subclass
        if not isinstance(solution_instance, solution_class):
            raise TypeError(
                f"solution_instance must be an instance of {solution_class.__name__} or its subclass, not {type(solution_instance).__name__}."
            )

        # Check if the action_callable is a method of solution_instance
        if not callable(wanted_action) or not hasattr(
            solution_instance, wanted_action.__name__
        ):
            raise AttributeError(
                f"The provided callable {wanted_action.__qualname__} is not a method of {solution_instance.__class__.__name__}."
            )
        # replace action by the one from the instance for inheritance handling
        action = getattr(solution_instance, wanted_action.__name__)

        await solution_instance.prepare()

        # call any preparation code needed before the actual nicegui.ui calls
        # are done
        solution_instance.prepare_ui()

        action_result= await action(*args, **kwargs)
        return action_result

    @classmethod
    def optionalDebug(self, args):
        """
        start the remote debugger if the arguments specify so

        Args:
            args(): The command line arguments
        """
        if args.debugServer:
            import pydevd
            from pydevd_file_utils import setup_client_server_paths

            print(
                f"remotePath: {args.debugRemotePath} localPath:{args.debugLocalPath}",
                flush=True,
            )
            if args.debugRemotePath and args.debugLocalPath:
                MY_PATHS_FROM_ECLIPSE_TO_PYTHON = [
                    (args.debugRemotePath, args.debugLocalPath),
                ]
                setup_client_server_paths(MY_PATHS_FROM_ECLIPSE_TO_PYTHON)
                # os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]='[["%s", "%s"]]' % (remotePath,localPath)
                # print("trying to debug with PATHS_FROM_ECLIPSE_TO_PYTHON=%s" % os.environ["PATHS_FROM_ECLIPSE_TO_PYTHON"]);

            pydevd.settrace(
                args.debugServer,
                port=args.debugPort,
                stdoutToServer=True,
                stderrToServer=True,
            )
            print(f"command line args are: {str(sys.argv)}")

    def run(self, args):
        """
        Runs the UI of the web server.

        Args:
            args (list): The command line arguments.
        """
        self.args = args
        self.debug = args.debug
        self.optionalDebug(args)
        # allow app specific configuration steps
        self.configure_run()
        ui.run(
            title=self.config.version.name,
            host=args.host,
            port=args.port,
            show=args.client,
            fastapi_docs=self.config.fastapi_docs,
            reload=False,
            storage_secret=self.config.storage_secret,
        )

    def configure_run(self):
        """
        Configures specific before run steps of a web server.
        This method is intended to be overridden
        by subclasses to provide custom run behavior.
        The base method does nothing and can be extended in subclasses.
        """
        pass

    def stop(self):
        """
        stop the server
        """


class WebSolution:
    """
    the user/client specific web context of a solution
    """

    def __init__(self, webserver: NiceGuiWebserver, client: Client):
        """
        construct a client specific WebSolution
        """
        self.webserver = webserver
        self.logger = webserver.logger
        self.config = self.webserver.config
        self.args = self.webserver.args
        self.client = client
        self.log_view = None
        self.container = None

    def notify(self, msg: str):
        """
        call ui.notify with a context
        """
        with self.content_div:
            ui.notify(msg)

    async def prepare(self):
        """
        make sure this solution context is ready for use
        """
        timeout = self.config.timeout
        if timeout is not None:
            await self.client.connected(timeout=timeout)

    def prepare_ui(self):
        """
        call any code necessary before the first nicegui.ui call is
        done e.g. handling command line arguments

        The base method does nothing and serves as a placeholder for subclasses to define their own UI preparation logic.
        """
        pass

    def link_button(self, name: str, target: str, icon_name: str, new_tab: bool = True):
        """
        Creates a button with a specified icon that opens a target URL upon being clicked.

        Args:
            name (str): The name to be displayed on the button.
            target (str): The target URL that should be opened when the button is clicked.
            icon_name (str): The name of the icon to be displayed on the button.
            new_tab(bool): if True open link in new tab

        Returns:
            The button object.


        see https://fonts.google.com/icons?icon.set=Material+Icons for potential icon names
        """
        with ui.link(text=" ", target=target, new_tab=new_tab) as link_btn:
            link_btn.button = ui.button(name, icon=icon_name)
        return link_btn

    def tool_button(
        self, tooltip: str, icon: str, handler: callable = None, toggle_icon: str = None
    ) -> ui.button:
        """
        Creates a button with icon that triggers a specified function upon being clicked.

        Args:
            tooltip (str): The tooltip to be displayed.
            icon (str): The name of the icon to be displayed on the button.
            handler (function): The function to be called when the button is clicked.
            toggle_icon (str): The name of an alternative icon to be displayed when the button is clicked.

        Returns:
            ui.button: The icon button object.

        valid icons may be found at:
            https://fonts.google.com/icons
        """
        icon_button = (
            ui.button("", icon=icon, color="primary")
            .tooltip(tooltip)
            .on("click", handler=handler)
        )
        icon_button.toggle_icon = toggle_icon
        return icon_button

    def toggle_icon(self, button: ui.button):
        """
        toggle the icon of the given button

        Args:
            ui.button: the button that needs the icon to be toggled
        """
        if hasattr(button, "toggle_icon"):
            # exchange icon with toggle icon
            toggle_icon = button._props["icon"]
            icon = button.toggle_icon
            button._props["icon"] = icon
            button.toggle_icon = toggle_icon
        button.update()

    def round_label(
        self, title: str, background_color: str = "#e6e6e6", **kwargs
    ) -> ui.label:
        """
        Creates a label with rounded corners and optional background color.

        Args:
            title (str): The text to be displayed in the label.
            background_color (str): Hex color code for the label's background.
                                    Defaults to a light grey color ("#e6e6e6").
            **kwargs: Additional keyword arguments passed to the select widget creation.

        Returns:
            ui.label: A NiceGUI label element with rounded corners and the specified background color.
        """
        background_style = (
            f"background-color: {background_color};" if background_color else ""
        )
        round_label = (
            ui.label(title, **kwargs)
            .classes("rounded p-2")
            .style(f"margin-right: 10px; {background_style}")
        )
        return round_label

    def add_select(
        self,
        title: str,
        selection: Union[List[Any], Dict[str, Any]],
        background_color: str = "#e6e6e6",
        **kwargs,
    ) -> Any:
        """
        Add a select widget with a given title, selection options, and optional styling.

        Args:
            title (str): The title or label for the select widget.
            selection (Union[List[Any], Dict[str, Any]]): The options available for selection.
                - If a List, each element represents an option.
                - If a Dict, keys are option labels and values are the corresponding values.
            background_color (str, optional): Hex color code for the background of the label. Defaults to "#e6e6e6".
            **kwargs: Additional keyword arguments passed to the select widget creation.

        Returns:
            Any: The created nicegui ui.select widget.
        """
        with ui.element("div").style("display: flex; align-items: center;"):
            self.round_label(title, background_color)
            s = ui.select(selection, **kwargs)
            # https://github.com/WolfgangFahl/nicegui_widgets/issues/64
            # s.validation={}
            return s

    def do_read_input(self, input_str: str) -> str:
        """Reads the given input.

        Args:
            input_str (str): The input string representing a URL or local path.

        Returns:
            str: the input content as a string
        """
        if input_str.startswith("http://") or input_str.startswith("https://"):
            with urllib.request.urlopen(input_str) as response:
                text = response.read().decode("utf-8")
                return text
        else:
            if os.path.exists(input_str):
                with open(input_str, "r") as file:
                    return file.read()
            else:
                raise Exception(f"File does not exist: {input_str}")

    async def toogle_hamburger(self):
        """
        toggle the hamburger menu
        """
        if not self.header:
            return

        self.header.toggle()
        self.footer.toggle()
        self.hamburger_button1.visible = not self.hamburger_button1.visible

    def setup_menu(self, detailed: bool = None):
        """
        set up the default menu home/settings and about

        Args:
            detailed(bool): if True add github,chat and help links
        """
        self.header = None
        version = self.config.version
        if detailed is None:
            detailed = self.config.detailed_menu
        self.config.color_schema.apply()
        # parent element for hamburger menu
        with ui.element("div").classes(
            "top-0 left-0 z-50 bg-transparent"
        ) as self.hamburger_container:
            self.hamburger_button1 = ui.button(
                icon="menu", on_click=self.toogle_hamburger
            )
            self.hamburger_button1.visible = False
        with ui.header() as self.header:
            self.hamburger_button = ui.button(
                icon="menu", on_click=self.toogle_hamburger
            )
            self.link_button("home", "/", "home", new_tab=False)
            self.link_button("settings", "/settings", "settings", new_tab=False)
            self.configure_menu()
            if detailed:
                self.link_button("github", version.cm_url, "bug_report")
                self.link_button("chat", version.chat_url, "chat")
                self.link_button("help", version.doc_url, "help")
                self.link_button("about", "/about", "info", new_tab=False)

    async def setup_footer(self):
        """
        setup the footer
        """
        with ui.footer() as self.footer:
            ui.label(self.config.copy_right)
            ui.link("Powered by nicegui", "https://nicegui.io/").style("color: #fff")

    async def setup_content_div(
        self,
        setup_content: Optional[Callable] = None,
        with_exception_handling: bool = True,
        **kwargs,
    ):
        """
        Sets up the content frame div of the web server's user interface.

        Args:
            setup_content (Optional[Callable]): A callable for setting up the main content.
                                                 It can be a regular function or a coroutine.
            with_exception_handling(bool): if True handle exceptions

        Note:
            This method is asynchronous and should be awaited when called.
        """
        # Setting up the menu
        self.setup_menu()

        with ui.element("div").classes("w-full h-full") as self.content_div:
            self.container = self.content_div
            # Execute setup_content if provided
            if setup_content:
                try:
                    if asyncio.iscoroutinefunction(setup_content):
                        await setup_content(**kwargs)
                    else:
                        setup_content(**kwargs)
                except Exception as ex:
                    if with_exception_handling:
                        self.handle_exception(ex)
                    else:
                        raise ex

        await self.setup_footer()

    def handle_exception(self, e: BaseException, trace: Optional[bool] = None):
        """Handles an exception by creating an error message.

        Args:
            e (BaseException): The exception to handle.
            trace (bool, optional): Whether to include the traceback in the error message. Default is False.
        """
        if trace is None and self.webserver:
            trace = self.webserver.do_trace
        if trace:
            self.error_msg = str(e) + "\n" + traceback.format_exc()
        else:
            self.error_msg = str(e)
        if self.log_view:
            self.log_view.push(self.error_msg)
        print(self.error_msg, file=sys.stderr)
