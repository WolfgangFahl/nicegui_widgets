"""
Created on 2023-12-14

Test suite for the nicegui_projects module in the ngwidgets package.

@author: wf
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from dateutil.parser import parse

from ngwidgets.basetest import Basetest
from ngwidgets.components import Components
from ngwidgets.progress import TqdmProgressbar
from ngwidgets.projects import GitHubAccess, Project, Projects, PyPi


class TestNiceguiProjects(Basetest):
    """
    Test cases for the nicegui_projects module.
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.pypi_test_projects = [
            (
                "dynamic-competence-map",
                "https://pypi.org/project/dynamic-competence-map/",
            ),
            ("ngwidgets", "https://pypi.org/project/ngwidgets/"),
            ("nicescad", "https://pypi.org/project/nicescad/"),
            ("nicegui-extensions", "https://pypi.org/project/nicegui-extensions/"),
        ]

    def test_get_package_info(self):
        """
        Test getting detailed information about a package from PyPI.
        """
        pypi = PyPi(debug=self.debug)
        for project_name, url in self.pypi_test_projects:
            package_info = pypi.get_package_info(project_name)

            project = Project.from_pypi(package_info)
            if pypi.debug:
                print("Package Info:")
                print(json.dumps(package_info["info"], indent=2))

                print("Project Data:")
                print(json.dumps(asdict(project), indent=2, default=str))
            self.assertIsNotNone(package_info)
            self.assertIn("info", package_info)
            self.assertIn("summary", package_info["info"])
            self.assertEqual(url, project.pypi)

    def test_search_packages(self):
        """
        Test searching for nicegui packages on PyPI.
        """
        pypi = PyPi()
        search_result = pypi.search_packages("nicegui")
        if self.debug:
            for package_record in search_result:
                print(json.dumps(package_record["info"], indent=2))
        self.assertIsNotNone(search_result)
        self.assertTrue(len(search_result) > 0)

    def test_search_projects(self):
        """
        Test searching for nicegui projects on PyPI.
        """
        pypi = PyPi()
        search_result = pypi.search_projects("nicegui")
        if self.debug:
            for project in search_result:
                print(json.dumps(asdict(project), indent=2, default=str))
        self.assertIsNotNone(search_result)
        self.assertTrue(len(search_result) > 0)

    def test_search_repositories_by_topic(self):
        """
        Test searching for repositories by a specific topic.
        """
        github_access = GitHubAccess()
        query = "topic:nicegui"
        repositories = github_access.search_repositories(query)
        self.assertIsNotNone(repositories)
        self.assertTrue(len(repositories) > 0)
        if self.debug:
            # Sort the repositories first by owner login, then by repository full name
            sorted_repos = sorted(
                repositories.items(), key=lambda item: (item[1].owner.login, item[0])
            )

            for index, (repo_name, repo) in enumerate(sorted_repos, start=1):
                print(f"{index:4}: {repo.owner.login:40} → {repo_name}  ")
        self.assertIn("WolfgangFahl/nicegui_widgets", repositories)

    def test_project_from_github(self):
        """
        Test creating a Project instance from a GitHub repository.
        """
        github_access = (
            GitHubAccess()
        )  # Assuming GitHubAccess is already defined and properly set up
        projects = Projects(topic="nicegui")
        # List of tuples with repository names and expected attributes
        example_repos = [
            (
                "WolfgangFahl/dcm",
                {
                    "github": "https://github.com/WolfgangFahl/dcm",
                    "component_count": 1,
                },
            ),
            (
                "justpy-org/justpy",
                {
                    "github": "https://github.com/justpy-org/justpy",
                    "stars": 1110,
                    "github_description": "An object oriented high-level Python Web Framework that requires no frontend programming",
                    "avatar": "https://avatars.githubusercontent.com/u/112261672?v=4",
                    "component_count": 228,
                },
            ),
            (
                "WolfgangFahl/nicegui_widgets",
                {
                    "name": "nicegui_widgets",
                    "github": "https://github.com/WolfgangFahl/nicegui_widgets",
                    "stars": 3,
                    "github_description": "nicegui widgets",
                    "github_author": "WolfgangFahl",
                    "created_at": "2023-09-10 06:12:30+00:00",
                },
            ),
            (
                "zauberzeug/rosys",
                {
                    "name": "rosys",
                    "github": "https://github.com/zauberzeug/rosys",
                    "stars": 37,
                    "github_description": "An all-Python robot system based on web technologies. The purpose is similar to ROS, but it's based on NiceGUI and easier to use for mobile robotics.",
                    "github_author": "zauberzeug",
                    "created_at": "2020-07-20 13:29:11+00:00",
                },
            ),
            # Add more test cases here as needed
        ]
        for repo_name, expected_attributes in example_repos:
            url = expected_attributes["github"]
            ex_repo_name = projects.extract_repo_name_from_url(url)
            self.assertEqual(repo_name, ex_repo_name)
            repo = github_access.github.get_repo(repo_name)

            # Create a Project from the GitHub repository
            project = Project.from_github(repo)

            # Debug printout
            if self.debug:
                print(
                    f"Project for GitHub {repo_name}:\n{json.dumps(asdict(project), indent=2,default=str)}"
                )

            # Assert that the Project has been properly created with expected attributes
            for attribute, expected_value in expected_attributes.items():
                actual_value = getattr(project, attribute)
                if isinstance(actual_value, datetime):
                    # Parse the expected date string into a datetime object for comparison
                    expected_date = parse(expected_value)
                    self.assertEqual(actual_value, expected_date)
                elif isinstance(actual_value, int) and attribute == "stars":
                    self.assertGreaterEqual(actual_value, expected_value)
                else:
                    self.assertEqual(actual_value, expected_value)

            if project.components_url:
                components = project.get_components(
                    cache_directory=projects.default_directory
                )
                if self.debug:
                    print(
                        f"found {len(components.components)} components for {project.name}"
                    )

    def test_update_save_and_load_projects(self):
        """
        Test updating, saving, and loading projects for a specific topic using the Projects class.
        """
        limit_github = 10
        limit_pypi = 5
        topic = "nicegui"
        test_directory = "/tmp/projects_test"
        projects_manager = Projects(topic=topic)
        projects_manager.default_directory = test_directory
        progress_bar = None
        if self.debug:
            progress_bar = TqdmProgressbar(
                total=0, desc="update projects", unit="steps"
            )
        # Update the projects (this method should be implemented to fetch projects from PyPI and GitHub)
        projects_manager.update(
            progress_bar=progress_bar, limit_github=limit_github, limit_pypi=limit_pypi
        )
        projects_manager.save()

        # Load the projects
        loaded_projects = projects_manager.load()

        # Verify that projects are loaded
        self.assertIsNotNone(loaded_projects)
        self.assertTrue(len(loaded_projects) > 0)

        # Optionally, inspect some properties of the loaded projects
        for project in loaded_projects:
            self.assertIsNotNone(project.name)

        # Clean up: remove the created directory and its contents
        if not self.debug:
            if projects_manager.file_path.exists():
                projects_manager.file_path.unlink()
            if Path(test_directory).exists():
                Path(test_directory).rmdir()

    def test_components_from_url(self):
        """
        test loading components from url
        """
        cases = [
            (
                217,
                "https://raw.githubusercontent.com/justpy-org/justpy/master/.components.yaml",
            )
        ]
        for expected, url in cases:
            components = Components.load_from_yaml_url(url)
            if self.debug:
                for index, component in enumerate(components.components):
                    print(f"{index}:{component.to_yaml()}")
            self.assertTrue(len(components.components) >= expected)
