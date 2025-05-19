"""
LiveTest
Minimal live environment using Webserver/WebSolution/WebCmd
of nicegui_widgets environment
WF 2025-05-18

"""

import threading
import time
from typing import Any, Callable, Dict, List

import requests
from fastapi.responses import JSONResponse
from nicegui import Client, app, ui

from ngwidgets.basetest import Basetest
from ngwidgets.cmd import WebserverCmd
from ngwidgets.input_webserver import InputWebserver, InputWebSolution
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
    """

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

        # Default test handler returns a simple status message
        self._test_handler = lambda: {"status": "ok"}

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
        self._test_handler = handler

    def get_test_handler(self) -> Callable[[], Dict[str, Any]]:
        """
        Get the current test handler

        Returns:
            The current handler function
        """
        return self._test_handler

class LiveCmd(WebserverCmd):
    """
    Minimal CLI cmd class with only --timeout
    """

    def __init__(self):
        # Get the config from the webserver class
        config = LiveWebserver.get_config()
        # Initialize with the config and webserver class
        super().__init__(config=config, webserver_cls=LiveWebserver)

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
    Runs a NiceGUI Webserver in a thread
    """

    def __init__(self, ws_cmd:WebserverCmd, args:List[str], timeout=5.0):
        self.ws_cmd = ws_cmd
        self.timeout = timeout
        self.thread = threading.Thread(target=self.ws_cmd.cmd_main, args=(args,))
        self.thread.daemon = True

    def start(self):
        app._already_running = True
        self.thread.start()

    def stop(self):
        app.shutdown()
        self.thread.join(timeout=self.timeout)


class LiveWebTest(Basetest):
    """
    Real IO LiveTest against LiveWebserver
    """

    def setUp(self, debug=False, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    @classmethod
    def setUpClass(cls):
        # Create the webserver
        cls.ws = LiveWebserver()

        # Create the cmd instance and get properly configured args
        cls.cmd = LiveCmd()
        # Parse minimal arguments - just --serve is needed for testing
        args = ["--serve"]

        # Create runner with proper args
        cls.runner = LiveServerRunner(cls.cmd, args=args)
        cls.runner.start()
        cls.base_url = f"http://127.0.0.1:{cls.ws.config.default_port}"
        cls.max_secs_to_wait=5
        cls.wait_until_ready(cls.max_secs_to_wait)

    @classmethod
    def tearDownClass(cls):
        cls.runner.stop()

    @classmethod
    def wait_until_ready(cls,secs:int):
        url = f"{cls.base_url}/live-htmltest"
        for _ in range(secs*10):
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    return
            except Exception:
                pass
            time.sleep(0.1) # 100 millisecs per loop
        raise TimeoutError("Live server did not start")

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
