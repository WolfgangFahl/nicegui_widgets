"""
Created on 2025-06-14

@author: wf
"""

import hashlib
from pathlib import Path

class ShortUrl:
    """
    A utility for mapping arbitrary code snippets to short base36 IDs,
    storing and retrieving them in a persistent directory.

    Designed for reuse across different code types (.scad, .py, .sql, etc.)
    with configurable file suffix and ID length.
    """

    def __init__(self, base_path: Path, suffix: str = ".txt", length: int = 8):
        """
        Initialize the ShortUrl utility.

        Args:
            base_path (Path): Directory to store code files.
            suffix (str): File extension to use (e.g. ".scad").
            length (int): Length of the generated base36 short ID.
        """
        self.base_path = base_path
        self.suffix = suffix
        self.length = length
        self.base_path.mkdir(parents=True, exist_ok=True)

    def short_id_from_code(self, code: str) -> str:
        """
        Generate a short base36 ID from the MD5 hash of the given code.

        Args:
            code (str): The code string.

        Returns:
            str: A base36-encoded ID of fixed length.
        """
        digest = hashlib.md5(code.encode("utf-8")).hexdigest()
        value = int(digest, 16)
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        result = ""
        while value > 0:
            value, rem = divmod(value, 36)
            result = chars[rem] + result
        return result.zfill(self.length)[-self.length:]

    def path_for_code(self, code: str) -> Path:
        """
        Get the file path for a given code string.

        Args:
            code (str): The code content.

        Returns:
            Path: The full path where the code would be saved.
        """
        return self.base_path / f"{self.short_id_from_code(code)}{self.suffix}"

    def path_for_id(self, short_id: str) -> Path:
        """
        Get the file path for a given short ID.

        Args:
            short_id (str): The short ID.

        Returns:
            Path: Full path to the file corresponding to the ID.
        """
        return self.base_path / f"{short_id}{self.suffix}"

    def file_exists(self, short_id: str) -> bool:
        """
        Check if a file exists for the given short ID.

        Args:
            short_id (str): The short ID.

        Returns:
            bool: True if the file exists.
        """
        return self.path_for_id(short_id).exists()

    def save(self, code: str) -> str:
        """
        Save the code to a file derived from its short ID.

        Args:
            code (str): Code to save.

        Returns:
            str: The short ID assigned to the saved file.
        """
        path = self.path_for_code(code)
        short_id = path.stem
        if not path.exists():
            path.write_text(code, encoding="utf-8")
        return short_id

    def load(self, short_id: str) -> str:
        """
        Load code content by its short ID.

        Args:
            short_id (str): The ID of the code file.

        Returns:
            str: Code content.

        Raises:
            FileNotFoundError: If no file with this ID exists.
        """
        path = self.path_for_id(short_id)
        if not path.exists():
            raise FileNotFoundError(f"No code found for ID {short_id}")
        return path.read_text(encoding="utf-8")
