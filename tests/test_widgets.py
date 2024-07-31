"""
Created on 2023-09-10

@author: wf
"""

from ngwidgets.basetest import Basetest
from ngwidgets.widgets import Link


class TestNiceGuiWidgets(Basetest):
    """
    test nice gui widgets
    """

    def test_widgets(self):
        """
        test the Link create method
        """
        link_html = Link.create("http://nicegui.io", "nicegui", "nicegui")
        debug = self.debug
        # debug=True
        if debug:
            print(link_html)
        expected = "<a href='http://nicegui.io' title='nicegui' style='color: blue;text-decoration: underline;'>nicegui</a>"
        self.assertTrue(expected, link_html)
