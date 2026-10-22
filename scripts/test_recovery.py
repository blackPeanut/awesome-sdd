#!/usr/bin/env python3
"""Real Git fixtures for task recovery and strict settings; requires PyYAML."""
import importlib.util
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SETTINGS = ROOT / "skills/_shared/scripts/settings.py"
RESUME = ROOT / "skills/implement/scripts/resume.py"
spec = importlib.util.spec_from_file_location("settings", SETTINGS)
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)


class SettingsTests(unittest.TestCase):
    def test_invalid_existing_file_never_defaults_or_changes(self):
        cases = ["", "auto_commit: off\n", "---\nauto_commit: off\n", "---\nauto_commit: [\n---\n",
                 "---\nauto_commit: off\nauto_commit: per_task\n---\n", "---\n- auto_commit\n---\n",
                 "---\nauto_commit: false\n---\n", "---\ntdd: yes\n---\n",
                 "---\nmax_parallel_agents: true\n---\n", "---\nmax_red_retries: 0\n---\n"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"settings.md"
            for text in cases:
                with self.subTest(text=text):
                    path.write_text(text)
                    with self.assertRaises(settings.SettingsError):
                        settings.load_settings(path)
                    self.assertEqual(path.read_text(), text)

    def test_off_legacy_language_unknown_keys_and_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"settings.md"
            self.assertEqual(settings.load_settings(path)["auto_commit"], "per_task")
            self.assertFalse(path.exists())
            text = "---\nauto_commit: off # keep\nartifact_language: uk\ncustom: [one, two]\n---\nNotes\n"
            path.write_text(text)
            value = settings.load_settings(path)
            self.assertEqual(value["auto_commit"], "off")
            self.assertEqual(value["artifact_language"], "en")
            self.assertTrue(value["tdd"])
            self.assertNotIn("custom", value)
            self.assertEqual(path.read_text(), text)


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sdd-recovery-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tasks_path = "docs/features/toggle/tasks.json"
        self.feature = self.root/"docs/features/toggle"
        (self.feature/"tasks").mkdir(parents=True)
        (self.root/".claude").mkdir()
        self.config = self.root/".claude/sdd.local.md"
        self.config.write_text("---\nauto_commit: per_task\n---\n")
        (self.root/".gitignore").write_text(".claude/*.local.md\n__pycache__/\n")
        (self.root/"app.py").write_text("VALUE = 1\n")
        (self.root/"test_app.py").write_text("from app import VALUE\nassert VALUE == 2\n")
        self.tasks = {"slug": "toggle", "tasks": [{"id": "T1", "status": "in_progress", "deps": [],
            "title": "Set toggle value", "layer": "domain", "dod": "VALUE is 2 and its test passes",
            "acs": ["AC-1"], "files_hint": ["app.py", "test_app.py"], "file": "docs/features/toggle/tasks/change.md"}]}
        self.write_tasks()
        (self.feature/"tasks/change.md").write_text("---\nstatus: in_progress\nstep: GATE\n---\nImplement AC-1.\n")
        self.git("init", "-q")
        self.git("config", "user.name", "SDD test")
        self.git("config", "user.email", "test@sdd")
        self.git("add", "-A")
        self.git("commit", "-qm", "baseline")
        (self.root/"app.py").write_text("VALUE = 2\n")
        self.gate = shlex.quote(sys.executable) + " -B test_app.py"

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE).decode().strip()

    def write_tasks(self):
        (self.root/self.tasks_path).write_text(json.dumps(self.tasks))

    def run_helper(self, action, *extra):
        result = subprocess.run([sys.executable, "-B", str(RESUME), action, "--tasks", self.tasks_path, *extra],
                                cwd=self.root, capture_output=True, text=True)
        return result, json.loads(result.stdout)

    def capture(self, *extra):
        result, body = self.run_helper("capture", "--task", "T1", "--gate", self.gate, *extra)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return body

    def state(self):
        result, body = self.run_helper("check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return body["results"][0]["state"]

    def commit_task(self, feature="toggle"):
        self.git("add", "-A")
        self.git("commit", "-qm", f"Implement toggle\n\nSDD-Feature: {feature}\nSDD-Task: T1\nSDD-AC: AC-1")

    def test_crash_after_done_before_commit_is_not_skipped(self):
        self.capture()
        self.tasks["tasks"][0]["status"] = "done"
        self.write_tasks()
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_interrupted_combined_worker_is_unfinished_without_gate_evidence(self):
        (self.feature/"tasks/change.md").write_text(
            "---\nstatus: in_progress\nstep: GREEN+REFACTOR+GATE\n---\nImplement AC-1.\n")
        before = self.git("rev-parse", "HEAD")
        self.assertEqual(self.state(), "needs_reconciliation")
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertEqual((self.root/"app.py").read_text(), "VALUE = 2\n")

    def test_successful_commit_is_recovered_even_with_in_progress_mirror(self):
        self.capture()
        self.commit_task()
        self.assertEqual(self.state(), "verified_committed")

    def test_status_updates_do_not_invalidate_gate_evidence(self):
        self.capture()
        self.tasks["tasks"][0]["status"] = "done"
        self.write_tasks()
        (self.feature/"tasks/change.md").write_text("---\nstatus: done\nstep: COMMIT\n---\nImplement AC-1.\n")
        self.commit_task()
        self.assertEqual(self.state(), "verified_committed")

    def test_commits_off_accepts_verified_work_without_committing(self):
        self.config.write_text("---\nauto_commit: off\n---\n")
        self.capture()
        self.assertEqual(self.state(), "verified_uncommitted")
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), "1")

    def test_changed_inputs_require_reverification(self):
        self.capture()
        self.commit_task()
        (self.root/"app.py").write_text("VALUE = 3\n")
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_changed_acceptance_criteria_require_reverification(self):
        self.capture()
        self.commit_task()
        self.tasks["tasks"][0]["acs"].append("AC-2")
        self.write_tasks()
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_per_phase_commit_recovers_every_task(self):
        self.config.write_text("---\nauto_commit: per_phase\n---\n")
        second = dict(self.tasks["tasks"][0], id="T2", deps=["T1"])
        self.tasks["tasks"].append(second)
        self.write_tasks()
        self.capture()
        result, body = self.run_helper("capture", "--task", "T2", "--gate", self.gate)
        self.assertEqual(result.returncode, 0, body)
        self.git("add", "-A")
        self.git("commit", "-qm", "Phase\n\nSDD-Feature: toggle\nSDD-Task: T1\nSDD-Task: T2\nSDD-AC: AC-1")
        result, body = self.run_helper("check")
        self.assertEqual(result.returncode, 0, body)
        self.assertEqual([r["state"] for r in body["results"]], ["verified_committed"] * 2)

    def test_off_mode_changed_to_per_task_requires_commit(self):
        self.config.write_text("---\nauto_commit: off\n---\n")
        self.capture()
        self.config.write_text("---\nauto_commit: per_task\n---\n")
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_unreachable_commit_is_not_completion(self):
        self.capture()
        base = self.git("rev-parse", "HEAD")
        self.commit_task()
        self.git("reset", "--soft", base)
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_glob_hints_detect_new_matching_inputs(self):
        self.tasks["tasks"][0]["files_hint"] = ["*.py"]
        self.write_tasks()
        self.capture()
        self.commit_task()
        self.assertEqual(self.state(), "verified_committed")
        (self.root/"new.py").write_text("VALUE = 9\n")
        result, body = self.run_helper("check")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("omits required inputs", body["error"])

    def test_symlink_input_is_not_silently_verified(self):
        (self.root/"linked.py").symlink_to("app.py")
        result, body = self.run_helper("capture", "--task", "T1", "--gate", self.gate, "--path", "linked.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Symlink", body["error"])

    def test_directory_hint_ignores_gate_cache_but_tracks_new_source(self):
        (self.root/"src").mkdir()
        (self.root/"src/module.py").write_text("VALUE = 2\n")
        self.tasks["tasks"][0]["files_hint"].append("src")
        self.write_tasks()
        self.capture("--gate", "mkdir -p src/__pycache__ && touch src/__pycache__/generated")
        self.commit_task()
        self.assertEqual(self.state(), "verified_committed")
        (self.root/"src/new.py").write_text("VALUE = 3\n")
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_wrong_feature_trailer_is_not_completion_evidence(self):
        self.capture()
        self.commit_task("another-feature")
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_old_done_without_receipt_is_not_trusted(self):
        self.tasks["tasks"][0]["status"] = "done"
        self.write_tasks()
        self.assertEqual(self.state(), "needs_reconciliation")

    def test_failed_gate_invalidates_old_success(self):
        self.capture()
        result, _ = self.run_helper("capture", "--task", "T1", "--gate", "exit 9")
        self.assertNotEqual(result.returncode, 0)
        result, body = self.run_helper("check")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(body["ok"])

    def test_mutating_gate_does_not_certify_changed_code(self):
        command = shlex.quote(sys.executable) + ' -c "open(\'app.py\', \'w\').write(\'VALUE = 3\\n\')"'
        result, body = self.run_helper("capture", "--task", "T1", "--gate", command)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed recorded inputs", body["error"])

    def test_malformed_settings_prevent_gate_commands_and_evidence_writes(self):
        self.config.write_text("---\nauto_commit: off\ntdd: [\n---\n")
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result, body = self.run_helper("capture", "--task", "T1", "--gate", "touch should-not-exist")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(body["ok"])
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_deleted_input_is_verifiable(self):
        (self.root/"obsolete.txt").write_text("old")
        self.git("add", "obsolete.txt")
        self.git("commit", "-qm", "old file")
        (self.root/"obsolete.txt").unlink()
        self.capture("--path", "obsolete.txt")
        self.commit_task()
        self.assertEqual(self.state(), "verified_committed")


if __name__ == "__main__":
    unittest.main()
