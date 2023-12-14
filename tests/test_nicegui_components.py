"""
Created on 2023-12-14

Test suite for the nicegui_components module in the ngwidgets package.

@author: wf
"""
import json
from dataclasses import asdict
from ngwidgets.basetest import Basetest
from ngwidgets.nicegui_component import PyPi, Component

class TestNiceguiComponents(Basetest):
    """
    Test cases for the nicegui_components module.
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.test_projects = [
            {"name": "CatDesign", "url": "https://github.com/ofenbach/CatDesign"},
            {"name": "nicegui-extensions", "url": "https://pypi.org/project/nicegui-extensions/"}
        ]

    def test_get_package_info(self):
        """
        Test getting detailed information about a package from PyPI.
        """
        pypi = PyPi(debug=self.debug)
        project_name = self.test_projects[1]["name"]
        package_info = pypi.get_package_info(project_name)
        component=pypi.as_component(package_info)
        if self.debug:
            print(json.dumps(package_info,indent=2))
            print(json.dumps(asdict(component),indent=2,default=str))
        self.assertIsNotNone(package_info)
        self.assertIn("info", package_info)
        self.assertIn("summary", package_info["info"])

    def test_search_packages(self):
        """
        Test searching for nicegui packages on PyPI.
        """
        pypi = PyPi()
        search_result = pypi.search_packages("nicegui")
        if self.debug:
            for package_record in search_result:
                print(json.dumps(package_record,indent=2))
        self.assertIsNotNone(search_result)
        self.assertTrue(len(search_result) > 0)