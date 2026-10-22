# Annotated adaptive pass — engineering feature

Illustrative dialogue, **not an executed eval or evidence of a real product incident**.
The illustrative project file and owner's replies below are test inputs, not verified facts.

## Starting context

Owner: “Our on-call engineers cannot tell whether yesterday's exports finished. We already use
PostgreSQL. I want one place to see the last outcome; no new notification service.”
Saved ceiling: medium. No opening depth question. The interviewer preserves this raw text,
including PostgreSQL, and reads the supplied `docs/export-operations.md`.

> Illustrative file evidence: the existing worker records completion/failure per export.
> A real run must cite the actual inspected file/section, not this example.

## Questions adapt to evidence

**Q1 — fact, open text:** “What happened during the most recent incident?”
Owner: “The worker failed, the engineer reran the export, then discovered the first run had
completed late. We need to see both outcomes before rerunning.”

Record this as owner-reported. Do not infer failure frequency, a financial loss, or a demand metric.
The existing operation record answers whether new result storage is needed; no competitor search.

**Q2 — decision:** “Should this first change show recorded outcomes only, or also control reruns?”
Recommend read-only visibility because the owner excluded a new service and the incident points
at missing information; explain that controlling reruns adds operational behavior.
Owner: “Visibility only, including late completion. Keep current access rules.”

**Scoped evidence check:** inspect the existing read path/access policy if available. If absent,
record the access constraint and the missing verification; do not infer that every engineer has access.
This example assumes the supplied project source establishes an existing permitted read path.

**Q3 — accepted direction:** “Use the existing outcome records for a read-only view, preserve
current access, and leave rerun control out. Is that the direction to specify?”
Owner: “Yes.”

Three substantive questions under a medium ceiling; no target of six or ten questions.
The owner confirmed the direction, not independent truth of every factual premise.

## Result

Outcome: `ready-for-specify` when the inspected source supports the read path and no blocker
remains. Brief §1 is unchanged; §2 describes the reported incident and intended behavior; §5
preserves access and excludes rerun control; §6 distinguishes owner report from source evidence;
§7 records acceptance and the simpler reuse option; §8 says None identified if true.
State separately: structural checks passed; evidence/readiness checked. The helper count can be zero.

## Contrasting endings

- If access would change or data exposure is consequential, dispatch explicit `mode: interview`
  critique, even with an easy ceiling. Preserve any material finding until resolved.
- If the existing records omit late completion and the feasibility is unknown, outcome is
  `needs-evidence`: name the check and owner. Do not promise the proposed reuse approach works.
- If the owner says “summary” before Q3, record recommendation unconfirmed; not ready.
- In Plan Mode/outside a repo, return the same proposed brief in the conversation without writes.
- In headless mode, stop before this dialogue: example answers are not a live owner.
