"""Risk acceptance is scoped to the exact source and archive, not an empty finding list."""
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "Scripts"))
import public_release_check as gate


class PublicReleaseGateTests(unittest.TestCase):
    def test_stream_checks_across_chunk_boundaries(self):
        with self.assertRaisesRegex(ValueError, "Excluded font"):
            gate.scan_stream(io.BytesIO(b"before0123456789after"), {"excluded": b"0123456789"}, chunk_size=4)
        with self.assertRaisesRegex(ValueError, "missing"):
            gate.scan_stream(io.BytesIO(b"abcdef"), {}, {"required": b"gh"}, chunk_size=2)
        self.assertEqual(
            gate.scan_stream(io.BytesIO(b"before0123456789after"), {}, {"required": b"0123456789"}, chunk_size=4),
            gate.hashlib.sha256(b"before0123456789after").hexdigest(),
        )

    def test_decision_is_specific_and_retains_unresolved_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("Rust/Cargo.lock", "Notices/Source/krilla/krilla-0.8.2.crate",
                         "Notices/Source/krilla/README.md", "Notices/Upstream/krilla/NOTICE.md",
                         "Notices/Upstream/krilla/LICENSE_APACHE", "Notices/Upstream/krilla/LICENSE_MIT",
                         "Notices/Upstream/krilla/MPL-2.0-reference.txt"):
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            decision = json.loads((ROOT / "Documentation/RELEASE-RISK-DECISION.json").read_text())
            inventory = {"unresolved": [gate.KRILLA_FINDING, gate.HISTORICAL_FINDING]}
            gate.verify_decision(root, inventory, decision)
            for altered in (dict(decision, artifact_sha256="0" * 64),
                            dict(decision, decision="resolved"),
                            dict(decision, independent_legal_review=True)):
                with self.subTest(altered=altered), self.assertRaises(ValueError):
                    gate.verify_decision(root, inventory, altered)
            with self.assertRaises(ValueError):
                gate.verify_decision(root, {"unresolved": inventory["unresolved"] + ["another finding"]}, decision)
            (root / "Notices/Source/krilla/krilla-0.8.2.crate").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                gate.verify_decision(root, inventory, decision)


if __name__ == "__main__":
    unittest.main()
