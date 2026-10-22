# Settings — the `implement` engine's delta (step 2)

**The canon lives in [`../../_shared/settings-file.md`](../../_shared/settings-file.md)**: the
documented template, the create-when-absent procedure, the `.gitignore` patch, the semantics of
every key, the edit rules, and the who-creates-who-changes-who-reads table. This file carries only
what is specific to the **engine** — which keys it consumes, how model + effort resolve at
dispatch, and how `.size` scales them. Values are changed by [`../../config/SKILL.md`](../../config/SKILL.md)
(`/awesome-sdd:config`) and by nothing else.

`implement` **ensures** the file the same way the other five creating skills do (protocol step 2:
absent → write the canonical template + patch `.gitignore`; present → read, never overwrite). The
file is normally already there — the backbone's earlier stages create it — so this is the
jump-straight-to-implement path, not the usual one.

## Keys the engine reads

| Group | Keys | Effect |
|---|---|---|
| TDD loop | `tdd`, `stop_on_red`, `max_red_retries` | skip RED; halt-vs-continue on a surviving red; attempts before escalation → [`escalation.md`](./escalation.md) |
| Execution mode | `team_mode`, `workflow_mode`, `max_parallel_agents`, `isolation` | feed the decision tree → [`decision-tree.md`](./decision-tree.md). `team_mode` wins when both could apply; `isolation: inplace` forces parallelism to 1 |
| Gate | `gate_lint`, `gate_vet`, `require_integration` | which tiers the per-task gate runs; `require_integration: always` BLOCKS before dispatch when no Docker daemon answers |
| Commands | `cmd_test_unit`, `cmd_test_integration`, `cmd_lint`, `cmd_vet` | a non-empty value short-circuits detection → [`command-detection.md`](./command-detection.md) |
| Git | `auto_commit`, `branch_strategy` | commit granularity; feature branch vs. current |
| Dispatch | `model_test_author`, `model_implementer`, `model_reviewer`, `effort_test_author`, `effort_implementer`, `effort_reviewer`, `judgment_model` | the model + effort each spawned agent runs at |

**Not engine keys, read elsewhere:** `interview_depth` (the Q&A skills' depth dial) and
`artifact_language` (compatibility key fixed to English in this fork —
[`../../_shared/artifact-language.md`](../../_shared/artifact-language.md)). The engine neither
reads nor writes them; they live in the same file because it is one per-project settings file, not
an implement-only one.

## Model + effort at dispatch

Reuse `runtime` from [host capabilities](../../_shared/host-capabilities.md) and apply
[the roster policy](../../_shared/agent-roster.md) for every role. Claude's override precedence
and judgment **floor** apply only on Claude. Codex inherits the session model and effort unless
an explicit authorized override is supported by the live tool. Saved Claude values stay intact.
Do not export environment variables to try to reconfigure an already-running host.

The banner reports effective model/effort (including inheritance), execution mode and limitations.
L/XL raises desired review depth per the roster; never claim a runtime setting changed when it did not.

## Reading semantics

Apply the shared [strict preflight](../../_shared/settings-file.md#reading-semantics) before any
mutation or worker dispatch. Defaults apply only to missing files/keys. Invalid YAML, duplicate
keys, invalid known values or unreadable settings stop the run with the error; they never enable
automatic commits. The engine is a reader and never repairs the file. `config` owns explicit repair.
