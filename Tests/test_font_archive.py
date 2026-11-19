"""Check archive byte guards without requiring Cargo or a network connection."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

script = Path(__file__).resolve().parents[1] / "Scripts" / "font_archive.py"
spec = importlib.util.spec_from_file_location("font_archive", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FontArchiveTests(unittest.TestCase):
    def test_missing_included_and_present_excluded_font_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "bridge.a"
            excluded = {"old.otf": b"old-font-data-123"}
            included = {"new.otf": b"new-font-data-456"}
            archive.write_bytes(b"archive" + included["new.otf"])
            module.verify_font_bytes(archive, excluded, included)
            archive.write_bytes(b"archive" + included["new.otf"] + excluded["old.otf"])
            with self.assertRaisesRegex(ValueError, "Excluded font bytes found"):
                module.verify_font_bytes(archive, excluded, included)
            archive.write_bytes(b"archive without fonts")
            with self.assertRaisesRegex(ValueError, "Expected STIX font bytes not found"):
                module.verify_font_bytes(archive, excluded, included)


if __name__ == "__main__":
    unittest.main()
