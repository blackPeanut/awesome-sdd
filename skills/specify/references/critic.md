# specify — delta over the shared critic

Read [`../../_shared/critic.md`](../../_shared/critic.md) for the canonical dispatch and F1–F6 skeleton. specify supplies only the deltas below; the skill fills the placeholders and dispatches one clean-context `Agent`.

## Placeholders

- **`{{ARTIFACT_NAME}}`** = "Product spec (context / goals / user stories / acceptance criteria / NFRs / KPIs)".
- **`{{DRAFT}}`** = the path `docs/features/<slug>/spec.md` — the critic Reads the file from disk (it was written section by section); the skill patches that file with the findings the user accepts.
- **`{{EDITS_LOG}}`** = the step-7 edits-log.
- **`{{UPSTREAM_FILES}}`** (the critic Reads these itself):
  - `docs/features/<slug>/CONTEXT.md` — canonical glossary (roles, domain terms).
  - `docs/idea-brief.md` when reused, plus the current owner corrections supplied in the prompt.
  - any reference module / doc the user named in step 5 (paths only).

## F5 structural floor (this artifact)

- §4 holds ≥1 US per glossary role + per §2 goal.
- §5 holds ≥1 AC of each of the 5 coverage types **after** drops + OQ-migrations.
- §6 NFR rows all carry a numeric target + measurement (no adjectives, no lone TBD).
- §8 Open Questions has a row for every `save_as_oq` with owner + due.

## F6 specialization — forbidden-token leak (the load-bearing check)

This is specify's primary F6. Scan §5 AC text for the forbidden tokens in [`draft-generation.md`](./draft-generation.md) (HTTP verbs, URL paths, status numerics, `module.error_name` strings, JSON fragments, SQL/driver constructs). **List every hit**, one bullet per AC line:

```
- **[F6] AC-NN contains forbidden tokens** — line: "<verbatim snippet>"; hits: <token1>, <token2>; suggested: rewrite into business form (actor-observable outcome) OR move the HTTP/error/schema detail to `api`.
```

Also flag any concrete technology name (datastore / broker / framework / library) appearing in §1–§3 — those belong to `design`.

## Brief preservation check

When interview was reused, check the draft against its accepted scope/constraints, rejected
alternatives, evidence limits, and current owner corrections per [`brief-reuse.md`](./brief-reuse.md).
Do not demand new competitive tables or RICE/matrix cells for already covered decisions. Flag
an unverified claim promoted to fact, a blocking unknown silently answered, or a confirmed
constraint dropped during product-level rephrasing. Technical detail stays traceable in the
brief/design source; its absence as a technology name in an AC is not itself lost scope.

## F1 specialization — approach drift

If the edits-log dropped/edited a US or AC tied to the committed approach in §1 ¶3, check that §1 ¶3 still states that approach accurately. A spec whose body no longer matches its own «committed approach» paragraph is drift.
