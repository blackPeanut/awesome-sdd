#!/usr/bin/env python3
"""Exercise copied installs and failed upgrades in disposable prefixes, on macOS/Linux."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def files(path):
    return {str(p.relative_to(path)): (p.read_bytes(), p.stat().st_mode & 0o777)
            for p in path.rglob("*") if p.is_file()}


class UpgradeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sdd-upgrade-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.env = dict(os.environ)

    def setup_tool(self, tool):
        self.prefix = self.base / tool
        self.tool = tool
        self.skills = self.prefix / (".agents/skills/sdd" if tool == "codex" else ".cursor/skills/sdd")
        self.agents = self.prefix / f".{tool}/agents"
        self.state = self.prefix / (".agents/.sdd-installer" if tool == "codex" else ".cursor/.sdd-installer")
        self.assertEqual(self.install().returncode, 0)
        (self.agents / "other-agent.md").write_text("unrelated agent")
        (self.skills / "user-note.txt").write_text("previous installation")
        self.before = (files(self.skills), files(self.agents),
                       (self.prefix/".claude/sdd.local.md").read_bytes(), (self.prefix/".gitignore").read_bytes())

    def install(self, source=ROOT, extra=()):
        args = ["bash", str(ROOT/"install.sh"), self.tool, "--prefix", str(self.prefix)]
        if source is not None:
            args += ["--src", str(source)]
        return subprocess.run(args + list(extra), env=self.env, text=True, capture_output=True)

    def unchanged(self):
        self.assertEqual(self.before, (files(self.skills), files(self.agents),
                         (self.prefix/".claude/sdd.local.md").read_bytes(), (self.prefix/".gitignore").read_bytes()))
        self.assertFalse((self.state/"lock").exists())

    def stub(self, name, script):
        directory = self.base / "bin"
        directory.mkdir(exist_ok=True)
        path = directory/name
        path.write_text("#!/bin/sh\n" + script)
        path.chmod(0o755)
        self.env["PATH"] = str(directory) + os.pathsep + os.environ["PATH"]

    def test_invalid_source_preserves_install(self):
        for tool in ("codex", "cursor"):
            with self.subTest(tool=tool):
                self.setup_tool(tool)
                self.assertNotEqual(self.install(self.base/"missing").returncode, 0)
                self.unchanged()

    def test_failed_download_preserves_install(self):
        self.setup_tool("codex")
        self.stub("curl", "exit 22\n")
        self.assertNotEqual(self.install(None).returncode, 0)
        self.unchanged()

    def test_invalid_generated_agent_preserves_install(self):
        for tool in ("codex", "cursor"):
            with self.subTest(tool=tool):
                self.setup_tool(tool)
                source = self.base / f"bad-{tool}"
                shutil.copytree(ROOT/"skills", source/"skills")
                shutil.copytree(ROOT/"agents", source/"agents")
                path = source/"agents/reviewer.md"
                path.write_text(path.read_text().replace("name: reviewer", "name: invalid"))
                self.assertNotEqual(self.install(source).returncode, 0)
                self.unchanged()

    def test_partial_swap_rolls_back_skills_and_agents(self):
        for tool in ("codex", "cursor"):
            with self.subTest(tool=tool):
                self.env = dict(os.environ)
                self.setup_tool(tool)
                real = shutil.which("mv")
                self.stub("mv", f'case "$1" in */staged-agents/*) exit 73;; esac\nexec "{real}" "$@"\n')
                result = self.install()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("previous skills and agents restored", result.stderr)
                self.unchanged()
                self.assertFalse((self.state/"pending").exists())

    def test_unclosed_skill_frontmatter_preserves_install(self):
        self.setup_tool("codex")
        source = self.base / "bad-skill"
        shutil.copytree(ROOT/"skills", source/"skills")
        shutil.copytree(ROOT/"agents", source/"agents")
        (source/"skills/specify/SKILL.md").write_text("---\nname: specify\ndescription: unfinished\n")
        self.assertNotEqual(self.install(source).returncode, 0)
        self.unchanged()

    def test_signal_during_swap_restores_previous(self):
        self.setup_tool("codex")
        real = shutil.which("mv")
        self.stub("mv", f'case "$1" in */staged-agents/*) kill -TERM "$PPID"; exit 143;; esac\nexec "{real}" "$@"\n')
        self.assertNotEqual(self.install().returncode, 0)
        self.unchanged()

    def test_uncatchable_kill_recovers_after_stale_lock_is_cleared(self):
        self.setup_tool("codex")
        real = shutil.which("mv")
        self.stub("mv", f'case "$1" in */staged-agents/*) kill -KILL "$PPID"; exit 137;; esac\nexec "{real}" "$@"\n')
        self.assertNotEqual(self.install().returncode, 0)
        self.assertTrue((self.state/"pending").exists())
        self.assertTrue((self.state/"lock/pid").exists())
        # The subprocess is known to have exited; model the documented stale-lock recovery.
        shutil.rmtree(self.state/"lock")
        self.env = dict(os.environ)
        self.assertNotEqual(self.install(self.base/"missing").returncode, 0)
        self.unchanged()

    def test_success_keeps_backup_removes_stale_agents_and_uninstall_is_scoped(self):
        self.setup_tool("codex")
        (self.agents/"sdd-obsolete.toml").write_text("old")
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.skills/"user-note.txt").exists())
        self.assertFalse((self.agents/"sdd-obsolete.toml").exists())
        backups = [p for p in self.state.glob("transaction.*") if (p/"previous-skills/user-note.txt").exists()]
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0]/"previous-agents/sdd-obsolete.toml").read_text(), "old")
        result = self.install(extra=("--uninstall",))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.skills.exists())
        self.assertEqual((self.agents/"other-agent.md").read_text(), "unrelated agent")
        self.assertTrue(backups[0].exists())

    def test_pending_journal_restored_before_next_failed_install(self):
        self.setup_tool("cursor")
        saved = self.state/"transaction.interrupted"
        shutil.copytree(self.skills, saved/"previous-skills")
        (saved/"previous-agents").mkdir()
        for path in self.agents.glob("sdd-*"):
            shutil.copy2(path, saved/"previous-agents"/path.name)
        (saved/"ready").touch()
        (self.state/"pending").write_text(str(saved))
        (self.skills/"partial.txt").write_text("incomplete swap")
        result = self.install(self.base/"missing")
        self.assertNotEqual(result.returncode, 0)
        self.unchanged()
        self.assertFalse((self.state/"pending").exists())

    def test_concurrent_install_refuses_without_changes(self):
        self.setup_tool("codex")
        (self.state/"lock").mkdir()
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another install", result.stderr)
        (self.state/"lock").rmdir()
        self.unchanged()


if __name__ == "__main__":
    unittest.main()
