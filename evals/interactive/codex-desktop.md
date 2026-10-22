# Codex desktop workflow evaluation (manual)

Use a disposable project with the current SDD plugin selected. Record the plugin revision,
app version, installation method, transcript and before/after git diff. These checks require
an actual app session; CLI eval success does not count as passing this protocol.

1. Add `.claude/sdd.local.md` with `artifact_language: uk`, `judgment_model: opus`,
   `team_mode: true`, `workflow_mode: auto`, `max_parallel_agents: 3`, `auto_commit: off`.
   Add Ukrainian prose in README. Invoke SDD classify-size for `desktop-toggle` with no signals.
2. Confirm a supported native question channel is used, or plain text if unavailable. Leave the
   question unanswered. No size/route writes or fabricated approval may occur. With asynchronous
   questions, only independent work may continue. Capture the pending state.
3. Answer: one PR, under a day, no new module/API/migration, no breaking change. Confirm that the
   next decision proposes XS and quick together. Accept. Check one-token `.size` and `.route`,
   English throughout, untouched settings and no automatic commit.
4. Check the final handoff names the artifacts and an invocation actually exposed by this install.
   It must not instruct `/clear`. Forward-stage handoffs should say new chat in the same project;
   utility stages may stay in context. Start that new chat yourself and invoke the next stage.
5. Confirm the new session reads disk artifacts and preserves accepted decisions. It must not
   re-use old host capabilities without checking the new session, or repeat answered discovery.
6. Preview SDD config. Confirm inherited Codex models, no Claude tier menu, no assumed generated
   agent IDs, and effective sequential execution when compatible backends are absent. Saved
   preferences stay unchanged. If role work runs inline it must be labelled self-check.

Record each item PASS/FAIL with observable evidence; unavailable UI access is NOT RUN, not PASS.
