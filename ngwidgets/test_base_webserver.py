"""
Refactored on 2025-05-19


@author: wf
"""
import json
import sys
import threading
import time
from argparse import Namespace
from typing import Any, Optional
from nicegui import app
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
        # prevent middleware error if app already started
        if hasattr(app, "_already_running"):
            self.ws.run = lambda _args: None  # avoid double run
        else:
            app._already_running = True  # mark NiceGUI as started
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

class BaseWebserverTest(Basetest):
    """
    Common base class for both TestClient and real HTTP testing scenarios

    This provides a unified interface for testing web server responses
    whether using FastAPI TestClient or real HTTP requests.
    """

    def setUp(self, debug=False, profile=True):
        """Set up the test environment"""
        super().setUp(debug=debug, profile=profile)

    def get_response(self, path: str, expected_status_code: int = 200) -> Any:
        """
        Get a response for the given path and verify its status code

        Args:
            path: The path to request
            expected_status_code: The expected HTTP status code

        Returns:
            The response object
        """
        raise NotImplementedError("Subclasses must implement get_response method")

    def get_html(self, path: str, expected_status_code: int = 200) -> str:
        """
        Get HTML content for the given path

        Args:
            path: The path to request
            expected_status_code: The expected HTTP status code

        Returns:
            The HTML content as a string
        """
        response = self.get_response(path, expected_status_code)
        if hasattr(response, 'content'):
            html = response.content.decode()

            if self.debug:
                print(html)
            return html
        return ""

    def get_json(self, path: str, expected_status_code: int = 200) -> Any:
        """
        Get JSON content for the given path

        Args:
            path: The path to request
            expected_status_code: The expected HTTP status code

        Returns:
            The parsed JSON data
        """
        response = self.get_response(path, expected_status_code)
        try:
            if hasattr(response, 'json'):
                # Both requests.Response and TestClient responses have a json method
                return response.json()
            else:
                # Fallback
                return json.loads(response.content)
        except json.JSONDecodeError as e:
            self.fail(f"Failed to decode JSON for request {path}: {str(e)}")