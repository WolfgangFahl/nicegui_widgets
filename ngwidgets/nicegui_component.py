"""
Created on 2023-14-12

@author: wf
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup, Tag, ResultSet

@dataclass
class Component:
    name: str = None
    package: str = None
    demo: str = None
    forum_post: str = None
    github: str = None
    pypi: str = None
    image_url: str = None
    stars: int = None
    github_description: str = None
    pypi_description: str = None
    avatar: str = None
    search_text: str = None
    github_author: str = None
    pypi_author: str = None
    created_at: datetime = None
    downloads: int = None
    categories: List[str] = None


class PyPi:
    """
    Wrapper class for interacting with PyPI, including search functionality.
    """

    def __init__(self,debug:bool=False):
        self.base_url = "https://pypi.org/pypi"
        self.debug=debug
        
    def get_package_info(self, package_name: str) -> dict:
        response = requests.get(f"{self.base_url}/{package_name}/json")
        package_data={}
        if response.status_code == 200:
            package_data=response.json()
        return package_data


    def search_packages(self, term: str, limit: int = None) -> list:
        """Search a package in the pypi repositories
    
        `Arguments:`
    
        **term** -- the term to search in the pypi repositories
    
        **limit** -- the maximum amount of results to find
        """

        # Constructing a search URL and sending the request
        url = "https://pypi.org/search/?q=" + term
        req = requests.get(url)
    
        soup = BeautifulSoup(req.text, 'html.parser')
        packagestable = soup.find('ul', {'class': 'unstyled'})
    
        # If no package exists then there is no table displayed hence soup.table will be None
        if packagestable is None:
            return []
    
        if not isinstance(packagestable, Tag):
            return []
    
        packagerows: ResultSet[Tag] = packagestable.findAll('li')
    
        # Constructing the result list
        packages = []
        if self.debug:
            print(f"found len{packagerows} package rows")
        for package in packagerows[:limit]:
            nameSelector = package.find('span', {'class': 'package-snippet__name'})
            if nameSelector is None:
                continue
            name = nameSelector.text
    
            link = ""
            if package.a is not None:
                href = package.a['href']
                if isinstance(href, list):
                    href = href[0]
                link = "https://pypi.org" + href
            
            packagedata = {
                'name': name,
                'link': link,
                'description': (package.find('p', {'class': 'package-snippet__description'}) or Tag()).text,
                'version': (package.find('span', {'class': 'package-snippet__version'}) or Tag()).text,
                'install_instruction': '$ pip install ' + name
            }
            packages.append(packagedata)
    
        # returning the result list back
        return packages

