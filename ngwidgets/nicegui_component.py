"""
Created on 2023-12-14

This module, developed as part of the ngwidgets package under the instruction of WF, provides 
classes and methods for interacting with the Python Package Index (PyPI). It includes the 
`Project` data class for representing software projects and the `PyPi` class for searching 
and retrieving package information from PyPI. The code facilitates the creation of tools and 
applications that interact with PyPI for information about Python packages.

Prompts for LLM: 
- Create Python classes Project and Projects (holding a list of Project elements) for interacting with PyPI and github, including search functionality.
- Develop a data class in Python to represent a software project with the attributes.
        name (str): The name of the project.
        package (str): The package name on PyPI.
        demo (str): A URL to a demo of the project, if available.
        forum_post (str): A URL to a forum post discussing the project.
        github (str): A URL to the GitHub repository of the project.
        pypi (str): A URL to the PyPI page of the project.
        image_url (str): A URL to an image representing the project.
        stars (int): Number of stars on GitHub.
        github_description (str): Description of the project from GitHub.
        pypi_description (str): Description of the project from PyPI.
        avatar (str): A URL to the avatar image of the author/maintainer.
        search_text (str): Text used for searching the project.
        github_author (str): The GitHub username of the project's author.
        pypi_author (str): The PyPI username of the project's author.
        created_at (datetime): The date when the project was created.
        downloads (int): Number of downloads from PyPI.
        categories (List[str]): Categories associated with the project.
        version (str): The current version of the project on PyPI.
 
- Implement methods to search PyPI and github for packages/repos that represent projects and retrieve detailed package information on a given topic.
- allow saving and loading the collected projects

Main author: OpenAI's language model (instructed by WF)
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib import error, request

from bs4 import BeautifulSoup, ResultSet, Tag
from github import Github, Repository


class GitHubAccess:
    def __init__(self, access_token=None):
        """
        Initialize the GitHub instance.
        If access_token is provided, use it for authenticated access.
        Otherwise, access is unauthenticated with lower rate limits.
        """
        self.github = Github(access_token) if access_token else Github()

    def search_repositories(self, query):
        """
        Search for repositories with a given query.
        Returns a list of repository names.
        """
        repositories = self.github.search_repositories(query)
        return [repo.full_name for repo in repositories]


@dataclass
class Project:
    """
    A data class representing a software project, potentially from PyPI or GitHub.

    Attributes:
        name (str): The name of the project.
        package (str): The package name on PyPI.
        demo (str): A URL to a demo of the project, if available.
        forum_post (str): A URL to a forum post discussing the project.
        github (str): A URL to the GitHub repository of the project.
        pypi (str): A URL to the PyPI page of the project.
        image_url (str): A URL to an image representing the project.
        stars (int): Number of stars on GitHub.
        github_description (str): Description of the project from GitHub.
        pypi_description (str): Description of the project from PyPI.
        avatar (str): A URL to the avatar image of the author/maintainer.
        search_text (str): Text used for searching the project.
        github_author (str): The GitHub username of the project's author.
        pypi_author (str): The PyPI username of the project's author.
        created_at (datetime): The date when the project was created.
        downloads (int): Number of downloads from PyPI.
        categories (List[str]): Categories associated with the project.
        version (str): The current version of the project on PyPI.
        solution_tags(str): a list of comma separated tags for checking the conformance of the project
        to the solution bazaar guidelines
    """

    name: Optional[str] = None
    package: Optional[str] = None
    demo: Optional[str] = None
    forum_post: Optional[str] = None
    github: Optional[str] = None
    pypi: Optional[str] = None
    image_url: Optional[str] = None
    stars: Optional[int] = None
    github_description: Optional[str] = None
    pypi_description: Optional[str] = None
    avatar: Optional[str] = None
    search_text: Optional[str] = None
    github_author: Optional[str] = None
    pypi_author: Optional[str] = None
    created_at: Optional[datetime] = None
    downloads: Optional[int] = None
    categories: List[str] = field(default_factory=list)
    version: Optional[str] = None
    solution_tags: Optional[str] = ""

    @property
    def install_instructions(self) -> str:
        """
        Get the installation instructions for the project.

        Returns:
            str: Installation instructions for the project.
        """
        return f"pip install {self.package}"

    @classmethod
    def from_github(cls, repo_name: str, github_access: GitHubAccess) -> "Project":
        """
        Class method to create a Project instance from a GitHub repository.

        Args:
            repo_name (str): The name of the GitHub repository (e.g., 'user/repo').
            github_access (GitHubAccess): Instance of GitHubAccess for API calls.

        Returns:
            Project: An instance of the Project class filled with GitHub repository details.
        """
        repo: Repository.Repository = github_access.github.get_repo(repo_name)
        avatar_url = repo.owner.avatar_url if repo.owner.avatar_url else None
        stars = repo.stargazers_count
        project = cls(
            name=repo.name,
            github=repo.html_url,
            stars=stars,
            github_description=repo.description,
            github_author=repo.owner.login,
            created_at=repo.created_at,
            avatar=avatar_url,
            # Other fields can be filled in as needed
        )
        return project

    @classmethod
    def from_pypi(cls, package_info: Dict) -> "Project":
        """
        Class method to create a Project instance from a PyPI package.

        Args:
            package_info (Dict): Dictionary containing package data from PyPI.

        Returns:
            Project: An instance of the Project class filled with PyPI package details.
        """
        info = package_info.get("info", {})
        github = None
        project_urls = info.get("project_urls", {})
        if project_urls:
            github_url = project_urls.get("Repository") or project_urls.get("Source")
            if github_url and "github" in github_url:
                github = github_url

        project = cls(
            name=info.get("name"),
            package=info.get("name"),
            pypi=info.get("package_url"),
            pypi_description=info.get("summary"),
            version=info.get("version"),
            github_description=info.get("description"),
            github=github,
        )
        return project


class Projects:
    """
    handle a list of python projects on a specific topic
    """

    def __init__(self, topic: str):
        """
        Constructor
        Args:
            topic (str): The topic of the projects.
        """
        self._topic = topic
        self._default_directory = Path.home() / ".nicegui"
        self.projects = []
        self.last_update_time = self.get_file_update_time()

    def get_file_update_time(self):
        """
        Get the last modification time of the projects file.

        Returns:
            datetime: The last modification time of the file or None if file does not exist.
        """
        if self.file_path.exists():
            file_mod_time = os.path.getmtime(self.file_path)
            return datetime.fromtimestamp(file_mod_time)
        return None

    @property
    def default_directory(self) -> Path:
        """
        The default directory for saving and loading projects.
        Returns:
            Path: The default directory path.
        """
        return self._default_directory

    @default_directory.setter
    def default_directory(self, directory: str):
        """
        Set the default directory for saving and loading projects.
        Args:
            directory (str): The path to the new default directory.
        """
        self._default_directory = Path(directory)

    @property
    def file_path(self) -> Path:
        """
        The file path for saving and loading projects, based on the topic.
        Returns:
            Path: The file path.
        """
        filename = f"components_{self._topic}.json"
        return self._default_directory / filename

    def save(self, projects: List[Project] = None, directory: str = None):
        """
        Save a list of Project instances to a JSON file.
        Args:
            projects (List[Project]): A list of Project instances to be saved.
            directory (str, optional): The directory where the file will be saved. If None, uses the default directory.
        """
        if projects is None:
            projects = self.projects
        directory = Path(directory or self.default_directory)
        os.makedirs(directory, exist_ok=True)

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(
                [project.__dict__ for project in projects], file, indent=4, default=str
            )

    def load(self, directory: str = None, set_self: bool = True) -> List[Project]:
        """
        Load a list of Project instances from a JSON file.
        Args:
            directory (str, optional): The directory where the file is located. If None, uses the default directory.
            set_self(bool): if True set self.projects with the result
        Returns:
            List[Project]: A list of Project instances loaded from the file.

        """
        directory = Path(directory or self.default_directory)

        if not self.file_path.exists():
            raise FileNotFoundError(f"No such file: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as file:
            projects_records = json.load(file)

        projects = []
        for project_record in projects_records:
            project = Project(**project_record)
            projects.append(project)
        if set_self:
            self.projects = projects
        return projects
    
    def get_github_projects(self,github_access):
        """
        Retrieve GitHub projects both specifically tagged and generally related to the topic.
        """
        
        queries = [
            f"topic:{self._topic}",  # Specific topic query
            f"{self._topic}"         # General topic query
        ]
        all_projects = {}

        for query in queries:
            github_repos = github_access.search_repositories(query)
            for repo in github_repos:
                project = Project.from_github(repo, github_access)

                # If this is from a specific topic query, add 'topic' to solution_tags
                if query.startswith("topic:"):
                    if project.solution_tags:
                        project.solution_tags += ","
                    project.solution_tags += "topic"

                all_projects[project.name] = project

        return list(all_projects.values())

    def update(self):
        """
        Update the list of projects by retrieving potential projects from PyPI and GitHub based on the topic.
        """
        # pypi access
        pypi = PyPi()

        # Fetch projects from PyPI
        pypi_projects = pypi.search_projects(self._topic)
        # Fetch repositories from GitHub
        github_access = GitHubAccess()
        self.projects= self.get_github_projects(github_access)
        # Create a dictionary to map GitHub URLs to projects
        comp_by_github_url = {
            comp.github: comp for comp in self.projects if comp.github
        }

        # Merge PyPI projects into the GitHub projects
        for comp in pypi_projects:
            if comp.github in comp_by_github_url:
                # Merge PyPI data into existing GitHub project
                pypi_comp = comp_by_github_url[comp.github]
                pypi_comp.pypi = comp.pypi
                pypi_comp.package = comp.package
                pypi_comp.pypi_description = comp.pypi_description
                pypi_comp.version = comp.version
            else:
                # Check if the PyPI project has a GitHub URL
                if comp.github:
                    repo_name = self.extract_repo_name_from_url(comp.github)
                    if not repo_name:
                        raise ValueError(f"Can't determine repo_name for {comp.github}")
                    # Create a Project instance from GitHub
                    github_comp = Project.from_github(repo_name, github_access)
                    # Merge PyPI data into the newly created GitHub project
                    github_comp.pypi = comp.pypi
                    github_comp.pypi_description = comp.pypi_description
                    github_comp.version = comp.version
                    self.projects.append(github_comp)
                else:
                    # PyPI project without a GitHub URL
                    self.projects.append(comp)
        # sort projects by name
        self.projects = sorted(
            self.projects, key=lambda comp: comp.name.lower() if comp.name else ""
        )
        self.last_update_time = datetime.now()

    def extract_repo_name_from_url(self, url: str) -> str:
        """
        Extract the repository name in 'user/repo' format from a GitHub URL.

        Args:
            url (str): The GitHub URL.

        Returns:
            str: The repository name or None if not extractable.
        """
        # Assuming the URL format is https://github.com/user/repo
        parts = url.split("/")
        if len(parts) > 4 and parts[2] == "github.com":
            return "/".join(parts[3:5])
        return None


class PyPi:
    """
    Wrapper class for interacting with PyPI, including search functionality.
    """

    def __init__(self, debug: bool = False):
        self.base_url = "https://pypi.org/pypi"
        self.debug = debug

    def search_projects(self, term: str, limit: int = None) -> List[Project]:
        """
        Search for packages on PyPI and return them as Project instances.

        Args:
            term (str): The search term.
            limit (int, optional): Maximum number of results to return.

        Returns:
            List[Project]: A list of Project instances representing the search results.
        """
        package_dicts = self.search_packages(term, limit)
        return [Project.from_pypi(pkg) for pkg in package_dicts]

    def get_package_info(self, package_name: str) -> dict:
        """
        Get detailed information about a package from PyPI using urllib.

        Args:
            package_name (str): The name of the package to retrieve information for.

        Returns:
            dict: A dictionary containing package information.

        Raises:
            urllib.error.URLError: If there is an issue with the URL.
            ValueError: If the response status code is not 200.
        """
        url = f"{self.base_url}/{package_name}/json"

        response = request.urlopen(url)

        if response.getcode() != 200:
            raise ValueError(
                f"Failed to fetch package info for {package_name}. Status code: {response.getcode()}"
            )

        package_data = json.loads(response.read())

        return package_data

    def search_packages(self, term: str, limit: int = None) -> list:
        """Search a package in the pypi repositories and retrieve detailed package information.

        Args:
            term (str): The search term.
            limit (int, optional): Maximum number of results to return.

        Returns:
            List[Dict]: A list of dictionaries containing detailed package information.

                see https://raw.githubusercontent.com/shubhodeep9/pipsearch/master/pipsearch/api.py
        """
        # Constructing a search URL and sending the request
        url = "https://pypi.org/search/?q=" + term
        try:
            response = request.urlopen(url)
            text = response.read()
        except Exception as e:
            raise e

        soup = BeautifulSoup(text, "html.parser")
        packagestable = soup.find("ul", {"class": "unstyled"})

        # If no package exists then there is no table displayed hence soup.table will be None
        if packagestable is None:
            return []

        if not isinstance(packagestable, Tag):
            return []

        packagerows: ResultSet[Tag] = packagestable.findAll("li")

        # Constructing the result list
        packages = []
        if self.debug:
            print(f"found len{packagerows} package rows")
        for package in packagerows[:limit]:
            nameSelector = package.find("span", {"class": "package-snippet__name"})
            if nameSelector is None:
                continue
            name = nameSelector.text

            link = ""
            if package.a is not None:
                href = package.a["href"]
                if isinstance(href, list):
                    href = href[0]
                link = "https://pypi.org" + href

            description = (
                package.find("p", {"class": "package-snippet__description"}) or Tag()
            ).text

            version = (
                package.find("span", {"class": "package-snippet__version"}) or Tag()
            ).text
            package_info = self.get_package_info(name)
            package_info["package_url"] = link
            packages.append(package_info)

        # returning the result list back
        return packages
