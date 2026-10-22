#!/usr/bin/env python3
"""Deterministic tests for the live harness; never contact a model."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_codex", ROOT / "evals/run_codex.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def stream(*extra, thread="test-thread", complete=True):
    events = [{"type": "thread.started", "thread_id": thread}, *extra]
    if complete:
        events.append({"type": "turn.completed"})
    return "\n".join(json.dumps(e) for e in events)


class Events(unittest.TestCase):
    def test_complete(self):
        thread, messages, _ = runner.parse_events(stream({"type": "item.completed", "item": {
            "type": "agent_message", "text": "Ready"}}), "Ready")
        self.assertEqual((thread, messages), ("test-thread", ["Ready"]))

    def test_fail_closed(self):
        for raw, final in [("bad json", "Ready"), (stream(complete=False), "Ready"),
                           (stream(), ""), (stream({"type": "error"}), "Ready"),
                           (stream({"type": "turn.failed"}), "Ready"),
                           (stream({"type": "thread.started", "thread_id": "other"}), "Ready")]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                runner.parse_events(raw, final)

    def test_all_conversation_checked(self):
        for text in ("Продовжуємо", "Run /clear", "Run /awesome-sdd:specify tiny-toggle"):
            with self.subTest(text=text), self.assertRaises(AssertionError):
                runner.verify_turn({"messages": [text], "final": "All done"})


class Invocation(unittest.TestCase):
    def fake_process(self, command, **kwargs):
        self.command = command
        final = Path(command[command.index("--output-last-message") + 1])
        final.write_text("Done")
        kwargs["stdout"].write(stream(thread=self.thread))
        kwargs["stdout"].flush()
        class Process:
            returncode = 0
            def communicate(self, prompt, timeout):
                pass
        return Process()

    def test_resume_exact_id_and_sandbox(self):
        self.thread = "owned-test-thread"
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner.subprocess, "Popen", self.fake_process):
            runner.invoke("codex", Path(tmp), Path(tmp), "resume", "Confirm", 1, self.thread)
        self.assertIn(self.thread, self.command)
        self.assertNotIn("--last", self.command)
        self.assertEqual(self.command[self.command.index("--sandbox") + 1], "workspace-write")
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", self.command)

    def test_resume_mismatch_rejected(self):
        self.thread = "wrong-thread"
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner.subprocess, "Popen", self.fake_process):
            with self.assertRaisesRegex(ValueError, "different thread"):
                runner.invoke("codex", Path(tmp), Path(tmp), "resume", "Confirm", 1, "owned-test-thread")

    def test_judge_is_read_only(self):
        self.thread = "judge-thread"
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner.subprocess, "Popen", self.fake_process):
            runner.invoke("codex", Path(tmp), Path(tmp), "judge", "Judge", 1, schema=Path(tmp)/"schema.json")
        self.assertEqual(self.command[self.command.index("--sandbox") + 1], "read-only")

    def test_timeout_kills_process_group(self):
        class Hung:
            pid = 123456
            def communicate(self, prompt, timeout):
                raise subprocess.TimeoutExpired("codex", timeout)
            def wait(self):
                pass
        with tempfile.TemporaryDirectory() as tmp, patch.object(runner.subprocess, "Popen", return_value=Hung()), \
                patch.object(runner.os, "killpg") as kill:
            with self.assertRaisesRegex(RuntimeError, "timeout"):
                runner.invoke("codex", Path(tmp), Path(tmp), "hung", "Prompt", 1)
            kill.assert_called_once_with(123456, runner.signal.SIGKILL)


class DiskContract(unittest.TestCase):
    def test_saved_preferences_and_accepted_prose_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)/"work"
            work.mkdir()
            runner.fixture(work, Path(tmp)/"plugin", True)
            before = runner.snapshot(work)
            feature = work/"docs/features/tiny-toggle"
            (feature/".size").write_text("M\n")
            (feature/".route").write_text("standard\n")
            spec_path = feature/"spec.md"
            spec_path.write_text(spec_path.read_text().replace("feature_size: S", "feature_size: M"))
            runner.verify_files(before, work, True)
            original = spec_path.read_text()
            spec_path.write_text(original.replace("off by default", "on by default"))
            with self.assertRaisesRegex(AssertionError, "accepted prose"):
                runner.verify_files(before, work, True)
            spec_path.write_text(original)
            (work/".claude/sdd.local.md").write_text("overwritten")
            with self.assertRaisesRegex(AssertionError, "Unexpected file changes"):
                runner.verify_files(before, work, True)


class PortableProtocols(unittest.TestCase):
    def test_entrypoints_resolve_runtime(self):
        for path in [*ROOT.glob("skills/*/SKILL.md"), *ROOT.glob("agents/*.md")]:
            with self.subTest(path=path):
                self.assertIn("host-capabilities.md", path.read_text())

    def test_recipes_cannot_bypass_resolver(self):
        for path in ROOT.glob("skills/**/*.md"):
            if path.name in ("agent-roster.md", "settings-file.md") or "config/references" in str(path):
                continue
            with self.subTest(path=path):
                text = path.read_text()
                self.assertNotIn("subagent_type:", text)
                self.assertNotIn("CLAUDE_CODE_", text)
                self.assertNotRegex(text, r"model:\s*(haiku|sonnet|opus)\b")


if __name__ == "__main__":
    unittest.main()
