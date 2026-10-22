# specify — delta over the shared Socratic loop

Read [`../../_shared/socratic-loop.md`](../../_shared/socratic-loop.md) for the canonical 4-state machine and edits-log, and [`../../_shared/write-and-commit.md`](../../_shared/write-and-commit.md) for the disk-write + commit discipline. specify supplies only the deltas below.

**Disk writes.** `spec.md` was bootstrapped from the template in step 1. Each walked section (§4, §5, §6, §7) is written into it as each decision resolves; a `save_as_oq` row lands in §8 immediately. No commit here — the commits come once, after the critic + F6 scan (step 8).

## Sections walked (in order)

§4 User stories → §5 Acceptance criteria → §6 NFR → §7 KPIs. §1–§3 are drafted and briefly summarized only as needed but not per-item walked (they have no decision set — the user edits them inline if needed).

## Decision-types

- **User story** (§4) — Approve / Edit / Drop / Save-as-OQ. Dropping a US that owns the only AC of a coverage type triggers the §5 coverage gate.
- **Acceptance criterion** (§5) — the internal resolution states, also accepting “add another behavior” in ordinary words (user dictates a new AC; skill drafts it in business form and runs a one-question mini-batch on it). Dropping / OQ-migrating the **last AC of a retained §4 user story** fires the use-case floor below (regenerate an AC for that US).
- **NFR row** (§6) — Approve / Edit (change the number or measurement) / Save-as-OQ (number is TBD, owner+due). A bare adjective («fast») is never Approvable — force a number or an OQ.
- **KPI** (§7) — Approve / Edit / Drop. baseline=TBD forces an inline measurement plan or an OQ.

## Per-skill gate — §5 coverage floors (two, both re-checked after every resolution)

After every §5 resolution, re-check **both** floors below (OQ-migrated AC do NOT count toward either — they live in §8 now). Both are the specify analogue of `design`'s blast-radius gate; both hold at every interview depth.

1. **Coverage-type floor.** ≥1 AC of each of the 5 coverage types (happy / error / authorization / domain invariant / cross-context) still stands after drops + OQ-migrations. If a type is empty, regenerate a replacement AC of that type and run a one-question mini-batch.
2. **Use-case floor (§4 US → ≥1 §5 AC).** **Every *retained* §4 user story still has ≥1 acceptance criterion.** If a Drop / OQ-migration leaves a retained US with no AC, regenerate (or use the «Add another AC» option) an AC for that US and run a one-question mini-batch — a user story with no AC is incomplete and silently breaks the downstream `sequences` use-case coverage and `review`'s end-to-end trace. (Dropping the **whole** US is a legitimate de-scope and does not fire this floor — only a retained US losing its last AC does.) This also applies at **draft time**: if the initial §5 draft gave some §4 US no AC, add one before the walk begins.

## Open-Questions table

`save_as_oq` rows land in **§8 Open questions** as a checkbox line: `- [ ] <headline>? — owner: <…>, due: <…>`. Capture owner and due one missing fact at a time. Missing fields remain visibly pending and block dependent work; uncertainty is never silently dropped.
