# Agent roster — roles and portable dispatch

Resolve [host capabilities](./host-capabilities.md) once, then use that `runtime` for every
dispatch. A role is a task contract in `agents/*.md`, not a promise that a named agent is registered.

| Role | Work | Desired reasoning depth |
|---|---|---|
| `explorer` | cited read-only codebase scan | low |
| `test-author` | failing regression tests | medium; high on escalation |
| `implementer` | implementation, refactor and gates | medium; high on escalation |
| `reviewer` | independent code and acceptance review | high |
| `critic` | artifact coherence review | high |
| `devils-advocate` | ambiguity and grounded interview risks | high |
| `researcher` | cited research and bounded fact-checking | medium |
| `strategist` | alternative approaches | high |
| `analyst` | multi-perspective synthesis | high |
| `pen-keeper` | reconcile design library with the canon | medium |

## Dispatch

1. Read the role definition and supply its instructions, input paths, constraints and required
   report shape. Do not assume a generic worker automatically loads the file.
2. If `runtime.delegation` permits delegation, use its advertised tool and schema. Only select
   a named role when that exact ID is advertised. Claude plugin IDs may be `awesome-sdd:<role>`;
   generated copied-install IDs may be `sdd-<role>`. Neither is assumed to exist in Codex.
3. For independent review, request a fresh context only through an actual context-control field.
   If the tool cannot guarantee isolation, disclose shared context. If delegation is unavailable
   or unauthorized, apply the role inline and label the result **self-check**, not independent review.
4. Resolve model and effort below before the call. Never send a Claude alias to Codex.

## Model and effort resolution

**Codex and other hosts:** inherit the session model and effort by default (omit dispatch overrides).
Claude frontmatter, `judgment_model: opus`, `model_*: sonnet` and `CLAUDE_CODE_*` variables are not
portable runtime choices. Preserve these saved values but do not apply them outside Claude.
An explicit user-selected host model or effort may be used only when the live tool supports it
and session instructions permit the override; unknown values are not guessed or translated.
If no override is possible, report inheritance, not an escalation that never happened.

**Claude Code only:** compatible overrides resolve in this order: host environment > explicit
invocation > `model_<role>` > `judgment_model` (judgment roles only) > agent frontmatter > session.
The frontmatter's haiku/sonnet/opus defaults are Claude-specific. An unset judgment default is a
**floor**, not a pin: when the host establishes that the session model is stronger, inherit it;
when comparison is unknown, inherit rather than invent a tier ranking. Explicit values remain
explicit. `CLAUDE_CODE_SUBAGENT_MODEL` and `CLAUDE_CODE_EFFORT_LEVEL` apply only through a supported
Claude dispatch mechanism; a shell export cannot retroactively reconfigure an existing tool.
Do not claim a setting took effect without evidence from the host.

For L/XL, desired execution depth rises to high and reviewer/critic depth to the highest supported
level up to xhigh. Explicit authorized effort choices win. On hosts without supported override
controls this changes review thoroughness, not the model or reasoning setting.

## Model availability — degrade, don't block

If an allowed override fails specifically because the model or effort is unavailable, retry the
same task once using host inheritance (omit the override, or use `inherit` only if the schema
accepts it). Disclose the fallback. Do not retry authentication, permission or task errors as
model errors. Never edit saved settings to make a retry work.

## The shared agent contract

1. **Context is host-dependent.** Supply paths, goals and accepted decisions explicitly. For
   critique, have the worker read original artifacts rather than the parent's paraphrase. Never
   claim that the parent history is absent unless the tool guarantees it.
2. **Collect the actual report.** Use the host's return/wait mechanism. Completion or idle status
   alone is not a verdict. Do not instruct workers to message another chat unless the user has
   authorized that communication. Missing reports leave the review incomplete.
3. **Bound the worker.** Ask it to execute its assigned work directly, use tools, avoid further
   delegation and report absolute paths. This is a task boundary, not a claim that all hosts
   prohibit nested agents. The lead owns coordination.
4. **Verify before claiming done.** Identify the command, run it, read the output, then report
   the evidence. Unsupported or skipped checks must be named.
5. **Cite or drop.** Judgment findings need file:line plus the relevant artifact/AC clause.
