"""Ensure local Cargo patches cannot disappear from the license inventory."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

script = Path(__file__).resolve().parents[1] / "Scripts" / "license_paths.py"
spec = importlib.util.spec_from_file_location("license_paths", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LicensePathTests(unittest.TestCase):
    def test_registry_and_local_packages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Rust/vendor/krilla").mkdir(parents=True)
            self.assertIsNone(module.inventory_source(root, {"source": None, "manifest_path": str(root / "Rust/Cargo.toml")}))
            self.assertEqual(module.inventory_source(root, {"source": None, "manifest_path": str(root / "Rust/vendor/krilla/Cargo.toml")}), "path:Rust/vendor/krilla")
            self.assertEqual(module.inventory_source(root, {"source": "registry+example"}), "registry+example")
            with self.assertRaises(ValueError):
                module.inventory_source(root, {"source": None, "manifest_path": str(root / "other/Cargo.toml")})

    def test_vendor_root_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Rust").mkdir()
            (root / "other/krilla").mkdir(parents=True)
            (root / "Rust/vendor").symlink_to(root / "other", target_is_directory=True)
            with self.assertRaises(ValueError):
                module.inventory_source(root, {"source": None, "manifest_path": str(root / "Rust/vendor/krilla/Cargo.toml")})


if __name__ == "__main__":
    unittest.main()
