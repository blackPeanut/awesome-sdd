# Changing a decision without starting over

Use when the user changes an accepted behavior or an upstream artifact contradicts accepted
downstream work. An explicit correction authorizes updating that choice within the current task;
it does not authorize unrelated redesign, deployment, migration of live data or remote writes.

1. State the new behavior in one sentence. Ask only if its meaning or a material consequence is
   unclear. Keep separate choices separate: changing how long people stay signed in does not
   also decide whether a password change signs out their other devices.
2. Inspect the original decision and its actual references: ACs, flows, contracts, task briefs,
   tests and code. Follow task dependency edges and shared interfaces to find affected consumers.
   Do not infer impact from matching words alone. If the boundary is uncertain, mark the uncertain
   consumers for checking; do not claim that everything else is unaffected.
3. Explain the practical impact briefly: “This changes sign-in expiry and its tests. Password
   changes still work as agreed.” Ask about a new tradeoff only when one actually arises. Existing
   answers remain accepted. Do not restart the interview or ask for whole-document approval.
4. Follow [protect-work.md](./protect-work.md). Record the old/new choice and affected identifiers
   in the existing decision log or source artifact, with a small pending/completed checklist of
   downstream updates. Write this plan before propagation so an interruption can resume it.
   Update the source and affected parts in place; preserve IDs, unrelated sections and task history.
   Supersede an accepted ADR when necessary, keeping its history; do not renumber the ADR set.
5. Refresh affected task briefs and tests. For work already implemented, add a narrowly scoped
   follow-up task or reopen only the affected task with the reason. Hold dependent work until the
   changed contract is verified. Completed unrelated tasks and their code remain in place.
6. Re-run the checks affected by the change, plus shared gates required by the project. Previous
   evidence cannot certify changed inputs. Use [implementation reconciliation](../implement/references/resume.md)
   and [review freshness](../review/references/freshness.md) before reporting ready. Broader file
   fingerprints can require rechecking otherwise unchanged work; this is verification, not a
   reason to rewrite its code or replay its questions. Never edit old receipts to make them pass.

Keep the pending checklist until every affected item is updated and verified. If work is outside
the current authorization, record exactly what remains and stop that dependent work. A source
document edit alone does not mean the code now follows the new choice. Finish with a short
[handoff](./handoff.md) naming the changed behavior and any remaining work.
