#!/usr/bin/env python3
"""Test native installer routing with a stub executable.

With --native-catalog, briefly register a unique local test marketplace in Codex,
check discovery, and remove that entry. No plugins are installed by this test.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
NATIVE = "--native-catalog" in sys.argv
if NATIVE:
    sys.argv.remove("--native-catalog")


class NativeInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sdd-desktop-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.log = self.root / "calls.jsonl"
        stub = self.root / "codex-stub"
        stub.write_text("#!" + sys.executable + "\n" +
                        "import json,os,sys\n" +
                        "with open(os.environ['SDD_TEST_LOG'],'a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\n" +
                        "sys.exit(17 if os.environ.get('SDD_TEST_FAIL') == ' '.join(sys.argv[1:3]) else 0)\n")
        stub.chmod(0o755)
        self.env = dict(os.environ, SDD_CODEX_BIN=str(stub), SDD_TEST_LOG=str(self.log))

    def run_install(self, *args):
        return subprocess.run(["bash", str(ROOT / "install.sh"), "codex-app", *args],
                              cwd=self.root, env=self.env, capture_output=True, text=True)

    def calls(self):
        return [json.loads(s) for s in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_installs_native_plugin_without_loose_skills(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), [["plugin", "marketplace", "add", "blackPeanut/awesome-sdd"],
                                       ["plugin", "add", "awesome-sdd@awesome-sdd"]])
        for name in (".agents", ".codex", ".claude", ".gitignore"):
            self.assertFalse((self.root / name).exists(), name)
        self.assertIn("Restart the desktop app", result.stdout)

    def test_uninstall_does_not_remove_marketplace_or_project_files(self):
        sentinel = self.root / "keep.txt"
        sentinel.write_text("keep")
        result = self.run_install("--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls(), [["plugin", "remove", "awesome-sdd@awesome-sdd"]])
        self.assertEqual(sentinel.read_text(), "keep")

    def test_rejects_project_flags_before_mutating_configuration(self):
        for args in (("--prefix", str(self.root)), ("--src", str(ROOT)), ("--ref", "v2.4.2")):
            with self.subTest(args=args):
                self.assertNotEqual(self.run_install(*args).returncode, 0)
                self.assertEqual(self.calls(), [])

    def test_failed_marketplace_does_not_install(self):
        self.env["SDD_TEST_FAIL"] = "plugin marketplace"
        result = self.run_install()
        self.assertEqual(result.returncode, 17)
        self.assertEqual(len(self.calls()), 1)
        self.assertNotIn("Installed the native", result.stdout)

    def test_failed_plugin_does_not_report_success(self):
        self.env["SDD_TEST_FAIL"] = "plugin add"
        result = self.run_install()
        self.assertEqual(result.returncode, 17)
        self.assertNotIn("Installed the native", result.stdout)

    def test_missing_executable_has_actionable_error(self):
        self.env["SDD_CODEX_BIN"] = str(self.root / "missing")
        result = self.run_install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SDD_CODEX_BIN", result.stderr)
        self.assertEqual(self.calls(), [])

    @unittest.skipUnless(NATIVE, "requires --native-catalog and Codex installed")
    def test_real_codex_catalog_discovers_packaged_plugin(self):
        plugin = self.root / "plugins/sdd"
        plugin.mkdir(parents=True)
        for name in ("skills", "agents", "assets", ".codex-plugin"):
            shutil.copytree(ROOT / name, plugin / name)
        shutil.copy2(ROOT / "plugin.json", plugin / "plugin.json")
        catalog = self.root / ".agents/plugins/marketplace.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({"name": "sdd-native-test", "plugins": [{
            "name": "awesome-sdd", "source": {"source": "local", "path": "./plugins/sdd"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_USE"},
            "category": "Productivity"}]}))
        # A real registration exercises the same catalog loader used by native installs.
        # Use a unique temporary marketplace and remove only that entry in all exit paths.
        name = self.root.name
        manifest = json.loads(catalog.read_text())
        manifest["name"] = name
        catalog.write_text(json.dumps(manifest))
        subprocess.run(["codex", "plugin", "marketplace", "add", str(self.root), "--json"],
                       capture_output=True, text=True, check=True)
        try:
            result = subprocess.run(["codex", "plugin", "list", "--marketplace", name,
                                     "--available", "--json"],
                                    capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            matches = [p for p in data["available"] if p["marketplaceName"] == name]
            self.assertEqual(len(matches), 1, result.stderr)
        finally:
            subprocess.run(["codex", "plugin", "marketplace", "remove", name],
                           capture_output=True, text=True, check=True)
        actual = matches[0]
        self.assertEqual(actual["name"], "awesome-sdd")
        self.assertEqual(actual["version"], json.loads((ROOT / "plugin.json").read_text())["version"])
        self.assertEqual(actual["installPolicy"], "AVAILABLE")
        self.assertEqual(actual["authPolicy"], "ON_USE")


if __name__ == "__main__":
    unittest.main()
