# Review the version that will ship

A `PASS` applies to the inputs actually reviewed. It is not a permanent approval for a branch.
Read this when starting/finalizing review, checking status, or preparing to ship.

## Capture before review

Resolve the actual branch point once to a full commit SHA. Include the feature's committed diff,
staged and unstaged changes, new source/tests, and the spec/contracts. With commits off, review
the working copy explicitly. Do not review only `base..HEAD` and miss uncommitted changes.

From the project root, run the installed helper (Python 3.10+, standard library only):

```bash
python3 <installed-sdd>/skills/review/scripts/snapshot.py capture --slug <slug> --base <base-sha>
```

After settings preflight, save the successful JSON output in a **new** file under the feature's
`_review/` folder and name it in the corresponding pending review record. Keep the original
snapshot immutable. Use a unique date/time or run suffix; never overwrite an earlier review.
The helper itself only reads and prints; do not save an error response as evidence.

It hashes all tracked and nonignored working files, including mode and symlink target, not just
HEAD. Only this feature's `_review/` bookkeeping is excluded to avoid self-invalidation. Ensure
that folder contains no runtime code, fixtures or other review inputs; if it does, stop and move
those inputs into normal project paths before reviewing. Ignored/generated files, external
services and environment state are outside this snapshot: inspect any that affect the feature
and record separate evidence. Submodules and unresolved merges stop the helper; do not bypass
those errors by claiming a snapshot-backed PASS.

## Check before PASS and again before shipping

```bash
python3 <installed-sdd>/skills/review/scripts/snapshot.py check --receipt <snapshot-json>
```

Only a zero exit code with `ok: true` confirms unchanged inputs. Missing, malformed or legacy
snapshots mean freshness is unverified, even if a Markdown file says PASS. The helper checks
content, not review quality or user consent. The review report must also resolve all findings.

If inputs changed, keep the old report as history and mark the current review pending. Show a
short explanation, such as “The sign-in code changed since review. I'll check that part again.”
Have the reviewer inspect the listed changes and their affected consumers. Preserve findings
and accepted decisions that still apply. A document-only change may need only a document check;
changed contracts can require broader review. Capture a new snapshot **before** this follow-up
review, then check it again before issuing a new PASS. Never refresh a snapshot merely to make
an old approval pass. No need to ask the user to approve the same unchanged behavior again.

Check after final verification and packaging edits too: tests/hooks may change files, and a
changelog or roadmap edit still deserves a focused check. Immediately before pushing/opening
the PR, add `--committed` to confirm that HEAD contains the reviewed working content. With
`auto_commit: off`, leave verified edits untouched and report that publication is waiting on
committing them; do not create a PR that leaves reviewed work behind. Report-only commits are
allowed without repeating review; HEAD may change when reviewed file content stays identical.
