# Rubric — specify happy path

PASS requires ALL of:

1. `docs/features/rate-limit-bump/spec.md` exists and contains the eight spec sections §1–§8
   (Context, Goals, Non-goals, User stories, Acceptance criteria, NFR, KPI, Open questions —
   numbered headings or clearly equivalent).
2. The §5 acceptance criteria are business-observable: no HTTP verbs, no URL paths, no
   status-code numerics, no SQL fragments anywhere in §5.
3. `docs/features/rate-limit-bump/.size` exists and its content is exactly one token from
   {XS, S, M, L, XL}. If `.route` was written, it is exactly one of {quick, standard, full}.
4. The run's final message ends with a stage-handoff block: a "What I did" part, a
   "Review before continuing" part listing real `docs/features/rate-limit-bump/...` paths, and a
   "Run next" part naming the next `/awesome-sdd:` command.

5. Commits per `skills/_shared/write-and-commit.md`: after the baseline commit, `spec.md` and the
   `.size` + `.route` pair are committed in **separate** commits (the pair together in one; no
   commit mixes `spec.md` with `.size`), no commit touches files outside `docs/features/rate-limit-bump/`
   or `.gitignore`, and nothing under `docs/features/rate-limit-bump/` is left uncommitted. The
   handoff's "What I did" names the commits with their short SHAs.

FAIL if spec.md is missing, a section is absent with no explicit N/A, an AC leaks implementation
tokens, `.size` is malformed, no handoff block was printed, or the commits break item 5.
