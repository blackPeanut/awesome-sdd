# Interview depth — easy / medium / hard (the depth dial)

> **Reference-only.** Not a skill. The Q&A skills (`specify`, `clarify`, `design`, `interview`) read
> this for the canonical three levels and how each adapts. The dial tunes **how much the skill decides on
> its own vs. interrogates you** — question volume, autonomy, which analyses run, and whether each
> diagram is confirmed per-item or written-and-summarized. It does **not** tune *completeness*:
> every acceptance criterion is still covered at every level (see the coverage floor below).

## Adaptive interview exception

`interview` resolves a **ceiling**, not a mandatory interview length: explicit
`--depth=easy|medium|hard` → saved `interview_depth` → `medium`. It announces the ceiling and
starts from existing context, without a depth-selection question. Easy ≤4 substantive user
questions; medium ≤10; hard ≤15. Count all questions seeking user decisions/facts, including
identity clarification and final acceptance; reserve room for an unconfirmed consequential
choice. There is no minimum. Reaching a ceiling means summarize actual readiness and blockers,
not invent answers or automatically upgrade the budget. The owner may explicitly change it.

Risk controls independent critique; a decision-changing factual gap controls research. Neither
is switched on just because the ceiling is hard, nor switched off because it is easy. An
adversarial request triggers critique, not an automatic increase of question count. At every
level, label owner-reported/source-verified/assumption/unknown, and distinguish unconfirmed
recommendations from owner decisions. No decide-for-user easy mode in `interview`.
Its frontmatter `depth` stores the resolved ceiling even when the conversation ends earlier.

The generic rules below apply to other consumers; this exception has precedence for `interview`.

## How the level is chosen (other consuming skills, step 1)

Resolve `--depth=easy|medium|hard`, then an explicit conversation preference, then saved
`interview_depth`, then `medium`. Reuse the choice across stages. Do not open each stage with a
settings menu; briefly state the approach only when useful. A user who wants to choose each
meaningful step gets that conversation without being asked to select an internal depth label.
Changing this run's pacing does not rewrite settings; only `config` saves preferences.

At every level, follow [ask-style](./ask-style.md). Depth changes how much is discussed, never
question length or document-review burden. Split complex choices into small questions rather than
compressing them into a batch. Respect explicit question/time limits and the interview exception
above; a user may extend a budget. No minimum question count and no fatigue inference from short replies.

## What each level governs (the four axes)

| Axis | **easy** | **medium** (default) | **hard** |
|---|---|---|---|
| **Question volume + autonomy** | Skill decides the reversible / low-stakes calls itself with sensible defaults; asks ONLY the irreversible / high-blast-radius / genuinely-un-inferable ones. **States every assumption it made** (an assumptions ledger) so the user can veto. | The balanced Socratic walk — one `AskUserQuestion` per real decision, convention defaults recorded briefly. | Walks **every** decision; each question **foregrounds the trade-off** (what you gain / lose / the hidden catch); probes edge cases harder. |
| **Ideation analyses** (`specify` step 3) | Skip the suite — deep-dive answers only. | `researcher` (competitive/web) + `devils-advocate`. | Full suite: `researcher` + `strategist` (3 approaches) + `analyst` (multi-perspective) + `devils-advocate`, then the assistant-proposed RICE/feasibility confirm. |
| **Diagram confirmation** (`design` C4, `sequences` flows) | Write the diagram + a **one-line prose summary**, then proceed — no per-diagram question (per [`diagram-presentation.md`](./diagram-presentation.md)). | Prose description + `AskUserQuestion` confirm **per diagram**. | Same as medium — prose description + confirm per diagram (never raw Mermaid). |
| **Edge-case / ambiguity probing** | Only the edges that change the blast radius. | The spec's stated error/authz/edge criteria. | Adversarial — hunt for unstated edges, run the full `devils-advocate` pass, push on every «what if». |

Read the axes together, not in isolation: **easy** is «trust the defaults, show me what you assumed»; **medium** is «walk the real decisions with me»; **hard** is «interrogate me, run everything, leave nothing un-probed». The dial scales *effort spent asking*, not *effort spent being correct*.

## The assumptions ledger (easy only)

At `easy`, every decision the skill made **for** the user (instead of asking) is recorded as a one-line ledger entry and surfaced in small, relevant recaps before it is treated as settled:

```
- Assumed: <decision> = <chosen value>  — because <default rationale>.  [veto?]
```

Do not ask for blanket approval of a long assumptions ledger. If a default needs confirmation,
ask about that choice alone. A recap is not consent, and a veto becomes one concrete follow-up.
Keep the full ledger in the artifact; at medium/hard record directly answered decisions normally.

## The coverage floor is depth-independent (correctness, not a preference)

Depth tunes **how many questions** and **how much autonomy** — never **what gets covered**. The completeness guarantees hold at **every** level:

- Every spec §4 user story has ≥1 acceptance criterion (the **use-case floor**); §5 keeps ≥1 AC of each of the 5 coverage types (`specify`).
- Every §4 user story maps to ≥1 flow, and every §5 AC maps to a flow, a branch, or an explicit N/A (`sequences` use-case + AC→flow coverage check).
- Every user story + AC traces end-to-end spec → sequences → data-model → api → tasks → implement (`review`).

`easy` reaches these by **deciding** the «how» with defaults and listing them in the ledger; `hard` reaches them by **asking**. The destination is identical. A skill must never drop an AC, a coverage type, or a flow because the level is `easy` — that's a correctness bug, not a depth choice. If easy can't infer the «how» for a coverage-relevant decision, that decision is one of the «irreversible / un-inferable» ones it **must** ask about regardless of level.

## Per-skill adaptation (the delta each consuming skill applies)

- **`specify`** — the level gates step 3's ideation suite (table above) and the volume of the step-2 deep-dive + step-7 Socratic validation. The §5 coverage gates (≥1 of each of the 5 AC types **and ≥1 AC per §4 user story** — the use-case floor) are **floor, not dial** — enforced at every level.
- **`clarify`** — the level gates how aggressively the self-sweep + `devils-advocate` hunt (easy: only build-divergence that changes behavior, with assumptions stated; hard: adversarial, every fork surfaced) and the per-finding question volume. Every surfaced ambiguity is still Resolved or Deferred at every level — none dangling.
- **`design`** — the level gates the per-section Socratic question volume (easy: decide convention-defaults itself + ledger, ask only blast-radius decisions; hard: walk every decision, foreground each trade-off) and the C4 diagram confirmation (per [`diagram-presentation.md`](./diagram-presentation.md)). The blast-radius → ADR gate and the §11 owner+due rule are floors, enforced at every level.
- **`interview`** — use the adaptive exception above: ceilings, targeted evidence, risk-based
  critique, no opening selector, and no invented owner decisions. Its eight-section brief
  separates structural completeness from readiness; repo/Plan Mode/headless write gates apply.

A consuming skill adds a one-line pointer to this file at its depth-resolution step and otherwise reads the level as a parameter into its existing loop — it does not re-implement the dial.
