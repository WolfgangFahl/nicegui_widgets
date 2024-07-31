"""
Created on 2023-09-13

@author: wf
"""

import dataclasses
import json

from ngwidgets.basetest import Basetest
from ngwidgets.color_schema import ColorSchema


class TestColorSchema(Basetest):
    """
    test file selector
    """

    def test_indigo(self):
        """
        test the indigo schema
        """
        expected = {
            "name": "indigo",
            "primary": "#3F51B5",
            "secondary": "#5C6BC0",
            "accent": "#8A72AC",
            "dark": "#1A237E",
            "positive": "#28A745",
            "negative": "#D32F2F",
            "info": "#536DFE",
            "warning": "#FFB74D",
        }
        color_schema = ColorSchema.indigo()
        color_schema_dict = dataclasses.asdict(color_schema)
        debug = self.debug
        debug = True
        if debug:
            print(json.dumps(color_schema_dict, indent=2))
        self.assertEqual(expected, color_schema_dict)
