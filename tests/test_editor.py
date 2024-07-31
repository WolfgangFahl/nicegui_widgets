"""
Created on 2022-11-27

@author: wf
"""

from ngwidgets.basetest import Basetest
from ngwidgets.editor import Editor


class TestEditor(Basetest):
    """
    test opening an editor
    """

    def test_Editor(self):
        """
        test the editor
        """
        if not self.inPublicCI():
            # comment out to run test
            return
            # open this source file
            Editor.open(__file__)
            Editor.open(
                "https://stackoverflow.com/questions/1442841/lauch-default-editor-like-webbrowser-module"
            )
            Editor.open_tmp_text(
                "A sample text to be opened in a temporary file", file_name="sample.txt"
            )
