# Rubric — design writes progressively and commits once per document

The fixture holds `spec.md` (+ `.size` = S, `.route` = quick) for `rate-limit-bump` and nothing
else — greenfield, no source code, no `docs/architecture-map.md`. The design skill writes each
section to disk as soon as it resolves (no commit), and only after the step-7 critic + structural
self-check makes **one commit per document**: one for `sad.md` and one for **each** ADR file —
per `skills/_shared/write-and-commit.md`. There is no bootstrap commit, no per-section commit and
no batched-section commit on any route or depth. PASS requires ALL of:

1. `docs/features/rate-limit-bump/sad.md` exists, all 12 Arc42 sections (§1–§12) are filled
   OR carry an explicit `<!-- N/A: <reason> -->` marker, and its frontmatter `target_surfaces`
   is non-empty.
2. **Commit count (the key check).** Let N = the number of files in
   `docs/features/rate-limit-bump/adr/` (0 if the folder is absent). The commits after the
   fixture commit `baseline` number **exactly N + 1**: one that touches `sad.md` and one per ADR.
   FAIL on any other count.
3. **One document per commit.** The `sad.md` commit touches only `sad.md`; each ADR commit
   touches exactly one `adr/*.md` file. FAIL if a commit bundles `sad.md` with an ADR, bundles
   two ADRs, or touches unrelated files.
4. **No old-cadence commits.** No commit message after `baseline` contains `bootstrap`, a
   section marker like `§` / `sad §`, `finalization`, or `(quick)`.
5. Nothing is left uncommitted under `docs/features/rate-limit-bump/` (the uncommitted diff vs
   the last commit is empty for that folder).
6. The tail of the run's final message contains the stage-handoff block (*What I did* /
   *Review* / *Run next*); *What I did* lists the commits with short SHAs; *Run next* points at
   a next SDD stage — `/awesome-sdd:sequences rate-limit-bump`, or an auto-skip to
   `/awesome-sdd:data-model rate-limit-bump` or `/awesome-sdd:api rate-limit-bump`: ANY of these is legal on
   route quick; do not require one specific stage.

FAIL if the commit count is not N + 1, if any commit mixes documents, if `sad.md` is missing or
has unfilled sections without an `<!-- N/A: … -->` marker, or if the final message lacks the
handoff block.
