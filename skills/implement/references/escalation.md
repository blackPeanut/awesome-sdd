# Escalation — when RED won't go GREEN

A test that stays red after a normal GREEN attempt is a signal, not a nuisance. Climb this ladder in order; never short-circuit it by weakening the test.

## The ladder (in order)

1. **Re-attempt** up to `max_red_retries` times. Re-read the failing line, the task `acs`, and the relevant `data-model` / `openapi` / `adr`. Often the GREEN missed a detail the contract already specifies.
2. **Reassess with supported reasoning controls.** Use the already resolved runtime and roster policy. Raise model/effort only when the host supports it and the user/session authorizes it; never modify saved `model_implementer` or translate Claude tiers. Otherwise re-read the evidence with inherited settings and continue to task splitting. Disclose when no runtime escalation was possible.
3. **Split the task.** If the task turns out to bundle two concerns (e.g. a validation rule *and* an audit write), split it into two with a dep edge, and drive each with its own RED. Update `tasks.json` + `tracker.md` so the DAG stays the source of truth.
4. **Ask a human — the test may encode a wrong AC.** If the code is right and the *test* asserts something the AC doesn't actually require (or the AC itself is wrong), STOP and ask. Surface: the failing line, the AC text, and why they conflict. **Never** edit the test to be less strict to make a wrong AC pass — fixing the AC is a `specify`/`clarify` change with the human in the loop.
5. **Undo only this task's changes when safe.** Follow [protect-work.md](../../_shared/protect-work.md): compare with the task checkpoint, preserve earlier edits and the index, and undo only changes whose ownership is clear. If edits overlap or evidence is missing, leave them in place and report what remains blocked. Never reset to a commit to recover a failed task.

## `stop_on_red` decides what happens to the rest

After the ladder is exhausted on a task:

- **`stop_on_red: true`** (default) → set the task `blocked` with the step + reason in its task file, `tasks/tracker.md` and `tasks.json` ([`tdd-loop.md`](./tdd-loop.md) §Status protocol), then halt the run. Report the blocked task, the failing line, and where in the ladder it stalled. Nothing half-done is committed; the status files stay on disk for the next run's resume.
- **`stop_on_red: false`** → drop this task, **auto-block its transitive dependents** (their deps will never complete) — each recorded `blocked` on disk with its reason — and continue the independent branches. The final summary lists every dropped + blocked task with the reason.

## Never

- **Never weaken a test** to get green. The test is the spec made executable; if it's wrong, that's a human decision (step 4).
- **Never commit a red or a skipped hard-gate** as "done". A NON-red integration tier is labelled, not hidden.
- **Never erase existing work to get a clean tree.** If safe undo is uncertain, preserve the files, report the failing checks and block affected tasks.
