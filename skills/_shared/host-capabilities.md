# Host capabilities — resolve once, reuse throughout the workflow

**Settings preflight on every invocation:** validate existing `.claude/sdd.local.md` per
[reading semantics](./settings-file.md#reading-semantics) before any project write, command
with side effects, branch change, commit or worker dispatch. Invalid or unreadable settings
stop the run; never substitute defaults. Revalidate if the file changes during a run. This
preflight is separate from the cached runtime below. `config` may enter its explicit repair
dialogue, but cannot write until the user authorizes that repair.

At the first SDD invocation in a session, resolve the following **in-memory** `runtime` record
from the host's instructions, available tool schemas, current mode, and explicit user constraints.
Reuse it across stages and helpers. On resume in a new session, resolve again before acting;
in an existing session refresh only fields whose tools, mode, permissions, or installation changed.
Never persist this record in project settings. Never infer current capabilities from a directory,
an agent definition on disk, a model name, or a command pasted into a user message.

| Field | Resolution and use |
|---|---|
| `host`, `surface` | Actual host and desktop / interactive CLI / headless. Unknown is valid; ask only if the uncertainty affects the next action. |
| `questions` | Available native question tool, its schema, mode restrictions and whether asynchronous; otherwise plain text when another human turn is possible. In headless mode stop at unanswered decisions. A supplied answer answers only that decision. |
| `delegation` | Tool and permission to delegate under the session's instructions. Record advertised role IDs, context inheritance controls, and how final reports return. File presence does not register a role. No permission or tool → inline work. |
| `model_control`, `effort_control` | Supported dispatch parameters and values, plus permission to override. Use [Codex worker settings](./codex-dispatch.md) on Codex; record advertised model/effort pairs and any required context arguments. Fall back to inheritance when controls are unavailable or unauthorized. Never translate Claude tiers or invent a ranking. |
| `team_backend`, `workflow_backend` | True only when the specific TeamCreate / Workflow recipe's required tools, permission, isolation and reporting mechanisms exist. Generic delegation alone does not implement these schedulers. Otherwise sequential TDD. |
| `task_list`, `design_tools`, `file_open` | Actual available mechanisms, independent of host branding. Missing task list → use tasks.json/tracker; missing design tools → declared code-mode fallback. |
| `stage_invocation`, `fresh_context` | Use the exposed installation's invocation and context-reset UI from tool-adapters.md. If skill registration is unknown, use a plain-language request naming SDD, the stage and slug; do not invent a registered command. |

Before the first affected action, briefly state meaningful limitations (for example inherited models,
sequential execution, or self-review). Do not repeatedly print or re-detect the whole record.
All role references, `AskUserQuestion`, `/awesome-sdd:<stage>`, and `/clear` in downstream recipes are logical
operations: render them through this record. They are not permission to call unavailable tools.

For every user-facing decision and explanation, apply [the conversational question contract](./ask-style.md): describe practical outcomes in everyday language. Technical detail appears only when requested or necessary for an informed choice. Ask one concrete choice at a time; detailed records stay in files.

For questions, obey the resolved tool's option limits and mode restrictions over illustrative
question layouts. Pending asynchronous answers block dependent work; continue only independent
work. Never infer approval from time passing or a preselected option. Headless runs must not claim
an interactive interview happened.

Before any project edit, apply [protect-work.md](./protect-work.md), including worker integration
and document commits. When an accepted decision changes, use [change-decisions.md](./change-decisions.md)
to update only the affected work. For a progress-only request, use [status](../status/SKILL.md);
reading progress must not start work or create settings.

On resume, read the saved artifacts, settings and current git state before choosing the next step.
Preserve completed work and accepted answers; ask only genuinely missing decisions. A previous
host's commands, model tiers and delegation IDs do not survive a host change.

See [tool adapters](./tool-adapters.md) for presentation, [agent roster](./agent-roster.md) for
role dispatch, and [handoff](./handoff.md) for stage transitions.
