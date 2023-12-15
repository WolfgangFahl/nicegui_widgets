"""
Created on 2023-12-14

Test suite for the nicegui_components module in the ngwidgets package.

@author: wf
"""
import json
from pathlib import Path
from dataclasses import asdict
from ngwidgets.basetest import Basetest
from ngwidgets.nicegui_component import PyPi, Component,Components, GitHubAccess

class TestNiceguiComponents(Basetest):
    """
    Test cases for the nicegui_components module.
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.pypi_test_projects = [
            ("ngwidgets", "https://pypi.org/project/ngwidgets/"),
            ("nicegui-extensions", "https://pypi.org/project/nicegui-extensions/")           
        ]

    def test_get_package_info(self):
        """
        Test getting detailed information about a package from PyPI.
        """
        pypi = PyPi(debug=self.debug)
        for project_name, url in self.pypi_test_projects:
            package_info = pypi.get_package_info(project_name)
            component=Component.from_pypi(package_info)
            if pypi.debug:
                print("Package Info:")
                print(json.dumps(package_info["info"], indent=2))
                
                print("Component Data:")
                print(json.dumps(asdict(component), indent=2, default=str))
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
                print(json.dumps(package_record["info"],indent=2))
        self.assertIsNotNone(search_result)
        self.assertTrue(len(search_result) > 0)
        
    def test_search_components(self):
        """
        Test searching for nicegui components on PyPI.
        """
        pypi = PyPi()
        search_result = pypi.search_components("nicegui")
        if self.debug:
            for component in search_result:
                print(json.dumps(asdict(component), indent=2, default=str))
        self.assertIsNotNone(search_result)
        self.assertTrue(len(search_result) > 0)
        
    def test_search_repositories_by_topic(self):
        """
        Test searching for repositories by a specific topic.
        """
        github_access=GitHubAccess()
        topic = 'nicegui'
        repositories = github_access.search_repositories_by_topic(topic)
        self.assertIsNotNone(repositories)
        self.assertTrue(len(repositories) > 0)
        if self.debug:
            for repo in repositories:
                print (repo)
        self.assertIn("WolfgangFahl/nicegui_widgets",repositories)
            
    def test_component_from_github(self):
        """
        Test creating a Component instance from a GitHub repository.
        """
        repo_name = "WolfgangFahl/nicegui_widgets"
        github_access = GitHubAccess()  # Assuming GitHubAccess is already defined and properly set up

        # Create a Component from the GitHub repository
        component = Component.from_github(repo_name, github_access)

        # Debug printout
        if self.debug:
            print(f"Created Component from GitHub:\n{json.dumps(asdict(component), indent=2,default=str)}")

        # Assert that the Component has been properly created with expected attributes
        self.assertEqual(component.name, "nicegui_widgets")
        self.assertEqual(component.github, f"https://github.com/{repo_name}")
        self.assertIsNotNone(component.stars)
        self.assertIsNotNone(component.github_description)
        self.assertIsNotNone(component.github_author)
        self.assertIsNotNone(component.created_at)
        
    def test_update_save_and_load_components(self):
        """
        Test updating, saving, and loading components for a specific topic using the Components class.
        """
        topic = "nicegui"
        test_directory = "/tmp/components_test"
        components_manager = Components(topic=topic)
        components_manager.default_directory=test_directory

        # Update the components (this method should be implemented to fetch components from PyPI and GitHub)
        components_manager.update()
        components_manager.save()

        # Load the components
        loaded_components = components_manager.load()

        # Verify that components are loaded
        self.assertIsNotNone(loaded_components)
        self.assertTrue(len(loaded_components) > 0)

        # Optionally, inspect some properties of the loaded components
        for component in loaded_components:
            self.assertIsNotNone(component.name)
   
        # Clean up: remove the created directory and its contents
        if not self.debug:
            if components_manager.file_path.exists():
                components_manager.file_path.unlink()
            if Path(test_directory).exists():
                Path(test_directory).rmdir()