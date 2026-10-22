---
name: interview
model: inherit
effort: high
agents: [researcher, devils-advocate]
description: >
  Clarify and stress-test an engineering idea before roadmap or specification. Use for a product,
  feature, or technical change whose problem, outcome, scope, or key assumptions are unsettled:
  "interview {slug}", "idea brief", "stress test this idea", "/awesome-sdd:interview {slug}". Reuses existing context, adapts questions
  to uncertainty, checks decision-changing facts, and requests independent critique when risk
  warrants it. Returns a short brief with decisions, evidence, unknowns, and a justified next
  step. Does not implement code, design the architecture, or write specify's detailed requirements.
---

**English only:** Write all conversation, questions, options, progress updates, handoffs, reports, and generated document prose in English. Apply the [language policy](../_shared/artifact-language.md) even when settings or source documents use another language.

**Host runtime:** Resolve and reuse [host capabilities](../_shared/host-capabilities.md) before this protocol. Dispatch roles through the [agent roster](../_shared/agent-roster.md); render questions and handoffs through that runtime. Model/effort frontmatter applies only where the host supports it.

# Skill: interview

Turn an unsettled engineering idea into a **traceable decision**: what problem to address, for
whom, within which constraints, and what evidence is still needed. One interviewer owns the
conversation; optional helpers research or critique a bounded question, never interview the user.

Brief prose follows `artifact_language`; headings/tokens stay stable per
[`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner and inputs

The idea owner supplies intent and tradeoffs. Read their message, supplied ticket/links, any
existing `docs/idea-brief.md`, and relevant project instructions/map. Use the current conversation
as input: never ask the person to repeat an answer already given. A slug is optional; reuse or
propose one without spending a question unless identity is ambiguous.

Primary scope: product, feature, technical change. An already actionable bug belongs to `fix`;
an already settled feature can go to `specify`. For a non-engineering idea, explain the scope and
offer a general discussion; do not force it through engineering checks or overwrite a project brief.

## Write and interaction gates

- Locate the Git root once, read-only. **Outside a repo: write nothing**, including settings.
- **Plan Mode: write nothing**; keep the proposed brief in the conversation until writing is allowed.
- **Headless / no human response channel: stop before any write or helper dispatch.** State what
  needs an answer. Pre-filled examples and a simulated person's choices are not actual user answers.
- An existing brief is read first. Same idea → update only changed sections. Different idea or
  uncertain identity → ask how it relates; do not merge or replace it silently.
- Settings are read at entry; creation is deferred to the final authorized write point below.

## Depth, questions, and evidence

Resolve the question ceiling from explicit `--depth=easy|medium|hard`, else saved
`interview_depth`, else `medium`. No opening depth-selection question. The adaptive interview
exception and ceilings live in [`../_shared/interview-depth.md`](../_shared/interview-depth.md).
State the ceiling and the current reason for research/critique in one short line. Stop early
when the decision is clear; depth never forces research or a quota of questions.

Ask **one substantive question at a time**, adapting to the answer. Use choices for decisions
and open text for facts/experience; recommend a decision only when its basis is clear. The
interview-specific exception in [`../_shared/ask-style.md`](../_shared/ask-style.md) overrides its
generic long-menu requirements. Use the host's actual question channel per
[`../_shared/tool-adapters.md`](../_shared/tool-adapters.md). Research tools cannot answer for the owner.

Evidence classes: **owner-reported**, **source-verified**, **assumption**, **unknown**.
Agreement with a recommendation is a decision, not independent evidence for its factual premises.
Never turn a hypothetical failure signal into an observed incident. Keep sources and limits visible.

## Protocol

1. **Gather context.** Apply the gates above. Preserve the raw idea verbatim. Classify product /
   feature / technical change. Read supplied material, the existing brief, instructions, and a
   relevant architecture map. Use scoped code reading to answer a named question; do not run a
   full `survey` or scan unrelated areas. List known facts and consequential unknowns.
2. **Choose the next useful question.** Owner intent/tradeoff → ask. Discoverable fact → inspect
   or research. Unknown requiring new observations → name an experiment/data source. Prioritize
   answers that can change direction, scope, or whether to proceed. Probe concrete problems,
   affected actors, observable outcomes, constraints, non-goals, and existing workarounds.
   **Write as you go** ([`../_shared/write-and-commit.md`](../_shared/write-and-commit.md)): when the
   gates allow writes, after the **first real owner answer** copy
   [`templates/idea-brief.md`](templates/idea-brief.md) to `docs/idea-brief.md` (§1 = raw words,
   `status: Draft`), then write each section as soon as its content settles. Same-idea existing
   brief → patch the changed section in place; a different or uncertain idea is never written
   over before the owner says how it relates. No-write mode → the gates above win, nothing lands.
3. **Check decision-changing facts.** Follow [`references/research.md`](references/research.md):
   local evidence first, primary external sources when needed; use `researcher` in explicit
   `fact-check` mode for a bounded gap. Inspect its evidence before relying on it. Return to step 2
   only for a new decision or contradiction, not to repeat an answered question.
4. **Stress-test the direction.** Select fitting lenses from
   [`references/probing-frames.md`](references/probing-frames.md). Include existing contracts,
   reversibility, operational ownership, and how success/failure will be observed. Consequential
   access/data/public-contract changes, hard-to-reverse commitments, or an explicit stress-test
   request → `devils-advocate` in explicit `interview` mode, at most three grounded findings.
   The helper sees the raw idea, accepted decisions, evidence and unknowns, not a persuasive
   summary. Resolve findings with the owner when they change intent or accepted risk.
5. **Choose the next action.** Summarize the direction, strongest evidence, weakest assumption,
   and tradeoff. Offer a simpler/reuse/no-change alternative when it is credible; never fabricate
   three options. Record whether the owner accepted the recommendation. Outcomes are
   `ready-for-specify`, `ready-for-roadmap`, `needs-evidence`, `reframe`, or `stop`. A blocking
   unknown or unconfirmed consequential choice prevents either ready outcome. An exhausted
   question/research budget preserves the blocker; it never implies acceptance. User says
   "summary" → stop questions and report the actual incomplete state.
6. **Persist and hand off.** In a writable repo with real user answers, fill
   [`templates/idea-brief.md`](templates/idea-brief.md) without expanding it into a spec. Preserve
   eight headings and exactly four frontmatter keys; `depth` is the resolved ceiling, `status`
   stays `Draft` (readiness is in §7). **Ensure the settings file** at this write point using
   [`../_shared/settings-file.md`](../_shared/settings-file.md): create if absent, never overwrite
   values; only `config` changes settings. Then finish the sections not yet on disk, run the checks below, and only after they pass
   commit per [`../_shared/write-and-commit.md`](../_shared/write-and-commit.md): one commit
   `interview: <slug> idea-brief.md` (the `.gitignore` patch rides in it). Outside a repo / in
   Plan Mode, return the brief in the conversation, without settings, file writes, or a commit. Emit the utility stage-handoff block
   per [`../_shared/handoff.md`](../_shared/handoff.md): **What I did**, **Review**, **Run next**.

## Verification and Definition of Done

Run the **five-item structural self-check** per
[`../_shared/self-check.md`](../_shared/self-check.md), re-reading the saved brief (or emitted
conversation artifact when writes are prohibited):

1. All eight exact template headings are present with nonempty content.
2. No template instruction comments or unfilled template placeholders remain.
3. Exactly `status` / `owner` / `updated_at` / `depth`: `Draft`, identified owner (or explicitly
   unassigned), today's date, resolved easy/medium/hard ceiling; no invented keys.
4. §1 matches the actual raw user words verbatim; later changes did not replace the baseline.
5. Repo write → file exists at the Git root's `docs/idea-brief.md`; no-write mode → brief is in
   the conversation and no brief/settings/.gitignore changes were made.

Explicit "None identified" is valid; do not invent a risk or open question to fill a section.
Report the structural result as N/5, separately from the evidence/readiness judgment below.

Also verify: raw words unchanged; material assertions have an evidence class and origin;
accepted decisions are distinguished from proposals; sources were actually inspected; every
blocking unknown has consequence + verification action + owner (or explicitly unassigned);
the readiness outcome agrees with blockers and user decisions. Technology names are allowed in
quotes, evidence, and existing/owner-required constraints, not as unagreed design choices.
Fix + re-check at most twice; report unresolved problems rather than a clean verdict.

Report **structural** and **evidence/readiness** results separately. A complete interview may
legitimately end `needs-evidence`, `reframe`, or `stop`; it is not necessarily ready to specify.
Only ready outcomes hand off to `specify`/`roadmap`; the others name the next evidence action,
reframing question, or reason to stop. `specify` consumes the brief using
[`../specify/references/brief-reuse.md`](../specify/references/brief-reuse.md).

Worked dialogue and interrupted-run behavior →
[`references/annotated-pass.md`](references/annotated-pass.md).
