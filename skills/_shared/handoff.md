# Stage handoff — what every skill prints when it finishes (the output contract)

> **Reference-only.** Not a skill. **Every** skill ends by emitting the handoff block defined here —
> as its **last output**, after its structural self-check and its per-document commits
> ([`write-and-commit.md`](./write-and-commit.md)). The format lives only in this file; each
> skill keeps a one-line pointer and supplies its own *What I did* / *Review* / *next command*. This
> exists because a bare «Next: …» line is hard to act on — the user can't tell what changed, which
> files to open, or what to run next without scrolling back.

Use the already resolved `runtime` from [host capabilities](./host-capabilities.md).
Every `/awesome-sdd:` stage reference in the sequence below is logical notation, not literal output.
Render it with `runtime.stage_invocation`; render context resets with `runtime.fresh_context`.
Never print `/clear` as a Codex instruction. Unknown registration → plain-language SDD request.

## The handoff — brief, useful, with details by link

Use a short completion note in ordinary language. For example:

> Bookings now save immediately and retry failed emails. Your choices are recorded in the
> design document (link to its actual path); the checks passed and the changes are committed.
> Next: start a fresh conversation and ask SDD to plan the implementation tasks for booking.

Adapt the next step to the actual route and runtime. This is a summary, not another approval
request. If a decision is still needed, ask that single question instead of implying completion.

Include only what helps the user continue:

- **What changed:** one to three short outcomes, plus failures, skipped verification or unresolved
  choices that matter. Report self-check results honestly; do not repeat internal deliberation.
- **Records:** link the main changed artifact and its supporting folder/diff when useful. Keep
  detailed decision logs, ADR indexes and long commit lists in files; show a concise commit
  reference or explain why work is uncommitted. Full lists are available on request.
- **Next step:** one clear action with the real slug and the host's supported invocation. Use the
  resolved fresh-context instruction for a forward backbone handoff, not a literal Claude command
  on another host. Add a skip alternative only when it materially changes the user's next action.

State the size/route when newly chosen, changed or defaulted because missing; don't repeat
unchanged metadata at every handoff. The canonical table below is the agent's routing reference,
not a checklist the user must read. Detailed review remains available when requested. Never ask
for whole-document sign-off merely to reconfirm answers already given during the conversation.

## Variants

- **Backbone forward handoff** (`survey → … → review → ship`): `/clear` mandatory + the next stage.
- **Route-resolved forward handoff** (a backbone stage whose successor is an *optional* stage —
  `specify`, `clarify`, `design`, `sequences`, `data-model`, `api`, `tasks`): before printing *Run next*,
  resolve the next stage per `docs/features/<slug>/.route` and the Routes table in
  [`size-matrix.md`](./size-matrix.md):
  - **`quick`** — evaluate the next optional stage's N/A condition yourself. Holds → *Run next*
    names the post-skip stage, *What I did* states «auto-skipped `<stage>`: <reason>», and the
    `↳ or` line **inverts** — it offers the skipped stage («run the full path»). Doesn't hold →
    normal forward handoff (the stage is not skipped).
  - **`standard`** — normal forward handoff; add the `↳ or` skip-alternative when the N/A
    condition holds (the user picks).
  - **`full`** — normal forward handoff; **never** print an `↳ or` skip line.
  Missing `.route` → `standard`. The route steers handoffs only — a stage invoked directly always
  runs.
- **Loop-back** (`review → implement` on `CHANGES REQUESTED`): **no `/clear`** — you stay in context
  to iterate; *Run next* = `/awesome-sdd:implement <slug>` (fix), then re-review the changed surface.
- **Terminal** (`ship`): there is no `/sdd` successor. *Run next* becomes **Done** — the PR command/URL
  + «merging to main is your call»; still print *What I did* + *Review* (the changelog + PR).
- **Read-only recap** (`status`): summarize finished work, blockers and one next step from saved
  evidence. No writes, commit, context reset or automatic continuation.
- **Utility** (`interview`, `config`, `classify-size`, `glossary`, `decide-adr`, `roadmap`, `design-system`, `fix`): called ad-hoc, not a
  gate. `/clear` is **optional** (recommend it only if the context is large); *Run next* = «resume
  your backbone stage», naming the likely one (e.g. `/awesome-sdd:design <slug>`). Print *What I did* +
  *Review* (the one file it wrote). One exception: `fix` alone adds a **conditional** recommendation —
  when the fix touched >5 files or crossed a module boundary, *Run next* also offers
  `/awesome-sdd:review <slug>` (a recommendation, never a gate).

## Canonical sequence (stage → review-files → next)

| Stage | Review before continuing (files written) | Run next |
|---|---|---|
| `interview` | `docs/idea-brief.md` (eight sections; conversation artifact when writes are prohibited) | Only `ready-for-roadmap` → `/awesome-sdd:roadmap`; `ready-for-specify` → `/awesome-sdd:specify <slug>`. Otherwise name the evidence action, reframe, or stop. `survey` is suggested separately if a repo map is needed. |
| `survey` | `docs/architecture-map.md` (+ scaffold `tasks.json` on greenfield) | `/awesome-sdd:roadmap` when a brief is on disk (the map supplies the zones) ↳ or brownfield → `/awesome-sdd:specify <slug>`; greenfield → `/awesome-sdd:scaffold` |
| `scaffold` | the materialized skeleton (committed diff) + green smoke test | `/awesome-sdd:specify <slug>` |
| `specify` | `docs/features/<slug>/spec.md` | `/awesome-sdd:clarify <slug>` ↳ or `/awesome-sdd:ux-flows <slug>` (zero §8 OQ — fast lane; no human-facing UI → `/awesome-sdd:design <slug>`) |
| `clarify` | `docs/features/<slug>/spec.md` (tightened) | `/awesome-sdd:glossary <slug>` ↳ or `/awesome-sdd:ux-flows <slug>` (no human-facing UI → `/awesome-sdd:design <slug>`) |
| `ux-flows` | `docs/features/<slug>/ux-flows.md` (flows + SCR inventory) | `/awesome-sdd:design <slug>` |
| `design` | `sad.md` (C4 §3/§5 + `target_surfaces`) + `adr/` | `/awesome-sdd:sequences <slug>` ↳ or `/awesome-sdd:data-model <slug>` (XS/S, no multi-step flow — fast lane) |
| `sequences` | `sad.md` §6 (flows) | `/awesome-sdd:data-model <slug>` ↳ or `/awesome-sdd:api <slug>` (XS/S, no schema change — fast lane) |
| `data-model` | `data-model.md` + staged `migrations/` | `/awesome-sdd:api <slug>` ↳ or `/awesome-sdd:screens <slug>` (XS/S, no contract change — fast lane; no UI surface → `/awesome-sdd:tasks <slug>`) |
| `api` | `contracts/openapi.yaml` (+ `events.md`, `api-sync-report.md`) | `/awesome-sdd:screens <slug>` ↳ or `/awesome-sdd:tasks <slug>` (no UI surface in `target_surfaces` — fast lane) |
| `screens` | `docs/features/<slug>/screens.md` (+ `screens.pen` / Figma node-refs per tool) | `/awesome-sdd:tasks <slug>` |
| `tasks` | `tasks/` + `tasks.json` | `/awesome-sdd:plan-tests <slug>` ↳ then `/awesome-sdd:implement <slug>` |
| `plan-tests` | `test-plan.md` (or `spec.md` `## Test plan` for XS/S) | `/awesome-sdd:implement <slug>` |
| `implement` | the committed diff (code + tests) + `tasks/tracker.md` / `tasks.json` statuses (+ `docs/roadmap.md` `Status: building`) | `/awesome-sdd:review <slug>` |
| `review` | `_review/review-<date>.md` (committed; + `spec.md` when a finding was deferred) | `/awesome-sdd:ship <slug>` (PASS) · `/awesome-sdd:implement <slug>` (CHANGES, no `/clear`) |
| `ship` | `CHANGELOG` + `docs/roadmap.md` (each committed before the PR command) + the PR | **Done** — PR command/URL; merge is your call |
| `status` | existing artifacts and evidence (read-only) | one next action or unanswered choice; no automatic continuation |
| `config` | `.claude/sdd.local.md` (the settings file itself is gitignored — the `.gitignore` patch is the only thing to commit) | resume your backbone stage — e.g. `/awesome-sdd:specify <slug>` |
| `classify-size` | `.size` + `.route` | resume — e.g. `/awesome-sdd:specify <slug>` |
| `design-system` | `docs/design-system.md` | resume — e.g. `/awesome-sdd:ux-flows <slug>` |
| `glossary` | `CONTEXT.md` | resume — e.g. `/awesome-sdd:design <slug>` |
| `decide-adr` | `adr/NNNN-<title>.md` | resume — `/awesome-sdd:tasks <slug>` or `/awesome-sdd:plan-tests <slug>` |
| `roadmap` | `docs/roadmap.md` | resume your backbone stage |
| `fix` | `_fixes/<date>-<short>.md` + the diff (+ the spec patch if any) | resume — or `/awesome-sdd:review <slug>` when the fix was wide (>5 files / cross-module) |

The `↳ or` cells above show the `standard`-route rendering; on `quick` the stage auto-skips (and
the `↳ or` inverts), on `full` the `↳ or` line is dropped — per the *Route-resolved* variant.

## Discipline

- End with one concise handoff after the required checks and authorized writes/commits.
- Link real files or diffs; don't dump the artifacts into the conversation.
- Preserve blockers and uncertainty. A recap is not consent and does not mark pending work done.
- Use this shared presentation even when a skill's local wording names the old What I did /
  Review / Run next headings. Those are content roles, not mandatory lengthy sections.

## Where each skill calls this

Every skill's final protocol step ends with: «emit the **stage-handoff block** per
[`handoff.md`](./handoff.md)» + its own next command from the table above. The format + variants live
here; the skill supplies only the run-specific content.
