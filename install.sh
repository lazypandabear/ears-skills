#!/usr/bin/env bash
# Install EARS skills for Hermes Agent, Claude Code, or package zips for claude.ai upload.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"
MODE="copy"
TARGETS=()

usage() {
  cat <<EOF
Usage: ./install.sh [--hermes] [--claude-code] [--zip] [--all] [--link] [--hermes-home PATH]

  --hermes          Install into \$HERMES_HOME/skills/requirements/
  --claude-code     Install into ~/.claude/skills/
  --zip             Build one zip per skill in dist/ for claude.ai upload
  --all             All of the above
  --link            Symlink instead of copy (git pull updates skills in place)
  --hermes-home     Target a specific Hermes profile home (default: \$HERMES_HOME or ~/.hermes)
EOF
}

[[ $# -eq 0 ]] && { usage; exit 1; }
while [[ $# -gt 0 ]]; do
  case "$1" in
    --hermes) TARGETS+=(hermes) ;;
    --claude-code) TARGETS+=(claude-code) ;;
    --zip) TARGETS+=(zip) ;;
    --all) TARGETS+=(hermes claude-code zip) ;;
    --link) MODE="link" ;;
    --hermes-home) HERMES_HOME_DIR="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
  shift
done

place() { # src dest
  local src="$1" dest="$2"
  rm -rf "$dest"
  if [[ "$MODE" == "link" ]]; then ln -s "$src" "$dest"; else cp -R "$src" "$dest"; fi
}

for t in "${TARGETS[@]}"; do
  case "$t" in
    hermes)
      dest_root="$HERMES_HOME_DIR/skills/requirements"
      mkdir -p "$dest_root"
      for s in "$SKILLS_DIR"/*/; do
        name="$(basename "$s")"; place "${s%/}" "$dest_root/$name"
      done
      echo "Hermes: installed to $dest_root ($MODE). Start a new session or /reset."
      ;;
    claude-code)
      mkdir -p "$CLAUDE_SKILLS_DIR"
      for s in "$SKILLS_DIR"/*/; do
        name="$(basename "$s")"; place "${s%/}" "$CLAUDE_SKILLS_DIR/$name"
      done
      echo "Claude Code: installed to $CLAUDE_SKILLS_DIR ($MODE)."
      ;;
    zip)
      mkdir -p "$REPO_DIR/dist"
      for s in "$SKILLS_DIR"/*/; do
        name="$(basename "$s")"
        rm -f "$REPO_DIR/dist/$name.zip"
        (cd "$SKILLS_DIR" && zip -qr "$REPO_DIR/dist/$name.zip" "$name" -x '*/__pycache__/*' '*:Zone.Identifier')
      done
      echo "Zips: $REPO_DIR/dist/ (upload each to claude.ai skills)."
      ;;
  esac
done
