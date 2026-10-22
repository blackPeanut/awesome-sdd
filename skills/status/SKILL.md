---
name: status
model: inherit
effort: medium
agents: []
description: >
  Give a read-only SDD progress recap when asked "where are we?", "what is left?",
  "status {slug}", or "help me pick this up again". Read saved decisions, tasks, Git and
  verification evidence; report what is finished, blocked and next. Does not start work,
  repair settings or change task status. Explicit implementation requests use implement.
---

# Status — make it easy to pick up later

Use English per the [language policy](../_shared/artifact-language.md), the resolved
[host capabilities](../_shared/host-capabilities.md), and [plain question style](../_shared/ask-style.md).
This skill is read-only: do not create settings, write a recap file, update mirrors, run tests,
commit, dispatch workers or resume implementation. Reading malformed settings may reveal a
blocker; report it without applying defaults. You may still summarize other readable evidence.

## Read enough to establish the next step

Use the feature named in the request or clearly active in the conversation. Otherwise inspect
the roadmap and feature folders; if several could be active, give a short overview and ask which
one to continue. Do not select a feature just because its file was modified most recently.

Read the source artifacts, unresolved questions, any pending decision-change checklist, task
definitions/statuses, current Git diff/history and latest review. Missing files are useful
information, not permission to generate them. Show planning progress even before tasks exist.

When implementation evidence exists, run only the read-only `check` from
[resume.md](../implement/references/resume.md). Check a review's saved snapshot via
[freshness.md](../review/references/freshness.md). If either helper is unavailable or errors,
label completion as unverified and explain the immediate blocker. Never substitute a raw `done`
or `PASS` label for evidence. Distinguish verified uncommitted work from committed work.
Do not infer that a PR was merged or deployed from a local roadmap label.

## Answer briefly

Give three useful points, omitting empty ones:

- What's finished, with any verification limitation that matters.
- What's blocked or still needs checking.
- The next action or **one** unanswered choice, in everyday language.

For example: “Booking and email retries are built and checked, but not committed. Support alerts
still need a destination. Should failed bookings appear in the support dashboard?”

Before answering, perform the structural self-check: each completion claim must agree with the
saved evidence and current files, pending changes must remain visible, and the suggested next
step must follow the actual blocker. This is a read-only consistency check, not a test run.

Link the relevant source or task when useful. Do not dump every AC, task ID or commit. Emit the
stage-handoff block using the [handoff](../_shared/handoff.md) recap variant, with no context reset; it does not
claim a stage completed. Do not repeat settled questions, treat the recap as approval, or act on
the suggested next step until the user's request authorizes continuing.
