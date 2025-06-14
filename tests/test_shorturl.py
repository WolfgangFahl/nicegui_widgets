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
        """
        Create a temporary directory and initialize a ShortUrl instance with safety constraints.
        """
        super().setUp(debug=debug, profile=profile)
        self.temp_dir = Path(tempfile.mkdtemp())
        self.su = ShortUrl(
            base_path=self.temp_dir,
            suffix=".scad",
            length=8,
            max_size=1024,
            required_keywords=["cube", "translate"],
            blacklist=["system(", "#include", "evil"],
            lenient=False
        )
        if self.debug:
            print(f"📁 Test directory: {self.temp_dir}")

    def test_save_and_load_valid_code(self):
        """
        Code with required keywords should be saved and correctly reloaded.
        """
        code = "translate([0,0,0]) cube([1,2,3]);"
        short_id = self.su.save(code)
        if self.debug:
            print(f"✅ short id: {short_id} created for: {code}")
            print(f"📄 stored at: {self.su.path_for_id(short_id)}")
        self.assertTrue(self.su.file_exists(short_id))
        loaded = self.su.load(short_id)
        self.assertEqual(code, loaded)

    def test_reject_blacklisted_code(self):
        """
        Code containing blacklisted terms should raise a validation error.
        """
        code = "cube([1,1,1]); // system('/bin/rm -rf /')"
        with self.assertRaises(ValueError) as cm:
            self.su.save(code)
        self.assertIn("blacklisted", str(cm.exception))

    def test_reject_missing_required_keyword(self):
        """
        Code missing required keywords should be rejected.
        """
        code = "sphere(5);"
        with self.assertRaises(ValueError) as cm:
            self.su.save(code)
        self.assertIn("required keywords", str(cm.exception))

    def test_reject_too_large_code(self):
        """
        Excessively large code blocks should be rejected.
        """
        code = "translate([0,0,0]) cube([1,2,3]);" * 1000  # >1024 bytes
        with self.assertRaises(ValueError) as cm:
            self.su.save(code)
        self.assertIn("maximum allowed size", str(cm.exception))

    def test_short_id_is_deterministic(self):
        """
        The same code should always yield the same short ID.
        """
        code = "translate([0,0,0]) cube([1,2,3]);"
        id1 = self.su.short_id_from_code(code)
        id2 = self.su.short_id_from_code(code)
        if self.debug:
            print(f"🧪 deterministic test: {id1} == {id2} for: {code}")
        self.assertEqual(id1, id2)

    def test_file_does_not_exist_before_save(self):
        """
        A short ID should not point to an existing file before saving.
        """
        code = "translate([1,2,3]) cube([3,2,1]);"
        short_id = self.su.short_id_from_code(code)
        if self.debug:
            print(f"❌ file should not exist for id: {short_id}")
        self.assertFalse(self.su.file_exists(short_id))

    def test_load_nonexistent_file_raises(self):
        """
        Trying to load a non-existent short ID should raise FileNotFoundError.
        """
        short_id = "nonexistent"
        if self.debug:
            print(f"🚫 attempting to load missing ID: {short_id}")
        with self.assertRaises(FileNotFoundError):
            self.su.load(short_id)