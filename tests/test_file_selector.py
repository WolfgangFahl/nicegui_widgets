"""
Created on 2023-07-23

@author: wf
"""

import json
import os

from ngwidgets.basetest import Basetest
from ngwidgets.file_selector import FileSelector


class TestFileSelector(Basetest):
    """
    test file selector
    """

    # Define a filter function for files starting with 'test_'
    @staticmethod
    def filter_test_files(item_name: str) -> bool:
        return item_name.startswith("test_")

    def test_get_dir_tree(self):
        """
        test getting the directory tree structure for
        the directory of the script
        """
        # Get the directory path of the current script
        script_directory = os.path.dirname(os.path.abspath(__file__))
        extensions = {"python": ".py"}
        # Instantiate FileSelector with the filter function
        file_selector = FileSelector(
            script_directory,
            extensions=extensions,
            filter_func=self.filter_test_files,
            create_ui=False,
        )

        debug = self.debug
        # debug = True
        if debug:
            print(json.dumps(file_selector.tree_structure, indent=2))

        self.assertTrue(file_selector.file_count >= 7)
        tree = file_selector.tree_structure
        found = False
        for child in tree["children"]:
            if child["label"] == "test_file_selector.py":
                found = True
        self.assertTrue(found)
