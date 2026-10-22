---
name: config
model: inherit
effort: medium
agents: []
description: >
  Use to create and tune the per-project settings file `.claude/sdd.local.md` — the one place that
  decides how deeply the pipeline interviews you, which model tier its judgment agents run at, how
  strict the TDD gates are, and how tasks execute and commit. All conversation and documents
  are written in English. Triggers on "config", "settings", "configure sdd", "tune the pipeline", "change the
  judgment model", "set the interview depth", "/awesome-sdd:config".
  Creates the file with documented defaults FIRST (so you have a working config before answering
  anything), reads what already differs from the defaults, then asks the applicable decision groups and
  patches only the keys you confirm — preserving your comments, key order and unknown keys.
  Never touches the pipeline's artifacts; the settings file is gitignored, only the .gitignore
  patch is committed.
---

**English only:** Write all conversation, questions, options, progress updates, handoffs, reports, and generated document prose in English. Apply the [language policy](../_shared/artifact-language.md) even when settings or source documents use another language.

**Host runtime:** Resolve and reuse [host capabilities](../_shared/host-capabilities.md) before this protocol. Dispatch roles through the [agent roster](../_shared/agent-roster.md); render questions and handoffs through that runtime. Model/effort frontmatter applies only where the host supports it.

# Skill: config

The settings file has many creators and **one editor: this one**. Six pipeline skills
(`interview` / `survey` / `roadmap` / `scaffold` / `specify` / `implement`) — and this skill too —
write `.claude/sdd.local.md` with documented defaults, so the pipeline always finds a real file.
None of the six offers to change a value. That offer lives here, and only here.

Everything about the file itself — the template, the create procedure, the `.gitignore` patch, the
key semantics, the edit rules — is canonical in
[`../_shared/settings-file.md`](../_shared/settings-file.md). This skill is the **conversation**
over it.

## Owner

Whoever owns the repo's setup — usually the lead who runs the pipeline first, once per project.

## Inputs

- Nothing is required. No gate, no upstream artifact: a bare repo is a valid starting point.
- (Optional) an existing `.claude/sdd.local.md` — read, diffed against the defaults, patched in
  place. Never regenerated.

## Protocol

1. **Ensure the settings file (first thing, after this skill's own gate).** If `.claude/sdd.local.md`
   is absent, create it now from the canonical template — documented defaults + the self-documenting body — and
   patch `.gitignore`; if it exists, read it and never overwrite. The one procedure lives in
   [`../_shared/settings-file.md`](../_shared/settings-file.md). Creating is unconditional;
   **changing values is only ever offered by [`config`](../config/SKILL.md)**. Say one line:
   «`.claude/sdd.local.md` created with documented defaults — `/awesome-sdd:config` to tune it».
   (Here that line is the opening move, not a footnote: the user has a working config before the
   first question.)

2. **Read the current state.** Report in three lines: which keys **differ from the documented
   defaults** (with both values), which **unknown keys** and inline comments are present (they are
   preserved verbatim — say so), and whether the frontmatter parsed. **A malformed frontmatter is
   never repaired silently** — print the lines that failed to parse and offer exactly two ways
   forward: rewrite from the template (naming what will be lost) or stop so the user fixes it by
   hand.

3. **Start with the requested change.** If the user already named a behavior, address it directly.
   Otherwise ask whether to keep the current settings or tune something, per
   [`../_shared/ask-style.md`](../_shared/ask-style.md). Keeping means no resets; skip to step 7.

4. **Reuse the resolved host runtime.** Report effective limitations without re-detecting the host.
   Ask only if unresolved evidence affects the next action. See [`./references/detection.md`](./references/detection.md).

5. **Ask one behavioral choice at a time through `runtime.questions`.** Use
   [`./references/interview.md`](./references/interview.md) as an internal topic-to-key map, not
   verbatim UI. Ask only the requested topics, or walk them individually for a requested full
   setup. Separate gate, execution, commit and branch choices; no large preset that changes
   unrelated preferences. Explain coupled effects before the answer. Reuse known choices and
   offer only host-supported controls. All output stays English; legacy language normalization
   requires an explicit choice. Preserve command overrides unless changing one was requested.

6. **Write the confirmed keys, key by key.** Patch only the lines whose values were confirmed;
   preserve comments, key order and unknown keys exactly. Print a `old → new` line per changed key,
   and **separately** state effective runtime fallbacks and unchanged command overrides.
   Never write host-derived clamps; only explicit user choices change settings. Nothing else on disk is touched.

7. **Structural self-check + handoff.** Run the **structural self-check** per
   [`../_shared/self-check.md`](../_shared/self-check.md) — re-read the file **from disk** and verify
   **6 items**: (1) `.claude/sdd.local.md` exists (`test -f`); (2) its frontmatter parses and every
   confirmed key holds the confirmed value; (3) every key present before the run is still present —
   none dropped, including unknown ones; (4) every inline comment that was there is still there;
   (5) `.gitignore` contains `.claude/*.local.md` and `.worktrees/`, each exactly once; (6) no file
   outside `.claude/sdd.local.md` + `.gitignore` was modified (`git status --short`). Fix + re-check
   ≤2 cycles; surface anything unresolved. Then commit per [`../_shared/write-and-commit.md`](../_shared/write-and-commit.md):
   one commit `config: .gitignore sdd settings` **only if `.gitignore` actually changed** — the
   settings file is gitignored and has nothing to commit. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md)
   — *What I did* (the changed keys + the self-check line + the commit SHA or «nothing to commit») + *Review* (`.claude/sdd.local.md`) +
   *Run next* (utility variant: `/clear` optional, resume your backbone stage — name the likely one).

## Definition of Done

- `.claude/sdd.local.md` exists and parses, whichever branch the run took (defaults or tuned).
- Every key the user confirmed holds the confirmed value; every key they didn't confirm is
  byte-identical to what was there before.
- Unknown keys, key order and inline comments survived the run.
- Effective runtime fallbacks were disclosed without changing saved preferences.
- `.gitignore` covers `.claude/*.local.md` and `.worktrees/`.
- The 6-item check in step 7 is this skill's structural self-check; its result is one line in the
  handoff.

## Anti-patterns

- **Asking before creating.** The file lands with documented defaults first; a user who answers
  nothing still ends up better off than before the run.
- **Regenerating the file from the template** because a key looked stale. That is how a
  hand-written comment or a hand-added key disappears. Patch key by key.
- **Persisting runtime detection.** Current capabilities do not change saved project preferences.
- **Offering unavailable backends.** Offer team/workflow choices only when the runtime supports them.
- **Asking about `cmd_*`.** Empty = autodetect, which is the recommended answer; asking invites a
  pinned command that goes stale.
- **A settings question inside another skill.** The six pipeline skills create and read.
  Only `config` tunes.
- **Touching pipeline artifacts.** This skill writes two files and no others.

## References

- [`../_shared/settings-file.md`](../_shared/settings-file.md) — the canonical template, procedure and key semantics.
- [`./references/detection.md`](./references/detection.md) — reuse of the resolved runtime without persistent host clamps.
- [`./references/interview.md`](./references/interview.md) — the conversational topics + the exact question → keys map.
- [`../_shared/ask-style.md`](../_shared/ask-style.md) — how every question is phrased.
- [`../_shared/tool-adapters.md`](../_shared/tool-adapters.md) — what each Claude mechanism maps to under Codex desktop / CLI.
- [`../_shared/agent-roster.md`](../_shared/agent-roster.md) — what the model tier actually changes.
- [`../implement/references/settings.md`](../implement/references/settings.md) — the engine-side delta.
