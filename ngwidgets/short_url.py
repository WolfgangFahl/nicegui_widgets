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

    Includes validation features:
    - maximum file size (in bytes)
    - required keywords (must be present)
    - blacklist keywords (must not be present)
    """

    def __init__(self, base_path: Path, suffix: str = ".txt", length: int = 8,
                 max_size: int = 32 * 1024,
                 required_keywords=None,
                 blacklist=None):
        """
        Initialize the ShortUrl utility.

        Args:
            base_path (Path): Directory to store code files.
            suffix (str): File extension to use (e.g. ".scad").
            length (int): Length of the generated base36 short ID.
            max_size (int): Maximum size in bytes of allowed code.
            required_keywords (List[str]): Keywords that must appear in the code.
            blacklist (List[str]): Keywords that must not appear in the code.
        """
        self.base_path = base_path
        self.suffix = suffix
        self.length = length
        self.max_size = max_size
        self.required_keywords = required_keywords or []
        self.blacklist = blacklist or []
        self.base_path.mkdir(parents=True, exist_ok=True)

    def short_id_from_code(self, code: str) -> str:
        """
        Compute a base36-encoded short ID from the MD5 hash of the code.

        Args:
            code (str): The code string.

        Returns:
            str: base36 string of fixed length.
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
        """Get file path for the given code."""
        return self.base_path / f"{self.short_id_from_code(code)}{self.suffix}"

    def path_for_id(self, short_id: str) -> Path:
        """Get file path for a given short ID."""
        return self.base_path / f"{short_id}{self.suffix}"

    def file_exists(self, short_id: str) -> bool:
        """Check whether a file exists for the given short ID."""
        return self.path_for_id(short_id).exists()

    def validate_code(self, code: str):
        """
        Validates code against defined rules: size, blacklists, required keywords.

        Raises:
            ValueError: if the code violates any constraint.
        """
        if len(code.encode("utf-8")) > self.max_size:
            raise ValueError(f"Code exceeds maximum allowed size of {self.max_size} bytes")
        if self.blacklist and any(bad in code for bad in self.blacklist):
            raise ValueError("Code contains blacklisted content")
        if self.required_keywords and not any(req in code for req in self.required_keywords):
            raise ValueError("Code does not contain required keywords")

    def save(self, code: str) -> str:
        """
        Save the code to a file named after its short ID.

        Args:
            code (str): The code content to save.

        Returns:
            str: The short ID.
        """
        self.validate_code(code)
        path = self.path_for_code(code)
        short_id = path.stem
        if not path.exists():
            path.write_text(code, encoding="utf-8")
        return short_id

    def load(self, short_id: str) -> str:
        """
        Load code content by its short ID.

        Args:
            short_id (str): The short ID.

        Returns:
            str: Loaded code content.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = self.path_for_id(short_id)
        if not path.exists():
            raise FileNotFoundError(f"No code found for ID {short_id}")
        return path.read_text(encoding="utf-8")
