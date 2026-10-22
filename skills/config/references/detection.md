# Config uses the shared host runtime

Read [host capabilities](../../_shared/host-capabilities.md) at session entry and reuse that record.
Config does not re-detect the host from invocation spelling, repository folders or configuration
left by another tool. Those are historical installation traces, not live capabilities.

State meaningful effective limitations. Ask a host question only when available evidence is
ambiguous and resolving it changes the next action. A known Codex session needs no host interview.

Absent compatible team/workflow backends means **effective sequential execution for this run**.
Do not write host clamps to `team_mode`, `workflow_mode` or `max_parallel_agents`. Preserve saved
preferences for the next host; change them only when the user explicitly selects new preferences.
A host switch triggers fresh resolution, not a settings migration.
