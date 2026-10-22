# Contributing to Awesome SDD

## Adding or editing a skill

A skill lives in `skills/<name>/` and is the **source of truth** for its stage.

1. **`SKILL.md` is a short spine.** Frontmatter (`name` + a third-person `description` with
   3–5 English trigger phrases) then a numbered Protocol. Keep it lean — target well
   under ~140 lines. Heavy detail goes in `references/`; output scaffolds go in `templates/`.
2. **Don't duplicate shared logic.** The 4-state Socratic machine, the clean-context critic,
   the size matrix, and the `AskUserQuestion` style live once in `skills/_shared/`. Reference
   them with a relative link and keep only a short per-skill **delta** (your decision-types,
   your section list, your F6 specialization).
3. **Stay stack-agnostic.** No hard-coded language, tracker, test framework, or load tool.
   Detect what the repo uses, or name the detected tool as «whatever your repo already uses».
4. **Gate your inputs.** If a prerequisite artifact is missing, hard-refuse with a pointer to
   the skill that produces it.
5. **One level of `references/`.** No nested reference folders.

All skill instructions, examples, questions, and generated prose use English. Follow
[`skills/_shared/artifact-language.md`](./skills/_shared/artifact-language.md); preserve original
license attribution when maintaining this plugin.

## Subagents

Engine subagents live in `agents/*.md` with `name` / `description` / `model` / `effort`
frontmatter and a system prompt that instructs them to read upstream artifacts directly. Each
agent carries Claude-specific tier defaults; [the roster](./skills/_shared/agent-roster.md)
resolves them for the current host. Codex uses separate `codex_*` preferences and the read-only
[dispatch resolver](./skills/_shared/scripts/resolve_dispatch.py). Copied Codex agent files omit
model and effort so they do not override per-project dispatch settings. Keep requests distinct
from host-confirmed settings, and preserve fallback behavior when controls are unavailable.

Run `python3 scripts/test_codex_dispatch.py` (requires PyYAML) when changing this policy. It tests
the actual planned dispatch arguments, settings precedence, fresh-context requirements and
read-only failure paths without calling a model.

## Before you open a PR

Run the validator locally — it's the same gate the `validate` GitHub workflow runs, and it now
enforces the plugin's **conventions**, not just its structure:

```bash
python3 scripts/validate_plugin.py
python3 scripts/test_native_install.py
```

It checks that the plugin + marketplace manifests agree on name / version / description, that the
version is semver, that every skill and agent carries its required frontmatter (and that `_shared/`
stays reference-only), **and** the consistency invariants in the checklist below. It also greps for
references to the excluded legacy dirs. (The check count is a moving target — CI asserts exit 0, not
a fixed number.)

### Pre-PR checklist

- [ ] **`python3 scripts/validate_plugin.py` passes** (exit 0).
- [ ] **One canonical source / DRY.** Shared logic — the Socratic machine, the critic, the size
      matrix, the ask-style, the surface taxonomy, the handoff block — lives once in
      `skills/_shared/`. Link to it with a relative path and keep only your per-skill *delta*; never
      copy a `_shared/` table (e.g. the surface taxonomy) into a `SKILL.md`.
- [ ] **Stack-agnostic.** No hard-coded language, tracker, test framework, or build/load tool —
      detect what the repo uses, or name it «whatever your repo already uses».
- [ ] **Every skill ends with the handoff block** ([`skills/_shared/handoff.md`](./skills/_shared/handoff.md))
      as its final step.
- [ ] **Invocation form is `/awesome-sdd:<name>`** — the namespaced form, never the hyphenated `/sdd-<name>`.
- [ ] **Relative links resolve.** A `[text](./path.md)` target is a real file. The one exception is a
      template-runtime path (`../spec.md`, `../sad.md`, `../contracts/…`, …) that resolves only inside
      a generated `docs/features/<slug>/` folder — those are allowlisted in the validator.
- [ ] **References in `references/`, templates in `templates/`** — one level deep, no nested folders.
- [ ] **Skill frontmatter never pins an entitlement-gated tier** (`model: opus` / `model: fable`) —
      frontmatter executes before any settings are read, so an account without that tier hard-fails
      at skill start; skills declare `model: inherit` and the validator fails otherwise.
- [ ] **No version-pinned model-capability claims** (like «only on Opus 4.8») — they rot with every
      model release; phrase by tier / by what the resolved model supports.

### Behaviour evals (on-demand — NOT in CI)

`evals/` holds end-to-end skill-behaviour scenarios (they invoke `claude -p` headlessly and an
LLM judge — they cost tokens and are non-deterministic, so they never run in CI). When you change
a skill's *protocol* (gates, routing, artifact shape), run the closest scenario locally:

```bash
./evals/run.sh design-gate-refusal    # or: specify-happy-path, classify-size
```

See [`evals/README.md`](./evals/README.md) for prerequisites and how to add a scenario.

For a local native-catalog smoke check, run `python3 scripts/test_native_install.py --native-catalog`.
This briefly registers a unique temporary marketplace using the installed Codex executable,
checks discovery, and removes that entry. It does not install a plugin.

## Releasing

1. Bump the version in **all five** manifests — `.claude-plugin/plugin.json`,
   `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`,
   and root `plugin.json` —
   the validator fails on any mismatch.
2. `python3 scripts/validate_plugin.py` → exit 0; push to `main`; tag `vX.Y.Z`.
3. Claude Code and Codex pick the release up straight from git (`/plugin install awesome-sdd@awesome-sdd` +
   `/reload-plugins`; `codex plugin marketplace upgrade awesome-sdd`). The `install.sh` path always
   downloads `main` (or `--ref vX.Y.Z`).
