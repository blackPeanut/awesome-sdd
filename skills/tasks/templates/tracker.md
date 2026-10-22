# Tracker — <slug>

> Status of every task in the epic. `implement` updates **Status** and **Step** after every
> subagent it runs (and commits them with the task), so this table shows where the run is right now.
> Status: `todo` · `in_progress` · `blocked` · `review` · `done`.
> Step: `SELECT` · `RED` · `GREEN` · `REFACTOR` · `GATE` · `REVIEW` · `COMMIT` (`—` before the task starts).
> A `blocked` row carries its reason in Step, e.g. `GATE — lint red after 3 retries`.

| # | Task | Layer | Owner | Estimate | Blocked by | Status | Step |
|---|---|---|---|---|---|---|---|
| T1 | <title> | migration | <owner / TBD> | S | — | todo | — |
| T2 | <title> | domain | <owner / TBD> | M | — | todo | — |
| T3 | <title> | infra | <owner / TBD> | M | T1, T2 | todo | — |
| T4 | <title> | app | <owner / TBD> | M | T3 | todo | — |
| T5 | <title> | ports | <owner / TBD> | M | T4 | todo | — |
| T6 | <title> | tests | <owner / TBD> | S | T5 | todo | — |

**Total:** <N> tasks, ~<P> person-days.
