"""
Created on 2023-08-15

@author: wf
"""

import argparse
import json
import os

import bcrypt


class Users:
    """
    A class to manage user credentials stored in a JSON file.

    Attributes:
        dir_path (str): The directory path where the JSON file resides.
        file_path (str): The full path to the JSON file.
    """

    def __init__(self, path_str: str):
        """
        Initialize the Users class and set file paths.
        """
        self.dir_path = os.path.expanduser(path_str)
        self.file_path = os.path.join(self.dir_path, "users.json")
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Create the directory if it doesn't exist."""
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def save_password_data(self, data):
        """
        Save user data to the JSON file.

        Args:
            data (dict): Dictionary containing username: password pairs.
        """
        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    def load_password_data(self):
        """
        Load user data from the JSON file.

        Returns:
            dict: Dictionary containing username: password pairs.
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                return json.load(file)
        return {}

    def add_user(self, username, password):
        """
        Add a new user with a hashed password to the data file.

        Args:
            username (str): The username of the new user.
            password (str): The password for the new user.
        """
        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        data = self.load_password_data()
        data[username] = hashed_password
        self.save_password_data(data)

    def check_password(self, username, password):
        """
        Validate a password against its hashed version.

        Args:
            username (str): The username of the user.
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        data = self.load_password_data()
        hashed_password = data.get(username)
        if not hashed_password:
            return False
        ok = bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        return ok


def main():
    parser = argparse.ArgumentParser(description="Manage user data.")
    parser.add_argument("-u", "--username", required=True, help="The username.")
    parser.add_argument("-p", "--password", required=True, help="The password.")
    parser.add_argument(
        "-c", "--project", required=True, help="The configuration name/project"
    )
    parser.add_argument(
        "-a",
        "--add",
        action="store_true",
        help="Add a user. Otherwise, checks the password.",
    )
    args = parser.parse_args()

    user_manager = Users(f"~/.solutions/{args.project}/")

    if args.add:
        user_manager.add_user(args.username, args.password)
        print(f"User {args.username} added successfully!")
    else:
        if user_manager.check_password(args.username, args.password):
            print(f"Password for {args.username} is correct!")
        else:
            print(f"Password for {args.username} is incorrect!")


if __name__ == "__main__":
    main()
