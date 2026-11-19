"""Fast integrity checks for the artifact assembly/packaging scripts."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "CTypstBridge.artifactbundle/"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fixture(path, triple, payload=b"example static archive", *, corrupt=False, root=ROOT):
    relative = f"lib/{triple}/libswift_typst_bridge.a"
    variant = {"path": relative, "supportedTriples": [triple], "staticLibraryMetadata": {
        "headerPaths": ["include"], "moduleMapPath": "include/module.modulemap"}}
    info = {"schemaVersion": "1.0", "artifacts": {"CTypstBridge": {
        "type": "staticLibrary", "version": "0.1.0", "variants": [variant]}}}
    paths = [root / "LICENSE", root / "Rust/Cargo.toml", root / "Rust/Cargo.lock"]
    paths += sorted((root / "Rust/src").rglob("*.rs"))
    paths += sorted((root / "Rust/fonts").rglob("*"))
    paths += sorted((root / "Rust/vendor").rglob("*"))
    paths += sorted((root / "Sources/CTypstBridge/include").iterdir())
    paths += sorted((root / "Notices").rglob("*"))
    sources = {str(p.relative_to(root)): sha(p.read_bytes()) for p in paths if p.is_file()}
    record = {"typst": "0.15.1", "rustTarget": triple, "rustVersion": "rustc 1.94.1 fixture",
              "profile": "release", "sources": sources, "cargoLockSHA256": sources["Rust/Cargo.lock"],
              "archiveSHA256": sha(b"wrong" if corrupt else payload)}
    files = {"info.json": json.dumps(info).encode(), "provenance.json": json.dumps({triple: record}).encode(),
             relative: payload,
             "include/module.modulemap": (root / "Sources/CTypstBridge/include/module.modulemap").read_bytes(),
             "include/typst_bridge.h": (root / "Sources/CTypstBridge/include/typst_bridge.h").read_bytes(),
             "LICENSE": (root / "LICENSE").read_bytes(),
             "typst-assets-NOTICE.txt": (root / "Notices/typst-assets-0.15.1-NOTICE.txt").read_bytes()}
    files.update({"notices/" + str(p.relative_to(root / "Notices")): p.read_bytes()
                  for p in (root / "Notices").rglob("*") if p.is_file()})
    with zipfile.ZipFile(path, "w") as output:
        for name, data in files.items():
            output.writestr(PREFIX + name, data)


class ArtifactPipelineTests(unittest.TestCase):
    def run_script(self, name, *args, check=True):
        return subprocess.run([sys.executable, str(ROOT / "Scripts" / name), *map(str, args)],
                              check=check, capture_output=True, text=True)

    def test_merge_validate_and_package_deterministically(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            a, b = temp / "a.zip", temp / "b.zip"
            fixture(a, "first-target")
            fixture(b, "second-target", b"other archive")
            bundle = temp / "CTypstBridge.artifactbundle"
            self.run_script("merge-artifacts.py", bundle, a, b)
            out1, out2 = temp / "out1.zip", temp / "out2.zip"
            for out in (out1, out2):
                self.run_script("package-artifact.py", out, "--bundle", bundle,
                                "--require", "first-target", "--require", "second-target")
            self.assertEqual(out1.read_bytes(), out2.read_bytes())
            source_path = "notices/Source/krilla/krilla-0.8.2.crate"
            with zipfile.ZipFile(out1) as archive:
                self.assertEqual(archive.read(PREFIX + source_path),
                                 (ROOT / "Notices/Source/krilla/krilla-0.8.2.crate").read_bytes())
                self.assertIn(PREFIX + "notices/Source/krilla/README.md", archive.namelist())
                self.assertIn(PREFIX + "notices/Upstream/krilla/NOTICE.md", archive.namelist())
            failed = self.run_script("package-artifact.py", temp / "missing.zip", "--bundle", bundle,
                                     "--require", "missing-target", check=False)
            self.assertNotEqual(failed.returncode, 0)
            (bundle / "notices" / "README.md").write_text("modified notice")
            failed = self.run_script("package-artifact.py", temp / "modified.zip", "--bundle", bundle, check=False)
            self.assertNotEqual(failed.returncode, 0)

    def test_packaging_rejects_missing_krilla_source_in_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            variant = temp / "variant.zip"
            fixture(variant, "first-target")
            bundle = temp / "CTypstBridge.artifactbundle"
            self.run_script("merge-artifacts.py", bundle, variant)
            (bundle / "notices/Source/krilla/krilla-0.8.2.crate").unlink()
            result = self.run_script("package-artifact.py", temp / "missing-source.zip", "--bundle", bundle, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Bundled license evidence is missing", result.stderr + result.stdout)

    def test_merge_rejects_corrupt_and_duplicate_variants(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            bad, good = temp / "bad.zip", temp / "good.zip"
            fixture(bad, "first-target", corrupt=True)
            fixture(good, "first-target")
            result = self.run_script("merge-artifacts.py", temp / "bad" / "CTypstBridge.artifactbundle", bad, check=False)
            self.assertNotEqual(result.returncode, 0)
            result = self.run_script("merge-artifacts.py", temp / "duplicate" / "CTypstBridge.artifactbundle", good, good, check=False)
            self.assertNotEqual(result.returncode, 0)

    def test_packaging_rejects_changed_vendored_source(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            root = temp / "repository"
            root.mkdir()
            for directory in ("Rust", "Sources", "Notices", "Scripts"):
                shutil.copytree(ROOT / directory, root / directory, ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy2(ROOT / "LICENSE", root / "LICENSE")
            vendor = root / "Rust/vendor/krilla/src/content.rs"
            vendor.parent.mkdir(parents=True)
            vendor.write_text("original vendored source")
            archive = temp / "static.a"
            archive.write_bytes(b"example static archive")
            assemble = root / "Scripts/assemble-artifact.py"
            built = subprocess.run([sys.executable, str(assemble), "first-target", str(archive),
                                    "--rust-target", "first-target", "--rust-version", "fixture",
                                    "--profile", "release"], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            bundle = root / "Artifacts/CTypstBridge.artifactbundle"
            provenance = json.loads((bundle / "provenance.json").read_text())
            sources = provenance["first-target"]["sources"]
            self.assertEqual(sources["Rust/vendor/krilla/src/content.rs"], sha(vendor.read_bytes()))
            package = root / "Scripts/package-artifact.py"
            before = subprocess.run([sys.executable, str(package), str(temp / "before.zip"),
                                     "--bundle", str(bundle)], capture_output=True, text=True)
            self.assertEqual(before.returncode, 0, before.stdout + before.stderr)
            vendor.write_text("changed vendored source")
            after = subprocess.run([sys.executable, str(package), str(temp / "after.zip"),
                                    "--bundle", str(bundle)], capture_output=True, text=True)
            self.assertNotEqual(after.returncode, 0)
            self.assertIn("Sources or lockfile changed", after.stderr + after.stdout)
            vendor.write_text("original vendored source")
            (vendor.parent / "alias.rs").symlink_to(vendor)
            linked = subprocess.run([sys.executable, str(package), str(temp / "linked.zip"),
                                     "--bundle", str(bundle)], capture_output=True, text=True)
            self.assertNotEqual(linked.returncode, 0)
            self.assertIn("Symlinks are not allowed", linked.stderr + linked.stdout)
            linked_assemble = subprocess.run([sys.executable, str(assemble), "first-target", str(archive),
                                             "--rust-target", "first-target", "--rust-version", "fixture",
                                             "--profile", "release"], capture_output=True, text=True)
            self.assertNotEqual(linked_assemble.returncode, 0)
            self.assertIn("Symlinks are not allowed", linked_assemble.stderr + linked_assemble.stdout)

            (vendor.parent / "alias.rs").unlink()
            source = root / "Notices/Source/krilla/krilla-0.8.2.crate"
            source.write_bytes(b"incorrect crate")
            for script, arguments in ((assemble, ["second-target", str(archive), "--rust-target", "second-target",
                                                   "--rust-version", "fixture", "--profile", "release"]),
                                      (package, [str(temp / "bad-source.zip"), "--bundle", str(bundle)])):
                result = subprocess.run([sys.executable, str(script), *arguments], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("krilla source archive checksum mismatch", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
