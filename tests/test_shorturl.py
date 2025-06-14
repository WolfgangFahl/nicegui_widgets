"""
Created on 2025-06-14

@author: wf
"""

import tempfile
from pathlib import Path
from ngwidgets.basetest import Basetest
from ngwidgets.short_url import ShortUrl

class TestShortUrl(Basetest):
    """
    Unit tests for the ShortUrl class.
    """

    def setUp(self, debug=True, profile=True):
        super().setUp(debug=debug, profile=profile)
        self.temp_dir = Path(tempfile.mkdtemp())
        self.su = ShortUrl(base_path=self.temp_dir, suffix=".txt", length=8)

    def test_save_and_load(self):
        """
        Verify saving and loading code via ShortUrl works as expected.
        """
        code = 'echo("Hello SCAD World");'
        short_id = self.su.save(code)
        path = self.su.path_for_id(short_id)
        if self.debug:
            print(f"short id: {short_id} created for {code}")
            print(f"saved at: {path}")
        self.assertTrue(path.exists())
        loaded_code = self.su.load(short_id)
        self.assertEqual(code, loaded_code)

