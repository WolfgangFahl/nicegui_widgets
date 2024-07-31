"""
Created on 2023-11-03

@author: wf
"""

import json
import sys
import threading
import time
from argparse import Namespace
from typing import Any, Optional

from fastapi.testclient import TestClient
from nicegui import app
from starlette.responses import Response

from ngwidgets.basetest import Basetest


class ThreadedServerRunner:
    """
    run the Nicegui Server in a thread
    """

    def __init__(
        self,
        ws: Any,
        args: Optional[Namespace] = None,
        shutdown_timeout: float = 5.0,
        debug: bool = False,
    ) -> None:
        """
        Initialize the ThreadedServerRunner with a web server instance, optional arguments, and a shutdown timeout.

        Args:
            ws: The web server instance to run.
            args: Optional arguments to pass to the web server's run method.
            shutdown_timeout: The maximum time in seconds to wait for the server to shutdown.
            debug: sets the debugging mode
        """
        self.debug = debug
        self.ws = ws
        self.args = args
        self.shutdown_timeout = shutdown_timeout
        self.thread = threading.Thread(target=self._run_server)
        self.thread.daemon = True

    def _run_server(self) -> None:
        """Internal method to run the server."""
        # The run method will be called with the stored argparse.Namespace
        self.ws.run(self.args)

    def start(self) -> None:
        """Start the web server thread."""
        self.thread.start()

    def warn(self, msg: str):
        """
        show the given warning message
        """
        if self.debug:
            print(msg, file=sys.stderr)

    def stop(self) -> None:
        """
        Stop the web server thread, signaling the server to exit if it is still running.
        """
        if self.thread.is_alive():
            # Mark the start time of the shutdown
            start_time = time.time()
            # call the shutdown see https://github.com/zauberzeug/nicegui/discussions/1957
            app.shutdown()
            # Initialize the timer for timeout
            end_time = start_time + self.shutdown_timeout

            # Wait for the server to shut down, but only as long as the timeout
            while self.thread.is_alive() and time.time() < end_time:
                time.sleep(0.05)  # Sleep to prevent busy waiting

            # Calculate the total shutdown time
            shutdown_time_taken = time.time() - start_time

            if self.thread.is_alive():
                # The server didn't shut down within the timeout, handle appropriately
                if self.debug:
                    self.warn(
                        f"Warning: The server did not shut down gracefully within the timeout period. Shutdown attempt took {shutdown_time_taken:.2f} seconds."
                    )
            else:
                # If shutdown was successful, report the time taken
                if self.debug:
                    self.warn(
                        f"Server shutdown completed in {shutdown_time_taken:.2f} seconds."
                    )


class WebserverTest(Basetest):
    """
    a webserver test environment

    Attributes:
        ws: An instance of the web server being tested.
        ws_thread: The thread running the web server.
        client: A test client for interacting with the web server.
    """

    def setUp(self, server_class, cmd_class, debug=False, profile=True):
        """
        Create and start a test instance of a web server using the specified server and command classes.

        Args:
            server_class: The class of the server to be tested. This should be a class reference that
                          includes a static `get_config()` method and an instance method `run()`.
            cmd_class: The command class used to parse command-line arguments for the server.
                       This class should have an initialization accepting `config` and `server_class`
                       and a method `cmd_parse()` that accepts a list of arguments.

        Returns:
            An instance of WebserverTest containing the started server thread and test client.

        Raises:
            ValueError: If an invalid server_class or cmd_class is provided.

        Example:
            >>> test_server = WebserverTest.get_webserver_test(MyServerClass, MyCommandClass)
            >>> test_server.client.get('/')
            <Response [200]>
        """
        Basetest.setUp(self, debug=debug, profile=profile)
        self.config = (
            server_class.get_config()
        )  # Assumes `get_config()` is a class method of server_class
        self.config.default_port += (
            10000  # Use a different port for testing than for production
        )

        self.cmd = cmd_class(
            self.config, server_class
        )  # Instantiate the command class with config and server_class
        argv = []
        args = self.cmd.cmd_parse(
            argv
        )  # Parse the command-line arguments with no arguments passed

        self.ws = server_class()  # Instantiate the server class
        self.server_runner = ThreadedServerRunner(self.ws, args=args, debug=self.debug)
        self.server_runner.start()  # start server in separate thread

        self.client = TestClient(
            self.ws.app
        )  # Instantiate the test client with the server's app

    def tearDown(self):
        """
        tear Down everything
        """
        super().tearDown()
        # Stop the server using the ThreadedServerRunner
        self.server_runner.stop()

    def get_response(self, path: str, expected_status_code: int = 200) -> Response:
        """
        Sends a GET request to a specified path and verifies the response status code.

        This method is used for testing purposes to ensure that a GET request to a
        given path returns the expected status code. It returns the response object
        for further inspection or testing if needed.

        Args:
            path (str): The URL path to which the GET request is sent.
            expected_status_code (int): The expected HTTP status code for the response.
                                        Defaults to 200.

        Returns:
            Response: The response object from the GET request.
        """
        response = self.client.get(path)
        self.assertEqual(response.status_code, expected_status_code)
        return response

    def get_html(self, path: str, expected_status_code=200) -> str:
        """
        get the html content for the given path
        """
        response = self.get_response(path, expected_status_code)
        self.assertTrue(response.content is not None)
        html = response.content.decode()
        if self.debug:
            print(html)
        return html

    def getHtml(self, path: str) -> str:
        """
        get the html content for the given path
        """
        html = self.get_html(path)
        return html

    def get_html_for_post(self, path: str, data) -> str:
        """
        get the html content for the given path by posting the given data
        """
        response = self.client.post(path, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content is not None)
        html = response.content.decode()
        if self.debug:
            print(html)
        return html

    def get_json(self, path: str, expected_status_code: int = 200) -> Any:
        """
        Sends a GET request to a specified path, verifies the response status code,
        and returns the JSON content of the response.

        This method is useful for testing API endpoints that return JSON data.
        It ensures that the request to a given path returns the expected status code
        and then parses and returns the JSON response.

        Args:
            path (str): The URL path to which the GET request is sent.
            expected_status_code (int): The expected HTTP status code for the response.
                                        Defaults to 200.

        Returns:
            Any: The parsed JSON data from the response.

        Raises:
            AssertionError: If the response status code does not match the expected status code.
            JSONDecodeError: If the response body cannot be parsed as JSON.
        """
        response = self.get_response(path, expected_status_code)
        try:
            json_data = response.json()
            return json_data
        except json.JSONDecodeError as e:
            self.fail(
                f"Failed to decode JSON for request {path} from response: {str(e)}"
            )
