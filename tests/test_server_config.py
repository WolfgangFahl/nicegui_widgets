"""
Created on 2024-01-23

@author: wf
"""

import os

import yaml

from ngwidgets.basetest import Basetest
from ngwidgets.webserver import WebserverConfig  # Import the correct class


class TestWebserverConfig(Basetest):
    """
    Test cases for the WebserverConfig class.
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)

    def test_webserver_config(self):
        """
        test the webserver configuration via a YAML file
        """
        test_secret = "test_secret"
        config_path = "/tmp/.solution/test_webserver-config"
        storage_path = f"{config_path}/storage"
        short_name = "test_config"
        yaml_path = f"{config_path}/{short_name}_config.yaml"
        os.makedirs(config_path, exist_ok=True)
        # Example configuration data
        config_data = {
            "short_name": short_name,
            "storage_secret": test_secret,
            "config_path": config_path,
        }
        with open(yaml_path, "w") as yaml_file:
            yaml.dump(config_data, yaml_file)
        # Create a config object with the temporary file's directory and basename
        config = WebserverConfig(
            short_name=short_name,
            config_path=config_path,
        )
        # Use the get method to load the configuration
        server_config = WebserverConfig.get(config)

        # Check if the configuration is loaded correctly
        self.assertEqual(server_config.storage_secret, test_secret)
        self.assertEqual(server_config.config_path, config_path)
        self.assertEqual(server_config.storage_path, storage_path)

    def test_webserver_config_default(self):
        """
        Test the WebserverConfig with default YAML path.
        This will create a real file in the user's home directory. Use with caution.
        """
        # Create a default config object with minimal setup
        config = WebserverConfig(
            short_name="test_default",  # Ensure this is unique to avoid conflicts with real configs
        )
        # Clean up: Remove the existing
        # configuration file that might be left over from a  previous test
        yaml_path = f"{config.config_path}/{config.short_name}_config.yaml"
        if os.path.exists(yaml_path):
            os.remove(yaml_path)
        server_config = WebserverConfig.get(config)
        if self.debug:
            print(server_config.to_yaml())
        # Add assertions to verify the default configuration is as expected
        self.assertIsNotNone(server_config.storage_secret)
        self.assertIsNotNone(server_config.storage_path)
        self.assertIsNotNone(server_config.config_path)
        self.assertTrue(os.path.exists(server_config.config_path))
        self.assertTrue(os.path.exists(server_config.storage_path))
        server_config2 = WebserverConfig.get(config)
        self.assertEqual(server_config, server_config2)
