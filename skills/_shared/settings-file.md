# The settings file — `.claude/sdd.local.md` (the one canonical template + procedure)

> **Reference-only.** Not a skill. Every skill that ensures, reads or edits the per-project
> settings file reads this. The template below is written **verbatim** — the frontmatter to the
> top of the file, the «What each key does» section as its body — so the file explains itself
> without opening the plugin docs. The engine-side delta (which keys `implement` actually reads,
> model precedence, `.size` scaling) stays in
> [`../implement/references/settings.md`](../implement/references/settings.md).

## Who creates it, who changes it, who reads it

| Role | Who | What they do with it |
|---|---|---|
| **Create** (unconditional, idempotent) | the six pipeline skills — `interview` · `survey` · `roadmap` · `scaffold` · `specify` · `implement` — **and `config` itself** | first protocol step: absent → write the template below + patch `.gitignore`; present → read, never overwrite. `interview` defers creation to its final write point after real answers; outside a repo, in Plan Mode, or headless it writes nothing, settings included. |
| **Change values** (the only writer of existing keys) | [`config`](../config/SKILL.md) | asks, then patches confirmed keys in place. No other skill ever offers to tune a value. |
| **Read** `interview_depth` | `interview` · `specify` · `clarify` · `design` · `sequences` · `ux-flows` | question ceiling in `interview`; otherwise supplies the discussion default → [`interview-depth.md`](./interview-depth.md) |
| **Read** `artifact_language` | every artifact-writing skill | the prose language of pipeline documents → [`artifact-language.md`](./artifact-language.md) |
| **Read** `judgment_model` / `model_<role>` / `effort_<role>` | every skill that dispatches an agent | the tier each agent runs at → [`agent-roster.md`](./agent-roster.md) |
| **Read** the engine keys (`tdd`, `team_mode`, `workflow_mode`, `max_parallel_agents`, `isolation`, `stop_on_red`, `max_red_retries`, `gate_*`, `require_integration`, `auto_commit`, `branch_strategy`, `cmd_*`) | `implement` (`cmd_*` + gates also `fix`) | → [`../implement/references/settings.md`](../implement/references/settings.md) |
| **Read** `auto_commit` | every skill that writes a document | `off` → no commits, the handoff prints the commands → [`write-and-commit.md`](./write-and-commit.md) |

## Create when absent (the procedure)

Run this **first thing in the skill's protocol, after that skill's own gate**, except `interview`,
which reads settings first and creates them only at its final authorized brief-write point.
`scaffold` clears its hard refuse and `implement` its preconditions first, so a refusal leaves
the repo untouched; other skills with no preceding gate simply run it first. It is unconditional — a settings file the user never asked for
is strictly better than a stage that discovers it is missing three commands later — and idempotent.

1. **`.claude/sdd.local.md` exists?** → validate it per Reading semantics and stop this creation procedure. Invalid → stop the skill before mutations. **Never** overwrite, never
   regenerate it from this template, never «refresh» it because a key looks stale.
2. **Absent** → write it: the documented frontmatter below at the top, then the «What each key
   does» section as the file's markdown body. Keep the inline comments — they carry the allowed
   values, which is what makes the file self-documenting.
3. **Patch `.gitignore`** (create it if absent) so it contains `.claude/*.local.md` and
   `.worktrees/` — both are per-developer and must never be committed. The `.claude/*.local.md`
   glob already covers `sdd.local.md`; don't add a redundant explicit line, and don't duplicate a
   line that is already there.
4. **Say one line** and move on — no question, no menu:
   «`.claude/sdd.local.md` created with documented defaults — `/awesome-sdd:config` to tune it».
   Render the config request through the already resolved `runtime.stage_invocation`;
   native and copied installations can expose different names → [`tool-adapters.md`](./tool-adapters.md).

The settings file itself is **never committed** (it's gitignored). The `.gitignore` patch is, and
rides along in the stage's first commit ([`write-and-commit.md`](./write-and-commit.md)).

## The documented frontmatter

<!-- This block is written verbatim to the top of `.claude/sdd.local.md`; the «What each key does»
     section below becomes the file's body. Keep the inline comments — they list the allowed values. -->

```yaml
interview_depth: medium    # easy | medium | hard — plugin-wide default for specify/clarify/design (see _shared/interview-depth.md)
artifact_language: en      # English only; legacy non-en values are treated as en (see _shared/artifact-language.md)
tdd: true                  # enforce red→green→refactor
team_mode: true            # true → agent team via TeamCreate
workflow_mode: auto        # auto → dynamic Workflow; off → never
max_parallel_agents: 3     # integer ≥1 — fan-out cap for team/workflow modes (1 = sequential)
isolation: worktree        # worktree | inplace (parallel>1 ⇒ forces worktree)
stop_on_red: true          # halt on a red that survives escalation, vs drop-and-continue
max_red_retries: 3         # integer ≥1 — RED→GREEN attempts before escalation
gate_lint: true            # true | false — include lint in the per-task gate
gate_vet: true             # true | false — include vet / static-analysis in the per-task gate
require_integration: auto  # auto | always | never (Docker-probed)
auto_commit: per_task      # per_task | per_phase | off — off also stops document-stage commits
branch_strategy: feature   # feature | current
cmd_test_unit: ""          # empty = autodetect (escape hatch)
cmd_test_integration: ""
cmd_lint: ""
cmd_vet: ""
model_test_author: sonnet     # per-role model (see _shared/agent-roster.md); inherit = session model
model_implementer: sonnet
model_reviewer: opus
judgment_model: opus       # Claude-only preference; other hosts inherit; per-role overrides win
effort_test_author: medium    # per-role effort; raised to high on escalation
effort_implementer: medium
effort_reviewer: high
```

## What each key does

- **`interview_depth`** — `easy | medium | hard`. The plugin-wide default for the **Q&A skills'** depth dial (`specify` / `clarify` / `design`), which governs how much each skill decides on its own vs. interrogates you (question volume, autonomy, which ideation analyses run, per-diagram confirm vs. proceed). Reuse it without a repeated opening menu; an explicit conversation preference or `--depth=` overrides it for the run. Question length stays short at every depth. It does **not** affect AC-completeness (that's a floor at every level). For `interview`, the same setting is a question ceiling without an opening selector; risk/research are independent (see its adaptive exception). Full semantics → `skills/_shared/interview-depth.md`.
- **`artifact_language`** — `en` only in this fork. All conversation and generated document prose is English. Treat legacy non-English values as `en` at runtime without rewriting the settings file. `config` may offer to normalize the value to `en`; no language selection menu. Existing files and neighbouring documents never override this policy. Preserve machine tokens and exact source evidence per [`artifact-language.md`](./artifact-language.md).
- **`tdd`** — when false, RED is skipped and the engine writes code directly (warns; you lose the safety net).
- **`team_mode` / `workflow_mode`** — feed the `implement` decision tree. `team_mode` wins when both could apply. Both need compatible resolved backends (`TeamCreate` / `Workflow`); absent backends mean effective sequential execution without rewriting saved preferences → `skills/_shared/tool-adapters.md`.
- **`max_parallel_agents`** — fan-out cap for team/workflow modes. `1` forces sequential.
- **`isolation`** — `worktree` gives each parallel agent its own git worktree under `.worktrees/`; `inplace` edits the checkout directly and **forces parallelism to 1**.
- **`stop_on_red`** — `true`: a red that survives escalation halts the run. `false`: drop that task, auto-block its dependents, continue other branches.
- **`max_red_retries`** — RED→GREEN attempts before escalation.
- **`gate_lint` / `gate_vet`** — include lint / vet in the per-task gate (skipped gracefully if no command is detected).
- **`require_integration`** — `auto`: run integration tests if a Docker daemon answers, else mark NON-red; `always`: BLOCK before dispatch if Docker is absent; `never`: skip the integration tier entirely.
- **`auto_commit`** — `per_task` (default), `per_phase`, or `off` (leave commits to the user). Read by **every stage**: document stages commit one commit per document at the end of the step on `per_task` / `per_phase` and only print the commands on `off` (→ `skills/_shared/write-and-commit.md`); in `implement`, `per_task` commits each task, `per_phase` batches per dependency layer.
- **`branch_strategy`** — `feature`: ensure work is on a feature branch (create one if on the default branch); `current`: commit on the current branch.
- **`cmd_*`** — explicit command overrides; non-empty values short-circuit detection (the escape hatch for unusual repos). **Empty is the better default** — the detection cascade reads the repo's own Makefile / package scripts / language manifests, so a pinned command is one more thing to keep in sync.
- **`model_*` / `effort_*`** — per-role model + effort for the three execution agents, applied when the engine spawns them (it overrides the agent's frontmatter default). Roster defaults + rationale → `skills/_shared/agent-roster.md`.
- **`judgment_model`** — Claude-only judgment model preference; default `opus`, with per-role overrides taking precedence. Other hosts preserve it but inherit their session model. See [agent roster](./agent-roster.md) for the floor rule, supported overrides and unavailable-model fallback.

## Editing an existing file (only `config` does this)

The file is the user's. It carries their edits, their comments, and possibly keys this version of
the plugin has never heard of. So:

- **Patch key by key.** Rewrite only the lines whose values the user just confirmed. Never
  regenerate the file from the template — that is how a hand-written comment or a hand-added key
  silently disappears.
- **Preserve comments, key order, and unknown keys** exactly as they are. An unknown key is a
  forward-compatibility feature, not garbage to clean up.
- **Write each value in its documented form** — bare `off`, not `"off"`; bare `3`, not `"3"`. The
  template above is the reference spelling; a re-quoted value reads as a different setting on the
  next diff.
- **Show `old → new`** for every key you touch, and separately name anything that was **derived
  rather than asked** (an effective runtime fallback, an unchanged autodetect value) — a value the user didn't choose
  must never appear as if they had.
- **A malformed frontmatter is never fixed silently.** Show what failed to parse and offer the
  choice: rewrite from the template (stating what will be lost) or stop and let the user fix it
  by hand.

## Reading semantics

Missing files and missing keys use documented defaults. An existing file must have closed YAML
frontmatter containing a mapping with unique string keys. Parse it with a safe parser: bare
`off` is a string, only `true`/`false` are booleans. Validate known enums, boolean types, positive
integer limits, string commands/models and documented effort values. Unknown keys are ignored
after parsing and preserved on disk. Legacy language values resolve to English without rewriting.

Run the read-only helper [`scripts/settings.py`](./scripts/settings.py) with Python 3.10+ and
PyYAML from an available environment:

```bash
python3 <installed-sdd>/skills/_shared/scripts/settings.py .claude/sdd.local.md
```

It returns JSON and exits nonzero on invalid/unreadable settings. Report its path and parsing or
validation error, then **stop before mutations**: no artifact/status writes, test/build commands,
workers, branches, staging or commits. Never reinterpret a malformed file as missing or use a
previously cached configuration after the file changes. Do not repair it, discard individual
invalid keys or silently turn `auto_commit` back on. Only `config`'s explicitly authorized repair
may write a replacement; revalidate it before resuming any workflow.

If the helper's runtime is unavailable, an existing reliable safe YAML parser with these same
boolean, duplicate-key and schema checks may perform preflight. Otherwise report the missing
dependency and stop; never parse settings with regex or proceed on guessed defaults. The
implementation evidence helper requires Python 3.10+ and PyYAML; dependency installation is
subject to the host's normal permissions.
