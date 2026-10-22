# Dynamic-workflow execution (`workflow_mode: auto`)

**Capability gate:** This backend recipe runs only when the shared `runtime.workflow_backend` is true. All role dispatch and model/effort selection still use the agent roster. Otherwise use sequential TDD; generic Codex delegation is not this scheduler.


When the decision tree selects the workflow, the engine **generates a `Workflow` script** from the DAG and runs it. This is the unattended, maximally-parallel mode: each independent task flows through its own pipeline, and a failure drops only that task's subtree while other branches keep going.

## Why a generated workflow (not a fixed one)

The shape of the work is `tasks.json` — different every feature. So the engine emits a script tailored to this DAG: validate → layer → fan-out → per-task pipeline. The script is data-driven from the tasks array; the engine fills it in and invokes `Workflow`.

## Generated script shape

```js
export const meta = {
  name: 'sdd-implement-<slug>',
  description: 'TDD-implement <slug> from tasks.json (dynamic DAG)',
  phases: [{ title: 'Implement' }, { title: 'Review' }],
}

// tasks + deps are inlined from tasks.json by the engine
const TASKS = /* [{id, title, acs, dod, files_hint, deps, layer, file}, ...] */;
// `file` = docs/features/<slug>/tasks/<task-slug>.md — every prompt below points the agent at it
// as its brief (redPrompt/greenPrompt/verifyPrompt/reviewPrompt all carry t.file).

// Kahn layers → phases; within a layer, fan out up to the parallel cap.
// Each task is one independent pipeline: write-test → implement → verify → [review]. NO commit
// stage: stage agents never commit and never write status files (the script cannot touch disk).
const blocked = new Set();
for (const layer of kahnLayers(TASKS)) {              // computed from deps
  const ready   = layer.filter(t => !t.deps.some(d => blocked.has(d)));
  const skipped = layer.filter(t => !ready.includes(t))          // a dep is blocked → never starts
                       .map(t => ({ id: t.id, res: null, reason: `dep ${t.deps.find(d => blocked.has(d))} blocked` }));
  const results = await parallel(ready.map(t => () =>
    pipeline([t],
      () => agent(redPrompt(t),     { phase:'Implement', label:`red:${t.id}`,   schema: RED_VERDICT }),
      r  => agent(greenPrompt(t,r), { phase:'Implement', label:`green:${t.id}`, schema: GATE_VERDICT }),
      g  => agent(verifyPrompt(t,g),{ phase:'Implement', label:`verify:${t.id}`,schema: GATE_VERDICT }),
      v  => agent(reviewPrompt(t,v),{ phase:'Review',    label:`review:${t.id}`,schema: REVIEW_VERDICT }),
    ).then(res => ({ id: t.id, worktree: wt(t), res }))      // res === null → dropped
  ));
  // One serial writer per layer: status + step for every task, tracker.md / tasks.json rebuilt,
  // the layer's green tasks committed one by one in dependency order. Cheap model — it is mechanical.
  const closed = await agent(closeLayerPrompt(layer, [...results, ...skipped]), {
    phase:'Implement', label:`close-layer:${layerIndex(layer)}`, schema: CLOSE_VERDICT });
  for (const b of closed.blocked) blocked.add(b.id);  // dropped + skipped → transitively blocked downstream
}
```

- **The brief is a path, not a paste.** Each generated prompt hands the agent `t.file` and tells it to read that first; the engine never inlines the task body into the prompt string. Upstream artifacts stay the fallback when a slice is insufficient — same order as everywhere else ([`./inputs.md`](./inputs.md)). A task with no `file` (an older breakdown) falls back to the JSON fields + spec §5, and the engine says so in the banner.
- **Schema-validated verdicts.** Each stage returns a structured verdict (`RED_VERDICT { class: GOOD|BAD|false_pass|NON, failing_line }`, `GATE_VERDICT { unit, integration, lint, vet, gate_green }`, `REVIEW_VERDICT { ac_satisfied, issues[] }`, and per layer `CLOSE_VERDICT { committed[], blocked[] }`) so the orchestrator branches on data, not prose.
- **Fail drops the subtree.** A stage that throws (or returns `gate_green: false` past retries) drops that task to `null`; `close-layer` records it `blocked` and returns it in `CLOSE_VERDICT.blocked`, so every transitively-dependent task is skipped. Independent branches finish unaffected — this is the workflow's advantage over a team halt.
- **Which tree the stage agents work in.** `isolation: worktree` → the task's **first** stage (`red`) creates one worktree for the task, `git worktree add .worktrees/<slug>-<id> HEAD` (HEAD already holds every earlier layer's commits), and every later stage of that task (`green`, `verify`, `review`) is handed the same path and works only there. Do **not** pass `isolation: 'worktree'` to each `agent()` call — that gives every stage a fresh tree and the GREEN agent never sees the RED test. `isolation: inplace` forces `parallel = 1` (the decision-tree guard), so the stages work in the main checkout one task at a time.
- **`close-layer` — the one writer.** Runs in the main checkout after the layer's `parallel()` returns, with collected stage verdicts. Apply successful worktree changes first; stop on conflict, preserving worktrees. Capture the actual enabled gates and input fingerprints on the integrated tree per [resume](./resume.md). Only then write provisional `done / COMMIT` to all three status mirrors and commit code, receipt and mirrors with `SDD-Feature`/`SDD-Task`/`SDD-AC` trailers via `git commit -- <paths>`. Confirm completion through reconciliation before releasing dependents or removing worktrees. Gate/commit failures become `blocked` with the reason; skipped dependents remain blocked. For a phase batch, verify all included receipts against the final combined tree. Returns `CLOSE_VERDICT { committed: [{id, sha}], blocked: [{id, reason}] }`. Status moves per layer; the main session mirrors it into the native task list. A worker verdict or raw `done` never substitutes for evidence.
- **Parallel cap.** `parallel(...)` respects `max_parallel_agents` (the workflow runtime also caps concurrency); a wide layer queues the overflow.

## Serialization inside the workflow

The same lanes as the team apply: `layer: migration` tasks are forced into a single ordered sub-sequence (don't place two migrations in the same parallel layer — chain them via synthetic deps before computing Kahn layers), and tasks with overlapping `files_hint` get a synthetic dep so they never land in the same parallel batch. A **compile-coupled pair** (shared contract file in `files_hint`) gets the same synthetic dep AND its commit step is merged — one shared gate, one commit with every task's `SDD-Task`/`SDD-AC` trailers ([`tdd-loop.md`](./tdd-loop.md) §COMMIT). Each migration task **promotes** its staged `docs/features/<slug>/migrations/<NN>_*` file into the live `migrations/` (next free number, in ordinal order) before applying it — see [`./inputs.md`](./inputs.md).

## Commit + integration

- Commits are produced **only** by `close-layer`, serially in dependency order, with `SDD-Feature`/`SDD-Task`/`SDD-AC` trailers — never by a parallel pipeline stage (concurrent commits race on `.git/index.lock` and break the linear history). `auto_commit: per_phase` → `close-layer` makes one commit for the whole layer (every task's trailers); `off` never reaches this mode — the decision-tree guard downgrades it to sequential, because the next layer's worktrees start from a HEAD that only commits move.
- Integration tier follows `require_integration`: in CI (Docker present) the integration RED→GREEN runs inside the verify stage; locally under `auto` with no Docker it's NON-red and the proving run relies on CI for the integration green.

## Graceful fallback

If the `Workflow` tool is **not available** at runtime, this whole mode is skipped by the decision-tree guard — the engine falls through to the team (if eligible) or to sequential single-agent TDD. The generated script is never a hard dependency.
