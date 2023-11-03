"""
Created on 2023-11-03

@author: wf
"""
from ngwidgets.webserver_test import WebserverTest
from ngwidgets.ngwidgets_cmd import WebserverCmd
from ngwidgets.widgets_demo import Webserver

class TestDemoWebserver(WebserverTest):
    """
    test the demo webserver
    """
    
    def setUp(self,debug=False, profile=True):
        server_class=Webserver
        cmd_class=WebserverCmd
        WebserverTest.setUp(self, server_class, cmd_class, debug=debug, profile=profile)
         
    def testDemoWebserver(self):
        """
        test API docs access
        """
        #self.debug=True
        html=self.getHtml("/docs")
        self.assertTrue("Swagger" in html)
        