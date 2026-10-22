# Write as you go, commit per document — the disk + git contract every artifact skill follows

> **Reference-only.** Not a skill. Every skill that writes a pipeline document follows this file
> for **when** the document lands on disk and **how** it is committed. Skills keep a one-line
> pointer («Commit per [`write-and-commit.md`](../_shared/write-and-commit.md)») plus their own
> list of documents; the rules live only here.

## 1. Progressive writes

- **Protect existing work first**, per [protect-work.md](./protect-work.md). Checkpoint paths
  before editing; existing content and staging survive failures and interrupted runs.
- **Validate settings first**, per [reading semantics](./settings-file.md#reading-semantics).
  Invalid settings stop writes and commits; do not fall back to defaults. Revalidate changed settings.
- **Bootstrap at the first write point.** The first time the skill has something real to write,
  it copies the artifact's template to its target path (frontmatter stamped, every section still a
  placeholder). From then on the file on disk is the artifact — not a draft in the conversation.
- **Write each resolved unit immediately.** A section, an AC, a row, a step, a screen, a finding —
  whatever the skill's unit is — goes to disk right after its resolution: `Approve`, `Edit` (after
  the final answer), `Save as Open Question` (the OQ row too), or, for a skill with no dialogue,
  right after it is generated. `Drop` writes the removal. Never hold the whole document in memory
  and write it once at the end.
- **Downstream readers read the disk.** The clean-context critic (read-only) reads the file from
  disk; the skill patches the file with whatever the user accepts from its findings. The
  structural self-check ([`self-check.md`](./self-check.md)) reads the disk too.
- **Exceptions** (no progressive write, by design):
  - `interview` in its no-write mode (Plan Mode, headless, outside a git repo) — it writes nothing
    at all; its own SKILL.md rules win.
  - single-shot writers whose whole output is one token or one line (`classify-size`'s `.size` +
    `.route`) — written once, which already *is* immediately.

## 2. Commit at the end of the step — one commit per document

**Code stages differ.** `implement` and `fix` commit **per task / per fix** after that unit's GATE (with `SDD-Task` / `SDD-Fix` trailers) — their own SKILL.md rules govern; the guards in §3 and the `git commit -- <paths>` discipline still apply. Everything below is about **document** stages.

**Order is fixed:** structural self-check passes → commits → stage-handoff block. A failed or
unresolved self-check means **zero commits** — say so in the handoff and leave the files
uncommitted for the user to inspect. No commits per section or per decision: progressive writes
protect against a lost session; commits mark a finished, checked document.

**One commit per document the step created or changed.** These sets are indivisible and go in
**one** commit:

| Set | Why together |
|---|---|
| a migration pair `*.up.sql` + `*.down.sql` | one change; a lone half is broken |
| `.size` + `.route` | one classification |
| the whole `tasks/` directory + `tasks.json` | one model rendered twice (`tasks` contract) |
| a review report + its named input snapshot | the verdict and the content it reviewed form one evidence unit |
| a skeleton materialized by `scaffold` | one bootable unit |

An **ADR is always its own commit**, separate from `sad.md` / the architecture map that cites it.

**Commands (per document):**

```bash
git status --porcelain -- <paths>          # empty → nothing changed, skip this commit
git add -- <paths>
git commit -m "<stage>: <slug> <doc>" -- <paths>
```

- An empty `git status` is normal (`clarify` that resolved nothing in-file, `review` with no
  spec defer, an unchanged `.pen`) — skip silently, don't create an empty commit.
- `git commit -- <paths>` commits exactly those paths, so unrelated changes the user has staged
  elsewhere stay staged and out of the commit.
- **Never** `git add -A` / `git add .`, `--no-verify`, `--amend`, force anything.
- **Message:** English, `<stage>: <slug> <doc>` — e.g. `specify: checkout-v2 spec.md`,
  `data-model: checkout-v2 migration 0003_orders`, `design: checkout-v2 ADR-0004 event bus`.
  Repo-level documents drop the slug (`survey: architecture-map.md`).
- **The `.gitignore` patch** from the settings-file procedure ([`settings-file.md`](./settings-file.md))
  rides in the step's **first** commit. The settings file itself is never committed.
- **Branch:** document stages commit to the **current** branch. `branch_strategy` is an
  `implement` rule only.

## 3. Guards — when not to commit

| Situation | Do |
|---|---|
| not a git repo | write files, no commits; say so in *What I did* |
| merge / rebase / cherry-pick in progress (`.git/MERGE_HEAD`, `rebase-merge/`, `rebase-apply/`, `CHERRY_PICK_HEAD`) | don't commit; say so; the user finishes their operation first |
| `auto_commit: off` in `.claude/sdd.local.md` | don't commit; print the ready-to-run commands from §2 in the handoff |
| a pre-commit hook fails | show its output, stop committing; never bypass with `--no-verify` |
| a commit path contains prior user edits (staged, unstaged or untracked) | leave it uncommitted unless the user explicitly authorized including those edits; follow [protect-work.md](./protect-work.md). A warning alone is not consent |

`auto_commit` is shared by every stage: `per_task` and `per_phase` both mean «commit» for a
document stage (the task/phase distinction only shapes `implement`); `off` means «print the
commands, don't run them».

## 4. Report

*What I did* in the stage-handoff block ([`handoff.md`](./handoff.md)) lists every commit made,
short SHA + message, one per line:

```
- committed `a1b2c3d` specify: checkout-v2 spec.md
- committed `d4e5f6a` specify: checkout-v2 .size+.route
```

A skipped commit (nothing changed, guard hit, `auto_commit: off`) is named with its reason.

## Anti-patterns

- **The whole document written at the end.** A crash or a `/clear` loses every decision made so far.
- **Per-section commits.** Twelve commits for one SAD bury history; the disk already holds the
  partial work.
- **Committing before the self-check.** A commit should mark a checked document.
- **`git add -A`.** Sweeps in the user's unrelated work.
- **One commit for every document of the step.** An ADR, a migration pair and the spec revert
  independently; keep them apart.
