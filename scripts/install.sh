#!/usr/bin/env bash
# Install paved-road skills into Claude Code, Codex CLI, and/or Gemini CLI skill folders.
#
#   ./scripts/install.sh                       # all agents, user scope, symlink
#   ./scripts/install.sh --agent codex         # one agent: claude | codex | gemini | all
#   ./scripts/install.sh --scope project       # into ./.claude/skills and ./.agents/skills
#   ./scripts/install.sh --copy                # copy instead of symlink
#   ./scripts/install.sh --uninstall           # remove what this script installed
#
# Codex CLI and Gemini CLI both read ~/.agents/skills, so they share one install.
# Claude Code reads ~/.claude/skills.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
AGENT="all"
SCOPE="user"
MODE="link"
ACTION="install"

usage() { sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) AGENT="${2:-}"; shift 2 ;;
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --copy) MODE="copy"; shift ;;
    --uninstall) ACTION="uninstall"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

case "$SCOPE" in
  user) BASE="$HOME" ;;
  project) BASE="$PWD" ;;
  *) echo "--scope must be user or project" >&2; exit 1 ;;
esac

case "$AGENT" in
  all)    DESTS=("$BASE/.claude/skills" "$BASE/.agents/skills") ;;
  claude) DESTS=("$BASE/.claude/skills") ;;
  codex|gemini) DESTS=("$BASE/.agents/skills") ;;
  *) echo "--agent must be claude, codex, gemini, or all" >&2; exit 1 ;;
esac

for dest in "${DESTS[@]}"; do
  mkdir -p "$dest"
  for skill in "$SKILLS_DIR"/*/; do
    name="$(basename "$skill")"
    path="$dest/$name"
    if [[ "$ACTION" == "uninstall" ]]; then
      if [[ -L "$path" || -d "$path" ]]; then rm -rf "$path"; echo "removed  $path"; fi
      continue
    fi
    if [[ -e "$path" || -L "$path" ]]; then rm -rf "$path"; fi
    if [[ "$MODE" == "link" ]]; then
      ln -s "${skill%/}" "$path"
    else
      cp -R "${skill%/}" "$path"
    fi
    echo "$MODE  $path"
  done
done

if [[ "$ACTION" == "install" ]]; then
  echo
  echo "Done. Restart Claude Code / Codex, or run /skills reload in Gemini CLI."
fi
