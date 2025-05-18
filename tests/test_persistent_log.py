"""
Created on 2024-10-04

@author: wf
"""

from ngwidgets.basetest import Basetest
from ngwidgets.persistent_log import Log


class TestPersistentLog(Basetest):
    """
    test the persistent log handling
    """

    def setUp(self, debug=True, profile=True):
        Basetest.setUp(self, debug=debug, profile=profile)
        self.log = Log()
        if debug:
            self.log.do_log = False
            self.log.do_print = True

    def test_positive_logging(self):
        """Test normal logging and level summary."""
        self.log.log("❌", "system", "An error occurred.")
        self.log.log("⚠️", "validation", "A warning message.")
        self.log.log("✅", "process", "Process completed successfully.")

        # Verify entries
        self.assertEqual(len(self.log.entries), 3)
        self.assertEqual(self.log.entries[0].msg, "❌:An error occurred.")
        self.assertEqual(self.log.entries[1].msg, "⚠️:A warning message.")
        self.assertEqual(self.log.entries[2].msg, "✅:Process completed successfully.")

        # Verify level counts
        count, summary = self.log.get_level_summary("error")
        self.assertEqual(count, 1)
        self.assertIn("system", summary)

        count, summary = self.log.get_level_summary("warn")
        self.assertEqual(count, 1)
        self.assertIn("validation", summary)

        count, summary = self.log.get_level_summary("info")
        self.assertEqual(count, 1)
        self.assertIn("process", summary)

        yaml_file = "/tmp/persistent_log_test.yaml"
        self.log.save_to_yaml_file(yaml_file)
        # Later or in another session
        loaded_log = Log.load_from_yaml_file(yaml_file)
        self.assertEqual(self.log, loaded_log)

    def test_robustness(self):
        """Test clearing logs and handling unsupported icons."""
        self.log.log("❌", "system", "First error.")
        self.log.log("⭐", "unknown", "Unknown log level.")  # Unsupported icon
        self.log.clear()

        # Verify entries are cleared
        self.assertEqual(len(self.log.entries), 0)

        # Verify level counts are reset
        count, summary = self.log.get_level_summary("error")
        self.assertEqual(count, 0)
        self.assertIn("No entries found", summary)
