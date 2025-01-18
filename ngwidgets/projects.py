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
import re
import time
import unicodedata
import urllib
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from bs4 import BeautifulSoup, ResultSet, Tag
from github import Github

from ngwidgets.components import Components
from ngwidgets.progress import Progressbar
from ngwidgets.yamlable import lod_storable


class GitHubAccess:
    """
    A class to handle GitHub API access.

    This class provides functionalities to access the GitHub API, either with authenticated or unauthenticated access.
    It can read a GitHub access token from a YAML file in a specified directory for authenticated access,
    which increases the rate limit for API requests. If no access token is provided or found in the YAML file,
    it defaults to unauthenticated access with lower rate limits.

    Attributes:
        github (Github): An instance of the Github class from the PyGithub library, configured for either authenticated or unauthenticated access.
    """

    def __init__(
        self, default_directory: str = None, access_token: Optional[str] = None
    ):
        """
        Initialize the GitHub instance.

        If an access_token is provided, use it for authenticated access to increase the rate limit.
        Otherwise, attempt to read the access token from a YAML file in the default directory.
        If no token is found, access is unauthenticated with lower rate limits.

        Args:
            default_directory (str): Path to the directory where the access token file is stored.
            access_token (Optional[str]): A GitHub personal access token. Defaults to None.
        """
        if not access_token and default_directory:
            access_token = self._read_access_token(default_directory)
        self.github = Github(access_token)

    def _read_access_token(self, default_directory: str) -> Optional[str]:
        """
        Read the GitHub access token from a YAML file located in the default directory.

        Args:
            default_directory (str): Path to the directory where the access token file is stored.

        Returns:
            Optional[str]: The access token if found, otherwise None.
        """
        token_file = Path(default_directory) / "github_access_token.yaml"
        if token_file.exists():
            with open(token_file, "r") as file:
                data = yaml.safe_load(file)
                return data.get("access_token", None)
        return None

    def search_repositories(self, query: str) -> dict:
        """
        Search for GitHub repositories matching a given query.

        Args:
            query (str): The search query string.

        Returns:
            dict: A dictionary of repository objects keyed by their full names.
        """
        repositories = self.github.search_repositories(query)
        repo_dict = {repo.full_name: repo for repo in repositories}
        return repo_dict


@lod_storable
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

    Solution bazaar attributes:
        component_url(str): the url of a yaml file with component declarations, demo, install and usage information
        solution_tags(str): a list of comma separated tags for checking the conformance of the project
        to the solution bazaar guidelines
    """

    name: Optional[str] = None
    package: Optional[str] = None
    demo: Optional[str] = None
    forum_post: Optional[str] = None
    github_owner: Optional[str] = None
    github_repo_name: Optional[str] = None
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
    # solution bazaar properties
    components_url: Optional[str] = None
    solution_tags: Optional[str] = ""
    solution_id: Optional[str] = None

    def __post_init__(self):
        if self.github_owner and self.github_repo_name:
            self.solution_id = self._generate_solution_id()

    def _generate_solution_id(self) -> str:
        owner = self.github_owner or ""
        repo_name = self.github_repo_name or ""
        base_id = f"{owner}_{repo_name}"
        base_id = base_id.replace("/", "_").replace(
            "\\", "_"
        )  # Replace slashes with underscores
        normalized_id = (
            unicodedata.normalize("NFKD", base_id)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        return re.sub(r"[^\w\s.-]", "", normalized_id)

    @property
    def component_count(self) -> int:
        """
        Counts the number of components associated with the project.
        Returns 0 if there are no components or if components_url is not set.
        """
        if not self.components_url:
            return 0
        components = self.get_components()
        return len(components.components) if components else 0

    @property
    def install_instructions(self) -> str:
        """
        Get the installation instructions for the project.

        Returns:
            str: Installation instructions for the project.
        """
        return f"pip install {self.package}"

    def get_components(
        self, cache_directory: str = None, cache_valid_secs: int = 3600
    ) -> Components:
        """
        method to lazy-loaded components. Loads components from URL if components_url is set.
        If a cache directory is provided, it caches the YAML file in that directory. The cache validity period
        can be specified in seconds.

        Args:
            cache_directory (str, optional): Directory for caching the YAML files. If None, caching is disabled.
            cache_valid_secs (int, optional): The number of seconds for which the cache is considered valid. Defaults to 3600 seconds (1 hour).

        Returns:
            Components: The components associated with the project.
        """
        if not self.components_url:
            return None

        # (slow) load from url is the default
        load_from_url = True

        # potentially we speed up by caching
        if cache_directory:
            cache_directory = Path(cache_directory) / "components"
            os.makedirs(cache_directory, exist_ok=True)
            filename = f"{self.solution_id}.yaml"
            file_path = cache_directory / filename

            if file_path.exists():
                file_size = file_path.stat().st_size
                if file_size > 0 and not self._is_file_outdated(
                    file_path, cache_valid_secs
                ):
                    load_from_url = False
                    components = Components.load_from_yaml_file(str(file_path))

        if load_from_url:
            components = Components.load_from_yaml_url(self.components_url)
            if cache_directory:
                components.save_to_yaml_file(str(file_path))

        return components

    def _is_file_outdated(self, file_path: Path, cache_valid_secs: int = 3600) -> bool:
        """
        Check if the file is outdated (older than 1 hour).
        """
        file_mod_time = file_path.stat().st_mtime
        return (time.time() - file_mod_time) > cache_valid_secs

    def merge_pypi(self, pypi):
        """
        merge the given pypi project info to with mine
        """
        self.pypi = pypi.pypi
        self.package = pypi.package
        self.pypi_description = pypi.pypi_description
        self.version = pypi.version

    @classmethod
    def get_raw_url(
        cls, owner: str, repo_name: str, branch_name: str, file_path: str
    ) -> str:
        """
        Construct the URL for the raw  file_path from the owner, repository name, and branch name.

        Args:
            owner (str): The owner of the GitHub repository.
            repo_name (str): The name of the GitHub repository.
            branch_name (str): The name of the branch.
            file_path(str): the file_path to get the raw content for

        Returns:
            str: The URL of the raw file_path if it exists

        """
        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch_name}{file_path}"
        try:
            # Attempt to open the raw URL
            with urllib.request.urlopen(raw_url) as response:
                # Check if the response status code is 200 (OK)
                if response.getcode() == 200:
                    return raw_url
        except urllib.error.URLError as ex:

            pass  # Handle any exceptions here
        return None  # Return None if .component.yaml doesn't exist

    @classmethod
    def from_github(cls, repo) -> "Project":
        """
        Class method to create a Project instance from a GitHub repository.

        Args:
            repo(Repository.Repository): The github repository
            github_access (GitHubAccess): Instance of GitHubAccess for API calls.

        Returns:
            Project: An instance of the Project class filled with GitHub repository details.
        """
        avatar_url = repo.owner.avatar_url if repo.owner.avatar_url else None
        stars = repo.stargazers_count
        owner = repo.owner.login
        repo_name = repo.name

        components_url = cls.get_raw_url(
            owner, repo_name, repo.default_branch, "/.components.yaml"
        )
        project = cls(
            name=repo.name,
            github=repo.html_url,
            github_repo_name=repo.name,
            github_owner=repo.owner.login,
            stars=stars,
            github_description=repo.description,
            github_author=repo.owner.login,
            created_at=repo.created_at,
            avatar=avatar_url,
            components_url=components_url,
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
            # Preferred keys for GitHub URLs
            preferred_keys = ["Repository", "Source", "Home"]
            github_base_url = "https://github.com/"

            # Iterate over the preferred keys and check if any URL starts with the GitHub base URL
            for key in preferred_keys:
                url = project_urls.get(key)
                if url and url.startswith(github_base_url):
                    github = url
                    break
            else:
                # If no GitHub URL is found, you may choose to handle this case (e.g., logging, fallback logic)
                github = None

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


@lod_storable
class Projects:
    """
    handle a list of python projects on a specific topic
    """

    topic: str
    _default_directory: Path = field(init=False)
    projects: List = field(default_factory=list, init=False)
    last_update_time: datetime = field(init=False)

    def __post_init__(self):
        """
        Post-initialization to set non-static attributes.
        """
        self._default_directory = Path.home() / ".nicegui"
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
        filename = f"components_{self.topic}.json"
        return self._default_directory / filename

    def get_project4_solution_id(self, solution_id: str) -> Project:
        """
        Get a project based on the provided solution_id.

        Args:
            solution_id (str): The solution_id to search for.

        Returns:
            Project: The Project instance matching the provided solution_id, or None if not found.
        """
        for project in self.projects:
            if project.solution_id == solution_id:
                return project
        return None

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

    def load(
        self, directory: str = None, set_self: bool = True, lenient: bool = True
    ) -> List[Project]:
        """
        Load a list of Project instances from a JSON file.
        Args:
            directory (str, optional): The directory where the file is located. If None, uses the default directory.
            set_self(bool): if True set self.projects with the result
            lenient(bool): if True allow that there is no projects json file
        Returns:
            List[Project]: A list of Project instances loaded from the file.

        """
        directory = Path(directory or self.default_directory)
        projects = []
        if not self.file_path.exists():
            if not lenient:
                raise FileNotFoundError(f"No such file: {self.file_path}")
        else:
            with open(self.file_path, "r", encoding="utf-8") as file:
                projects_records = json.load(file)

            for project_record in projects_records:
                project = Project(**project_record)
                projects.append(project)
        if set_self:
            self.projects = projects
        return projects

    def get_github_projects(
        self, repo_dict: dict, progress_bar=None
    ) -> Dict[str, Project]:
        """
        Get GitHub projects related to the specified topic.

        Args:
            github_access (GitHubAccess): An instance of GitHubAccess for API calls.

        Returns:
            Dict[str, Project]: A dictionary of GitHub projects with their URLs as keys and Project instances as values.
        """
        projects_by_url = {}
        for repo in repo_dict.values():
            if progress_bar:
                progress_bar.update(1)
            project = Project.from_github(repo)
            projects_by_url[repo.html_url] = project
        return projects_by_url

    def sort_projects(self, projects: List[Project], sort_key: str):
        """
        Sorts a list of projects based on the specified sort key, converting integers to fixed-length strings.

        Args:
            projects (list): List of Project instances.
            sort_key (str): Attribute name to sort the projects by.

        Returns:
            list: Sorted list of projects.
        """

        # Define the function to determine the sorting value
        def get_sort_value(proj):
            attr = getattr(proj, sort_key, None)

            # Handle None values; place them at the end of the sorted list
            if attr is None:
                return " "  # Assuming you want None values to appear last

            # Convert integers to zero-padded strings, and others to strings
            if isinstance(attr, int):
                return f"{attr:010d}"  # Zero-pad to 10 digits
            else:
                return str(attr).lower()

        # Determine if sorting should be in reverse
        reverse_sort = sort_key in ["stars", "downloads", "component_count"]

        return sorted(projects, key=get_sort_value, reverse=reverse_sort)

    def update(
        self,
        progress_bar: Optional[Progressbar] = None,
        limit_github: Optional[int] = None,
        limit_pypi: Optional[int] = None,
    ):
        """
        Update the list of projects by retrieving potential projects from PyPI and GitHub based on the topic.

        Args:
            progress_bar (Optional[Progressbar]): A progress bar instance to update during the process.
            limit_github (Optional[int]): If set, limit the maximum number of GitHub projects to retrieve.
            limit_pypi (Optional[int]): If set, limit the maximum number of PyPI projects to retrieve.
        """
        # Initialize progress bar if provided
        if progress_bar:
            cached_projects = self.load()
            progress_bar.total = len(cached_projects)
            progress_bar.reset()
            progress_bar.set_description("Updating projects")

        # pypi access
        pypi = PyPi()

        # Fetch projects from PyPI
        pypi_projects = pypi.search_projects(self.topic)
        # Apply limit to the PyPI projects
        if limit_pypi is not None:
            pypi_projects = pypi_projects[:limit_pypi]
        # Fetch repositories from GitHub
        github_access = GitHubAccess(self.default_directory)
        query = self.topic
        repo_dict = github_access.search_repositories(query)
        # Apply limit to the GitHub repositories
        if limit_github is not None:
            repo_dict = dict(list(repo_dict.items())[:limit_github])
        total = len(repo_dict) + len(pypi_projects)
        if progress_bar:
            progress_bar.total = total

        projects_by_github_url = self.get_github_projects(repo_dict, progress_bar)
        self.projects = list(projects_by_github_url.values())

        # Merge PyPI projects into the GitHub projects
        for pypi in pypi_projects:
            matched_project = None  # Reset for each PyPI project
            if pypi.github:
                for github_url in projects_by_github_url.keys():
                    if pypi.github.startswith(github_url):
                        matched_project = projects_by_github_url[github_url]
                if matched_project:
                    matched_project.merge_pypi(pypi)
                else:
                    # we have github url but it was not in our search list
                    # check the gitub repo for more details
                    repo_name = self.extract_repo_name_from_url(pypi.github)
                    if not repo_name:
                        raise ValueError(
                            f"Can't determine repo_name for {pypi.github} of pypi package {pypi.package}"
                        )
                    # Create a Project instance from GitHub
                    repo = github_access.github.get_repo(repo_name)
                    github_comp = Project.from_github(repo)
                    # Merge PyPI data into the newly created GitHub project
                    github_comp.merge_pypi(pypi)
                    self.projects.append(github_comp)
            else:
                # PyPI project without a GitHub URL
                self.projects.append(pypi)
            if progress_bar:
                progress_bar.update(1)
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
        self.cache_dir = Path.home() / ".pypi"
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "pypi-package-list.json"
        self.cache_ttl = 3600  # 1 hour

    def pypi_request(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Make pypi request with simple file caching."""
        data = None
        if self.cache_file.exists():
            file_age = time.time() - self.cache_file.stat().st_mtime
            if file_age < self.cache_ttl:
                try:
                    with open(self.cache_file) as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    pass

        if not data:
            data = self._make_request(url, headers)
            if data:
                with open(self.cache_file, "w") as f:
                    json.dump(data, f)

        return data

    def _make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to PyPI API and return JSON response."""
        try:
            request = urllib.request.Request(url, headers=headers if headers else {})
            response = urllib.request.urlopen(request)
            if response.getcode() == 200:
                json_response = json.loads(response.read())
                return json_response
        except (urllib.error.URLError, json.JSONDecodeError) as e:
            if self.debug:
                print(f"Error in request to {url}: {e}")
        return None

    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """Get detailed info for a specific package."""
        url = f"{self.base_url}/{package_name}/json"
        package_data = self._make_request(url)
        if package_data:
            package_data["package_url"] = f"https://pypi.org/project/{package_name}"
        return package_data

    def search_packages(self, term: str, limit: Optional[int] = None) -> List[Dict]:
        """Search packages using PyPI JSON API."""
        headers = {"Accept": "application/vnd.pypi.simple.v1+json"}
        url = "https://pypi.org/simple/"
        packages = []

        projects = self.pypi_request(url, headers)
        if projects:
            matched_projects = [
                p for p in projects["projects"] if term.lower() in p["name"].lower()
            ]
            if limit:
                matched_projects = matched_projects[:limit]

            for project in matched_projects:
                package_info = self.get_package_info(project["name"])
                if package_info:
                    packages.append(package_info)

        return packages

    def search_projects(self, term: str, limit: Optional[int] = None) -> List[Project]:
        """Get PyPI package info as Project instances."""
        package_dicts = self.search_packages(term, limit)
        projects = []
        for package in package_dicts:
            if package:
                project = Project.from_pypi(package)
                projects.append(project)
        return projects
