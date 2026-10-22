---
name: implement
model: inherit
effort: medium
agents: [test-author, implementer, reviewer]
description: >
  Use to implement a feature from its tasks.json with test-driven development — writes a failing
  test first, makes it pass, refactors, gates, and commits per task. Triggers on "implement {slug}",
  "build {slug}", "TDD {slug}", "code up the tasks for {slug}", "/awesome-sdd:implement {slug}". Reads
  docs/features/{slug}/tasks.json + the upstream artifacts, detects the repo's test/lint/vet
  commands stack-agnostically, builds a dependency DAG, and runs one of three modes — sequential
  sequential TDD, an agent team (TeamCreate), or a dynamic Workflow — chosen from settings +
  DAG shape with graceful fallback. Hard-refuses if tasks.json is missing.
---

**English only:** Write all conversation, questions, options, progress updates, handoffs, reports, and generated document prose in English. Apply the [language policy](../_shared/artifact-language.md) even when settings or source documents use another language.

**Host runtime:** Resolve and reuse [host capabilities](../_shared/host-capabilities.md) before this protocol. Dispatch roles through the [agent roster](../_shared/agent-roster.md); render questions and handoffs through that runtime. Model/effort frontmatter applies only where the host supports it.

# Skill: implement

The implementation engine. It turns `tasks.json` into committed, tested code through a strict TDD cycle per task — `SELECT → RED → GREEN → REFACTOR → GATE → COMMIT` — and orchestrates that cycle in one of three modes (sequential / agent-team / dynamic-workflow) picked by an unambiguous decision tree. Everything is stack-agnostic: the test, lint, and vet commands are **detected**, never hard-coded.

This file is the spine. Each step delegates to a file in `references/`.

## Owner

Tech Lead drives; the engine runs the cycle. The three subagents ship with the plugin: [`test-author`](../../agents/test-author.md) (RED), [`implementer`](../../agents/implementer.md) (GREEN/REFACTOR/GATE), [`reviewer`](../../agents/reviewer.md) (read-only review).

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** `docs/features/<slug>/tasks.json`. Missing → «run `tasks <slug>` first».
- Read for context (the agents read these directly, not via paraphrase): `spec.md` (AC), `data-model.md` + the **staged** migrations under `docs/features/<slug>/migrations/` (a `layer: migration` task **promotes** these into the live `migrations/` tree — see [`./references/inputs.md`](./references/inputs.md)), `contracts/openapi.yaml`, `test-plan.md`, `sad.md`, Accepted `adr/`.
- Settings: `.claude/sdd.local.md` — created with documented defaults by whichever of the six creating skills runs first (normally `specify` at the backbone start; `implement` creates it too if you jump straight here) per [`../_shared/settings-file.md`](../_shared/settings-file.md); values are tuned only by [`../config/SKILL.md`](../config/SKILL.md). Which keys this engine reads → [`./references/settings.md`](./references/settings.md).

## Protocol

1. **Preconditions.** Apply [work protection](../_shared/protect-work.md) before editing, changing branches or integrating worker output. Complete the shared strict settings preflight before any mutation or dispatch. Verify `tasks.json` exists and parses; load the upstream artifacts list. Detail → [`./references/inputs.md`](./references/inputs.md).
2. **Ensure the settings file (first thing, after this skill's own gate).** If `.claude/sdd.local.md` is absent, create it now from the canonical template — documented defaults + the self-documenting body — and patch `.gitignore`; if it exists, read it and never overwrite. The one procedure lives in [`../_shared/settings-file.md`](../_shared/settings-file.md). Creating is unconditional; **changing values is only ever offered by [`config`](../config/SKILL.md)**. Say one line: «`.claude/sdd.local.md` created with documented defaults — `/awesome-sdd:config` to tune it». Which keys this engine then reads, and how model + effort resolve at dispatch → [`./references/settings.md`](./references/settings.md).
3. **Detect commands.** Run the stack-agnostic cascade (settings override → Makefile → package scripts → language manifests → Docker probe for the integration tier) to resolve unit / integration / lint / vet commands. Print what was detected. → [`./references/command-detection.md`](./references/command-detection.md).
4. **Build the DAG + resume.** Parse `tasks.json`, validate `deps` is acyclic, topologically sort into phases (Kahn). Compute `task_count`, `longest_chain`, `parallel_width`. Mark serialization lanes (`layer: migration`; tasks with overlapping `files_hint`). Reconcile every task's status with Git and successful gate evidence before skipping or scheduling → [`./references/resume.md`](./references/resume.md). Never blindly skip `done` or reset interrupted work. Verified uncommitted work is complete when `auto_commit: off`; unresolved tasks hold their dependents.
5. **Pick the mode.** Run the decision tree (below; full form → [`./references/decision-tree.md`](./references/decision-tree.md)). Apply the guards.
6. **Generate the run-plan.** Sequential → an ordered task list. Team → a shared TaskList with the full task text in each body. Workflow → a generated `Workflow` script (DAG → Kahn phases → fan-out pipeline → one `close-layer` writer per layer). → [`./references/team-exec.md`](./references/team-exec.md) / [`./references/workflow-exec.md`](./references/workflow-exec.md). When the session has `TaskCreate` / `TaskUpdate`, also create one native task per `T<n>` — a mirror of the status files, never their source; no such tools → skip silently.
7. **Banner + branch + roadmap.** Print the active mode and the settings that drove it: `mode=<…> tdd=<…> isolation=<…> parallel=<n> integration=<…>`. Include one short model/effort line from the [roster](../_shared/agent-roster.md), labelling requests, inheritance and inline fallback accurately. The user sees how the engine will behave before it acts. Then settle the branch per `branch_strategy` ([`./references/inputs.md`](./references/inputs.md) §Repo state). Then, if `docs/roadmap.md` exists and has a step for this feature, set that step's `Status: building` (unless it already is) and commit it alone per [`../_shared/write-and-commit.md`](../_shared/write-and-commit.md) — `implement: <slug> roadmap.md building` (honours `auto_commit: off` like every other commit).
8. **Execute** in the chosen mode. Every task runs the TDD cycle → [`./references/tdd-loop.md`](./references/tdd-loop.md), and **every observed transition or worker boundary is written to disk as it happens** — status + step in the task file, `tasks/tracker.md` and `tasks.json` (+ the native task list when present), by exactly one writer per mode (engine / lead / `close-layer`) → §Status protocol there. A `layer: migration` task first **promotes** its staged migration(s) (`docs/features/<slug>/migrations/<NN>_*`) into the live `migrations/` tree — assigning the real sequence number / timestamp per the repo's convention, in ordinal order — *then* applies + reverts them; detail → [`./references/inputs.md`](./references/inputs.md).
9. **Per-task gate + commit.** After GREEN+REFACTOR: unit + (integration if available) + lint + vet must be clean, capture evidence and commit (unless `auto_commit: off`) with trailers `SDD-Feature: <slug>`, `SDD-Task: <id>` and `SDD-AC: <id>` (one per satisfied AC). Tasks in one **compile-coupled lane** (shared contract file in `files_hint`) pass one shared gate and one commit carrying every task's trailers — the sanctioned exception in [`./references/tdd-loop.md`](./references/tdd-loop.md) §COMMIT. The receipt and provisional `done` mirrors ride in the commit; confirm completion by [reconciliation](./references/resume.md) before skipping or releasing dependents. With commits off, report verified uncommitted work. Escalation or `stop_on_red` → `blocked` with the reason (dependents too) → [`./references/escalation.md`](./references/escalation.md).
10. **Summary + hand off.** Report covered AC, commits made (with `SDD-Task` trailers) or verified uncommitted work, any task unresolved/dropped/blocked, and the per-task gate results. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* (covered AC, commits with short SHAs + `SDD-Task` trailers, gate results, tasks left `blocked` with reasons) + *Review* (the committed or verified working diff + `tasks/tracker.md`) + *Run next* (`/clear`, then `/awesome-sdd:review <slug>` — a clean-context pass over the whole diff), then `/awesome-sdd:ship <slug>`. In team mode the [`reviewer`](../../agents/reviewer.md) may also run per-task, but the authoritative independent review of the whole change lives in the `review` skill — `implement` does not self-certify.

## Decision tree (compact)

```
parallel_eligible := isolation==worktree AND max_parallel>1 AND parallel_width>=2
                     AND (size in {M,L,XL} OR task_count>=4)

if team_mode AND parallel_eligible AND runtime.team_backend:                          → AGENT TEAM (TeamCreate) over the DAG
elif workflow_mode=="auto" AND parallel_eligible AND runtime.workflow_backend: → DYNAMIC WORKFLOW
else:                                                        → SEQUENTIAL TDD (topo order)
```

**Guards (apply before dispatch):** `team_mode` but not eligible → warn + downgrade to the next mode. `max_parallel>1` with `isolation: inplace` → clamp parallel to 1 (no two agents edit one tree). `workflow_mode: off` → never generate a Workflow. `tdd: false` → skip RED (warn loudly — you lose the safety net). `require_integration: always` but Docker absent → **BLOCK** before dispatch; `auto` → run unit-only and mark integration NON-red; `never` → skip the integration tier. Full table → [`./references/decision-tree.md`](./references/decision-tree.md). Graceful degrade: if `Workflow`/`TeamCreate` is unavailable at runtime, fall through to sequential.

## TDD cycle (per task)

`SELECT → RED → GREEN → REFACTOR → GATE → COMMIT`. The RED step is load-bearing: write the test first, run it, and **classify the first run** — GOOD red (assertion fails / unimplemented) vs BAD red (the test itself won't compile → fix the test) vs false-pass (green immediately → the test is too weak, strengthen it) vs NON-red (skipped because Docker is absent → governed by `require_integration`, counts as neither red nor green). Quote the failing line before writing any production code. Escalation on persistent red → [`./references/escalation.md`](./references/escalation.md): supported effort increase → retry → split the task → if the test encodes a wrong AC, **ask a human** (never weaken the test) → undo only task-owned edits when safe, otherwise preserve the files and report the blocker. `stop_on_red` decides halt vs drop-and-continue (dependents auto-block).

## Definition of Done

- Every task has reconciled completion: committed with gate evidence and `SDD-Feature`/`SDD-Task`/`SDD-AC` trailers, verified uncommitted with `auto_commit: off`, or explicitly reported as unresolved/dropped/blocked with its reason.
- Unit gate green; integration green where available (or NON-red recorded with the policy reason); lint + vet clean per the detected commands.
- The active mode + settings were printed in the banner before execution.
- `tracker.md`, every task file and `tasks.json` reflect the final status + step of every task (they were updated at each observed transition or worker boundary); the summary reports the gate results and hands off to `review` (the independent review gate) — `implement` does not self-certify the whole change.
- The per-task GATE (unit + integration + lint + vet) is this skill's **structural self-check** ([`../_shared/self-check.md`](../_shared/self-check.md)); its results are reported in the handoff.

## Anti-patterns

- **Code before the test.** RED first, always (unless `tdd: false`, which warns).
- **Weakening a test to make it pass.** If the AC is wrong, ask a human and fix the AC; never edit the test to be less strict.
- **Skipping the RED classification.** A false-pass that looks green hides a useless test.
- **Parallel agents editing one working tree.** Parallelism requires worktree isolation — the guard clamps it.
- **Committing with a red or skipped gate** and calling it done. A NON-red integration tier must be labelled, not hidden.
- **Spawning a team for <4 tasks** — coordination overhead exceeds the gain; the eligibility check forbids it.
- **Claiming integration passed when Docker was absent.** Report NON-red honestly.
- **Status only at the end.** A tracker that jumps from `todo` to `done` tells nobody where a crashed run stopped. Record each observed transition or combined worker boundary as it happens.
- **Two writers of the status files.** Teammates and parallel workflow stages never write them; the engine / lead / `close-layer` does.

## References & template

`inputs.md` · `settings.md` · `command-detection.md` · `decision-tree.md` · `tdd-loop.md` · `resume.md` · `team-exec.md` · `workflow-exec.md` · `escalation.md` — all in [`./references/`](./references/).
