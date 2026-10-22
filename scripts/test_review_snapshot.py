#!/usr/bin/env python3
"""Exercise review freshness against real disposable Git repositories."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "skills/review/scripts/snapshot.py"
spec = importlib.util.spec_from_file_location("review_snapshot", SCRIPT)
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class ReviewSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git("init", "-q")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.invalid")
        self.write("app.py", "original\n")
        self.write(".gitignore", "cache/\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").decode().strip()
        self.write("app.py", "implemented\n")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)

    def capture(self):
        return snapshot.snapshot(self.root, "booking", self.base)

    def test_working_review_survives_commit_but_cannot_publish_early(self):
        receipt = self.capture()
        self.assertTrue(snapshot.check(self.root, receipt)["ok"])
        self.assertEqual(snapshot.check(self.root, receipt, True)["uncommitted"], ["app.py"])
        self.git("add", "app.py")
        self.git("commit", "-qm", "implement")
        self.assertTrue(snapshot.check(self.root, receipt, True)["ok"])

    def test_staged_and_unstaged_changes_are_both_visible(self):
        receipt = self.capture()
        self.write("app.py", "staged fix\n")
        self.git("add", "app.py")
        self.assertEqual(snapshot.check(self.root, receipt)["changed"], ["app.py"])
        self.write("app.py", "implemented\n")
        # The working version still matches, but committing the staged version would not.
        self.assertTrue(snapshot.check(self.root, receipt)["ok"])
        self.git("commit", "-qm", "staged only")
        self.assertFalse(snapshot.check(self.root, receipt, True)["ok"])

    def test_added_deleted_and_mode_changed_inputs_invalidate(self):
        receipt = self.capture()
        self.write("new-test.py", "test\n")
        (self.root / "app.py").unlink()
        (self.root / ".gitignore").chmod(0o755)
        self.assertEqual(snapshot.check(self.root, receipt)["changed"],
                         [".gitignore", "app.py", "new-test.py"])

    def test_contract_change_is_not_hidden_by_green_code(self):
        self.write("docs/features/booking/spec.md", "keep signed in\n")
        receipt = self.capture()
        self.write("docs/features/booking/spec.md", "sign out on close\n")
        self.assertEqual(snapshot.check(self.root, receipt)["changed"],
                         ["docs/features/booking/spec.md"])

    def test_review_bookkeeping_and_ignored_cache_do_not_invalidate(self):
        receipt = self.capture()
        self.write("docs/features/booking/_review/snapshot.json", json.dumps(receipt))
        self.write("docs/features/booking/_review/report.md", "PASS\n")
        self.write("cache/build.bin", "generated\n")
        self.assertTrue(snapshot.check(self.root, receipt)["ok"])
        # Other feature records aren't silently excluded.
        self.write("docs/features/other/_review/report.md", "new decision\n")
        self.assertFalse(snapshot.check(self.root, receipt)["ok"])

    def test_symlink_target_change_invalidates_without_reading_target(self):
        link = self.root / "link"
        link.symlink_to("missing-original")
        receipt = self.capture()
        link.unlink()
        link.symlink_to("missing-new")
        self.assertEqual(snapshot.check(self.root, receipt)["changed"], ["link"])

    def test_submodule_is_refused(self):
        self.git("update-index", "--add", "--cacheinfo", "160000", self.base, "vendor")
        with self.assertRaisesRegex(ValueError, "Submodules"):
            self.capture()

    def test_malformed_receipts_fail_closed(self):
        for receipt in ({}, {"schema": 1}, dict(self.capture(), files={}),
                        dict(self.capture(), files={"../escape": "100644:" + "a" * 64})):
            with self.subTest(receipt=receipt), self.assertRaises(ValueError):
                snapshot.check(self.root, receipt)

    def test_cli_check_is_read_only_and_reports_stale(self):
        receipt = self.capture()
        saved = self.root / "docs/features/booking/_review/snapshot.json"
        self.write(str(saved.relative_to(self.root)), json.dumps(receipt))
        self.git("add", "app.py")
        self.write("app.py", "later user edit\n")
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        result = subprocess.run([sys.executable, str(SCRIPT), "check", "--receipt", str(saved)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["changed"], ["app.py"])
        after = {str(p.relative_to(self.root)): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after, "check changed project or Git index state")


if __name__ == "__main__":
    unittest.main()
