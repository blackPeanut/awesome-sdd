#!/usr/bin/env python3
"""Exercise Codex dispatch arguments, settings isolation and read-only failure paths."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
HELPERS = ROOT / "skills/_shared/scripts"
sys.path.insert(0, str(HELPERS))
from settings import SettingsError, load_settings
from resolve_dispatch import resolve


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="sdd-dispatch-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "settings.md"
        self.settings = load_settings(self.path)
        self.runtime = {
            "host": "codex", "delegation": True, "overrides_allowed": True,
            "model_parameter": "model", "effort_parameter": "reasoning_effort",
            "inherited_model": "session-model", "inherited_effort": "xhigh",
            "models": {"gpt-6.1-sol": ["low", "medium", "high", "xhigh", "max", "ultra"],
                       "gpt-6-luna": ["low", "medium", "high", "xhigh", "max"],
                       "session-model": ["medium", "high", "xhigh"]},
            "override_context": {"fork_turns": "none"}}

    def plan(self, role="implementer", **kwargs):
        return resolve(self.settings, role, self.runtime, **kwargs)

    def write_settings(self, body):
        self.path.write_text("---\n" + body + "\n---\nKeep my notes.\n")
        self.settings = load_settings(self.path)

    def test_defaults_produce_real_tool_arguments_for_each_role(self):
        expected = {"explorer": ("gpt-6-luna", "high"),
                    "test-author": ("gpt-6.1-sol", "medium"),
                    "implementer": ("gpt-6.1-sol", "medium"),
                    "reviewer": ("gpt-6.1-sol", "high"),
                    "critic": ("gpt-6.1-sol", "high"),
                    "devils-advocate": ("gpt-6.1-sol", "high"),
                    "strategist": ("gpt-6.1-sol", "high"),
                    "analyst": ("gpt-6.1-sol", "high"),
                    "researcher": ("gpt-6.1-sol", "medium"),
                    "pen-keeper": ("gpt-6.1-sol", "medium")}
        for role, (model, effort) in expected.items():
            with self.subTest(role=role):
                result = self.plan(role)
                self.assertEqual(result["dispatch_args"], {
                    "model": model, "reasoning_effort": effort, "fork_turns": "none"})
                self.assertFalse(result["confirmed"])
        self.assertFalse(self.path.exists())

    def test_claude_preferences_are_preserved_and_do_not_leak(self):
        self.write_settings("model_implementer: opus\neffort_implementer: max\njudgment_model: fable")
        before = self.path.read_bytes()
        self.assertEqual(self.plan()["requested"], {"model": "gpt-6.1-sol", "effort": "medium"})
        self.assertEqual(self.settings["model_implementer"], "opus")
        self.assertEqual(self.path.read_bytes(), before)

    def test_saved_role_model_and_effort_override_shared_default(self):
        self.write_settings("codex_model_implementer: gpt-6-luna\ncodex_effort_implementer: xhigh")
        args = self.plan()["dispatch_args"]
        self.assertEqual((args["model"], args["reasoning_effort"]), ("gpt-6-luna", "xhigh"))

    def test_invocation_preferences_win_even_on_escalation(self):
        self.write_settings("codex_model_implementer: gpt-6-luna\ncodex_effort_implementer: high")
        args = self.plan(model="gpt-6.1-sol", effort="low", escalation=True)["dispatch_args"]
        self.assertEqual((args["model"], args["reasoning_effort"]), ("gpt-6.1-sol", "low"))

    def test_complex_work_and_escalation_raise_only_execution_effort(self):
        for kwargs in ({"complex_work": True}, {"escalation": True}):
            for role in ("test-author", "implementer"):
                self.assertEqual(self.plan(role, **kwargs)["dispatch_args"]["reasoning_effort"], "high")
            self.assertEqual(self.plan("researcher", **kwargs)["dispatch_args"]["reasoning_effort"], "medium")

    def test_complex_work_never_lowers_higher_effort(self):
        self.write_settings("codex_effort_implementer: xhigh")
        self.assertEqual(self.plan(complex_work=True)["dispatch_args"]["reasoning_effort"], "xhigh")

    def test_complex_effort_inherit_disables_increase(self):
        self.write_settings("codex_effort_complex: inherit")
        self.assertEqual(self.plan(escalation=True)["dispatch_args"]["reasoning_effort"], "medium")

    def test_inherit_both_omits_overrides_and_preserves_known_host_values(self):
        self.write_settings("codex_model: inherit\ncodex_effort_implementer: inherit")
        result = self.plan(escalation=True)
        self.assertEqual(result["dispatch_args"], {})
        self.assertEqual(result["selection"], {"model": "session-model", "effort": "xhigh", "source": "inherited"})

    def test_role_effort_inherit_is_not_raised_and_model_only_effort_is_unknown(self):
        self.write_settings("codex_effort_implementer: inherit")
        result = self.plan(escalation=True)
        self.assertEqual(result["dispatch_args"], {"model": "gpt-6.1-sol", "fork_turns": "none"})
        self.assertIsNone(result["selection"]["effort"])

    def test_unavailable_model_falls_back_without_editing_settings(self):
        self.write_settings("codex_model: unavailable-model\nauto_commit: off")
        before = self.path.read_bytes()
        result = self.plan()
        self.assertEqual(result["dispatch_args"], {})
        self.assertIn("not advertised", " ".join(result["notes"]))
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.settings["auto_commit"], "off")

    def test_unsupported_model_effort_pair_falls_back_as_a_pair(self):
        self.runtime["models"]["gpt-6.1-sol"] = ["low"]
        result = self.plan()
        self.assertEqual(result["dispatch_args"], {})
        self.assertEqual(result["selection"]["model"], "session-model")

    def test_missing_catalog_does_not_guess_access(self):
        self.runtime.pop("models")
        self.assertEqual(self.plan()["dispatch_args"], {})

    def test_no_delegation_reports_inline_and_never_applies_role_preferences(self):
        self.runtime["delegation"] = False
        result = self.plan("reviewer")
        self.assertEqual(result["status"], "inline")
        self.assertEqual(result["dispatch_args"], {})
        self.assertIn("self-check", " ".join(result["notes"]))

    def test_permissions_disable_overrides_even_when_fields_exist(self):
        self.runtime["overrides_allowed"] = False
        self.assertEqual(self.plan()["dispatch_args"], {})

    def test_effort_only_control_uses_the_inherited_model_capabilities(self):
        self.runtime["model_parameter"] = None
        result = self.plan()
        self.assertEqual(result["dispatch_args"], {"reasoning_effort": "medium", "fork_turns": "none"})
        self.assertEqual(result["selection"]["model"], "session-model")
        self.runtime["inherited_model"] = None
        self.assertEqual(self.plan()["dispatch_args"], {})

    def test_model_only_control_does_not_claim_requested_effort(self):
        self.runtime["effort_parameter"] = None
        result = self.plan()
        self.assertEqual(result["dispatch_args"], {"model": "gpt-6.1-sol", "fork_turns": "none"})
        self.assertIsNone(result["selection"]["effort"])

    def test_live_field_names_and_context_are_used_without_claude_arguments(self):
        self.runtime["effort_parameter"] = "model_reasoning_effort"
        self.runtime["override_context"] = {"fork_context": False}
        self.assertEqual(self.plan()["dispatch_args"], {
            "model": "gpt-6.1-sol", "model_reasoning_effort": "medium", "fork_context": False})

    def test_availability_retry_preserves_context_but_omits_selection_arguments(self):
        result = self.plan(availability_fallback=True)
        self.assertEqual(result["dispatch_args"], {"fork_turns": "none"})
        self.assertFalse(result["confirmed"])

    def test_unknown_inherited_values_stay_unknown(self):
        self.runtime.update(overrides_allowed=False, inherited_model=None, inherited_effort=None)
        self.assertIsNone(self.plan()["selection"]["model"])
        self.assertIsNone(self.plan()["selection"]["effort"])

    def test_invalid_codex_settings_stop_instead_of_using_defaults(self):
        for line in ("codex_model: opus", "codex_model: false", "codex_model: ''",
                     "codex_model_test_author: [gpt-6.1-sol]", "codex_effort_reviewer: huge",
                     "codex_effort_explorer: 3", "codex_effort_critic: true",
                     "codex_effort_complex: [high]", "codex_model: one\ncodex_model: two"):
            with self.subTest(line=line):
                self.path.write_text("---\nauto_commit: off\n"+line+"\n---\n")
                before = self.path.read_bytes()
                with self.assertRaises(SettingsError):
                    load_settings(self.path)
                self.assertEqual(self.path.read_bytes(), before)

    def test_unknown_settings_are_preserved_and_ignored(self):
        self.write_settings("codex_future: [custom, values]\ncustom_note: keep")
        before = self.path.read_bytes()
        self.assertNotIn("codex_future", self.settings)
        self.plan()
        self.assertEqual(self.path.read_bytes(), before)

    def test_role_alias_and_custom_judgment_settings(self):
        self.write_settings("codex_effort_judgment: xhigh\ncodex_effort_devils_advocate: medium")
        self.assertEqual(self.plan("critic")["dispatch_args"]["reasoning_effort"], "xhigh")
        self.assertEqual(self.plan("reviewer")["dispatch_args"]["reasoning_effort"], "high")
        self.assertEqual(self.plan("devils-advocate")["dispatch_args"]["reasoning_effort"], "medium")

    def test_invalid_runtime_or_invocation_cannot_produce_dispatch(self):
        cases = [{"host": "claude"}, {"delegation": "false"}, {"models": []},
                 {"effort_parameter": "model"}, {"override_context": {"model": "opus"}}]
        for patch in cases:
            runtime = self.runtime | patch
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                resolve(self.settings, "implementer", runtime)
        with self.assertRaises(ValueError):
            self.plan("invented-role")
        with self.assertRaises(ValueError):
            self.plan(model="sonnet")
        with self.assertRaises(ValueError):
            self.plan(effort="unlimited")

    def test_cli_round_trip_is_read_only_and_fails_on_invalid_settings(self):
        runtime = self.root / "runtime.json"
        runtime.write_text(json.dumps(self.runtime))
        self.write_settings("auto_commit: off\nmodel_implementer: opus")
        command = [sys.executable, "-B", str(HELPERS / "resolve_dispatch.py"),
                   "--runtime", str(runtime), "--settings", str(self.path), "--role", "implementer"]
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        process = subprocess.run(command, capture_output=True, text=True, cwd=self.root)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["dispatch_args"]["model"], "gpt-6.1-sol")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
        self.path.write_text("---\nauto_commit: off\ncodex_effort_implementer: true\n---\n")
        process = subprocess.run(command, capture_output=True, text=True, cwd=self.root)
        self.assertNotEqual(process.returncode, 0)
        self.assertNotIn("dispatch_args", json.loads(process.stdout))


if __name__ == "__main__":
    unittest.main()
