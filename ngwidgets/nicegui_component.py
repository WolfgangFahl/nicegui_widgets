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

from bs4 import BeautifulSoup, ResultSet, Tag


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
        return f"$ pip install {self.package}"


class PyPi:
    """
    Wrapper class for interacting with PyPI, including search functionality.
    """

    def __init__(self, debug: bool = False):
        self.base_url = "https://pypi.org/pypi"
        self.debug = debug

    def as_component(self, package_info: Dict) -> Component:
        """
        Convert a package dictionary to a Component instance.

        Args:
            package_info (Dict): Dictionary containing package data from PyPI.

        Returns:
            Component: An instance of the Component class populated with package data.
        """
        info = package_info.get('info', {})
        component = Component(
            name=info.get('name'),
            package=info.get('name'),
            pypi=package_info.get('package_url'),
            pypi_description=info.get('summary'),
            version=info.get('version'),
            github_description=info.get('description')
        )
        return component

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
        return [self.as_component(pkg) for pkg in package_dicts]


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
            
            # Creating the packagedata dictionary
            packagedata = {
                "name": name,
                "package_url": link,
                "description": description,
                "version": version
            }
            packages.append(packagedata)

        # returning the result list back
        return packages
