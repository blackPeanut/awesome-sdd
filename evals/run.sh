#!/usr/bin/env bash
# SDD eval harness — on-demand, NOT CI (it invokes `claude` and costs tokens).
#
#   ./evals/run.sh                      # all scenarios
#   ./evals/run.sh design-gate-refusal  # one (or more) by name
#
# Env: SDD_EVAL_MODEL=<model>  SDD_EVAL_MAX_TURNS=<n, default 40>
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$EVALS_DIR/.." && pwd)"   # the sdd plugin under test — loaded via --plugin-dir
MAX_TURNS="${SDD_EVAL_MAX_TURNS:-40}"
# NB: an EMPTY array + `set -u` breaks on macOS bash 3.2 — expand with the
# ${arr[@]+"${arr[@]}"} idiom everywhere.
MODEL_ARGS=()
[ -n "${SDD_EVAL_MODEL:-}" ] && MODEL_ARGS=(--model "$SDD_EVAL_MODEL")

# Keep the existing Claude suite; Codex has multi-turn/resume scenarios of its own.
if [ "${1:-}" = "--host" ]; then
  case "${2:-}" in
    codex) shift 2; exec python3 "$EVALS_DIR/run_codex.py" "$@" ;;
    claude) shift 2 ;;
    *) echo "FATAL: --host must be claude or codex" >&2; exit 2 ;;
  esac
fi

command -v claude >/dev/null 2>&1 || { echo "FATAL: claude CLI not found" >&2; exit 2; }
command -v jq >/dev/null 2>&1 || { echo "FATAL: jq not found" >&2; exit 2; }

run_scenario() {
  local name="$1"
  local dir="$EVALS_DIR/scenarios/$name"
  [ -d "$dir" ] || { echo "FATAL: no such scenario: $name" >&2; return 2; }

  local work meta
  work="$(mktemp -d "${TMPDIR:-/tmp}/sdd-eval-$name.XXXXXX")"
  meta="$(mktemp -d "${TMPDIR:-/tmp}/sdd-eval-$name-meta.XXXXXX")" # transcript + judge prompt live OUTSIDE the repo under test
  echo "== $name  (workdir: $work)"

  # 1. Fixture → git baseline.
  cp -R "$dir/fixture/." "$work/"
  git -C "$work" init -q
  git -C "$work" add -A
  git -C "$work" -c user.email=eval@sdd -c user.name=sdd-eval commit -qm baseline

  # 2. The run under test — headless; the prompt pins --depth=easy (a headless
  #    run cannot answer AskUserQuestion). --plugin-dir loads the sdd plugin
  #    from THIS checkout, so the eval exercises the working tree, not whatever
  #    version happens to be installed.
  # --allowedTools lets the run actually `git commit` in the throwaway workdir —
  # without it, acceptEdits blocks commits and commit-cadence rubrics go vacuous
  # (0 commits observed regardless of the skill's real cadence).
  local out="$meta/run.json" prompt run_rc=0
  prompt="$(cat "$dir/prompt.txt")"
  # Direct agent contract evals need an unambiguous path to this checkout.
  prompt="${prompt//\{\{PLUGIN_ROOT\}\}/$REPO_ROOT}"
  ( cd "$work" && claude -p "$prompt" \
      --plugin-dir "$REPO_ROOT" --add-dir "$REPO_ROOT" \
      --permission-mode acceptEdits --max-turns "$MAX_TURNS" \
      --allowedTools "Bash(git:*)" \
      --output-format json ${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"} > "$out" ) || run_rc=$?

  # --output-format json is an object in some CLI versions, an array of
  # messages (result last) in others — accept both.
  local extract='if type=="array" then (last.result // empty) else (.result // empty) end'
  # A judge must not award a pass to an errored run or inaccessible plugin instructions.
  if [ "$run_rc" -ne 0 ] || ! jq -e 'if type=="array" then last else . end | .is_error == false' "$out" >/dev/null 2>&1; then
    echo "== $name: FAIL (CLI run failed; inspect $out)"
    return 1
  fi
  if jq -e --arg root "$REPO_ROOT/" 'if type=="array" then last else . end |
      any((.permission_denials // [])[]; .tool_name == "Read" and
        ((.tool_input.file_path // "") | startswith($root)))' "$out" >/dev/null; then
    echo "== $name: FAIL (plugin instruction read denied; inspect $out)"
    return 1
  fi
  local final_msg tree gitlog diff
  final_msg="$(jq -r "$extract" "$out" 2>/dev/null || true)"
  tree="$(cd "$work" && find . -path ./.git -prune -o -type f -print | sort)"
  gitlog="$(git -C "$work" log --oneline | head -30)"
  # Diff vs the FIXTURE BASELINE (the root commit), not vs HEAD — so the judge sees the
  # run's full change (committed + uncommitted) even when the run made its own commits.
  local base
  base="$(git -C "$work" rev-list --max-parents=0 HEAD)"
  git -C "$work" add -A
  diff="$( { git -C "$work" diff --cached --stat "$base" | head -40; git -C "$work" diff --cached "$base" | head -400; } || true)"

  # 3. The judge — rubric + observed outcome → one JSON verdict.
  local jp="$meta/judge-prompt.md"
  # shellcheck disable=SC2016  # the backticks are literal markdown fences
  {
    cat "$EVALS_DIR/judge-prompt.md"
    printf '\n## Rubric\n\n'; cat "$dir/rubric.md"
    printf '\n## File tree after the run\n\n```\n%s\n```\n' "$tree"
    printf '\n## Git log after the run (newest first; "baseline" is the fixture commit)\n\n```\n%s\n```\n' "$gitlog"
    printf '\n## Git diff vs the fixture baseline (the run'\''s full change, committed + uncommitted)\n\n```\n%s\n```\n' "$diff"
    printf '\n## The run'\''s final message\n\n```\n%s\n```\n' "$final_msg"
  } > "$jp"

  local judge_out verdict
  judge_out="$(claude -p "$(cat "$jp")" --output-format json ${MODEL_ARGS[@]+"${MODEL_ARGS[@]}"} | jq -r "$extract")"
  verdict="$(printf '%s' "$judge_out" | sed -n 's/.*"verdict"[[:space:]]*:[[:space:]]*"\([A-Z]*\)".*/\1/p' | head -1)"

  printf '%s\n' "$judge_out"
  echo "== $name: ${verdict:-UNPARSEABLE}"
  [ "$verdict" = "PASS" ]
}

# No args → every scenario (dir names are kebab-case, splitting is safe).
if [ "$#" -eq 0 ]; then
  # shellcheck disable=SC2046
  set -- $(ls "$EVALS_DIR/scenarios")
fi

rc=0
for s in "$@"; do
  run_scenario "$s" || rc=1
done
exit $rc
