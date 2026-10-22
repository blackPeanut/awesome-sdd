---
name: review
model: inherit
effort: high
agents: [reviewer]
description: >
  Use to run an independent, clean-context code review of an implemented feature against its
  spec and acceptance criteria before shipping. Triggers on "review {slug}", "code review the
  changes for {slug}", "review the diff for {slug}", "is {slug} ready to ship", "/awesome-sdd:review {slug}". Dispatches the reviewer
  subagent over the whole feature diff (stage 1 spec/AC compliance, stage 2 quality), collects
  cited findings, and resolves each with you. Hard-refuses if the feature isn't implemented yet.
---

**English only:** Write all conversation, questions, options, progress updates, handoffs, reports, and generated document prose in English. Apply the [language policy](../_shared/artifact-language.md) even when settings or source documents use another language.

**Host runtime:** Resolve and reuse [host capabilities](../_shared/host-capabilities.md) before this protocol. Dispatch roles through the [agent roster](../_shared/agent-roster.md); render questions and handoffs through that runtime. Model/effort frontmatter applies only where the host supports it.

# Skill: review

The independent review gate. After `implement` has written + tested + committed the code, `review` looks at the **whole change at once, with fresh eyes** — does it actually satisfy every acceptance criterion, and is it good code? This is distinct from the per-task gate inside `implement` (which proves each task green): `review` is the cross-cutting, clean-context pass a human reviewer would do on the PR.

It reuses the shared clean-context discipline ([`../_shared/critic.md`](../_shared/critic.md)) and the [`reviewer`](../../agents/reviewer.md) subagent (read-only). Question phrasing per [`../_shared/ask-style.md`](../_shared/ask-style.md).

Review-record prose follows `artifact_language` (carry the language in the reviewer's dispatch prompt) — the verdict literals `PASS` / `CHANGES REQUESTED` / `REVIEW_CLEAN` and cited identifiers stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

## Owner

Tech Lead / a reviewer who did **not** write the code (independence is the point).

## Inputs

- `<slug>` — feature slug.
- **Gate (hard refuse):** an implemented change must exist (commits on the feature branch, or a non-empty working diff). Nothing to review → «run `implement <slug>` first».
- Read for the review baseline — the **whole AC chain**, so the trace can be checked end-to-end: `docs/features/<slug>/spec.md` §5 (the full AC set — the source of truth, not the diff's trailers), `sad.md` §6 (the sequence flows/branches each AC should appear in), `data-model.md` / `contracts/openapi.yaml` / Accepted `adr/` (the contracts the code must honour), `test-plan.md` (the AC→test map, if a separate file), and `tasks.json` (which AC each task claimed).

## Protocol

1. **Scope and capture the actual inputs.** Follow [review freshness](./references/freshness.md): resolve the branch point, inspect the committed diff plus staged, unstaged and untracked changes, and save a new immutable snapshot before dispatch. Include source requirements and contracts. Note the `SDD-AC` trailers — the ACs the implementation claims to satisfy. A limited review of named files is not a whole-feature PASS.
2. **Dispatch the independent reviewer.** Run the [`reviewer`](../../agents/reviewer.md) agent — role `reviewer` via the resolved runtime (read-only, **clean context** — it re-reads spec/contracts itself, no paraphrase; **model and effort per the roster and resolved runtime**, per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) — over the diff along the dimensions in [`./references/review-dimensions.md`](./references/review-dimensions.md): **stage 1** — every claimed AC genuinely satisfied **and the whole §4 user-story set + §5 AC set traced end-to-end (spec → sequences §6 → data-model → api → tasks → implement): every §4 user story has ≥1 AC and a §6 flow, and every §5 AC reaches code+test — spanning every surface declared in `sad.md` `target_surfaces` (a UI AC traces to a component / e2e-through-UI test, not only a backend one) — flagging any user story or AC that dropped out anywhere in the chain, not only the ACs the diff claims via its `SDD-AC` trailers**; **stage 2** — conventions, error/edge handling, security, boundary violations, test adequacy. For a large diff, fan out one reviewer per dimension and merge.
3. **Collect cited findings.** Each finding cites `file:line` + the AC/contract it touches. Drop uncited findings (per the critic discipline). A clean review returns `REVIEW_CLEAN`. If the reviewer ran asynchronously and came back as an idle/completion signal with no report, **collect the full report through the resolved return/wait mechanism** — never accept a verdict without its text (→ [`../_shared/agent-roster.md`](../_shared/agent-roster.md), shared-contract point 2).
4. **Resolve each finding with the user — writing as you go.** Translate one finding at a time into the observed problem, practical impact and a short choice. Recommend a fix when supported; keep the full cited report in the review file. Never make the user approve an entire findings batch or understand internal severity/AC codes to answer. Before the first question, create a uniquely named `docs/features/<slug>/_review/review-<date>.md` (scope + diff stat, snapshot filename, findings list empty, gate `pending`; add a run suffix rather than overwrite an earlier report); after **each** resolution, append that finding with its verdict to the file — and on Defer write the spec §8 row — immediately, never all at the end ([`../_shared/write-and-commit.md`](../_shared/write-and-commit.md) §1). Resolve via `AskUserQuestion`: **Fix now** (hand the actionable finding back to `implement`/the author as a follow-up task — re-enter the TDD loop for it) / **Defer** (record in spec §8 Open questions with owner + due) / **Not an issue** (the reviewer misread; record why). Never ship an unresolved stage-1 (AC) finding.
5. **Finalize the review record.** `docs/features/<slug>/_review/review-<date>.md` already holds the scope (diff stat) and every finding with its verdict; check its saved snapshot against the current files per [freshness.md](./references/freshness.md). Changed inputs need a focused follow-up review before a new PASS. Set the gate result (`PASS` / `CHANGES REQUESTED`) only after fixes are actually rechecked and findings resolved; stale or missing evidence stays pending.
6. **Commit** per [`../_shared/write-and-commit.md`](../_shared/write-and-commit.md) — the review record and its named JSON snapshot are one evidence unit in `review: <slug> review-<date>.md`; `review: <slug> spec.md deferred findings` only when a Defer changed `spec.md` (otherwise `git status` is empty and the commit is skipped). With commits off, keep both files together as verified uncommitted evidence.
7. **Verdict + next.** Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* (incl. the commits with short SHAs) + *Review* (`_review/review-<date>.md`) + *Run next*: `PASS` → (`/clear`, then `/awesome-sdd:ship <slug>`); `CHANGES REQUESTED` → `/awesome-sdd:implement <slug>` for the fixes (**no `/clear`** — stay in context to iterate), then re-review the changed surface.

## Definition of Done

- The independent reviewer ran over the whole feature diff (not just per-task).
- Every claimed AC was checked for genuine satisfaction; **the whole §4 user-story set + §5 AC set was traced end-to-end (spec → sequences → data-model → api → tasks → implement)** — every §4 US has ≥1 AC and a §6 flow, every §5 AC reaches code+test — and anything that dropped out anywhere in the chain was flagged, not just the ACs the diff claims. Every in-scope user story / AC is covered or explicitly deferred with owner + due.
- Every finding is resolved (fixed / deferred / dismissed-with-reason); no open stage-1 finding remains.
- A review record names the snapshot actually reviewed; PASS requires that snapshot to remain current and all findings to be resolved.
- The clean-context reviewer pass (the whole skill is a verifier) is this skill's **structural self-check** ([`../_shared/self-check.md`](../_shared/self-check.md)); the verdict is its report.

## Anti-patterns

- **Calling self-review independent.** Request isolated review when the runtime supports and authorizes it. Otherwise disclose an inline self-check; never imply that it supplies independent assurance.
- **Uncited findings.** «This feels off» is not actionable — cite `file:line` + the AC/contract or drop it.
- **Shipping with an open AC finding.** A stage-1 gap means the feature doesn't do what the spec says — fix or explicitly de-scope (spec change), never wave through.
- **Under-checking `added-by-fix` ACs.** An AC that entered §5 through a bug is proof the spec already missed that case once — trace it at least as strictly as the rest; the fix's pinning test is its floor, not proof of full coverage.
- **Trusting the diff's `SDD-AC` trailers as the complete AC set.** The trailers only list what the diff *claims*. Review traces the **whole** §5 set end-to-end — an AC that never reached the diff (no task wrote it, no test asserts it) is the most dangerous gap precisely because the trailers can't reveal it.
- **Re-litigating style the repo already settled.** Judge against the conventions + contracts, not personal taste.
- **Treating the per-task gate as the review.** Green tests prove each task; they don't prove the change coheres or that the AC are truly met end-to-end.

## References & template

- [`./references/review-dimensions.md`](./references/review-dimensions.md) — the review dimensions + the reviewer dispatch shape.
- [`../_shared/critic.md`](../_shared/critic.md) — the clean-context dispatch discipline this reuses.
