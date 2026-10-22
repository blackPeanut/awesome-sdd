# design — delta over the shared Socratic loop

Read [`../../_shared/socratic-loop.md`](../../_shared/socratic-loop.md) for the canonical 4-state machine (Approve / Edit / Save-as-OQ / Drop), the edits-log schema, the cadence; the disk-write + commit discipline is [`../../_shared/write-and-commit.md`](../../_shared/write-and-commit.md) (each section written as it resolves). design supplies only the deltas below.

## Sections walked (in order)

The 12 Arc42 sections of `sad.md`, in order:

§1 Introduction & goals → §2 Constraints → §3 Context & scope (C4 Context inline) → §4 Solution strategy → §5 Building blocks (C4 Container inline) → §6 Runtime → §7 Deployment → §8 Crosscutting → §9 Architecture decisions → §10 Quality requirements → §11 Risks → §12 Glossary.

§4 opens with the **Target-surface** decision (it gates §5's containers + every downstream stage, so it's resolved before any other §4 choice — see the decision-types catalog below). Each resolved section (`sad.md` edits + any ADR files the gate spawned) is written to disk immediately, with no commit; at the end of the step `sad.md` gets one commit and every ADR its own (spine step 7). Revisit a section only for a correction or a concrete conflict, without restarting the whole review. Section depth follows the size matrix; even XS/S walks all 12 (more `<!-- N/A: reason -->`, see [`../../_shared/size-matrix.md`](../../_shared/size-matrix.md)).

## Decision-types catalog

Each section holds a mix of these; the same 4-state machine applies to all. Each option describes its practical consequence (phrasing → [`../../_shared/ask-style.md`](../../_shared/ask-style.md)).

- **Surface** (§4, walked **first**) — *what's being built*: a multiSelect over the C4-grounded taxonomy (`backend-service` / `web-frontend` / `mobile-app` / `desktop-app` / `cli` / `worker` / `library-sdk`), Recommended-set derived from spec §1 «for whom» + §4 roles. It gates §5 (one container per surface) and every downstream stage, so it's resolved before any other §4 decision. The blast-radius gate fires whenever **>1 surface** is picked (multi-module + irreversible). On resolution, write `target_surfaces: [...]` to the `sad.md` frontmatter → [`../../_shared/surfaces.md`](../../_shared/surfaces.md).
- **UI-architecture** (§4, one per declared UI surface) — the follow-on to a `web-frontend` / `mobile-app` / `desktop-app` pick: web → SSR/SPA/hybrid; mobile → native/cross-platform; + state-management + routing only if complexity warrants. Option-set of 2–3, Recommended-first; gate fires often (irreversible delivery choice). This **evolves** the old §4 "read-side delivery (SSR/SPA/API-only)" item up into a per-surface decision. Kept light (no component-tree / token / screen artifact — Option B). It **references the existing design system / component library** from `architecture-map.md` §Frontend — the UI **reuses** that foundation (components, tokens, styling), it doesn't design greenfield → [`../../_shared/surfaces.md`](../../_shared/surfaces.md).
- **Strategic** (mostly §4, sometimes §7) — option-set of 2–4, Recommended-first. The blast-radius gate fires **almost always** (irreversible + multi-module). Create an ADR only when the actual gate warrants it; no count quota.
- **Building-block** (mostly §5) — module boundary (extend vs new), layering style (only ask if the spec signals divergence from the repo's convention), internal sub-package layout. Gate fires often (multi-module).
- **Crosscutting conventions** (§8) — reuse known defaults; ask about one real exception at a time. Gate rarely fires (convention-level, not blast-radius).
- **Quality scenario** (§10) — option-set rarely useful (numbers come verbatim from the spec NFR). Typical resolution: Approve / Edit (refine the verify method) / Save-as-OQ (verify method TBD by an owner).
- **Risk entry** (§11) — auto-generated from the edits-log + spec Open Questions + the brownfield scan. User Approves verbatim or Edits severity/mitigation/owner.
- **Open-architectural-decision row** (a special Risk entry) — created automatically when any earlier section resolves to Save-as-OQ. The skill writes the §11 row at that moment; the user does **not** see a second question for it (already approved when they picked Save-as-OQ). Severity column carries the literal `Open question`.

## Per-skill gate — the blast-radius gate (→ ADR)

This is design's equivalent of specify's coverage floor. On every accepted choice, including a clarified edit (not an unresolved edit, Drop or Save-as-OQ), run the 3-criteria blast-radius gate → [`./blast-radius.md`](./blast-radius.md): irreversible / multi-module / has legitimate alternatives. **2-of-3 fires → spawn an ADR**; on a 1-of-3 borderline, keep a short inline rationale unless the user requests a separate record. Do not interrupt for a file-format decision. An ADR spawn:

1. `NNNN` = `ls docs/features/<slug>/adr/*.md 2>/dev/null | wc -l` + 1, zero-padded to 4 digits.
2. Title in **decision-form** imperative kebab-case from the chosen option, not the problem (`0003-sliding-window-counter.md` ✓ vs `0003-rate-limiting.md` ✗).
3. Copy [`../templates/adr.md`](../templates/adr.md) → `docs/features/<slug>/adr/NNNN-<title>.md`. Status = `Accepted` (this skill is synchronous); Considered options include the rejected ones from the `AskUserQuestion`; no strawman options (an alternative an existing constraint already excludes).
4. Add a §9 row: `| NNNN | <imperative title> | Accepted | §N |`, written with the section. The ADR file gets its **own commit** at the end of the step, separate from `sad.md`.
5. Append to an in-memory ADR-spawns log (`{adr_id, title, section, triggered_by}`), kept **adjacent** to the edits-log — different signal (new artifact, not a user edit). The critic reads `adr/` directly; the spawns log is in-memory traceability only.

No ADR count target. Keep each warranted record concise: the choice, why, serious alternatives and material downsides. The user answers the underlying choice, not a second ADR approval menu.

## Open-Questions table

`save_as_oq` rows land in **§11 Risks** in this exact shape, with the literal `Open question` in the severity column:

```
| Open architectural decision: <headline> | Open question | Resolve before <stage trigger or YYYY-MM-DD>; <inline rationale> | <owner> |
```

Capture owner and due point with one missing fact per follow-up. Until known, retain a visibly pending row and block dependent work; never convert uncertainty into Drop. No gate — a defer is not an accepted decision.
