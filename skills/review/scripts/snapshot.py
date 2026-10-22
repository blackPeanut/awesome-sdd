#!/usr/bin/env python3
"""Read-only review snapshots. Prints JSON; never writes files or grants a PASS verdict."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def excluded(name, slug):
    # Only review bookkeeping is excluded, so saving a report doesn't invalidate itself.
    return name.startswith(f"docs/features/{slug}/_review/")


def digest(mode, data):
    return mode + ":" + hashlib.sha256(data).hexdigest()


def committed(root, revision, slug):
    result = {}
    for row in git(root, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if not row:
            continue
        metadata, raw_name = row.split(b"\t", 1)
        name = os.fsdecode(raw_name)
        if excluded(name, slug):
            continue
        mode, kind, oid = metadata.decode().split()
        if kind != "blob":
            raise ValueError(f"Submodule needs separate review evidence: {name}")
        result[name] = digest(mode, git(root, "cat-file", "blob", oid))
    return result


def working(root, slug):
    names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    result = {}
    for name in sorted({os.fsdecode(n) for n in names.split(b"\0") if n}):
        if excluded(name, slug):
            continue
        path = root / name
        # Never follow an ancestor symlink to read another tree.
        if any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents):
            raise ValueError(f"Symlink parent needs separate review evidence: {name}")
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue  # deletion is represented by absence
        if stat.S_ISLNK(info.st_mode):
            result[name] = digest("120000", os.fsencode(os.readlink(path)))
        elif stat.S_ISREG(info.st_mode):
            mode = "100755" if info.st_mode & 0o111 else "100644"
            result[name] = digest(mode, path.read_bytes())
        else:
            raise ValueError(f"Non-file input needs separate review evidence: {name}")
    return result


def snapshot(root, slug, base):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", slug):
        raise ValueError("Expected a simple feature slug")
    base_oid = git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").decode().strip()
    git(root, "merge-base", "--is-ancestor", base_oid, "HEAD")
    # Reject submodules even when their checkout is absent, and detect unresolved merges.
    if git(root, "ls-files", "--unmerged"):
        raise ValueError("Resolve the merge before reviewing")
    if any(row.startswith(b"160000 ") for row in git(root, "ls-files", "--stage", "-z").split(b"\0")):
        raise ValueError("Submodules need separate review evidence")
    before = working(root, slug)
    if before != working(root, slug):
        raise ValueError("Files changed during snapshot; retry when edits have stopped")
    return {"schema": 1, "slug": slug, "base": base_oid,
            "head": git(root, "rev-parse", "HEAD").decode().strip(), "files": before}


def validate(receipt):
    if not isinstance(receipt, dict) or receipt.get("schema") != 1:
        raise ValueError("Invalid review snapshot schema")
    if not isinstance(receipt.get("slug"), str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", receipt["slug"]):
        raise ValueError("Invalid review snapshot slug")
    for key in ("base", "head"):
        if not isinstance(receipt.get(key), str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", receipt[key]):
            raise ValueError(f"Invalid review snapshot {key}")
    files = receipt.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("Missing review input snapshot")
    for name, value in files.items():
        if (not name or Path(name).is_absolute() or ".." in Path(name).parts
                or ".git" in Path(name).parts or excluded(name, receipt["slug"])
                or not isinstance(value, str)
                or not re.fullmatch(r"(?:100644|100755|120000):[0-9a-f]{64}", value)):
            raise ValueError("Malformed review input entry")


def check(root, receipt, require_committed=False):
    validate(receipt)
    current = snapshot(root, receipt["slug"], receipt["base"])
    old, new = receipt["files"], current["files"]
    changed = sorted(name for name in old.keys() | new.keys() if old.get(name) != new.get(name))
    unpublished = []
    if require_committed:
        head = committed(root, "HEAD", receipt["slug"])
        unpublished = sorted(name for name in new.keys() | head.keys() if new.get(name) != head.get(name))
    return {"ok": not changed and not unpublished, "changed": changed,
            "uncommitted": unpublished, "base": current["base"], "head": current["head"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    capture = sub.add_parser("capture")
    capture.add_argument("--slug", required=True)
    capture.add_argument("--base", required=True)
    verify = sub.add_parser("check")
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--committed", action="store_true")
    args = parser.parse_args()
    try:
        root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").decode().strip())
        if args.command == "capture":
            result = snapshot(root, args.slug, args.base)
            validate(result)
        else:
            result = check(root, json.loads(args.receipt.read_text()), args.committed)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("ok", True) else 1
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
