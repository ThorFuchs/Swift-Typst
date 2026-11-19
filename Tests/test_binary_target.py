"""Verify release-manifest changes without publishing or downloading an asset."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "Scripts/configure-binary-target.py"
URL = "https://github.com/example/typst/releases/download/bridge-1/CTypstBridge.zip"
CHECKSUM = "a" * 64


class BinaryTargetTests(unittest.TestCase):
    def run_config(self, manifest, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(manifest), *args],
                              capture_output=True, text=True)

    def test_remote_and_local_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "Package.swift"
            original = (ROOT / "Package.swift").read_text()
            manifest.write_text(original)
            local = self.run_config(manifest, "--local")
            self.assertEqual(local.returncode, 0, local.stderr)
            local_source = manifest.read_text()
            remote = self.run_config(manifest, "--remote-url", URL, "--checksum", CHECKSUM)
            self.assertEqual(remote.returncode, 0, remote.stderr)
            self.assertIn(f'url: "{URL}", checksum: "{CHECKSUM}"', manifest.read_text())
            local = self.run_config(manifest, "--local")
            self.assertEqual(local.returncode, 0, local.stderr)
            self.assertEqual(manifest.read_text(), local_source)

    def test_rejects_unsafe_inputs_without_changing_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "Package.swift"
            original = (ROOT / "Package.swift").read_text()
            manifest.write_text(original)
            for url, checksum in (("http://example.com/a.zip", CHECKSUM),
                                  ("https://user@example.com/a.zip", CHECKSUM),
                                  ("https://example.com/a.zip?token=secret", CHECKSUM),
                                  ("https://example.com/a.zip", "bad"),
                                  ('https://example.com/"a.zip', CHECKSUM)):
                with self.subTest(url=url, checksum=checksum):
                    result = self.run_config(manifest, "--remote-url", url, "--checksum", checksum)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(manifest.read_text(), original)

    def test_rejects_an_ambiguous_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "Package.swift"
            source = (ROOT / "Package.swift").read_text()
            duplicate = source + "\n" + source
            manifest.write_text(duplicate)
            result = self.run_config(manifest, "--local")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(manifest.read_text(), duplicate)


if __name__ == "__main__":
    unittest.main()
