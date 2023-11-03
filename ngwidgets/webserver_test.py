"""
Created on 2023-11-03

@author: wf
"""
import threading
from fastapi.testclient import TestClient
from ngwidgets.basetest import Basetest
from nicegui.server import Server

class WebserverTest(Basetest):
    """
    a webserver test environment
    
    Attributes:
        ws: An instance of the web server being tested.
        ws_thread: The thread running the web server.
        client: A test client for interacting with the web server.
    """
    
    def setUp(self, server_class, cmd_class,debug=False, profile=True):
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
        self.config = server_class.get_config()  # Assumes `get_config()` is a class method of server_class
        self.config.default_port += 10000  # Use a different port for testing than for production

        self.cmd = cmd_class(self.config, server_class)  # Instantiate the command class with config and server_class
        argv = []
        args = self.cmd.cmd_parse(argv)  # Parse the command-line arguments with no arguments passed

        self.ws = server_class()  # Instantiate the server class
        self.ws_thread = threading.Thread(target=self.ws.run, name="webservice", kwargs={'args': args})
        self.ws_thread.start()  # Start the server in a separate thread

        self.client = TestClient(self.ws.app)  # Instantiate the test client with the server's app
        
    def tearDown(self):
        """
        tear Down everything
        """
        if hasattr(Server, "instance"):
            # here we should shutdown the server
            pass

    def getHtml(self,path:str)->str:
        """
        get the html content for the given path
        """
        response=self.client.get(path)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content is not None)
        html=response.content.decode()
        if self.debug:
            print(html)
        return html

        