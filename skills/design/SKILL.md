---
name: design
model: inherit
effort: high
agents: [explorer, critic]
description: >
  Use to produce a Software Architecture Document for a feature — Arc42 12 sections + C4 L1/L2
  inline + ADRs spawned on a blast-radius gate — once spec.md exists. Triggers on
  "design {slug}", "architecture for {slug}", "SAD for {slug}", "arc42 for {slug}",
  "C4 context+container for {slug}", "/awesome-sdd:design {slug}". Drafts §1–§12, discusses unresolved choices
  one at a time in plain language, spawns an ADR only when a decision crosses the
  blast-radius threshold (irreversible / multi-module / has legitimate alternatives), writes each
  resolved section + its ADRs to disk immediately, then runs a clean-context critic and commits
  sad.md + each ADR separately.
  Brownfield: dispatches an Explore subagent to map the repo first. Hard-refuse if spec.md
  is missing; CONTEXT.md is optional (when present its Glossary is canonical).
---

**English only:** Write all conversation, questions, options, progress updates, handoffs, reports, and generated document prose in English. Apply the [language policy](../_shared/artifact-language.md) even when settings or source documents use another language.

**Host runtime:** Resolve and reuse [host capabilities](../_shared/host-capabilities.md) before this protocol. Dispatch roles through the [agent roster](../_shared/agent-roster.md); render questions and handoffs through that runtime. Model/effort frontmatter applies only where the host supports it.

# Skill: design

Generator of the **Software Architecture Document** (`docs/features/<slug>/sad.md` — Arc42 12 sections, C4 Context inline in §3 and C4 Container inline in §5) plus supporting ADRs (`docs/features/<slug>/adr/NNNN-*.md`). It drafts all 12 sections in memory, walks them Socratically one section at a time, spawns an ADR only when a decision's *blast radius* (how painful it is to reverse the decision later) crosses the gate, writes each resolved section and its ADRs to disk as soon as it resolves, runs a clean-context critic over the finished SAD, and then commits once per document — `sad.md` plus each ADR on its own — per [`../_shared/write-and-commit.md`](../_shared/write-and-commit.md). The document itself is the state — resuming after an interrupt is free. L3 Component / L4 Code are out of scope. This file is the spine; detail lives in `references/`.

The Socratic machine, the critic, and the size matrix are **shared** — this skill keeps only its deltas:
→ [`../_shared/socratic-loop.md`](../_shared/socratic-loop.md) · [`../_shared/critic.md`](../_shared/critic.md) · [`../_shared/size-matrix.md`](../_shared/size-matrix.md) · [`../_shared/ask-style.md`](../_shared/ask-style.md)

`sad.md` + ADR prose follow `artifact_language` — the Arc42 section headings, frontmatter, C4/Mermaid keywords and ADR `Status` values stay English → [`../_shared/artifact-language.md`](../_shared/artifact-language.md).

Depth governs the per-section question volume + autonomy → [`../_shared/interview-depth.md`](../_shared/interview-depth.md). C4 diagrams are confirmed in prose, never as raw source → [`../_shared/diagram-presentation.md`](../_shared/diagram-presentation.md). design is also where the feature's **target surface(s)** are chosen — the first §4 decision, written to `sad.md` frontmatter `target_surfaces` and read (never re-derived) by every downstream stage → [`../_shared/surfaces.md`](../_shared/surfaces.md).

## Owner

Architect / Tech Lead (drives everything). PM is consulted only on §10 Quality goals and §11 Risk severities.

## Inputs

- `<slug>` — same feature slug used by every earlier stage.
- **Gate (hard-refuse if missing):** `docs/features/<slug>/spec.md`. If absent → STOP and point: «run `specify <slug>` first — design reads the spec's goals/NFRs as canonical».
- (Optional) `CONTEXT.md` — repo-root and/or `docs/features/<slug>/` → [`../glossary/SKILL.md`](../glossary/SKILL.md). When present, its `## Glossary` is canonical for roles + domain terms (per-feature wins over root on conflict); when absent, the spec's §4 roles are canonical and the handoff recommends `/awesome-sdd:glossary <slug>` before terms drift.
- (Optional) `docs/features/<slug>/ux-flows.md` — the user flows + SCR screen inventory from `ux-flows`. When present it is **evidence** for the §4 Target-surface + UI-architecture decisions and for the §5 containers — read it in step 2; its absence on a UI-touching feature is legal (the stage may have been skipped) but worth naming in the handoff.
- (Optional) `docs/features/<slug>/.size` — depth hint (MVP vs Full detail per the size matrix). Absent → default to M (full set) **and say so loudly in the handoff** — «size M (default — no `.size`; run `/awesome-sdd:classify-size <slug>`)».
- A git repo — so the Step-3 Explore subagent can read code on a brownfield.
- Skip if `sad.md` already has all 12 sections resolved and every gate-worthy decision is recorded (zero ADRs can be valid) — suggest review instead.

## Protocol

1. **Gate + size + set interview depth.** `test -f docs/features/<slug>/spec.md` → missing = refuse with the pointer above. Read `.size` if present (shapes detail; see the size matrix) and `.route` if present. **Resolve discussion depth** per [`../_shared/interview-depth.md`](../_shared/interview-depth.md): reuse the explicit or saved preference, otherwise medium. No repeated depth menu. Keep every question short at every level; the blast-radius and coverage checks still apply.
2. **Read upstream.** `spec.md` (§2 Goals, §3 Non-goals, §6 NFR with numeric targets + measurement, §6.1 Security/privacy + abuse cases, §7 KPIs, §8 Open questions, any §1 ¶4 «Decision override» bullets); `docs/features/<slug>/ux-flows.md` when present (platform decisions, flows, the SCR inventory — evidence for the §4 Target-surface + UI-architecture decisions and the §5 containers); `CONTEXT.md` `## Glossary` when present — read **both** repo-root (project-wide) and `docs/features/<slug>/CONTEXT.md` (feature-scoped); per-feature wins on conflict; canonical roles + domain terms win over anything that contradicts. Neither file exists → the spec's §4 roles are canonical; recommend `/awesome-sdd:glossary <slug>` in the handoff.
3. **Current architecture — read the map, don't re-scan.** Prefer `docs/architecture-map.md` (produced by `survey`): if it exists and is fresh (its `reflects_commit` ≈ current HEAD), read it — that IS the brownfield context (module layout, layering, datastores, conventions, the C4 of what exists). Re-scan only if the map is **absent or stale**: dispatch the [`explorer`](../../agents/explorer.md) agent — role `explorer` via the resolved runtime (host-inherited model, context isolation per [`../_shared/agent-roster.md`](../_shared/agent-roster.md)) — for «module layout, layering/ports conventions, datastores, inter-module comms, anything that constrains `<slug>`», and suggest the user run `survey` to persist it. Greenfield (no source + no map) → note `<!-- brownfield: N/A — greenfield repo -->` in §3. (Fallback to a the resolved explorer fallback Agent if `explorer` unavailable.)
4. **Bootstrap + read template.** Copy [`./templates/sad.md`](./templates/sad.md) → `docs/features/<slug>/sad.md`; patch frontmatter (`updated_at`, `feature_size` from `.size`; leave `target_surfaces: []` empty — it's filled when §4's Target-surface decision resolves in step 6). No commit — commits happen once, at the end of step 7. Read the template's `<!-- … -->` comments (the per-section contract) + [`./templates/adr.md`](./templates/adr.md) (MADR shape). This is the only file write between Step 4 and Step 6 — Step 5 drafts in-memory.
5. **Per-section draft (in-memory).** For each §1 → §12, draft proposed content + the decisions it contains, recording existing conventions and identifying only unresolved choices. Per-section sourcing, item-banks, the question budget, and pre-Socratic hygiene → [`./references/draft-generation.md`](./references/draft-generation.md). Do NOT write `sad.md` here.
6. **Socratic walk + blast-radius gate, per-section write.** For each §1 → §12: keep the section draft in the background and ask one short, concrete choice at a time per [ask-style](../_shared/ask-style.md); map natural replies to the shared internal resolution states (per-section question volume scales with the depth dial — at easy, decide convention-defaults yourself and ladder them into the assumptions ledger, asking only blast-radius decisions), apply answers, run the blast-radius gate on each accepted choice including a clarified edit (spawn an ADR on 2-of-3), then write each resolved part + any required concise ADR to disk immediately — **no commit here**, on any route or depth (an interrupt loses nothing: the disk already holds every resolved section). Revisit a settled choice only when the user corrects it or new evidence conflicts with it. **§4's first decision is the Target-surface selection** — *what's being built* (`backend-service` / `web-frontend` / `mobile-app` / `desktop-app` / `cli` / `worker` / `library-sdk`, derived from spec §1 «for whom» + §4 roles, **with `ux-flows.md` as evidence when it exists** — a real screen inventory is a strong signal for a UI surface; the spec itself names no surface), gated by the blast-radius gate (multi-surface is multi-module + irreversible ⇒ usually an ADR). On resolution, **write `target_surfaces: [...]` to the `sad.md` frontmatter** — it draws one §5 C4 container per surface and is read (never re-derived) by `api` / `sequences` / `tasks` / `plan-tests` / `review`. For each declared **UI surface**, walk the follow-on **UI-architecture decision** (web → SSR/SPA/hybrid; mobile → native/cross-platform; + state/routing if warranted), gated to an ADR like any §4 strategic choice → [`../_shared/surfaces.md`](../_shared/surfaces.md). **For the §3 C4Context and §5 C4Container sections, confirm the diagram per [`../_shared/diagram-presentation.md`](../_shared/diagram-presentation.md)** — write the block into `sad.md`, validate it, then **describe the context / containers in prose** (who talks to what, which systems it depends on) and confirm by prose; **never paste the raw C4 source as the question**. At `easy`, write + a one-line summary and proceed (no per-diagram question). design delta → [`./references/socratic.md`](./references/socratic.md) (section list, decision-types, the gate); gate scoring → [`./references/blast-radius.md`](./references/blast-radius.md); C4 syntax for §3/§5 → [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md); design-specific question shapes → [`./references/ask-examples.md`](./references/ask-examples.md). Maintain the edits-log + an adjacent ADR-spawns log.
7. **Critic + finalize.** Dispatch the [`critic`](../../agents/critic.md) agent — role `critic` via the resolved runtime (clean-isolated per [`../_shared/agent-roster.md`](../_shared/agent-roster.md); **model and effort per the roster and resolved runtime**; runtime fallback if unavailable) — with the design delta in [`./references/critic.md`](./references/critic.md) (over [`../_shared/critic.md`](../_shared/critic.md)) on the final `sad.md` + edits-log + ADR-spawns log; resolve each finding via `AskUserQuestion` (Accept revert / Accept amendment / Override-with-rationale → §1 ¶4 bullet). Run the pre-write backstop scans: **validate every Mermaid block in `sad.md` per [`../_shared/mermaid-check.md`](../_shared/mermaid-check.md)** (render-parse with `mmdc` if available, else the structural lint — fix any that don't parse, never commit a broken diagram); ADR title in decision-form kebab-case + Status `Accepted`; §9 closed against `adr/`; no `<placeholder>` stubs. On pass, write any amendments, then **commit per [`../_shared/write-and-commit.md`](../_shared/write-and-commit.md)** — one commit per ADR (`design: <slug> ADR-NNNN <title>`) and one for `sad.md` (`design: <slug> sad.md`); an unresolved self-check item means no commits. Then **emit the stage-handoff block** per [`../_shared/handoff.md`](../_shared/handoff.md) — *What I did* + *Review* (`sad.md`, `adr/`) + *Run next* — **resolve the next stage per `.route`** (the Routes table in [`../_shared/size-matrix.md`](../_shared/size-matrix.md)): forward `/awesome-sdd:sequences <slug>` (which writes flows into §6); `sequences`' N/A condition = **one actor and no multi-step runtime flow**, skip target `/awesome-sdd:data-model <slug>` (on `quick` — auto-skip with the reason + inverted `↳ or`; on `standard` — offer the `↳ or`; on `full` — no skip line); when skipping, carry the next conditions forward in order: no schema change either → `/awesome-sdd:api <slug>` directly; no contract change either → evaluate `screens`' N/A condition (no UI surface in `target_surfaces`) → `/awesome-sdd:screens <slug>`, or `/awesome-sdd:tasks <slug>` when that holds too.

## Definition of Done

- `docs/features/<slug>/sad.md` exists with all 12 Arc42 sections filled OR marked `<!-- N/A: <reason> -->`.
- §3 has a real `C4Context` block and §5 a real `C4Container` block — real names from the glossary/spec + the scan, no `<placeholder>` stubs, no `Container_Bondary` typos. §6 has ≥1 `sequenceDiagram` (the `sequences` stage then covers every critical flow / §5 AC — no cap).
- Frontmatter `target_surfaces: [...]` is non-empty (the Target-surface decision was made in §4) and §5 draws **one C4 container per declared surface**; each declared UI surface (`web-frontend` / `mobile-app` / `desktop-app`) carries a UI-architecture decision — an ADR, or an inline §4 note if it didn't cross the gate. → [`../_shared/surfaces.md`](../_shared/surfaces.md).
- §9 ADR table is closed against `adr/` (every file has a row, every row a file). No ADR count quota; every ADR Status = `Accepted`, title in decision-form (`0003-sliding-window-counter.md` ✓ vs `0003-rate-limiting.md` ✗), no strawman options.
- §10 scenarios are testable (When / Then / How-verify) and cite spec §6 NFR numbers verbatim (no inventing, no rounding).
- §11 carries a row for every `save_as_oq` decision with both owner AND due (severity literal `Open question`); never N/A.
- §1 Stakeholders + §3 actors match the glossary exactly when a `CONTEXT.md` exists (per-feature wins over root), else the spec's §4 roles (no invented `user`/`admin`).
- Step-3 Explore ran on a brownfield (or §3 has the greenfield note). Edits-log maintained. The critic ran on the post-Socratic SAD; every finding resolved or overridden.
- The step-7 critic + pre-write backstop scans (mermaid-check, ADR-title form, §9 closure, no-placeholder) are this skill's **structural self-check** ([`../_shared/self-check.md`](../_shared/self-check.md)); its result is reported in the handoff.

## Anti-patterns

- **An ADR for every decision** — kills the genre. Only blast-radius decisions become ADRs (no numeric quota). Conversely, missing an irreversibility under-ADRs the feature.
- **ADR `Status: Proposed` from this skill** — it is synchronous (you decide with the user now), so Status is `Accepted`. Use `decide-adr` for an async Proposed → Accepted flow.
- **ADR title in problem-form** (`0003-rate-limiting.md`) or with a **strawman option** (an alternative an existing constraint already excludes) — both dilute the ADR genre and trigger the critic's F6.
- **Inventing §10 numbers** the spec never agreed to — cite spec §6 NFR verbatim. **Naming a concrete stack in §2** that contradicts the repo's conventions without an Override note pointing at §11.
- **Skipping the Step-3 Explore on a brownfield** — guessing the layout produces a fictional §5 Container view and invented §2 Constraints.
- **Reopening settled choices without a reason** — apply user corrections and real conflicts, but do not make the user approve the same decision again as paperwork.
- **Losing a deferred decision** — capture missing ownership and timing one fact at a time; keep unresolved fields visible and block dependent work until resolved.
- **Resolving critic findings unilaterally** (without `AskUserQuestion`) — defeats the user-in-the-loop contract. **Per-section or batched commits** — the disk already protects an interrupted pass; history gets one `sad.md` commit + one per ADR, after the self-check.
- **Spilling into C4 L3/L4** — out of scope; suggest a separate diagramming pass.

## References & template

- [`./references/draft-generation.md`](./references/draft-generation.md) — Step 5: per-section sourcing for §1–§12, item-banks, the question budget, pre-Socratic hygiene.
- [`./references/socratic.md`](./references/socratic.md) — design's delta over the shared Socratic loop (section list, decision-types, the blast-radius gate, the §11 OQ table).
- [`./references/blast-radius.md`](./references/blast-radius.md) — the 3-criteria ADR gate (irreversible / multi-module / legitimate alternatives), scoring, concise records.
- [`./references/critic.md`](./references/critic.md) — design's delta over the shared critic (F5 floor, F6 = NFR-leak + strawman-ADR + §2-vs-repo, F1 = strategic-vector drift).
- [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md) — C4Context + C4Container Mermaid cheatsheet for §3/§5.
- [`./references/ask-examples.md`](./references/ask-examples.md) — design-specific question shapes (strategic-with-ADR-spawn, blast-radius gate, Save-as-OQ follow-up).
- [`../_shared/interview-depth.md`](../_shared/interview-depth.md) — the easy/medium/hard dial set in step 1 (per-section question volume + autonomy).
- [`../_shared/diagram-presentation.md`](../_shared/diagram-presentation.md) — how the §3/§5 C4 diagrams are confirmed in prose (write → validate → describe), never as raw source.
- [`../_shared/surfaces.md`](../_shared/surfaces.md) — the target-surface taxonomy (C4-container-grounded); design owns the selection (§4 first decision → frontmatter `target_surfaces`), downstream reads it.
- [`./templates/sad.md`](./templates/sad.md) · [`./templates/adr.md`](./templates/adr.md) · [`./templates/deployment.md`](./templates/deployment.md) — output scaffolds; inline comments are the per-section generation contract. (C4 syntax → [`./references/c4-mermaid-syntax.md`](./references/c4-mermaid-syntax.md).)
