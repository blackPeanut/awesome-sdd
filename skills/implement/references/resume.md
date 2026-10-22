# Completion evidence and recovery

Read this before selecting or skipping tasks, including after a host change. `done` is a status
mirror, not proof of completion. Preserve existing edits, the index and worktrees while inspecting
Git and evidence. Never reset an interrupted task's code to restart TDD. Apply [protect-work.md](../../_shared/protect-work.md)
before recovery edits. Pending [decision changes](../../_shared/change-decisions.md) hold affected
tasks even if older receipts still match; finish propagating the accepted choice before scheduling.

## Capture at GATE

Use [`../scripts/resume.py`](../scripts/resume.py) from the project root with Python 3.10+ and
PyYAML. Validate settings first; the helper repeats that check before writing or executing gates.
Resolve the helper from the installed skill's location, not from the user's project.

```bash
python3 <installed-sdd>/skills/implement/scripts/resume.py capture \
  --tasks docs/features/<slug>/tasks.json --task T1 \
  --path tests/task_test.py --path package.json --path package-lock.json \
  --gate '<detected unit command>' --gate '<detected lint command>'
```

Replace paths and commands with actual project inputs and enabled gates. This **runs** the gates;
do not feed it invented results or a no-op command. Include every actual changed source/test file,
relevant shared dependency, build configuration and lockfile with `--path`; `files_hint`, task
definition, settings and existing spec/SAD/test plan are included automatically. Expand glob hints
against working and tracked files; missing matches require clarification. Avoid broad state/output
directories and never include the evidence directory itself. Symlinks and submodules need separate
verification and are refused by this helper. Record intentionally unavailable integration tiers as
NON-red in the handoff; required integration cannot be replaced by a passing command.

The helper writes `tasks/evidence/<id>.json` atomically, invalidates older success **before** the
first gate, records commands, exit codes and output, and certifies only an unchanged input snapshot
after all commands pass. Review output for secrets before including it in a commit; redact sensitive
output without altering commands, exit codes or snapshots. A failed/interrupted capture cannot be
used as success. Status-only mirror changes are excluded from the input fingerprint.

Capture in the **main integrated checkout**, after applying worker changes and review fixes.
For `per_phase` or compile-coupled batches, capture each included task against the final combined
tree; overlapping changed inputs invalidate earlier receipts. Only the engine/lead/close-layer
writes evidence and status. Worker claims alone are insufficient.

## Commit or leave verified work for the user

For `per_task` / `per_phase`, gate-clean tasks may be written as **provisionally** `done / COMMIT`
immediately before the commit so status and evidence ride with the code. Include the receipt and
all three status mirrors in the task-scoped commit, with `SDD-Feature: <slug>`, one `SDD-Task` per
included task and its `SDD-AC` trailers. Do not release dependents or report completion until the
commit succeeds and reconciliation confirms it. A commit failure blocks the task and preserves
its edits; a crash before failure handling is caught by reconciliation on the next invocation.
Keep trailers in one contiguous final block (one message body/file, not separate `-m` paragraphs).
Never amend any commit merely to satisfy the checker, including one just created in this run;
inspect its content and use the manual reconciliation procedure below if metadata is missing.

With `auto_commit: off`, a successful current receipt permits `done` without any commit. Report
**verified, uncommitted**, keep the edits/evidence, and print optional commit commands. Never stage
or commit as a recovery shortcut. A user-selected change to commit mode requires reconciliation
under that new mode. Within a `per_phase` batch, verified inputs may unblock work inside the same
batch, but that batch is not durably complete until its commit succeeds.

## Reconcile before scheduling

```bash
python3 <installed-sdd>/skills/implement/scripts/resume.py check \
  --tasks docs/features/<slug>/tasks.json
```

`check` is read-only. It compares current inputs with saved successful gate evidence and searches
reachable Git history for exact feature/task trailers and matching committed content. Ignored
settings bind to the receipt but need not be committed. This is evidence for the recorded paths
and environment, not proof that the host selected every necessary gate or input: inspect coverage,
ACs and environment changes before trusting it. New toolchains/services or omitted dependencies
require fresh verification.

| Result | Scheduling and mirror update |
|---|---|
| `verified_committed` | Confirm coverage, synchronize mirrors to `done`, report SHA; skip reimplementation. Applies even when a mirror still says `in_progress` or `review`. |
| `verified_uncommitted` | Allowed only with current `auto_commit: off`; synchronize `done`, report verified working copy without a matching tagged commit. Preserve edits. |
| `pending` | No previous completion evidence and status absent/`todo`; inspect existing edits, then select normally when dependencies are verified. |
| `needs_reconciliation` | Do not skip or release dependents. Inspect diff, history and ACs. Re-run required gates on existing work; then finish a missing commit only when current settings permit it, or report a blocker. |
| `blocked` | Preserve blocker and ask whether to retry or leave blocked, including its dependents. |

Malformed/failed/interrupted receipts or helper errors stop scheduling; show the error and inspect
before recapturing. Legacy `done` tasks without receipts must be reverified. For older/manual
commits without trailers, inspect reachable commit content explicitly and rerun gates; document
that manual reconciliation and SHA rather than inventing trailers, amending history or creating an
empty duplicate commit. If completion cannot be established, leave unresolved and ask only for the
missing decision. Never downgrade all `in_progress`/`review` tasks blindly to `todo`.

After reconciliation, update task markdown, tracker, tasks.json and any native task mirror from the
verified result. If a crash splits those writes, repeat reconciliation; their inconsistency never
overrules the evidence. Dependencies require verified completion, not a raw `done` string.
