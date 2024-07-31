"""
Created on 2022-11-27

@author: wf
"""

import os
import platform
import subprocess
import tempfile
from pathlib import Path
from urllib.request import urlopen

from bs4 import BeautifulSoup


class Editor:
    """
    helper class to open the system defined editor

    see https://stackoverflow.com/questions/1442841/lauch-default-editor-like-webbrowser-module
    """

    @classmethod
    def open_filepath(cls, filepath: str):
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", filepath))
        elif platform.system() == "Windows":  # Windows
            os.startfile(filepath, "open")
        else:  # linux variants
            subprocess.call(("xdg-open", filepath))

    @classmethod
    def extract_text(cls, html_text: str) -> str:
        """
        extract the text from the given html_text

        Args:
            html_text(str): the input for the html text

        Returns:
            str: the plain text
        """
        soup = BeautifulSoup(html_text, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text

    @classmethod
    def open(
        cls,
        file_source: str,
        extract_text: bool = True,
        default_editor_cmd: str = "/usr/local/bin/atom",
    ) -> str:
        """
        open an editor for the given file_source

        Args:
            file_source(str): the path to the file
            extract_text(bool): if True extract the text from html sources

        Returns:
            str: the path to the file e.g. a temporary file if the file_source points to an url
        """
        # handle urls
        # https://stackoverflow.com/a/45886824/1497139
        if file_source.startswith("http"):
            url_source = urlopen(file_source)
            # https://stackoverflow.com/a/19156107/1497139
            charset = url_source.headers.get_content_charset()
            # if charset fails here you might want to set it to utf-8 as a default!
            text = url_source.read().decode(charset)
            if extract_text:
                # https://stackoverflow.com/a/24618186/1497139
                text = cls.extract_text(text)

            return cls.open_tmp_text(text)

        editor_cmd = None
        editor_env = os.getenv("EDITOR")
        if editor_env:
            editor_cmd = editor_env
        if platform.system() == "Darwin":
            if not editor_env:
                # https://stackoverflow.com/questions/22390709/how-can-i-open-the-atom-editor-from-the-command-line-in-os-x
                editor_cmd = default_editor_cmd
        if editor_cmd:
            os_cmd = f"{editor_cmd} {file_source}"
            os.system(os_cmd)
        return file_source

    @classmethod
    def open_tmp_text(cls, text: str, file_name: str = None) -> str:
        """
        open an editor for the given text in a newly created temporary file

        Args:
            text(str): the text to write to a temporary file and then open
            file_name(str): the name to use for the file

        Returns:
            str: the path to the temp file
        """
        # see https://stackoverflow.com/a/8577226/1497139
        # https://stackoverflow.com/a/3924253/1497139
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with open(tmp.name, "w") as tmp_file:
                tmp_file.write(text)
                tmp_file.close()
            if file_name is None:
                file_path = tmp.name
            else:
                # https://stackoverflow.com/questions/3167154/how-to-split-a-dos-path-into-its-components-in-python
                path = Path(tmp.name)
                # https://stackoverflow.com/a/49798311/1497139
                file_path = path.parent / file_name
                os.rename(tmp.name, file_path)

            return cls.open(str(file_path))
