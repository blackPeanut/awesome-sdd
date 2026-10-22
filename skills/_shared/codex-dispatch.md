# Codex worker settings

Use this procedure when a Codex stage dispatches a role from the [agent roster](./agent-roster.md).
It controls workers, not the model of the current chat. Other hosts use their own roster policy.

## Choose the preference

Read the validated project settings before each dispatch. Keep Claude's `model_*`, `effort_*`
and `judgment_model` untouched; they do not supply Codex values.

| Role | Model preference | Effort preference |
|---|---|---|
| explorer | `codex_model_explorer` (Luna) | `codex_effort_explorer` (high) |
| test-author | `codex_model` (Sol), unless a role override exists | `codex_effort_test_author` (medium) |
| implementer | `codex_model` (Sol), unless a role override exists | `codex_effort_implementer` (medium) |
| reviewer | `codex_model` (Sol), unless a role override exists | `codex_effort_reviewer` (high) |
| critic, devils-advocate, strategist, analyst | `codex_model`, unless a role override exists | `codex_effort_judgment` (high), unless a role override exists |
| researcher, pen-keeper | `codex_model`, unless a role override exists | medium, unless a role override exists |

The full IDs and defaults live in [settings-file.md](./settings-file.md). Optional role keys are
`codex_model_<role>` and `codex_effort_<role>`, with underscores replacing hyphens.
An explicit invocation choice wins, then a saved role preference, then the shared default.
`inherit` means omit that override. To inherit every model, `config` sets `codex_model` and any
existing/default role-model overrides (including explorer) to `inherit`; effort is a separate choice.

For test-author/implementer, raise effort to at least `codex_effort_complex` for an L/XL feature,
a task with difficult cross-module behavior, or escalation after repeated failures. State the
reason once. Never raise an explicit invocation effort or an `inherit` preference. Set
`codex_effort_complex: inherit` to disable automatic increases. Do not lower an already higher
role preference, switch models as an escalation guess, or rewrite the saved file.

## Resolve the live controls

The selected preferences are instructions to request worker overrides when the host permits them;
they do not bypass session permissions. Do not ask again for an already authorized preference.
Use the real tool schema, advertised models/efforts and context restrictions. Never infer a model
catalog from this document, installed files, a model's name, or a previous host.

Build a temporary runtime JSON outside the repo with these observed fields:

| Field | Meaning |
|---|---|
| `host` | `codex` |
| `delegation` | Is this worker dispatch available and authorized? |
| `overrides_allowed` | Do the session instructions permit these model/effort requests? |
| `model_parameter`, `effort_parameter` | Actual dispatch field names; null when unavailable. |
| `models` | Object mapping advertised model IDs to their supported effort lists; unknown = empty object. |
| `inherited_model`, `inherited_effort` | Verified inherited worker settings, or null when unknown. Account for host defaults/custom-agent settings; don't assume they equal the chat. |
| `override_context` | Any context arguments required for overrides. For a tool requiring a fresh worker, e.g. `{"fork_turns":"none"}`, use exactly its supported fields. Empty object if none. |

If a named agent pins conflicting settings, choose an available authorized generic worker and
supply the role instructions. If that is impossible, treat overrides as unavailable and disclose
inheritance. Never claim arguments override a custom-agent preset when the host says otherwise.
If required context cannot be provided, treat overrides as unavailable.

Run the read-only resolver with the same Python environment used for settings preflight:

```bash
python3 <installed-sdd>/skills/_shared/scripts/resolve_dispatch.py \
  --settings .claude/sdd.local.md --runtime <temporary-runtime.json> --role implementer
```

Add `--complex` or `--escalation` for the conditions above. `--model` and `--effort` are only for
explicit invocation choices, not a second copy of saved settings. A parse/validation error stops
dispatch. The helper neither edits configuration nor calls a model.

## Dispatch, collect, report

1. Use the returned `dispatch_args` in the **actual worker tool call**, alongside the task,
   absolute workspace path, role instructions and relevant artifact paths. A prompt saying
   “use high effort” is not an effort control. Supply accepted decisions explicitly to a fresh
   worker; don't request full parent history when overrides require a fresh context.
2. Preserve task scope, work protection and the selected execution mode. Model preferences do
   not authorize extra parallelism. Collect the worker's complete result before handing off.
3. Separate requested from confirmed values. Before dispatch, say briefly “Requesting Sol / medium
   for coding; Sol / high for review. Execution: sequential.” After dispatch, report actual host
   metadata when available; otherwise say “requested; host did not expose confirmation.” The
   resolver's `confirmed: false` is deliberate. Never use the worker's own guess as confirmation.
4. If a model or effort is unavailable, the resolver plans inheritance and explains why. If the
   tool itself returns a model/effort availability error, retry that role **once** with
   `--availability-fallback` (no model/effort overrides). Keep the same task and required review
   isolation. Permission, authentication and task errors are not availability errors. Never
   retry a timed-out spawn without reconciling whether a worker already exists.
5. If delegation is unavailable, work inline using the current session. Report that the coding
   preferences could not be applied; any inline review is a self-check. Do not spawn a worker
   solely to claim a different model was used.

Existing project settings gain missing defaults in memory; they are not migrated or rewritten.
Do not change user/global Codex configuration or bake project preferences into installed agent
files. The same dispatch procedure works for native and copied installations.
