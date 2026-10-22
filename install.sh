#!/usr/bin/env bash
# SDD installer: native Codex desktop plugin, copied Codex/Cursor skills, or Claude instructions.
#
# codex-app registers and installs the native plugin shared by desktop and CLI.
# The codex/cursor modes copy the skills/ + agents/ subtree VERBATIM under <skills-root>/sdd/ (the
# relative cross-links between skills, _shared/ and agents/ keep resolving by construction),
# prefixes every skill name with `sdd-` (the bare review/design/api would collide with
# generic names), and generates the host tool's functional agents from agents/*.md.
# How each Claude-specific mechanism maps: skills/_shared/tool-adapters.md.
#
# Usage:
#   install.sh <codex-app|codex|cursor|claude> [--global] [--prefix DIR] [--ref REF] [--src DIR] [--uninstall]
#
#   codex-app        install the native plugin for Codex desktop + CLI (user-wide)
#   codex | cursor   copy skills into a project (claude prints native /plugin commands)
#   --tool TOOL      the same target tool, named form — `--tool codex` == `codex`
#   --global         copied skills: install under $HOME; codex-app is always user-wide
#   --prefix DIR     install under DIR (overrides --global and $PWD; mainly for testing)
#   --ref REF        copied skills: git ref to download (codex-app uses main)
#   --src DIR        install from a local checkout instead of downloading
#   --uninstall      remove a previous install from the chosen prefix and exit
#
# Dependencies: curl + tar (download mode); python3 only for Codex custom agents (optional —
# without it the skills still install and agent dispatch degrades to inline).

set -euo pipefail

REPO="blackPeanut/awesome-sdd"

log()  { printf '%s\n' "$*"; }
warn() { printf 'warning: %s\n' "$*" >&2; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

usage() {
  sed -n '2,/^set -euo pipefail/{ /^set -euo pipefail/d; p; }' "$0" | sed 's/^# \{0,1\}//'
}

TOOL=""
PREFIX=""
GLOBAL=0
REF="main"
SRC=""
UNINSTALL=0

while [ $# -gt 0 ]; do
  case "$1" in
    codex-app|codex|cursor|claude) TOOL="$1" ;;
    --tool)
      shift
      case "${1:?--tool needs codex-app|codex|cursor|claude}" in
        codex-app|codex|cursor|claude) TOOL="$1" ;;
        *) usage; die "--tool must be codex-app, codex, cursor or claude (got: $1)" ;;
      esac
      ;;
    --global)    GLOBAL=1 ;;
    --prefix)    shift; PREFIX="${1:?--prefix needs a directory}" ;;
    --ref)       shift; REF="${1:?--ref needs a git ref}" ;;
    --src)       shift; SRC="${1:?--src needs a directory}" ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help)   usage; exit 0 ;;
    *) usage; die "unknown argument: $1" ;;
  esac
  shift
done

[ -n "$TOOL" ] || { usage; die "missing target tool: codex-app | codex | cursor | claude"; }

if [ "$TOOL" = "claude" ]; then
  cat <<'EOF'
SDD installs natively in Claude Code — run inside a Claude Code session:

  /plugin marketplace add blackPeanut/awesome-sdd
  /plugin install awesome-sdd@awesome-sdd
EOF
  exit 0
fi

# Native marketplace installation is shared by the Codex app and CLI. It does not
# copy loose skills or rewrite project settings; Codex manages cache and enablement.
if [ "$TOOL" = "codex-app" ]; then
  [ -z "$PREFIX" ] || die "codex-app is user-wide; --prefix is only for copied skills"
  [ -z "$SRC" ] || die "codex-app installs the published marketplace; --src is only for copied skills"
  [ "$REF" = "main" ] || die "codex-app follows main; --ref is only for copied skills"
  CODEX_BIN="${SDD_CODEX_BIN:-codex}"
  command -v "$CODEX_BIN" >/dev/null 2>&1 \
    || die "Codex executable not found. Put codex on PATH or set SDD_CODEX_BIN to your app's bundled executable."
  if [ "$UNINSTALL" = 1 ]; then
    "$CODEX_BIN" plugin remove awesome-sdd@awesome-sdd
    log "Removed the native SDD plugin; marketplace registration is retained."
    exit 0
  fi
  "$CODEX_BIN" plugin marketplace add "$REPO"
  "$CODEX_BIN" plugin add awesome-sdd@awesome-sdd
  log "Installed the native SDD plugin for Codex desktop and CLI."
  log "Restart the desktop app, open Plugins, and find Awesome SDD."
  log 'Start a new chat in your project; select SDD or ask it to survey the repository.'
  # shellcheck disable=SC2016  # literal skill names
  log 'This native install uses $survey / $specify, not the copied-skill $sdd-* names.'
  log "Use one install method: remove an older copied SDD install separately to avoid duplicates."
  exit 0
fi

if [ -z "$PREFIX" ]; then
  if [ "$GLOBAL" = 1 ]; then PREFIX="$HOME"; else PREFIX="$PWD"; fi
fi

case "$TOOL" in
  codex)  SKILLS_ROOT="$PREFIX/.agents/skills"; AGENTS_DIR="$PREFIX/.codex/agents" ;;
  cursor) SKILLS_ROOT="$PREFIX/.cursor/skills"; AGENTS_DIR="$PREFIX/.cursor/agents" ;;
esac

# Uninstall is intentionally separate from upgrade: never remove the live copy to prepare one.
LIVE_SKILLS_ROOT="$SKILLS_ROOT"
LIVE_AGENTS_DIR="$AGENTS_DIR"
STATE_ROOT="$(dirname "$SKILLS_ROOT")/.sdd-installer"
mkdir -p "$STATE_ROOT"
LOCK_DIR="$STATE_ROOT/lock"
mkdir "$LOCK_DIR" 2>/dev/null || die "another install may be running (lock: $LOCK_DIR). If interrupted, confirm its PID is no longer running before removing the lock and retrying."
printf '%s\n' "$$" > "$LOCK_DIR/pid"

CLEANUP_DIR=""
TRANSACTION=""
SWAPPING=0
INSTALL_DONE=0

restore_previous() {
  local saved="$1" failed=0 agent
  # A ready marker is written only after the complete backup exists.
  [ -f "$saved/ready" ] || return 1
  rm -rf "${LIVE_SKILLS_ROOT:?}/sdd" || failed=1
  if [ -e "$saved/previous-skills" ] || [ -L "$saved/previous-skills" ]; then
    cp -pR "$saved/previous-skills" "$LIVE_SKILLS_ROOT/sdd" || failed=1
  fi
  # Only SDD-owned agent names are touched; unrelated custom agents survive.
  for agent in "$LIVE_AGENTS_DIR"/sdd-*.toml "$LIVE_AGENTS_DIR"/sdd-*.md; do
    [ -e "$agent" ] || [ -L "$agent" ] || continue
    rm -f "$agent" || failed=1
  done
  for agent in "$saved"/previous-agents/*; do
    [ -e "$agent" ] || [ -L "$agent" ] || continue
    cp -pP "$agent" "$LIVE_AGENTS_DIR/" || failed=1
  done
  return "$failed"
}

cleanup() {
  local rc=$?
  trap - EXIT HUP INT TERM
  if [ "$SWAPPING" = 1 ] && [ "$INSTALL_DONE" != 1 ]; then
    if restore_previous "$TRANSACTION"; then
      rm -f "$STATE_ROOT/pending"
      warn "upgrade failed; previous skills and agents restored"
    else
      warn "automatic restore failed; backup retained at $TRANSACTION; retry after fixing filesystem access"
      rc=1
    fi
  fi
  if [ -n "$CLEANUP_DIR" ]; then rm -rf "$CLEANUP_DIR"; fi
  if [ -n "$TRANSACTION" ] && [ "$SWAPPING" = 0 ]; then rm -rf "$TRANSACTION"; fi
  rm -rf "$LOCK_DIR"
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

# A killed process cannot run its trap. After its stale lock is cleared, recover the journal
# before doing anything else, even if the next requested operation is uninstall.
if [ -f "$STATE_ROOT/pending" ]; then
  pending="$(cat "$STATE_ROOT/pending")"
  case "$pending" in "$STATE_ROOT"/transaction.*) ;; *) die "invalid install recovery journal" ;; esac
  restore_previous "$pending" || die "could not restore interrupted install from $pending"
  rm -f "$STATE_ROOT/pending"
  warn "restored previous installation after an interrupted swap"
fi

if [ "$UNINSTALL" = 1 ]; then
  rm -rf "${LIVE_SKILLS_ROOT:?}/sdd"
  rm -f "$LIVE_AGENTS_DIR"/sdd-*.toml "$LIVE_AGENTS_DIR"/sdd-*.md
  log "uninstalled sdd from $PREFIX ($TOOL); rollback backups retained in $STATE_ROOT"
  exit 0
fi

# Resolve, copy and validate entirely outside the live skill/agent discovery directories.
if [ -z "$SRC" ]; then
  command -v curl >/dev/null 2>&1 || die "curl is required to download $REPO"
  command -v tar  >/dev/null 2>&1 || die "tar is required to unpack $REPO"
  CLEANUP_DIR="$(mktemp -d)"
  log "downloading ${REPO}@${REF} …"
  curl -fsSL "https://codeload.github.com/${REPO}/tar.gz/${REF}" \
    | tar -xz --strip-components=1 -C "$CLEANUP_DIR" \
    || die "download/unpack of ${REPO}@${REF} failed — check the ref exists (e.g. --ref main or a release tag like v1.9.2) and your network"
  SRC="$CLEANUP_DIR"
fi

[ -f "$SRC/skills/specify/SKILL.md" ] \
  || die "source $SRC does not look like the sdd repo (skills/specify/SKILL.md missing)"

# --- collision check: a marketplace install would list every skill twice ------------------
# `codex plugin marketplace add` registers the ORIGINAL names ($specify); this script installs
# the sdd- prefixed copies. Both at once → a doubled skill list. Warn, don't block (README:
# "pick one of the two paths").
if [ "$TOOL" = "codex" ] && [ -f "$HOME/.codex/config.toml" ] \
   && grep -Eq 'plugins."(awesome-sdd|sdd)@' "$HOME/.codex/config.toml" 2>/dev/null; then
  warn "a marketplace install of SDD is already registered in ~/.codex/config.toml — adding the script install too will list each skill twice (\$specify AND \$sdd-specify); pick one path (see README), or remove the marketplace plugin"
fi

TRANSACTION="$(mktemp -d "$STATE_ROOT/transaction.XXXXXX")"
SKILLS_ROOT="$TRANSACTION/staged-skills"
AGENTS_DIR="$TRANSACTION/staged-agents"

# --- copy the subtree verbatim: <skills-root>/sdd/{skills,agents} ------------------------
mkdir -p "$SKILLS_ROOT/sdd"
cp -R "$SRC/skills" "$SKILLS_ROOT/sdd/skills"
cp -R "$SRC/agents" "$SKILLS_ROOT/sdd/agents"

# --- rename pass: frontmatter `name: <base>` → `name: sdd-<base>` ------------------------
# The repo validator guarantees the exact line `name: <dirname>` AND that every skill dir name
# matches [a-z0-9-]+ (no BRE metacharacters), so interpolating $base into the sed pattern is
# safe on both GNU and BSD sed. A new skill with ./_+ etc. in its dir name would break this —
# the validator rejects it first.
n_skills=0
validate_frontmatter() {
  awk '
    NR==1 { if ($0 != "---") exit 1; next }
    /^---$/ { closed=1; exit }
    /^description: *[^[:space:]]/ { description=1 }
    END { if (!closed || !description) exit 1 }
  ' "$1" || die "invalid or incomplete frontmatter: $1"
}
for skill_md in "$SKILLS_ROOT"/sdd/skills/*/SKILL.md; do
  validate_frontmatter "$skill_md"
  base="$(basename "$(dirname "$skill_md")")"
  case "$base" in *[!a-z0-9-]*|'') die "invalid skill directory name: $base" ;; esac
  tmp="${skill_md}.tmp"
  sed "s/^name: ${base}\$/name: sdd-${base}/" "$skill_md" > "$tmp"
  grep -q "^name: sdd-${base}\$" "$tmp" \
    || die "rename failed for $skill_md (expected the exact line 'name: ${base}')"
  mv "$tmp" "$skill_md"
  n_skills=$((n_skills + 1))
done

# --- functional agents per tool -----------------------------------------------------------
# (the verbatim copies under sdd/agents/ stay as documentation the skills cross-link)
mkdir -p "$AGENTS_DIR"
n_agents=0

if [ "$TOOL" = "cursor" ]; then
  for agent_md in "$SKILLS_ROOT"/sdd/agents/*.md; do
    validate_frontmatter "$agent_md"
    n="$(basename "$agent_md" .md)"
    case "$n" in *[!a-z0-9-]*|'') die "invalid agent name: $n" ;; esac
    out="$AGENTS_DIR/sdd-${n}.md"
    # rewrite two frontmatter lines only: the name (prefix) and the model (host-agnostic)
    sed -e "1,/^---\$/ s/^name: ${n}\$/name: sdd-${n}/" \
        -e "1,/^---\$/ s/^model: .*/model: inherit/" \
        "$agent_md" > "$out"
    grep -q "^name: sdd-${n}\$" "$out" \
      || die "agent rewrite failed for $agent_md (expected the exact line 'name: ${n}')"
    n_agents=$((n_agents + 1))
  done
else # codex: generate .codex/agents/sdd-<name>.toml (needs python3 — folded YAML description)
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$SKILLS_ROOT/sdd/agents" "$AGENTS_DIR" <<'PYEOF'
import functools
import json
import re
import sys
from pathlib import Path

dumps = functools.partial(json.dumps, ensure_ascii=False)
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
for md in sorted(src.glob("*.md")):
    text = md.read_text()
    if not text.startswith("---"):
        sys.exit(f"{md}: no frontmatter")
    end = text.find("\n---", 3)
    if end < 0:
        sys.exit(f"{md}: unterminated frontmatter")
    block = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")

    # parse the scalar keys + the folded `description: >` block (no yaml module in stdlib)
    fm, desc_lines, in_desc = {}, [], False
    for line in block.splitlines():
        if in_desc:
            if line.startswith((" ", "\t")):
                desc_lines.append(line.strip())
                continue
            in_desc = False
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, val = line.partition(":")
            key, val = key.strip(), val.strip()
            if key == "description" and val in (">", "|", ">-", "|-"):
                in_desc = True
            else:
                fm[key] = val

    desc = fm.get("description") or " ".join(desc_lines)
    if fm.get("name") != md.stem or not re.fullmatch(r"[a-z0-9-]+", md.stem) or not desc:
        sys.exit(f"{md}: invalid agent name or missing description")
    name = "sdd-" + fm["name"]
    tools = fm.get("tools", "")
    writes = any(t.strip() in ("Write", "Edit") for t in tools.split(","))
    sandbox = "workspace-write" if writes else "read-only"

    if not body.endswith("\n"):
        body += "\n"
    if "'''" in body:  # can't hold a TOML literal multi-line string — escape via JSON form
        instructions = "developer_instructions = " + dumps(body)
    else:
        instructions = "developer_instructions = '''\n" + body + "'''"

    toml = (
        f"name = {dumps(name)}\n"
        f"description = {dumps(desc)}\n"
        f"sandbox_mode = {dumps(sandbox)}\n"
        f"{instructions}\n"
    )
    (dst / f"{name}.toml").write_text(toml)
    print(f"  agent {name}.toml")
PYEOF
    n_agents="$(find "$AGENTS_DIR" -name 'sdd-*.toml' | wc -l | tr -dc '0-9')"
  else
    die "python3 is required to stage Codex custom agents; the existing installation was not changed"
  fi
fi

# --- backup then swap; the EXIT/signal trap restores the old pair on any failure ---------
[ "$n_skills" -gt 0 ] || die "source contains no skills"
[ "$n_agents" -gt 0 ] || die "source contains no agents"
mkdir -p "$LIVE_SKILLS_ROOT" "$LIVE_AGENTS_DIR" "$TRANSACTION/previous-agents"
if [ -e "$LIVE_SKILLS_ROOT/sdd" ] || [ -L "$LIVE_SKILLS_ROOT/sdd" ]; then
  cp -pR "$LIVE_SKILLS_ROOT/sdd" "$TRANSACTION/previous-skills"
fi
for agent in "$LIVE_AGENTS_DIR"/sdd-*.toml "$LIVE_AGENTS_DIR"/sdd-*.md; do
  [ -e "$agent" ] || [ -L "$agent" ] || continue
  cp -pP "$agent" "$TRANSACTION/previous-agents/"
done
# If backup fails above, the live installation has not been touched.
touch "$TRANSACTION/ready"
printf '%s\n' "$TRANSACTION" > "$STATE_ROOT/pending.tmp"
SWAPPING=1
mv "$STATE_ROOT/pending.tmp" "$STATE_ROOT/pending"
if [ -e "$LIVE_SKILLS_ROOT/sdd" ] || [ -L "$LIVE_SKILLS_ROOT/sdd" ]; then
  mv "$LIVE_SKILLS_ROOT/sdd" "$TRANSACTION/displaced-skills"
fi
mv "$SKILLS_ROOT/sdd" "$LIVE_SKILLS_ROOT/sdd"
for agent in "$LIVE_AGENTS_DIR"/sdd-*.toml "$LIVE_AGENTS_DIR"/sdd-*.md; do
  [ -e "$agent" ] || [ -L "$agent" ] || continue
  rm -f "$agent"
done
for agent in "$AGENTS_DIR"/*; do
  [ -f "$agent" ] || continue
  mv "$agent" "$LIVE_AGENTS_DIR/"
done
# Publish the completed transaction only after both destinations are in place.
rm -f "$STATE_ROOT/pending"
INSTALL_DONE=1
SKILLS_ROOT="$LIVE_SKILLS_ROOT"
AGENTS_DIR="$LIVE_AGENTS_DIR"
# The backup remains outside discovery paths for recovery; discard only staging/displaced data.
rm -rf "$TRANSACTION/staged-skills" "$TRANSACTION/staged-agents" "$TRANSACTION/displaced-skills"
log "  rollback backup → $TRANSACTION"

# --- project settings file -----------------------------------------------------------------
# Copied skills install into the project, so settings can be created here. Native
# plugin installs instead let the first pipeline skill create project settings.
# Skipped for --global: $HOME is not a project, and a settings file there configures nothing.
# Never overwrites an existing file, and --uninstall never removes it (it is the user's config).
SETTINGS_NOTE=""
if [ "$PREFIX" != "$HOME" ]; then
  settings_file="$PREFIX/.claude/sdd.local.md"
  canon="$SKILLS_ROOT/sdd/skills/_shared/settings-file.md"
  if [ -f "$settings_file" ]; then
    SETTINGS_NOTE="kept (already present)"
  elif [ -f "$canon" ]; then
    # Extract the two canonical pieces from _shared/settings-file.md — never a second copy of
    # the template in this script, which would drift the moment a key is added.
    fm="$(awk '/^## The documented frontmatter/{f=1} f&&/^```yaml$/{y=1;next} y&&/^```$/{exit} y' "$canon")"
    body="$(awk '/^## What each key does$/{f=1;print;next} f&&/^## /{exit} f' "$canon")"
    # Persist portable preferences; each session resolves effective host capabilities.
    if [ -n "$fm" ] && [ -n "$body" ] && mkdir -p "$PREFIX/.claude" 2>/dev/null; then
      {
        printf -- '---\n%s\n---\n\n' "$fm"
        printf '# SDD settings\n\nPer-project, per-developer, gitignored. Use the SDD config skill\nto change a value — it patches keys in place and keeps your comments.\n\n'
        printf '%s\n' "$body"
      } > "$settings_file" && SETTINGS_NOTE="created with documented defaults"
    fi
  fi
  if [ -z "$SETTINGS_NOTE" ]; then
    warn "could not write $settings_file (template missing or unwritable) — the skills create it on their first run instead"
  fi
  # .gitignore: both entries are per-developer and must never be committed.
  if [ -n "$SETTINGS_NOTE" ]; then
    gitignore="$PREFIX/.gitignore"
    touch "$gitignore" 2>/dev/null || true
    if [ -w "$gitignore" ]; then
      grep -qxF '.claude/*.local.md' "$gitignore" || printf '%s\n' '.claude/*.local.md' >> "$gitignore"
      grep -qxF '.worktrees/'        "$gitignore" || printf '%s\n' '.worktrees/'        >> "$gitignore"
      state_ignore="${STATE_ROOT#"$PREFIX"/}/"
      grep -qxF "$state_ignore" "$gitignore" || printf '%s\n' "$state_ignore" >> "$gitignore"
    fi
  fi
fi

log ""
log "installed sdd ($TOOL):"
log "  skills  → $SKILLS_ROOT/sdd  (${n_skills} skills)"
if [ "$n_agents" -gt 0 ]; then
  log "  agents  → $AGENTS_DIR  (${n_agents} agents, sdd-* prefixed)"
fi
case "$TOOL" in
  codex)  log "  invoke  → type \$sdd-… in codex, e.g. \$sdd-specify <slug>" ;;
  cursor) log "  invoke  → type / in the chat and pick sdd-…, e.g. sdd-specify" ;;
esac
if [ -n "$SETTINGS_NOTE" ]; then
  log "  config  → $PREFIX/.claude/sdd.local.md  (${SETTINGS_NOTE})"
fi
log "  mapping → $SKILLS_ROOT/sdd/skills/_shared/tool-adapters.md"
log "  remove  → re-run with --uninstall (upgrades validate and stage before replacing the live copy)"
