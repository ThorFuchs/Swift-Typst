"""A missing or malformed review must never pass the license gate."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

script = Path(__file__).resolve().parents[1] / "Scripts" / "check-license-readiness.py"
spec = importlib.util.spec_from_file_location("license_gate", script)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class LicenseGateTests(unittest.TestCase):
    def test_missing_or_invalid_findings_are_rejected(self):
        for inventory in (None, {}, {"unresolved": None}, {"unresolved": ""},
                          {"unresolved": [""]}, {"unresolved": ["  "]},
                          {"unresolved": [123]}):
            with self.subTest(inventory=inventory), self.assertRaises(ValueError):
                gate.unresolved_findings(inventory)

    def test_findings_are_explicit(self):
        self.assertEqual(gate.unresolved_findings({"unresolved": ["review required"]}), ["review required"])
        self.assertEqual(gate.unresolved_findings({"unresolved": []}), [])

    def test_gate_process_fails_closed_for_missing_or_malformed_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Scripts").mkdir()
            (root / "Notices" / "Rust").mkdir(parents=True)
            copy = root / "Scripts" / script.name
            shutil.copyfile(script, copy)
            inventory = root / "Notices" / "Rust" / "inventory.json"

            def run():
                return subprocess.run([sys.executable, str(copy)], text=True, capture_output=True)

            self.assertNotEqual(run().returncode, 0)
            for raw in ("{", "{}", '{"unresolved": null}'):
                inventory.write_text(raw)
                result = run()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("blocked", result.stdout)
            inventory.write_text(json.dumps({"unresolved": ["review required"]}))
            self.assertNotEqual(run().returncode, 0)
            inventory.write_text(json.dumps({"unresolved": []}))
            self.assertEqual(run().returncode, 0)


if __name__ == "__main__":
    unittest.main()
