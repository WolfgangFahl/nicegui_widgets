"""
Created on 2023-16-12

@author: wf
"""
import urllib.request
import yaml
from typing import Type, TypeVar, Generic

T = TypeVar('T')

class YamlAble(Generic[T]):
    """
    handle YAML load from url and file and store to file
    """
    @classmethod
    def load_from_file(cls: Type[T], filename: str) -> T:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
        return cls.from_dict(data)

    @classmethod
    def load_from_url(cls: Type[T], url: str) -> T:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = yaml.safe_load(response)
            else:
                raise Exception(f"Unable to load data from URL: {url}")
        return cls.from_dict(data)

    def save_to_file(self, filename: str):
        with open(filename, 'w') as file:
            yaml.dump(self.to_dict(), file)

    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        raise NotImplementedError

    def to_dict(self) -> dict:
        raise NotImplementedError