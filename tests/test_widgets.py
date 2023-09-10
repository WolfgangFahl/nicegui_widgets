'''
Created on 2023-09-10

@author: wf
'''
import unittest
from ngwidgets.widgets import Widgets

class TestNiceGuiWidgets(unittest.TestCase):
    """
    test nice gui widgets
    """
    
    def test_widgets(self):
        widgets=Widgets()

# This is the standard boilerplate to run the tests when the script is executed
if __name__ == '__main__':
    unittest.main()
