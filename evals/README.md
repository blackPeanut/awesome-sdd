# SDD behaviour evals — on-demand, NOT CI

End-to-end scenarios that drive real Claude or Codex sessions over a fixture repo and let an LLM judge
verify the outcome against a rubric. They complement `scripts/validate_plugin.py` (structure):
evals check that a **skill's protocol actually behaves** —
gates refuse, artifacts land in shape, handoffs are emitted.

> **Why not CI.** Each run invokes `claude -p` (the run under test) + a judge call — it costs real
> tokens, takes minutes, and is non-deterministic. Run evals locally when you change a skill's
> protocol; CI stays deterministic (`validate`).

## Live Codex workflows

Recovery mechanics also have deterministic regression suites, run in CI without model calls:

```sh
python3 scripts/test_safe_upgrade.py
python3 scripts/test_recovery.py  # Python 3.10+ and PyYAML
```

The installer suite injects download, validation and swap failures, termination and forced kills,
then checks that previous files survive or recover. The recovery suite uses real Git repositories
and executable gates for interrupted commits, phase commits, commits off, changed inputs, missing
evidence and malformed settings. These verify helpers and filesystem outcomes; they do not prove
that an agent selected every required verification input or followed every instruction.

```sh
./evals/run.sh --host codex
./evals/run.sh --host codex questions-resume
python3 evals/run_codex.py fresh-resume config-runtime --timeout 240
```

Requires an authenticated `codex` CLI, Python 3 and Git. This costs real model usage. The runner
uses the CLI's default model, ignores user config (auth remains available), and runs with
`workspace-write` sandboxing. The judge runs separately with a read-only sandbox. It neither
installs a plugin nor changes your home/configuration. Override the binary with `SDD_CODEX_BIN`.

The working checkout's skills and agents are copied to an isolated evidence directory and invoked
by explicit SKILL.md path. This tests actual workflow instructions in Codex, **not plugin discovery**;
`scripts/test_native_install.py --native-catalog` covers native catalog discovery separately.

| Scenario | Observable behavior |
|---|---|
| `questions-resume` | First turn asks without writes; an exact-session resume supplies four signals; a second resume confirms XS/quick. Files change only after confirmation, and the final handoff uses a Codex request. |
| `fresh-resume` | A new session reads saved size/route/spec, applies explicit reclassification, synchronizes the mirror and preserves the accepted decision word for word. |
| `config-runtime` | Config preview explains inherited Codex models and effective execution limits without offering Claude presets or overwriting saved preferences. |

All scenarios include legacy `artifact_language: uk`, Ukrainian source prose, and saved Claude
model/team settings. Every assistant message is checked for Cyrillic and leaked Claude commands.
File checks protect settings, unrelated artifacts and plugin sources. A separate Codex judge
checks semantic behavior using the full event transcript; missing criteria, malformed responses,
CLI errors, timeout, or missing completion fail the run. The judge cannot turn an infrastructure
failure into a pass. Deterministic harness tests run in CI without contacting any model.

The runner prints and retains an evidence directory with prompts, JSONL events, stderr, final
messages, fixture files and `results.json`; `--output NEW_DIRECTORY` selects its location.
Resume always uses the thread ID created by that scenario, never `--last`. These test sessions
are recorded by Codex so exact-session resume works. Keep transcripts when comparing revisions;
remove the temporary evidence directories when no longer needed.

The [2026-10-21 evaluation record](reports/2026-10-21-codex.md) documents the completed turns and rate-limited checks.

These are **headless text-turn tests with scripted answers**, not proof of native desktop question
widgets or a human interview. Desktop checks (including asynchronous waiting and new-chat handoff)
are documented in [the Codex desktop protocol](interactive/codex-desktop.md). Do not report that
manual protocol as passed unless it was actually run.

## Claude prerequisites


- `claude` CLI installed and logged in. The sdd plugin does **not** need to be installed —
  `run.sh` loads it from this checkout via `--plugin-dir`, so the eval exercises the working
  tree, not an installed version. The checkout is also passed with `--add-dir` so referenced
  instructions can be read from the fixture session.
- `jq`, `git` on PATH.
- Budget: one scenario ≈ one short agent session + one judge call.

## Run

```bash
./evals/run.sh                        # all scenarios
./evals/run.sh design-gate-refusal    # one scenario
SDD_EVAL_MODEL=opus ./evals/run.sh classify-size   # override the model
```

Exit code is non-zero when any scenario's verdict is `FAIL` (or unparseable), the CLI run
fails, or a plugin instruction read is denied.

## How a scenario works

1. `run.sh` copies `scenarios/<name>/fixture/` into a `mktemp` dir and `git init && commit`s it
   (the baseline).
2. It runs `claude -p "$(cat prompt.txt)" --permission-mode acceptEdits --max-turns 40
   --output-format json` **inside that dir**. Interactive skill scenarios pin `--depth=easy` and state
   «headless — no interactive user», because a headless run cannot answer `AskUserQuestion`.
   Direct agent contract scenarios supply the explicit mode and bounded inputs instead.
3. It then asks a judge (`claude -p` with [`judge-prompt.md`](./judge-prompt.md)) to verify the
   **rubric** against the file tree, the `git log` (so rubrics can count/inspect the run's
   commits — `Bash(git:*)` is pre-allowed in the throwaway workdir so runs CAN commit), the
   full `git diff` vs the fixture baseline (committed + uncommitted), and the complete
   run's final message. The judge answers one JSON object:
   `{"verdict": "PASS"|"FAIL", "checks": [...]}`.

## Scenarios

| Scenario | What it proves |
|---|---|
| `english-only-config` | Config questions and a sample handoff stay English despite legacy `artifact_language: uk` and Ukrainian source docs; preview leaves files untouched |
| `specify-happy-path` | `/awesome-sdd:specify` produces a spec.md with §1–§8, business-observable ACs, `.size` + `.route`, and the handoff block |
| `design-gate-refusal` | `/awesome-sdd:design` on a folder with `.size` but **no spec.md** refuses, points at `specify`, writes no sad.md/ADRs |
| `classify-size` | `/awesome-sdd:classify-size` writes one-token `.size` + `.route` and hands off (utility variant) |
| `api-fastlane-no-datamodel` | `/awesome-sdd:api` on a no-schema-change feature **without** data-model.md does not refuse — it derives the contract from the existing schema, names the legal skip + «existing schema» origins, and emits the handoff |
| `api-schema-change-refusal` | `/awesome-sdd:api` on a feature **with** a schema change (staged migration + new sad §5 entity) and no data-model.md hard-refuses, names `data-model`, writes no contract and no self-served data-model.md |
| `design-commit-per-document` | `/awesome-sdd:design` on route quick + depth easy writes all 12 SAD sections to disk as they resolve, then commits once per document after the self-check — exactly 1 `sad.md` commit + 1 per ADR; no bootstrap / per-section / batch commits |
| `tasks-compile-coupled-lane` | `/awesome-sdd:tasks` on a Go feature extending a shared interface emits no standalone interface-only task — it folds the contract change or marks the compile-coupled pair via a shared `files_hint` |
| `ux-flows-code-mode` | `/awesome-sdd:ux-flows` on a UI feature with a committed `docs/design-system.md` (`tool: code`, mobile-first) derives `ux-flows.md` headlessly — valid mermaid flowcharts, an SCR inventory, a full AC-coverage map, the mobile-first posture honoured, and a handoff forwarding to `design` |
| `roadmap-fog-unsized` | `/awesome-sdd:roadmap` on a brief whose second data source has never been inspected writes `fog` in that step's **`Size`** cell and parks it as ONE area in `## Not yet specified` instead of sizing the unformulated — and writes the file at all, with no architecture map in the fixture |
| `roadmap-same-zone-wave` | `/awesome-sdd:roadmap` keeps two steps that both edit `internal/checkout/pricing.go` out of the same wave (the graph permits it, the codebase doesn't) while still letting the `internal/notify/` step run in parallel |
| `clarify-judgment-sonnet` | `/awesome-sdd:clarify` with `judgment_model: sonnet` in the fixture settings completes the sweep on the sonnet tier — the setting is read + honoured, the handoff reflects sonnet and never claims opus. *Limitation:* headless can't simulate a missing entitlement, so this covers the configuration path only, not the hard-failure fallback (retry on `inherit` per `agent-roster.md` §Model availability) |

## Interview 2.0 regression scenarios

| Scenario | What it proves |
|---|---|
| `interview-headless-no-writes` | No human response channel means no brief, settings, gitignore, helper claim, or fabricated interview |
| `researcher-fact-check-conflict` | Fact-check mode retains conflicting source applicability and owner-report limits without becoming competitive research |
| `interview-critic-grounded` | Explicit interview mode returns at most three grounded risk findings, not an invented breach or a legacy quota |
| `specify-brief-reuse` | Specify preserves the accepted brief and asks no repeated discovery, while retaining source limits |

The helper scenarios exercise agent instructions directly, not a headless interview. They use
local fixtures and disable external research. `interview-headless-no-writes` tests refusal only;
prewritten answers do not simulate a live human. For actual adaptive questioning, use
[`interactive/interview.md`](./interactive/interview.md) with a human operator and retain the
conversation. Do not report a headless scenario as proof of interactive behavior.

## Adding a scenario

Create `scenarios/<name>/` with three parts:

- `fixture/` — the starting repo tree (committed as the git baseline; keep it minimal).
- `prompt.txt` — the exact `-p` prompt: the `/awesome-sdd:` command line plus the headless framing
  (state the idea/answers inline; pin `--depth=easy` for interactive skill protocols). Direct
  agent scenarios instead name the instruction file and explicit mode.
- `rubric.md` — numbered PASS conditions the judge can verify from the diff/tree/final message
  only. Make every item observable; «the model tried» is not a rubric item.

For direct agent contract scenarios, `{{PLUGIN_ROOT}}` in `prompt.txt` resolves to the checkout under test. Cite successful instruction loading in the final report so a missing agent definition cannot silently pass the behavioral rubric.
