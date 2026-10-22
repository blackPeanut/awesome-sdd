# Language policy — English only

> **Reference-only.** Every skill and agent follows this policy, including standalone utilities,
> config interviews, refusals, progress updates, and stage handoffs.

## Conversation and artifacts

Write all newly authored prose in **English**: questions, option labels and descriptions,
explanations, summaries, reports, diagram labels, specifications, ADRs, task descriptions,
review/fix records, changelogs, and PR bodies. Preserve template headings and machine tokens.
Do not infer the response language from a source document, a previous stage, a quoted example,
or a legacy project setting. Continue in English after context resets and stage transitions.

The `artifact_language` key in `.claude/sdd.local.md` is retained for compatibility with upstream
settings, but this fork supports only `en`. Treat a missing or non-English value as `en` at
runtime. Do not silently edit the settings file: if a conflicting value is found, explain once
in English that this fork uses English; `config` can offer to normalize that key to `en` while
preserving comments and unrelated settings. Never offer a non-English language option.
Keep the settings key out of generated artifact frontmatter.

## Never translate

These are parsed by the implement engine, downstream skills, or external tooling that greps the
artifacts — translating one silently breaks the pipeline:

- Headings downstream stages grep for: `## Shipped` (roadmap), `## Test plan` (spec), `## Glossary`
  (CONTEXT.md) — and every other template heading, as a class.
- Review verdict literals: `PASS`, `CHANGES REQUESTED`, `REVIEW_CLEAN`.
- Tracker states `todo / in_progress / review / done` and task ids `T<n>`.
- Frontmatter keys + values (`status: approved`, `test_cmd`, `reflects_commit`, `target_surfaces`, …)
  and the `.size` / `.route` token files.
- Mermaid keywords (`sequenceDiagram`, `participant`, `alt/else/end`, …) and diagram identifiers that
  name real modules / files / endpoints — labels are English; names stay unchanged.
- `tasks.json` machine fields (`id`, `layer`, `deps`, `acs`, `files_hint`, `slug`) and OpenAPI
  paths / `operationId` / status codes / schema names.
- ADR `Status:` values (`Proposed`, `Accepted`, `Deprecated`, `Superseded`).

Code, tests, test names, commit messages and branch names are **always English** — independent of legacy settings.

## Existing documents and source evidence

Write new documents and all newly written or revised prose in English, even if adjacent files
or the existing document use another language. Leave unrelated existing content untouched;
do not bulk-translate documents as a side effect of another task.
Preserve exact identifiers, API contracts, file paths, commands, proper names, and required
source quotations. Label a necessary non-English quotation as source evidence and explain it
in English; it must not set the language for surrounding prose. Product localization strings
and test fixtures that need a particular language are data, not the plugin's conversation.

## Agent reports

Carry this instruction into every agent dispatch: "Write your report and all newly authored
prose in English. Preserve identifiers, file paths, machine tokens, and exact source evidence."
Agent definitions also state this policy so direct invocation stays English. When incorporating
an agent result, keep the surrounding explanation and final handoff in English.

## Template comments

`<!-- ... -->` comments in templates are generation instructions, not artifact content.
Never copy them into generated output.
