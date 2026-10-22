# Protect existing work

Read before the first project edit, including task status, generated documents and worker
integration. This applies to `implement`, `fix` and document stages, with commits on or off.

## Before editing

- Inspect the working diff, staged diff and untracked files. Record the branch and HEAD, which
  paths already contain changes, and which changes are staged. A dirty file is not owned by SDD
  merely because it appears in `files_hint`.
- Before touching a path, save its exact current contents (including absence and file mode) in
  a durable local checkpoint outside the tracked project, with a unique run/task identifier.
  Record the checkpoint location in the task's recovery note. Include untracked files you will
  edit; a Git diff alone does not save them. Do not place secrets or private backups in commits.
- Keep a before/after patch for SDD's edits and refresh the after-image after each edit. Capture
  a new path before first touching it. Preserve the original before-image across retries and
  interrupted runs. Missing or uncertain ownership means no automatic undo of that path.
- If a requested edit overlaps existing work, preserve it and make the smallest necessary edit.
  Ask only when the intended result conflicts with that work. Do not stash, reset, clean, switch
  away from dirty work, or create a checkpoint commit as a shortcut.

## When a task fails

Undo only the failed task's own changes, relative to its checkpoint. The target is the state
before that task, which may contain earlier successful **uncommitted** tasks and user edits.
“Last green” never means resetting to a commit.

Before undoing a hunk, compare the current content with the recorded after-image. If another
edit overlaps, ownership is uncertain, or the checkpoint is missing, leave that content in
place and report the blocked task. Do not overwrite the entire file from a backup in that case.
Delete a newly created file only when it was absent at baseline and still exactly matches the
task's recorded output. Do not delete a directory recursively. Leave the index untouched.
Never use `reset --hard`, broad `restore`/`checkout`, `clean`, or blanket stash operations for
failure recovery. Refactor rollback follows the same rule.

Compare the remaining diff and staged diff with the baseline after undo. Confirm that earlier
user edits, earlier completed task edits and newly arrived changes are still present. A failed
undo stops recovery; do not retry with a broader destructive command.

Keep the failure reason and checkpoint location available for resume. Report remaining failing
checks honestly; preserving another person's work takes priority over a clean tree. If retained
changes affect another task, block that task too; continue only genuinely independent work.

## Before committing or integrating workers

Path-scoped commits still take the whole on-disk file. If a path contains earlier user work,
including staged or untracked work, do not stage or commit it without explicit authorization to
include those changes. Finish and verify the requested edit, leave it uncommitted, and ask the
one remaining choice if a commit is required. Never temporarily unstage the user's changes to
work around this rule. Unrelated staged paths stay staged.
Do not offer a ready-to-run whole-file commit command that would silently include those edits.

Each worker owns only its assigned changes in its isolated checkout. Before applying those
changes, the lead checkpoints the destination and checks for overlapping user or worker edits.
Conflicts stop integration of that patch; they are not permission to replace the destination.
Retain checkpoints until completion/recovery is verified; never silently discard the only copy.
