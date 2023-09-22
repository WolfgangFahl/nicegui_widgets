'''
Created on 2023-09-10

@author: wf
'''
from tests.basetest import Basetest
from ngwidgets.widgets import Link

class TestNiceGuiWidgets(Basetest):
    """
    test nice gui widgets
    """
    
    def test_widgets(self):
        link_html=Link.create("http://nicegui.io", "nicegui", "nicegui")
        if self.debug:
            print(link_html)
        expected="<a href='http://nicegui.io' title='nicegui'>nicegui</a>"
        self.assertEqual(expected,link_html)

