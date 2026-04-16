#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<EOF
Usage: $(basename "$0") sbx

  sbx           Docker Sandbox + agent settings
EOF
}

CMD="${1:-}"
[[ -z "$CMD" ]] && { usage; exit 1; }

case "$CMD" in
  sbx)
    mkdir -p "$SCRIPT_DIR/.claude"
    cp "$SCRIPT_DIR/settings/agent-claude-settings.json" "$SCRIPT_DIR/.claude/settings.json"
    cd "$SCRIPT_DIR"
    sbx run claude
    ;;
  *)
    echo "Unknown command: $CMD"; usage; exit 1 ;;
esac
