"""Replay success, mismatch, drift and overwrite-protection evidence."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import verify_reproducibility as replay


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.spec = self.base / "spec.json"
        self.spec.write_text(
            json.dumps(
                {
                    "version": 2,
                    "kind": "brief-report",
                    "output": "original.hwpx",
                    "title": "재현 검사",
                    "blocks": [{"type": "paragraph", "text": "품질 검증 결과 요약"}],
                    "quality": {"hancom": "off"},
                }
            ),
            encoding="utf-8",
        )

    def test_real_processes_match_and_preserve_original(self):
        original = self.base / "original.hwpx"
        original.write_bytes(b"preserve original")
        result = replay.verify(self.spec, self.base / "real", 2)
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["byte_identical"])
        self.assertEqual(original.read_bytes(), b"preserve original")
        self.assertEqual(result["visual_review"], "not_run")
        self.assertEqual(result["model_consistency"], "not_evaluated")

    def fake_run(self, payloads, mutate=None):
        real_run = subprocess.run

        def run(cmd, **kwargs):
            # platform.platform() may invoke `ver` on Windows through this same
            # subprocess module. Only replace the document builder subprocess.
            if (
                not isinstance(cmd, list)
                or str(ROOT / "scripts/one_shot.py") not in cmd
            ):
                return real_run(cmd, **kwargs)
            Path(cmd[-1]).write_bytes(payloads.pop(0))
            if mutate:
                mutate()
            return subprocess.CompletedProcess(
                cmd, 0, '{"ok":true,"published":true}', ""
            )

        return run

    def test_mismatch_and_expected_hash_are_not_passes(self):
        for name, data, expected in (
            ("different", [b"a", b"b"], None),
            ("unexpected", [b"a", b"a"], "0" * 64),
            ("expected", [b"a", b"a"], hashlib.sha256(b"a").hexdigest()),
        ):
            with patch.object(
                replay.subprocess, "run", side_effect=self.fake_run(data)
            ):
                result = replay.verify(self.spec, self.base / name, 2, expected)
            self.assertEqual(result["ok"], name == "expected")
            self.assertTrue((self.base / name / "reproducibility.json").is_file())

    def test_input_drift_fails_even_when_bytes_match(self):
        def mutate():
            value = json.loads(self.spec.read_text())
            value["title"] += " 변경"
            self.spec.write_text(json.dumps(value), encoding="utf-8")

        with patch.object(
            replay.subprocess, "run", side_effect=self.fake_run([b"a", b"a"], mutate)
        ):
            result = replay.verify(self.spec, self.base / "drift", 2)
        self.assertTrue(result["byte_identical"])
        self.assertFalse(result["inputs_unchanged"])
        self.assertFalse(result["ok"])

    def test_preflight_rejects_existing_or_invalid_options(self):
        with self.assertRaises(ValueError):
            replay.verify(self.spec, self.base)
        for runs, expected in [(1, None), (True, None), (21, None), (2, "bad")]:
            with self.assertRaises(ValueError):
                replay.verify(self.spec, self.base / "never-created", runs, expected)
        self.assertFalse((self.base / "never-created").exists())


if __name__ == "__main__":
    unittest.main()
