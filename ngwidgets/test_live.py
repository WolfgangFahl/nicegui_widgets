"""
LiveTest
Minimal live environment using Webserver/WebSolution/WebCmd
of nicegui_widgets environment
WF 2025-05-18
WF 2026-10-09 - one live server per process, nicegui 3 lifecycle

"""

import atexit
import threading
import time
from argparse import Namespace
from typing import Any, Callable, ClassVar, Dict, Optional

import requests
from nicegui import Client, app, core, ui

from ngwidgets.cmd import WebserverCmd
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
from ngwidgets.test_base_webserver import BaseWebserverTest
from ngwidgets.version import Version
from ngwidgets.webserver import WebserverConfig


class LiveSolution(InputWebSolution):
    """
    Minimal InputWebSolution subclass with a JSON test route
    """

    def __init__(self, webserver: "LiveWebserver", client: Client):
        """
        Initialize the LiveSolution.

        Args:
            webserver (LiveWebserver): The webserver instance associated with this context.
            client (Client): The client instance this context is associated with.
        """
        super().__init__(webserver, client)

    async def livetest(self):
        """
        Test endpoint that returns HTML response
        """

        def setup_test():
            ui.label("Test endpoint is working!")

        await self.setup_content_div(setup_test)

    async def home(self):
        """
        Provide the main content page
        """

        def setup_home():
            ui.label("Welcome to the Live Nicegui Widgets test environment!")

        await self.setup_content_div(setup_home)


class LiveWebserver(InputWebserver):
    """
    Minimal InputWebserver setup with configurable test handler

    the handler is shared by all instances of the process since the first
    registered /live-testhandler route answers for the whole process
    """

    test_handler: ClassVar[Callable[[], Dict[str, Any]]] = lambda: {"status": "ok"}

    @classmethod
    def get_config(cls) -> WebserverConfig:
        config = WebserverConfig(
            short_name="livetest",
            default_port=8668,
            version=Version(),
        )
        config.solution_class = LiveSolution
        return config

    def __init__(self):
        """
        constructor for Webserver
        """
        super().__init__(config=self.get_config())

        # Register the UI route for connectivity testing
        @ui.page("/live-htmltest")
        async def test_route(client: Client):
            return await self.page(client, LiveSolution.livetest)

        # Add a direct FastAPI endpoint for JSON responses
        @app.get("/live-testhandler")
        async def livetest():
            # Get the current handler from the webserver
            handler = self.get_test_handler()
            # Call the handler to get the data
            json_data = handler()
            # Return the data directly which FastAPI will serialize to JSON
            return json_data

    def set_test_handler(self, handler: Callable[[], Dict[str, Any]]):
        """
        Set the handler function for the test endpoint

        Args:
            handler: Function that returns a dictionary to be converted to JSON
        """
        LiveWebserver.test_handler = handler

    def get_test_handler(self) -> Callable[[], Dict[str, Any]]:
        """
        Get the current test handler

        Returns:
            The current handler function
        """
        handler = LiveWebserver.test_handler
        return handler


class LiveCmd(WebserverCmd):
    """
    Minimal CLI cmd class with only --timeout
    """

    def __init__(self, config=None, webserver_cls=None):
        if config is None:
            # Get the config from the webserver class
            config = LiveWebserver.get_config()
        if webserver_cls is None:
            webserver_cls = LiveWebserver
        # Initialize with the config and webserver class
        super().__init__(config=config, webserver_cls=webserver_cls)

    def getArgParser(self, description=None, version_msg=None):
        # Get the parser from the parent class
        parser = super().getArgParser(description, version_msg)

        # Add our timeout parameter
        parser.add_argument(
            "--timeout", type=float, default=5.0, help="Shutdown timeout"
        )
        return parser


class LiveServerRunner:
    """
    Runs the one NiceGUI server of this test process in a thread.

    nicegui allows a single ui.run per process: a second run fails with
    "Cannot add middleware after an application has started". Therefore the
    first LiveWebTest subclass starts the server and every later subclass
    reuses it - routes registered by their webservers are added to the
    running app. The server is shut down when the process exits.
    """

    instance: ClassVar[Optional["LiveServerRunner"]] = None

    def __init__(self, ws: Any, args: Namespace, timeout: float = 5.0):
        """
        constructor

        Args:
            ws: the webserver whose run method starts the server
            args: the parsed command line arguments for the run
            timeout: seconds to wait for the server thread on stop
        """
        self.ws = ws
        self.args = args
        self.timeout = timeout
        self.base_url = f"http://127.0.0.1:{args.port}"
        self.thread = threading.Thread(target=self.ws.run, args=(args,))
        self.thread.daemon = True

    @classmethod
    def get_instance(
        cls, ws: Any, args: Namespace, timeout: float = 5.0
    ) -> "LiveServerRunner":
        """
        get the running server of this process - started on first call

        Args:
            ws: the webserver to run if no server is running yet
            args: the parsed command line arguments for the run
            timeout: seconds to wait for the server thread on stop

        Returns:
            LiveServerRunner: the one runner of this process
        """
        if cls.instance is None:
            runner = cls(ws, args, timeout=timeout)
            runner.start()
            atexit.register(runner.stop)
            cls.instance = runner
        return cls.instance

    def leave_script_mode(self):
        """
        nicegui 3 refuses ui.run with pages once UI was created in the
        global scope - which widget tests run earlier in the same process do.
        The script client they filled is deleted and the core state reset
        before the server starts; the routes registered on app stay.
        """
        if core.script_client is not None:
            core.script_client.delete()
        core.reset()

    def start(self):
        """
        start the server thread
        """
        self.leave_script_mode()
        self.thread.start()

    def stop(self):
        """
        shut the server down and wait for the thread
        """
        if self.thread.is_alive():
            app.shutdown()
            self.thread.join(timeout=self.timeout)


class LiveWebTest(BaseWebserverTest):
    """
    Real IO LiveTest against LiveWebserver using HTTP requests
    """

    def setUp(self, debug=False, profile=True):
        """Set up the test environment"""
        super().setUp(debug=debug, profile=profile)
        self.base_url = self.__class__.base_url  # Get base_url from class variable

    @classmethod
    def setUpClass(cls):
        """Set up resources shared by all test methods"""
        # Create the webserver
        cls.ws = LiveWebserver()

        # Create the cmd instance and get properly configured args
        cls.cmd = LiveCmd()
        cls.start_runner()

    @classmethod
    def start_runner(cls):
        """
        start the live server of this process or reuse the running one
        """
        args = cls.cmd.parse_args(["--serve"])
        # a webserver joining the running server is never run and
        # therefore gets its args here, solutions read them on page requests
        cls.ws.args = args
        cls.runner = LiveServerRunner.get_instance(cls.ws, args, timeout=args.timeout)
        cls.base_url = cls.runner.base_url
        cls.max_secs_to_wait = 5
        cls.wait_until_ready(cls.max_secs_to_wait)

    @classmethod
    def tearDownClass(cls):
        """the server is shared by all test classes and stops with the process"""
        pass

    @classmethod
    def wait_until_ready(cls, secs: int):
        """Wait until the server is ready to accept requests"""
        url = f"{cls.base_url}/live-htmltest"
        for _ in range(secs * 10):
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    return
            except Exception:
                pass
            time.sleep(0.1)  # 100 millisecs per loop
        raise TimeoutError("Live server did not start")

    def get_response(self, path: str, expected_status_code: int = 200) -> Any:
        """
        Get a response for the given path using HTTP requests

        Args:
            path: The path to request
            expected_status_code: The expected HTTP status code

        Returns:
            The requests.Response object
        """
        url = f"{self.base_url}{path}"
        response = requests.get(url)
        self.assertEqual(response.status_code, expected_status_code)
        return response

    def get_html_for_post(self, path: str, data) -> str:
        """
        Get HTML content for the given path by posting the given data

        Args:
            path: The path to request
            data: The data to post (will be serialized to JSON)

        Returns:
            The HTML content as a string
        """
        url = f"{self.base_url}{path}"
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content is not None)
        html = response.content.decode()
        if self.debug:
            print(html)
        return html

    def set_test_handler(self, handler: Callable[[], Dict[str, Any]]):
        """
        Set the handler function for the test endpoint

        Args:
            handler: Function that returns a dictionary to be converted to JSON
        """
        self.ws.set_test_handler(handler)

    def get_test_url(self):
        """
        Get the URL for the JSON API endpoint

        Returns:
            The URL for the test API
        """
        return f"{self.base_url}/live-testhandler"
