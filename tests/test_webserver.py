"""
Created on 2023-11-03

@author: wf
"""

from ngwidgets.ngwidgets_cmd import NiceguiWidgetsCmd
from ngwidgets.projects import Projects
from ngwidgets.webserver_test import WebserverTest
from ngwidgets.widgets_demo import NiceGuiWidgetsDemoWebserver


class TestDemoWebserver(WebserverTest):
    """
    test the demo webserver
    """

    def setUp(self, debug=False, profile=True):
        server_class = NiceGuiWidgetsDemoWebserver
        cmd_class = NiceguiWidgetsCmd
        WebserverTest.setUp(self, server_class, cmd_class, debug=debug, profile=profile)

    def testDemoWebserver(self):
        """
        test API docs access
        """
        # self.debug=True
        html = self.getHtml("/docs")
        self.assertTrue("Swagger" in html)

    def testApi(self):
        """
        Tests the API by requesting specified paths and evaluating the responses.
        """
        paths = ["/solutions.yaml"]
        debug = self.debug
        debug = True
        for path in paths:
            response = self.get_response(path)
            yaml_str = response.text
            projects = Projects.from_yaml(yaml_str)
            if debug:
                for project in projects.projects:
                    print(project)
            pass
