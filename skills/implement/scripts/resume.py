#!/usr/bin/env python3
"""Capture real gate evidence and reconcile task completion without changing task status.

capture runs explicitly supplied gate commands in the project; check is read-only.
Both validate project settings before any writes or commands with side effects.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
module_spec = importlib.util.spec_from_file_location(
    "sdd_settings", Path(__file__).resolve().parents[2] / "_shared/scripts/settings.py")
settings_module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(settings_module)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def safe_path(root, value):
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or not path.parts or ".git" in path.parts:
        raise ValueError(f"Expected a project-relative path: {value}")
    # Reject external symlink parents, including for currently missing files.
    if not (root / path).parent.resolve().is_relative_to(root):
        raise ValueError(f"Path leaves project: {value}")
    if (root / path).is_symlink():
        raise ValueError(f"Symlink inputs require separate verification: {value}")
    return path.as_posix()


def normalize(path, data, tasks_path):
    # Status mirrors are not implementation evidence. Their other content still is.
    if path == tasks_path:
        value = json.loads(data)
        for task in value["tasks"]:
            task.pop("status", None)
        return json.dumps(value, sort_keys=True).encode()
    if path.endswith(".md") and "/tasks/" in path and data.startswith(b"---\n"):
        parts = data.split(b"\n---", 1)
        if len(parts) == 2:
            parts[0] = re.sub(rb"(?m)^(?:status|step):[^\n]*\n?", b"", parts[0])
            return b"\n---".join(parts)
    return data


def snapshot(root, paths, tasks_path, revision=None):
    result = {}
    for name in paths:
        safe_path(root, name)
        if revision and name == ".claude/sdd.local.md":
            # Settings are deliberately gitignored. Bind them to the live verified receipt,
            # never require committing a developer's configuration.
            result.update(snapshot(root, [name], tasks_path))
            continue
        if revision:
            rows = git(root, "ls-tree", "-r", "-z", revision, "--", name).split(b"\0")
            entries = []
            for row in rows:
                if not row:
                    continue
                metadata, path = row.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                if kind != "blob" or mode == "120000":
                    raise ValueError("Submodules and symlinks require separate verification")
                entries.append((path.decode(), mode, git(root, "cat-file", "blob", oid)))
        else:
            path = root / name
            if path.is_dir():
                # Include tracked + nonignored new inputs, not caches/build output from gates.
                names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", name)
                files = sorted({root / item for item in names.decode().split("\0") if item})
            else:
                files = [path]
            entries = []
            for file in files:
                rel = file.relative_to(root).as_posix()
                safe_path(root, rel)
                if file.is_symlink():
                    entries.append((rel, "120000", os.readlink(file).encode()))
                elif file.is_file():
                    mode = "100755" if file.stat().st_mode & 0o111 else "100644"
                    entries.append((rel, mode, file.read_bytes()))
        if not entries:
            result[name] = None
        for path, mode, data in entries:
            result[path] = mode + ":" + hashlib.sha256(normalize(path, data, tasks_path)).hexdigest()
    return result


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as file:
        json.dump(value, file, indent=2)
        file.flush()
        os.fsync(file.fileno())
        temp = file.name
    os.replace(temp, path)


def task_inputs(root, tasks_path, task, extra):
    # files_hint describes expected changes; --path adds actual tests/config/dependencies.
    paths = set(task.get("files_hint", [])) | set(extra) | {tasks_path, ".claude/sdd.local.md"}
    if task.get("file"):
        paths.add(task["file"])
    feature = Path(tasks_path).parent
    for name in ("spec.md", "sad.md", "test-plan.md", ".size", ".route"):
        if (root / feature / name).exists():
            paths.add(str(feature / name))
    expanded = set()
    for name in paths:
        safe_path(root, name)
        if any(char in name for char in "*?["):
            matches = {p.relative_to(root).as_posix() for p in root.glob(name)}
            matches.update(git(root, "ls-files", "-z", "--", name).decode().strip("\0").split("\0"))
            matches.discard("")
            if not matches:
                raise ValueError(f"File hint matches no working or tracked inputs: {name}")
            expanded.update(matches)
        else:
            expanded.add(name)
    for name in expanded:
        safe_path(root, name)
        if name == "." or "/evidence" in name or name.endswith("tracker.md") or name == str(feature / "tasks"):
            raise ValueError(f"Use concrete source/input paths, not state directories: {name}")
    return sorted(expanded)


def receipt_path(root, tasks_path, task_id):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", task_id):
        raise ValueError("Invalid task ID")
    rel = (Path(tasks_path).parent / "tasks/evidence" / f"{task_id}.json").as_posix()
    safe_path(root, rel)
    path = root / rel
    if path.is_symlink():
        raise ValueError("Evidence file must not be a symlink")
    return path


def capture(root, tasks_path, slug, task, settings, paths, commands):
    receipt = receipt_path(root, tasks_path, task["id"])
    before = snapshot(root, paths, tasks_path)
    record = {"version": 1, "slug": slug, "task": task["id"], "verified": False,
              "base_head": git(root, "rev-parse", "HEAD").decode().strip(),
              "auto_commit": settings["auto_commit"], "paths": paths, "snapshot": before, "gates": []}
    # Invalidate older success before attempting a new gate, including interrupted/failed runs.
    atomic_json(receipt, record)
    for command in commands:
        result = subprocess.run(command, cwd=root, shell=True, capture_output=True, text=True)
        record["gates"].append({"command": command, "exit_code": result.returncode,
                                "stdout": result.stdout, "stderr": result.stderr})
        atomic_json(receipt, record)
        if result.returncode:
            raise ValueError(f"Gate failed ({result.returncode}); evidence saved in {receipt}")
    if before != snapshot(root, paths, tasks_path):
        raise ValueError("Gate changed recorded inputs; review changes and verify again")
    record["verified"] = True
    atomic_json(receipt, record)
    return {"task": task["id"], "evidence": str(receipt), "verified": True}


def reconcile(root, tasks_path, slug, task, settings):
    receipt = receipt_path(root, tasks_path, task["id"])
    status = task.get("status", "todo")
    if status == "blocked":
        return {"task": task["id"], "state": "blocked", "reason": "Retain blocker; explicit retry required"}
    if not receipt.exists():
        return {"task": task["id"], "state": "pending" if status == "todo" else "needs_reconciliation",
                "reason": "No gate evidence; inspect existing code and Git before restarting or skipping"}
    record = json.loads(receipt.read_text())
    if (record.get("version") != 1 or record.get("slug") != slug or record.get("task") != task["id"]
            or record.get("verified") is not True or not record.get("gates")
            or any(g.get("exit_code") != 0 for g in record["gates"])):
        raise ValueError(f"{task['id']}: missing, interrupted or failed gate evidence")
    paths = record["paths"]
    required = task_inputs(root, tasks_path, task, [])
    if not set(required).issubset(paths) or not record.get("snapshot"):
        raise ValueError(f"{task['id']}: evidence omits required inputs")
    if snapshot(root, paths, tasks_path) != record["snapshot"]:
        return {"task": task["id"], "state": "needs_reconciliation", "reason": "Inputs changed since verification"}
    # Search only reachable history; exact feature + task trailers prevent T1 collisions.
    for commit in git(root, "log", "--format=%H", "--fixed-strings", "--grep", f"SDD-Task: {task['id']}").decode().splitlines():
        message = git(root, "show", "-s", "--format=%B", commit)
        trailers = subprocess.check_output(["git", "interpret-trailers", "--parse"], input=message).decode().splitlines()
        if f"SDD-Task: {task['id']}" not in trailers or f"SDD-Feature: {slug}" not in trailers:
            continue
        ancestor = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                                   record["base_head"], commit], capture_output=True)
        if ancestor.returncode == 0 and snapshot(root, paths, tasks_path, commit) == record["snapshot"]:
            return {"task": task["id"], "state": "verified_committed", "commit": commit}
    if settings["auto_commit"] == "off":
        return {"task": task["id"], "state": "verified_uncommitted", "reason": "Verified working copy; commits disabled"}
    return {"task": task["id"], "state": "needs_reconciliation", "reason": "Verified inputs, but no matching reachable commit"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "check"))
    parser.add_argument("--tasks", required=True, help="Project-relative tasks.json")
    parser.add_argument("--task", help="Required for capture; omitted checks all tasks")
    parser.add_argument("--path", action="append", default=[], help="Additional verification input")
    parser.add_argument("--gate", action="append", default=[], help="Authorized shell command; capture only")
    args = parser.parse_args()
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip()).resolve()
        settings = settings_module.load_settings(root / ".claude/sdd.local.md")
        tasks_path = safe_path(root, args.tasks)
        data = json.loads((root / tasks_path).read_text())
        tasks = [task for task in data["tasks"] if not args.task or task["id"] == args.task]
        if not tasks or len({t["id"] for t in data["tasks"]}) != len(data["tasks"]):
            raise ValueError("Missing or duplicate task IDs")
        if args.action == "capture":
            if not args.task or not args.gate:
                raise ValueError("capture requires one --task and at least one --gate")
            paths = task_inputs(root, tasks_path, tasks[0], args.path)
            results = [capture(root, tasks_path, data["slug"], tasks[0], settings, paths, args.gate)]
        else:
            results = [reconcile(root, tasks_path, data["slug"], task, settings) for task in tasks]
        print(json.dumps({"ok": True, "results": results}))
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
