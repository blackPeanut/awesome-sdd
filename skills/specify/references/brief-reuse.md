# Reuse an interview brief before specifying

Read `docs/idea-brief.md` **before** a new raw-idea/deep-dive prompt or ideation dispatch.
It is optional: no brief → the existing standalone specify protocol. Do not require interview.

## Identity and readiness

Match the requested feature to the brief's scope. A whole-product brief may supply only the
relevant slice; do not silently specify the entire product. Another idea/ambiguous match → ask
which source applies; do not overwrite the brief or borrow unrelated constraints.

A new brief's §7 outcome names readiness. `needs-evidence`, `reframe`, or `stop` is not approval
to proceed. Reconcile the blocking item or an explicit owner scope change first. Mark a resolved
blocker and the supporting evidence/decision in the source brief when writing is permitted;
otherwise retain the proposed update in the conversation. Never treat age or a file's existence
as approval. Legacy eight-section briefs without the new labels remain valid inputs: inspect
content and current owner instructions; missing provenance stays unknown, never source-verified.

## What to reuse

- Verbatim initial idea, problem, actors, expected outcome, agreed scope/non-goals and constraints.
- Owner-accepted decisions, alternatives rejected with reasons, and open questions with owners.
- Relevant evidence and its class: owner-reported / source-verified / assumption / unknown.

Current explicit owner corrections supersede old intent, with the change recorded; source
conflicts are surfaced, not silently resolved. A recommendation without acceptance remains a
proposal. Reading it does not make it accepted. A source-verified label still needs inspection
of the cited material for any material reliance; re-check local changes and time-sensitive facts.

Ask only what is missing for the spec: detailed observable behavior, user stories, AC, relevant
NFRs and measurement. Do not ask again who the user is or why the accepted direction was chosen.
Existing technical constraints stay traceable to brief §5 and later design; do not delete or
reinterpret them as optional. Product/AC phrasing still follows specify's existing contract:
reference the brief for implementation constraints rather than choosing a new stack in AC.

## Ideation reuse (all depths)

Before each researcher/strategist/analyst/adversary dispatch, name the remaining decision gap.
Already covered by relevant evidence + accepted decisions → reuse and cite that section instead
of rerunning. A hard depth is not permission to reopen the settled direction or fabricate three
approaches/RICE scores. Run only missing, changed, contradictory, or explicitly reopened work.
Research is scoped to the gap; an internal engineering fact may use `researcher` fact-check mode
instead of a competitor table. Critique of current consequential assumptions can use explicit
`mode: interview`; a full new product ideation pass retains legacy modes and ordering.

The spec recommendation may cite the reused brief, accepted decision, evidence, and remaining
limits. It must not cite matrix cells or scores that were never produced. No brief → retain the
standalone depth-gated suite. A need to reconfirm a material change is not a license to repeat
all discovery questions.

## Handoff and verification

Cite brief section(s) in the spec's traceability. Keep unknowns visible and distinguish a verified
source from a claimed observation. Before writing, check that the spec preserves agreed
constraints, does not resurrect rejected scope, and does not turn an open blocker into an AC
with a guessed answer. The critic receives the brief path and current owner corrections.
