# Tool adapters — presentation after capability resolution

Read [host capabilities](./host-capabilities.md) once and reuse `runtime`. This table renders
logical operations used throughout SDD; it does not detect tools or authorize delegation.
The live tool schema and session instructions always govern execution.

| Mechanism in recipes | Claude Code | Codex desktop / CLI |
|---|---|---|
| `/awesome-sdd:<stage>` | Registered plugin command, e.g. `/awesome-sdd:specify <slug>` | Select the exposed native skill (e.g. `$specify`) or copied skill (`$sdd-specify`). If registration is unknown, say “Use SDD specify for <slug>”. |
| `AskUserQuestion` | Resolved question tool | Resolved native tool within its mode and option limits, otherwise plain text and wait; headless stops at pending decisions. |
| `Agent` / role dispatch | Advertised named agent or generic worker with role instructions | Authorized native delegation with role instructions; no assumed generated named agents. Inline fallback is a self-check. |
| `TeamCreate` / `Workflow` | Only the resolved compatible backend | Only the resolved compatible backend; otherwise sequential TDD. Generic delegation is not a scheduler. |
| `/clear` / fresh context | `/clear` in interactive Claude | Desktop: new chat in the same project. Interactive CLI: `/new`. Headless: start a new invocation in the same workdir. Never create a chat without a user request. |
| `model:` / `effort:` | Claude-scoped roster policy | Inherit host settings unless an explicit authorized override is supported. Never translate tiers. |
| `TaskCreate` / `TaskUpdate` | Use `runtime.task_list` if available | Same; otherwise tasks.json and tracker.md remain the source of truth. |
| Design-tool MCP | Use `runtime.design_tools` | Same; absent → code-mode wireframes and a named limitation. |
| Shared artifacts and `.claude/sdd.local.md` | Repo-relative files | Identical files; `.claude/` is an ordinary directory here, not evidence of the current host. |

For other hosts use their exposed skill picker and new-chat mechanism, or plain-language stage
requests when unknown. No registered command or agent ID can be inferred from a copied directory.

Pencil writes need verified active-document identity; only the user's save persists the document.
Use available file-opening tools to show artifacts. Preserve the English-only policy everywhere.

Missing optional mechanisms degrade to sequential/inline work with accurate disclosure. Missing
human decisions, authorization, required inputs or failed gates do **not** become permission to
proceed. See [agent roster](./agent-roster.md) for model-error retries and report collection,
[ask style](./ask-style.md) for interaction, and [handoff](./handoff.md) for stage transitions.
