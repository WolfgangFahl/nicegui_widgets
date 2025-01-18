"""
pytest configuration

WF 2024-09-11
"""

import shutup

shutup.please()
import pytest
from selenium import webdriver

pytest_plugins = ["nicegui.testing.plugin"]


@pytest.fixture
def chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    return options
