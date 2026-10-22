# Config conversation — one behavior at a time

Read [ask-style](../../_shared/ask-style.md). The mapping below is for the agent, not a menu to
paste into chat. Reuse an explicit request (“leave commits to me”) and change only its confirmed
keys; don't make the user walk through unrelated setup first.

## Start with the user's goal

For a generic request: “Keep your current settings, or change something?” If they choose to tune,
ask which behavior they want to change, then work through that topic one question at a time.
On a fresh installation, say “defaults” instead of “current settings”. Keeping settings never
resets custom values. Existing comments, unknown keys and command overrides stay unchanged.

For a full walkthrough, visit the relevant topics below. Skip host-inapplicable controls and
already answered questions. Don't bundle execution, commits and branches into a single preset.

## Conversation topics and exact write scope

| Short question (adapt to current state) | Keys that may change after its answer |
|---|---|
| Should I write a failing test before changing code? | `tdd` |
| If a task stays broken, stop or continue independent work? | `stop_on_red` |
| How many repair attempts before I stop and report it? | `max_red_retries` |
| Include the repository's style checks? | `gate_lint` |
| Include its type/static checks? | `gate_vet` |
| Must integration checks run, run when available, or stay off? | `require_integration` |
| Run tasks one at a time or use supported parallel execution? | `team_mode`, `workflow_mode`, `max_parallel_agents`, `isolation` — disclose required coupling before the choice |
| What is the maximum number of tasks running together? | `max_parallel_agents` — ask only for supported parallel execution |
| Should I make commits automatically or leave them to you? | `auto_commit` — if automatic, ask separately per task vs per phase unless already specified |
| Use the current branch or create a feature branch? | `branch_strategy` |
| Should I choose routine defaults or discuss each meaningful choice? | `interview_depth` — easy/medium/hard semantics from the canonical depth policy; all questions stay short |

These topics are coverage for a requested full walkthrough, not a required questionnaire.
The four `cmd_*` overrides stay unchanged unless the user explicitly requests one; empty values
keep command detection. `artifact_language` stays effectively English; offer a legacy
normalization only when relevant, without rewriting it silently.

## Host and models

Resolve host capabilities from the live session, asking only if uncertainty affects an action.
On Codex, use [Codex dispatch](../../_shared/codex-dispatch.md). Explain the actual model/effort
controls available, including when work must remain inline. Ask only the relevant choice:

| Short question | Keys |
|---|---|
| Use the configured coding model, or follow the chat's model? | `codex_model`; for an all-role inheritance request also any role-model overrides, including `codex_model_explorer` |
| Use a lighter model for finding relevant code? | `codex_model_explorer` |
| How much reasoning should coding or tests use? | `codex_effort_implementer` or `codex_effort_test_author`, one role at a time unless both were requested |
| Give reviews more time to check edge cases? | `codex_effort_reviewer` |
| How much reasoning should design and decision checks use? | `codex_effort_judgment` |
| Give difficult coding tasks more reasoning automatically? | `codex_effort_complex`; `inherit` disables the automatic increase |
| Change the exploration effort? | `codex_effort_explorer` |

A requested custom role can use `codex_model_<role>` / `codex_effort_<role>` (underscores for
hyphens). Both accept `inherit`. A model choice does not also change effort. Preserve existing
Claude preferences. These settings affect future workers, never the running chat or global
Codex configuration. Offer only models/efforts supported by the live host; missing controls
mean inheritance, not a guessed mapping. On other non-Claude hosts, explain inheritance.

On Claude, ask a practical model choice only when relevant: “Use the session model throughout,
or use a stronger available model for reviews?” Explain the actual cost/quality tradeoff without
claiming access to an unavailable tier. For custom choices, handle one role/control at a time.
The seven writable keys are `judgment_model`, `model_test_author`, `model_implementer`,
`model_reviewer`, `effort_test_author`, `effort_implementer`, `effort_reviewer`. Preserve effort
unless the user chooses a change. Model `inherit` is not an effort value. Follow the
[agent roster](../../_shared/agent-roster.md) for overrides, floors and availability fallback.

## Write and explain

Before the user chooses, disclose any coupled changes necessary for that option. For example,
parallel execution needs separate working copies; never silently change commit preferences as
part of enabling it. If a custom combination doesn't match a preset, preserve it and ask only
about the aspect under discussion.

After each answer, briefly state the resulting behavior and patch only confirmed keys. Keep exact
`old → new` mappings in a compact change summary with the settings link; do not make the user
approve the same values again. A runtime fallback is not a settings change and must be labelled.
