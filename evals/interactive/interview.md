# Interview 2.0 — interactive acceptance protocol

Manual live-session protocol; **not an executed result**. Load this checkout with
`claude --plugin-dir <checkout>` in a disposable fixture repo. A human operator sends each
reply only after the interviewer asks. Record the host/model, checkout revision + diff,
actual user turns, helper dispatches/reports, tool results, final brief and git diff.
Never paste this entire answer script as the owner's conversation, and do not claim a
headless run tested adaptive questions. All inputs below are synthetic test cases.

## Core dialogue

Use the engineering example in `skills/interview/references/annotated-pass.md`; create an
operations note confirming existing outcome records and the authorized tenant-scoped read
path. Start: “Our on-call engineers cannot tell whether yesterday's exports finished. We
already use PostgreSQL. I want one place to see the last outcome; no new notification service.”

Only when asked about the incident, reply: “A worker completed late; the operator had already
started investigating. We need to see recorded outcomes, including late completion.”
When asked to choose scope, select read-only visibility and existing access. When the final
direction is correctly summarized, accept it. Do not introduce a new requirement silently.

PASS: no starting depth menu; no repeat of the supplied audience/stack/exclusion; questions
adapt to actual replies; no competitor search; raw PostgreSQL quote preserved; at most the
configured ceiling; eight sections/four keys; evidence classes distinguish records vs report;
ready-for-specify only after acceptance; structural N/5 separate from evidence/readiness.

## Variants (fresh fixture/session for each)

| Case | Change to input / operator behavior | Required observable result |
|---|---|---|
| Mature small feature | Supply scope, outcome and accepted direction at entry | Ends early; no filler questions, helper, or research quota |
| Vague product | Say only “make export operations better”; answer actor/problem before choosing solution | Establishes need before presenting approaches |
| Risky small change | Ask to show every tenant to operators, while preserving isolation | Independent interview critique or explicitly named inability; access contradiction remains until resolved |
| Existing brief | Supply a same-idea brief containing accepted answers | Reads/reuses; updates only changed sections; no repeated discovery |
| Different idea | Existing brief describes billing; request export status | Asks relationship before overwriting/merging |
| Contradictory sources | Historical doc says 100 per batch, operator reports 1000, no version known | Both origins retained; no unsupported limit/feasibility; concrete evidence action |
| No evidence/tool access | Required capability cannot be checked; operator says “I do not know” | Unknown with consequence/check/owner; no fabricated source or acceptance |
| Early summary/budget | Say “summary” before accepting; separately use easy with unresolved choices | Stops questions; no automatic readiness or budget escalation |
| Plan Mode | Enable host Plan Mode with the same fixture | Proposed brief in conversation; zero file/settings/gitignore changes |
| Outside Git | Run in a fresh folder outside a Git tree | Conversation artifact; no files/settings/commit |
| Specify handoff | Invoke specify after the accepted core brief | Reuses settled decisions, asks only detailed behavior gaps, preserves evidence limits |

For the refusal-only headless case use `evals/run.sh interview-headless-no-writes` instead.
For each live variant record PASS/FAIL with transcript references; unavailable host capabilities
are explicit limitations, not passing independent-critique evidence. A content-correct brief
alone cannot prove question order or lack of anchoring; inspect the actual turns.
