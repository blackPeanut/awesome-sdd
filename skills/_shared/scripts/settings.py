#!/usr/bin/env python3
"""Read and validate SDD settings without mutating files (requires PyYAML).

Uses YAML 1.2 boolean semantics: bare `off` is a string, never False.
Missing files/keys use the canonical template; invalid existing files never do.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    yaml = None


class SettingsError(ValueError):
    pass


def parse_mapping(text, label):
    if yaml is None:
        raise SettingsError("PyYAML unavailable; use a reliable YAML 1.2 parser or stop before mutations")

    class Loader(yaml.SafeLoader):
        pass

    Loader.yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)
    for key, resolvers in Loader.yaml_implicit_resolvers.items():
        Loader.yaml_implicit_resolvers[key] = [(tag, regex) for tag, regex in resolvers
                                              if tag != "tag:yaml.org,2002:bool"]
    Loader.add_implicit_resolver("tag:yaml.org,2002:bool", re.compile(r"^(?:true|false)$"), list("tf"))

    def mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise SettingsError(f"{label}: line {key_node.start_mark.line + 1}: keys must be strings")
            if key in result:
                raise SettingsError(f"{label}: line {key_node.start_mark.line + 1}: duplicate key {key}")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        value = yaml.load(text, Loader=Loader)
    except yaml.YAMLError as error:
        mark = getattr(error, "problem_mark", None)
        location = f" line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        raise SettingsError(f"{label}:{location}: invalid YAML ({getattr(error, 'problem', 'parse error')})") from None
    if not isinstance(value, dict):
        raise SettingsError(f"{label}: frontmatter must be a mapping")
    return value


ENUMS = {
    "interview_depth": {"easy", "medium", "hard"},
    "workflow_mode": {"auto", "off"}, "isolation": {"worktree", "inplace"},
    "require_integration": {"auto", "always", "never"},
    "auto_commit": {"per_task", "per_phase", "off"}, "branch_strategy": {"feature", "current"},
}
BOOLS = {"tdd", "team_mode", "stop_on_red", "gate_lint", "gate_vet"}
INTS = {"max_parallel_agents", "max_red_retries"}


CODEX_ROLES = {"explorer", "test_author", "implementer", "reviewer", "critic",
               "devils_advocate", "researcher", "strategist", "analyst", "pen_keeper"}
CODEX_MODEL_KEYS = {"codex_model"} | {f"codex_model_{role}" for role in CODEX_ROLES}
CODEX_EFFORT_KEYS = {f"codex_effort_{role}" for role in CODEX_ROLES | {"judgment", "complex"}}
CODEX_EFFORTS = {"inherit", "none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
CLAUDE_ALIASES = {"haiku", "sonnet", "opus", "fable"}


def valid_codex_model(value):
    return (isinstance(value, str) and bool(value) and not any(c.isspace() for c in value)
            and value not in CLAUDE_ALIASES)


def load_settings(path):
    path = Path(path)
    template = (Path(__file__).resolve().parents[1] / "settings-file.md").read_text()
    defaults = parse_mapping(template.split("```yaml\n", 1)[1].split("```", 1)[0], "canonical defaults")
    supplied = {}
    if path.exists() or path.is_symlink():
        lines = path.read_text().splitlines()
        if not lines or lines[0] != "---":
            raise SettingsError(f"{path}: line 1: expected opening ---")
        try:
            end = lines.index("---", 1)
        except ValueError:
            raise SettingsError(f"{path}: missing closing ---") from None
        # Include the first blank line so parser locations match the actual file.
        supplied = parse_mapping("\n" + "\n".join(lines[1:end]), str(path))
        for key, value in supplied.items():
            valid = True
            if key in CODEX_MODEL_KEYS:
                valid = valid_codex_model(value)
            elif key in CODEX_EFFORT_KEYS:
                valid = isinstance(value, str) and value in CODEX_EFFORTS
            elif key in ENUMS:
                valid = isinstance(value, str) and value in ENUMS[key]
            elif key in BOOLS:
                valid = type(value) is bool
            elif key in INTS:
                valid = type(value) is int and value >= 1
            elif key.startswith("effort_"):
                valid = (isinstance(value, str) and value in {"low", "medium", "high", "xhigh", "max"}
                         or type(value) is int and value >= 1)
            elif key in defaults or key.startswith("model_"):
                valid = isinstance(value, str) and (key.startswith("cmd_") or bool(value.strip()))
            if not valid:
                line = next((i for i, s in enumerate(lines, 1) if s.startswith(key + ":")), "?")
                raise SettingsError(f"{path}: line {line}: invalid value/type for {key}; no defaults applied")
    effective = defaults | {key: value for key, value in supplied.items()
                            if key in defaults or key in CODEX_MODEL_KEYS | CODEX_EFFORT_KEYS
                            or key.startswith(("model_", "effort_"))}
    effective["artifact_language"] = "en"
    return effective


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".claude/sdd.local.md")
    args = parser.parse_args()
    try:
        settings = load_settings(args.path)
    except (SettingsError, OSError, UnicodeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1
    print(json.dumps({"ok": True, "settings": settings}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
