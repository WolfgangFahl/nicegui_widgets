"""
Created on 2023-14-12

This module, developed as part of the ngwidgets package under the instruction of WF, provides 
classes and methods for interacting with the Python Package Index (PyPI). It includes the 
`Component` data class for representing software components and the `PyPi` class for searching 
and retrieving package information from PyPI. The code facilitates the creation of tools and 
applications that interact with PyPI for information about Python packages.

Prompts for LLM: 
- Create a Python class for interacting with PyPI, including search functionality.
- Develop a data class in Python to represent a software component with various attributes.
- Implement a method to search PyPI for packages and retrieve detailed package information.

Main author: OpenAI's language model (instructed by WF)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json
from urllib import request, error
from github import Github, Repository
from bs4 import BeautifulSoup, ResultSet, Tag
import os
from pathlib import Path

class GitHubAccess:
    def __init__(self, access_token=None):
        """
        Initialize the GitHub instance.
        If access_token is provided, use it for authenticated access.
        Otherwise, access is unauthenticated with lower rate limits.
        """
        self.github = Github(access_token) if access_token else Github()

    def search_repositories_by_topic(self, topic):
        """
        Search for repositories with a given topic.
        Returns a list of repository names.
        """
        query = f"topic:{topic}"
        repositories = self.github.search_repositories(query)
        return [repo.full_name for repo in repositories]
    
@dataclass
class Component:
    """
    A data class representing a software component, potentially from PyPI or GitHub.

    Attributes:
        name (str): The name of the component.
        package (str): The package name on PyPI.
        demo (str): A URL to a demo of the component, if available.
        forum_post (str): A URL to a forum post discussing the component.
        github (str): A URL to the GitHub repository of the component.
        pypi (str): A URL to the PyPI page of the component.
        image_url (str): A URL to an image representing the component.
        stars (int): Number of stars on GitHub.
        github_description (str): Description of the component from GitHub.
        pypi_description (str): Description of the component from PyPI.
        avatar (str): A URL to the avatar image of the author/maintainer.
        search_text (str): Text used for searching the component.
        github_author (str): The GitHub username of the component's author.
        pypi_author (str): The PyPI username of the component's author.
        created_at (datetime): The date when the component was created.
        downloads (int): Number of downloads from PyPI.
        categories (List[str]): Categories associated with the component.
        version (str): The current version of the component on PyPI.
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
    
    @property
    def install_instructions(self) -> str:
        """
        Get the installation instructions for the component.

        Returns:
            str: Installation instructions for the component.
        """
        return f"pip install {self.package}"
    
    @classmethod
    def from_github(cls, repo_name: str, github_access: GitHubAccess) -> 'Component':
        """
        Class method to create a Component instance from a GitHub repository.

        Args:
            repo_name (str): The name of the GitHub repository (e.g., 'user/repo').
            github_access (GitHubAccess): Instance of GitHubAccess for API calls.

        Returns:
            Component: An instance of the Component class filled with GitHub repository details.
        """
        repo: Repository.Repository = github_access.github.get_repo(repo_name)
        
        return cls(
            name=repo.name,
            github=repo.html_url,
            stars=repo.stargazers_count,
            github_description=repo.description,
            github_author=repo.owner.login,
            created_at=repo.created_at,
            # Other fields can be filled in as needed
        )
        
    @classmethod
    def from_pypi(cls, package_info: Dict) -> 'Component':
        """
        Class method to create a Component instance from a PyPI package.

        Args:
            package_info (Dict): Dictionary containing package data from PyPI.

        Returns:
            Component: An instance of the Component class filled with PyPI package details.
        """
        info = package_info.get('info', {})
        github = None
        project_urls = info.get('project_urls', {})
        if project_urls:
            github_url = project_urls.get('Repository') or project_urls.get('Source')
            if github_url and "github" in github_url:
                github = github_url

        return cls(
            name=info.get('name'),
            package=info.get('name'),
            pypi=package_info.get('package_url'),
            pypi_description=info.get('summary'),
            version=info.get('version'),
            github_description=info.get('description'),
            github=github
        )

class Components:
    """
    handle a list of python components on a specific topic
    """
    def __init__(self, topic: str):
        """
        Constructor
        Args:
            topic (str): The topic of the components.
        """
        self._topic = topic
        self._default_directory = Path.home() / ".nicegui"
        self.components=[]

    @property
    def default_directory(self) -> Path:
        """
        The default directory for saving and loading components.
        Returns:
            Path: The default directory path.
        """
        return self._default_directory

    @default_directory.setter
    def default_directory(self, directory: str):
        """
        Set the default directory for saving and loading components.
        Args:
            directory (str): The path to the new default directory.
        """
        self._default_directory = Path(directory)

    @property
    def file_path(self) -> Path:
        """
        The file path for saving and loading components, based on the topic.
        Returns:
            Path: The file path.
        """
        filename = f"components_{self._topic}.json"
        return self._default_directory / filename

    def save(self, components: List[Component]=None, directory: str = None):
        """
        Save a list of Component instances to a JSON file.
        Args:
            components (List[Component]): A list of Component instances to be saved.
            directory (str, optional): The directory where the file will be saved. If None, uses the default directory.
        """
        if components is None:
            components=self.components
        directory = Path(directory or self.default_directory)
        os.makedirs(directory, exist_ok=True)

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump([component.__dict__ for component in components], file, indent=4, default=str)

    def load(self, directory: str = None, set_self:bool=True) -> List[Component]:
        """
        Load a list of Component instances from a JSON file.
        Args:
            directory (str, optional): The directory where the file is located. If None, uses the default directory.
            set_self(bool): if True set self.components with the result
        Returns:
            List[Component]: A list of Component instances loaded from the file.
            
        """
        directory = Path(directory or self.default_directory)

        if not self.file_path.exists():
            raise FileNotFoundError(f"No such file: {self.file_path}")

        with open(self.file_path, "r", encoding="utf-8") as file:
            components_records = json.load(file)
        
        components=[]
        for component_record in components_records:
            component=Component(**component_record)
            components.append(component)
        if set_self:
            self.components=components
        return components

    def update(self):
        """
        Update the list of components by retrieving potential components from PyPI and GitHub based on the topic.
        """
        pypi=PyPi()
        github_access=GitHubAccess()
     
        # Fetch components from PyPI
        pypi_components = pypi.search_components(self._topic)
        # Fetch repositories from GitHub
        github_repos = github_access.search_repositories_by_topic(self._topic)
        github_components = [Component.from_github(repo, github_access) for repo in github_repos]

        self.components=github_components
        # Create a dictionary to map GitHub URLs to components
        comp_by_github_url = {comp.github: comp for comp in github_components if comp.github}

        # Merge PyPI components into the GitHub components
        for comp in pypi_components:
            if comp.github in comp_by_github_url:
                # Merge PyPI data into existing GitHub component
                existing_comp = comp_by_github_url[comp.github]
                existing_comp.pypi = comp.pypi
                existing_comp.pypi_description = comp.pypi_description
                existing_comp.version = comp.version
            else:
                self.components.append(comp)
        # sort components by name
        self.components = sorted(self.components, key=lambda comp: comp.name.lower() if comp.name else "")

        
        
class PyPi:
    """
    Wrapper class for interacting with PyPI, including search functionality.
    """

    def __init__(self, debug: bool = False):
        self.base_url = "https://pypi.org/pypi"
        self.debug = debug

 

    def search_components(self, term: str, limit: int = None) -> List[Component]:
        """
        Search for packages on PyPI and return them as Component instances.

        Args:
            term (str): The search term.
            limit (int, optional): Maximum number of results to return.

        Returns:
            List[Component]: A list of Component instances representing the search results.
        """
        package_dicts = self.search_packages(term, limit)
        return [Component.from_pypi(pkg) for pkg in package_dicts]

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
            raise ValueError(f"Failed to fetch package info for {package_name}. Status code: {response.getcode()}")
        
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
            text=response.read()
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
                package.find("p", {"class": "package-snippet__description"})
                or Tag()
            ).text
            
            version = (
                package.find("span", {"class": "package-snippet__version"})
                or Tag()
            ).text
            package_info=self.get_package_info(name)
            package_info["package_url"]=link
            packages.append(package_info)

        # returning the result list back
        return packages

