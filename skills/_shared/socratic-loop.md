# Socratic loop — conversational validation + 4-state machine + edits-log

> **Reference-only.** This file is not a skill — it has no `SKILL.md` and never triggers.
> Skills that run a Socratic validation pass (`specify`, `design`) read this file for the
> canonical machine and keep only a short **delta** of their own decision-types and section list.

## Contract — one decision at a time, records updated as answers arrive

For each section/group, the skill:

1. Read source material and accepted answers. Plan unresolved choices internally; do not show the
   full section or decision inventory. A one-line topic introduction is enough when it helps.
2. Ask the next meaningful choice per [ask-style.md](./ask-style.md): short context, actual options,
   a recommendation when justified. Wait for the answer; do not add unrelated questions.
3. Map the reply to a resolution below. A clear correction can be applied immediately; don't ask
   for another confirmation unless its meaning or consequences remain uncertain.
4. Run the per-skill gate on the resulting accepted choice (including an accepted edited choice).
   Deferred or dropped choices are not accepted and do not trigger an ADR.
5. Write that resolved part to its artifact and update the decision log immediately. Other parts
   can stay explicitly pending. No per-answer commits; commit per document after self-check.
6. When an earlier accepted choice changes, follow [change-decisions.md](./change-decisions.md)
   to trace and update affected downstream work without reopening unrelated choices.
   Continue with the next unresolved choice. Revisit an earlier answer only for a user correction,
   changed constraint or discovered conflict; explain the specific impact without restarting review.

The document is the durable record, not the questionnaire. Coverage and structural checks still
apply, but the user does not need to navigate section numbers or approve a complete document twice.

## The 4-state machine (uniform across every decision-type)

- **`Approve`** → keep the decision verbatim. No edits-log entry (Approved is the baseline). Run the per-skill gate if any. Move on.
- **`Edit`** → accept the correction in ordinary words and update the decision. Clarify only an unresolved ambiguity; there is no forced second approval and no rule that a second answer ends discussion. Log entry `action: "edit"`.
- **`Save as Open Question`** → decision leaves its native section and a row is appended to the artifact's Open-Questions / Risks table:

  ```
  | Open decision: <headline> | Open question | Resolve before <stage trigger or YYYY-MM-DD>; <inline rationale> | <owner> |
  ```

  Capture the responsible person and needed-by point (a date or stage) with short follow-ups, one missing fact at a time. Until known, keep the decision visibly unresolved with those fields pending. Never silently convert uncertainty into Drop; block dependent work when the decision is needed. Log entry `action: "save_as_oq"`. **No gate** — a defer is not an accepted decision.
- **`Drop`** → decision is removed. Two sub-paths:
  - **Mandatory decision** (e.g. a module boundary that every feature must have) → briefly explain what remains blocked and offer a simpler alternative or defer it. Do not keep rephrasing the same rejected choice or invent ownership.
  - **Optional decision** → leave it out, no replacement.
  - Log entry `action: "drop"` (`after: null`).

Option labels describe outcomes; bookkeeping actions remain internal — see [ask-style.md](./ask-style.md).

## Edits-log (mandatory)

After each `Edit` / `Drop` / `Save as Open Question` (NOT `Approve`), append one entry:

```
{decision_id: "DEC-<section>-<short-id>",
 action:      "edit" | "drop" | "save_as_oq",
 before:      "<verbatim wording/option/value before the action>",
 after:       "<verbatim wording after — for save_as_oq this is the OQ-row text incl. owner+due; for drop, null>",
 user_reason: "<the rationale the user gave, verbatim>"}
```

`Approve` decisions stay out of the log — they are the baseline. The log is the **sole** signal the clean-context critic uses to detect upstream-coherence drift caused by user edits. Without it the critic has no input for its F-classes. If the user gives no reason, record “not supplied”. Ask why only when it changes the next decision; do not demand a rationale for bookkeeping.

## Cadence

- A 1-line mini-recap of decisions so far every ~5 questions, so the user sees the dependency chain without scrolling.
- Keep a soft question budget per section sized to the feature class (see [size-matrix.md](./size-matrix.md)): XS/S lean on `<!-- N/A -->`, M+ walk every decision.
- **Question volume also scales with the interview-depth dial** ([interview-depth.md](./interview-depth.md)): `easy` decides the reversible calls itself and walks only the irreversible/high-stakes ones (stating its assumptions in a ledger), `medium` walks every real decision, `hard` walks every decision and foregrounds each trade-off. Depth and size compound — an XS feature at `easy` asks the least; an L feature at `hard` asks the most. Volume only: the disk-write discipline, the edits-log, and any coverage floor are unaffected by depth.

## Exit condition

A section is done when every decision in it has exactly one resolution applied, the resolved content + any gate-spawned files are on disk, and the edits-log has no pending entries. The whole pass is done when all sections are written and (for skills that run one) the critic phase has been dispatched — see [critic.md](./critic.md).

## Per-skill delta (what each consuming skill defines locally)

A consuming skill's `references/socratic.md` (or an inline ≤5-line block in `SKILL.md`) supplies only:

- **Section/group list** walked in order (e.g. `specify`: the 5 AC coverage types; `design`: Arc42 §1–§12).
- **Decision-types catalog** for this artifact (e.g. `design`: Strategic / Building-block / Crosscutting / Quality-scenario / Risk).
- **Per-skill gate** run on Approved decisions, if any (e.g. `design`: blast-radius → ADR).
- **Open-Questions table location** (which section absorbs `save_as_oq` rows).

Everything else — the 4-state machine, the edits-log schema, the cadence — comes from this file; the disk-write + commit discipline comes from [write-and-commit.md](./write-and-commit.md).
