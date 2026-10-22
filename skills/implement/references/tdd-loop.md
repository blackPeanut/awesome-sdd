# TDD loop — the per-task cycle (step 8)

Every task runs `SELECT → RED → GREEN → REFACTOR → GATE → COMMIT`. This is the same cycle whether the runner is the sequential agent, a team `implementer`, or a Workflow stage. The RED step is the load-bearing one — skip its discipline and the whole method collapses into "write code, write a test that happens to pass".

Every observed transition or dispatched worker boundary is written to disk as it happens — see **Status protocol** at the end of this file.

## Sequential role dispatch on Codex

Sequential means one active writer, not necessarily one model. When native delegation is
available and authorized, dispatch `test-author` for RED, wait for its complete report, then
`implementer` for GREEN + REFACTOR + GATE. Apply [Codex dispatch](../../_shared/codex-dispatch.md)
at each boundary. These are bounded workers in the same task checkout; do not leave a previous
writer running or spawn a team. With TDD off, dispatch only the implementer. The lead remains
the only writer of task/status mirrors and completion evidence and owns task commits; explicitly
instruct workers not to update those files or commit. Supply the test path, command, actual
failure and accepted task requirements to the implementer. Reconcile worker changes, capture
gate evidence and commit through the existing protocol. Whole-feature review still runs in the
separate review stage. Without delegation, execute inline and report inherited settings.

Before the combined worker starts, record `in_progress` / `GREEN+REFACTOR+GATE`. Refine that
step only from progress the lead actually observes; otherwise keep the combined step until the
worker returns, then record `GATE` while capturing evidence. A crash leaves unfinished work,
which resume reconciles before any retry. Do not invent intermediate progress.

## SELECT

Pick the next task whose `deps` are all `done` — completion established by [reconciliation](./resume.md), never by a status string or conversation memory alone. In sequential mode that's the topo order; in parallel modes the orchestrator hands it out. **Read the task file first** — `tasks.json`'s `file` field, `docs/features/<slug>/tasks/<task-slug>.md`: it carries the §5 acceptance criteria verbatim, the data delta, the API slice and the edge cases, each signed with its source. `spec.md §5` and the relevant `test-plan.md` rows are the **fallback**, opened when a slice is insufficient, ambiguous, or contradicted by the code ([`./inputs.md`](./inputs.md)); a task with no `file` falls back to them outright. Know, before writing anything, what observable outcome the test will assert.

Before changing a file or status mirror, establish the task checkpoint per
[protect-work.md](../../_shared/protect-work.md). On resume reuse the original checkpoint;
never redefine interrupted edits as a clean baseline. The same rule applies in every mode.

## RED — write the failing test first

1. Write the test(s) for this task's `acs` **before any production code**. Put them where the repo keeps tests for that layer (detected, not assumed).
2. Run the unit command. Capture the output.
3. **Classify the first run** — this is mandatory and must be stated aloud:

   | Class | What it looks like | Action |
   |---|---|---|
   | **GOOD red** | test compiles, runs, fails on an assertion or «not implemented» | proceed to GREEN |
   | **BAD red** | the test itself won't compile / import-errors / references a symbol that the test got wrong | the test is broken, not the code — **fix the test**, re-run, re-classify |
   | **false-pass** | green on the very first run, before any production code | the test is too weak (asserts nothing real) — **strengthen it** until it's GOOD red |
   | **NON-red** | skipped because its dependency is unavailable (e.g. Docker absent for an integration test) | not a pass and not a fail — record NON-red, governed by `require_integration` |

4. **Quote the failing line** (the assertion + expected-vs-actual, or the «undefined: X» line) before writing any production code. This is the proof that the test exercises the right thing.

A task with only a NON-red integration test and no unit coverage cannot be driven by TDD locally — write the unit-level RED too, and let the integration RED land in CI (the proving-run pattern).

## GREEN — minimal code to pass

Write the **least** code that turns the quoted failing assertion green. No speculative generality, no unrelated edits, nothing outside the task's `files_hint`. Re-run the unit command; confirm the previously-quoted failure is now green and nothing else broke.

## REFACTOR — clean while staying green

Tidy names, extract helpers, remove duplication — re-running the unit command after each change. If a refactor goes red and isn't trivially fixable, undo only that refactor's recorded edits per [protect-work.md](../../_shared/protect-work.md); preserve overlapping work and report a blocker if undo is uncertain.

## GATE — the task isn't done until this is clean

Run, per the detected commands + settings:

- **unit** — must be green.
- **integration** — green if available; NON-red recorded if Docker is absent under `require_integration: auto`; BLOCK was already enforced for `always`.
- **lint** (if `gate_lint` and a linter resolved) — clean.
- **vet/typecheck** (if `gate_vet` and a command resolved) — clean.

Capture the actual enabled gate commands and input fingerprints with the [evidence helper](./resume.md#capture-at-gate). Its successful receipt is required before completion; a worker report alone is insufficient.

Any hard-gate failure (unit red, or integration red when it ran, or lint/vet errors) → the task is not done. Fix, or escalate (see [`escalation.md`](./escalation.md)).

## COMMIT — task-scoped, traceable

Apply the [shared commit guards](../../_shared/write-and-commit.md#3-guards--when-not-to-commit), including prior user edits in the same path. When `auto_commit: per_task`, commit only this task's files with a message like:

```
<type>(<slug>): <task title>

<one-line what + why>

SDD-Feature: <slug>
SDD-Task: T3
SDD-AC: AC-02
SDD-AC: AC-04
```

One `SDD-AC` trailer per satisfied AC; `SDD-Feature` plus `SDD-Task` identify the task across features.
Follow [completion and recovery](./resume.md): capture gate evidence, write provisional `done`
status immediately before committing, include the receipt and all three status mirrors with the
code, then confirm the reachable commit before reporting completion or releasing dependents.
`per_phase` batches verified tasks; `off` records verified uncommitted completion without staging
or committing. A provisional `done` alone is never sufficient to skip work after an interruption.

**Compile-coupled lane exception.** Tasks in one compile-coupled lane (a shared-contract change + its implementer(s), marked by `tasks` via the shared contract file in `files_hint`) cannot each be committed green alone — the contract change breaks every implementer at compile time. They run **one shared GATE and one commit**: the commit carries an `SDD-Task` trailer **per task** and all of their `SDD-AC` trailers together, and the body names the coupling (e.g. «compile-coupled: T3 interface change + T4 implementation»). This is a sanctioned exception to task-scoped commits, not a license to batch unrelated tasks.

In parallel modes the **lead serializes commits in dependency order** even though the work happened concurrently — the history stays linear and bisectable.

## Status protocol — live task status on disk

`implement` keeps every task's progress on disk, updated **at each observed transition and before/after worker dispatch**. A
crashed or interrupted run can leave partially updated mirrors; the next run reconciles them
against gate evidence and Git before scheduling.

**Model.** `status` ∈ `todo · in_progress · blocked · review · done`; `step` ∈
`SELECT · RED · GREEN · GREEN+REFACTOR+GATE · REFACTOR · GATE · REVIEW · COMMIT` (for `blocked`, the reason). Three status
files carry it, all written together:

| File | Carries |
|---|---|
| `tasks/<task>.md` frontmatter | `status:` + `step:` |
| `tasks/tracker.md` | the task's row — **Status** + **Step** columns |
| `tasks.json` | `status` (optional key; absent = `todo`) — `step` is markdown-only |

**Transitions** (write all three files immediately at each):

| Event | status / step |
|---|---|
| task picked in SELECT | `in_progress` / `SELECT` |
| `test-author` dispatched (or RED begins inline) | `in_progress` / `RED` |
| RED handover accepted (GOOD red quoted) | `in_progress` / `GREEN` |
| sequential combined `implementer` dispatched | `in_progress` / `GREEN+REFACTOR+GATE`; refine only from observed progress; on return record `GATE` for evidence capture |
| `implementer` reports green through a live progress event | `in_progress` / `REFACTOR`, then `GATE` when the gate starts |
| per-task `reviewer` dispatched (team mode, or when configured) | `review` / `REVIEW` |
| verified commit about to run | provisional `done` / `COMMIT` — rides in the commit, but is not completion evidence |
| `auto_commit: off`, receipt verified | `done` / `GATE` — verified uncommitted; no Git mutation |
| the commit fails (pre-commit hook, conflict) | `blocked` / `COMMIT — <first line of the failure>` — preserve edits; a crash before this update is caught by evidence reconciliation |
| escalation exhausted, or `stop_on_red` halts | `blocked` / `<step> — <reason>` (e.g. `GATE — lint red after 3 retries`) |
| dependents of a blocked task (`stop_on_red: false`) | `blocked` / `dep T<n> blocked` |

`tdd: false` skips the `RED` / `GREEN` handover rows; the rest stand.

**Resume.** Run [reconciliation](./resume.md#reconcile-before-scheduling) on every task before
scheduling. It handles committed work, verified uncommitted work with commits off, interrupted
commits and missing/stale evidence. Never blindly skip `done` or reset `in_progress` / `review`.
Transit rows in another task's commit are expected and are reconciled by the same rules.

**Who writes — one writer per run, never two.**

- **Sequential** — the engine writes the three files before dispatch, on observed progress, and
  after each worker returns. Combined workers use the explicit combined step above. Inline work
  records each transition directly. The status files ride in the task's own commit.
- **Team** — the **lead** writes them after every teammate handover; teammates never touch the status
  files. The lead also makes the task's commit: it applies the teammate's worktree diff in the main
  checkout, adds the status files, and commits once ([`team-exec.md`](./team-exec.md) §Commits).
- **Workflow** — the script has no file-system access, so stage agents **do not** write status. After
  each Kahn layer the generated script runs **one `close-layer` agent** in the main checkout that
  receives the layer's collected verdicts, writes status + step for every task of the layer, rebuilds
  `tracker.md` / `tasks.json`, and commits the layer's tasks serially in dependency order
  ([`workflow-exec.md`](./workflow-exec.md)). Status in this mode moves per layer, not per stage.

**The native task list is a mirror, never the source.** When the session exposes `TaskCreate` /
`TaskUpdate`, the orchestrator (sequential engine, team lead, or the main session around a Workflow)
creates one native task per `T<n>` at the start and updates it at each transition — status
(`pending` / `in_progress` / `completed`) plus an `activeForm` naming the step («T3 · GREEN —
implementing order validation»). In team mode teammates may claim/complete native tasks themselves;
the lead only fills the gaps. No `runtime.task_list` mechanism → skip silently ([`../../_shared/tool-adapters.md`](../../_shared/tool-adapters.md)).
On disagreement, reconcile Git and gate evidence first, then synchronize all mirrors.
