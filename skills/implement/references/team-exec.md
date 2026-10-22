# Agent-team execution (`team_mode: true`)

**Capability gate:** This backend recipe runs only when the shared `runtime.team_backend` is true. All role dispatch and model/effort selection still use the agent roster. Otherwise use sequential TDD; generic Codex delegation is not this scheduler.


When the decision tree selects the team, the engine becomes a **lead** coordinating three roles through a shared task list, one git worktree per agent, with commits serialized by the lead. Use this for features with genuine parallel width and a desire for an independent review pass.

## Roles (the shipped subagents)

Resolve each role through the shared runtime and [agent roster](../../_shared/agent-roster.md).

- **[`test-author`](../../../agents/test-author.md)** (`test-author`) — RED only. Writes the failing test(s) for a task's `acs`, runs them, classifies the first run (GOOD/BAD/false-pass/NON-red per [`tdd-loop.md`](./tdd-loop.md)), and hands over the quoted failing line. Never writes production code.
- **[`implementer`](../../../agents/implementer.md)** — GREEN + REFACTOR + GATE. Takes a task with its red test, writes the minimal code to pass, refactors while green, runs the per-task gate. Never weakens the test.
- **[`reviewer`](../../../agents/reviewer.md)** — read-only. Two stages: stage-1 spec/AC compliance (does the change satisfy the `acs` it claims?), stage-2 quality (conventions, edge cases, anti-patterns). Has no write tools.

## Setup

1. Create the team (`TeamCreate`). Seed a shared **TaskList** from `tasks.json` — **the full task text goes in each task body**, and that text is the task's own markdown: read `tasks.json`'s `file` field (`docs/features/<slug>/tasks/<task-slug>.md`) and put **its body** in the TaskList entry, alongside the JSON's `id`, `title`, `dod` and `files_hint`. Do not reassemble a brief from JSON fields + spec §5 — `tasks` already inlined the §5 acceptance criteria verbatim into that file, with provenance signatures, and reassembling loses them. If a task has no `file` (an older breakdown), fall back to the JSON fields + spec §5 and say so in the banner. Teammates do NOT read the plan or the conversation; the task body is their whole brief, and upstream is their fallback when a slice falls short ([`./inputs.md`](./inputs.md)).
2. Give each agent its own git **worktree** under `.worktrees/<agent>` (`isolation: worktree` is required for the team — the guard enforces it). No two agents share a tree.
3. Resolve per-role model and effort through the roster and runtime; print effective values, including inheritance, in the banner.

## Flow per task

`test-author` (RED) → `implementer` (GREEN+REFACTOR+GATE) → `reviewer` (review). A task advances only when its `deps` have reconciled completion per [resume](./resume.md). The lead pulls ready tasks off the DAG and assigns them; up to `max_parallel_agents` run at once. After **every** handover the lead writes the task's status + step to its task file, `tasks/tracker.md` and `tasks.json` — the lead is the only writer of those files; teammates never touch them ([`tdd-loop.md`](./tdd-loop.md) §Status protocol). When the session has `TaskCreate` / `TaskUpdate`, teammates may claim and complete the native tasks themselves; the lead mirrors the step into `activeForm` and fills any gap.

## Serialization lanes (the lead enforces)

Even with worktrees, some tasks must not run concurrently:

- **`layer: migration`** — migrations are an ordered sequence (e.g. golang-migrate's numbered files); run them one at a time, in order. Each migration task first **promotes** its staged `docs/features/<slug>/migrations/<NN>_*` file into the live tree (next free number, in ordinal order) before applying it — see [`./inputs.md`](./inputs.md).
- **Overlapping `files_hint`** — two tasks that touch the same file run in the same lane (serialized), or the second rebases on the first. Compute lanes from `files_hint` intersections up front.
- **Compile-coupled pair** — a shared-contract change + its implementer(s) share the contract file in `files_hint`, so they land in one lane by the rule above; additionally the lead gives the pair a synthetic dep (contract → implementer) and closes it with **one shared gate + one commit** carrying every task's `SDD-Feature`/`SDD-Task`/`SDD-AC` trailers ([`tdd-loop.md`](./tdd-loop.md) §COMMIT) — neither task is separately committable green.

Tasks in different lanes with satisfied deps run in parallel; tasks in the same lane queue.

## Commits

The lead **serializes commits in dependency order** regardless of when the work finished, and makes each commit **itself** — teammates never commit to the feature branch. For a task that passed its gate (and review):

1. Apply the teammate's worktree diff in the main checkout: `git -C .worktrees/<agent> diff --binary HEAD` (plus any untracked files the task created) applied with `git apply --3way`. A conflict means two lanes overlapped — stop and resolve it before anything else commits.
2. Capture enabled gates and complete input fingerprints in this integrated checkout per [resume](./resume.md). Then set provisional `done` / `COMMIT` in all three mirrors.
3. Commit the task's code paths **plus** its evidence receipt and those three status files in one commit, with the `SDD-Feature`/`SDD-Task`/`SDD-AC` trailers ([`tdd-loop.md`](./tdd-loop.md) §COMMIT), using `git commit -- <paths>`.
4. Confirm completion by reconciliation before releasing dependents. Preserve the worktree on any gate/commit/recovery failure. Only after confirmed success, reset the teammate's worktree to the new feature-branch HEAD before it takes its next task.

`auto_commit: per_phase` → the lead holds each gate-verified task's applied diff + status files in the main checkout and commits once per Kahn layer, when every task of that layer is gate-verified or `blocked`; recapture affected receipts against the final combined tree before committing (one commit, every task's trailers); teammates' worktrees reset to that commit. (`off` never reaches this mode — the decision-tree guard downgrades it to sequential.)

The history is linear and bisectable even though the work was concurrent.

## Don't over-orchestrate

- **<4 tasks → no team.** The eligibility check already forbids it; if you somehow got here with a tiny DAG, downgrade to sequential. Coordination overhead exceeds the gain.
- A red that survives escalation in one lane follows `stop_on_red`: halt the whole team, or drop that task + auto-block its dependents and let other lanes finish ([`escalation.md`](./escalation.md)).
- Tear the team down at the end; remove worktrees (they auto-clean if unchanged).
