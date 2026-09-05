#!/usr/bin/env bash
# Neon Genie — Hermes Skill Installer
# Usage:
#   ./install.sh                 # installs to ~/.hermes/skills/neon-genie

set -euo pipefail

TARGET_BASE="${HERMES_HOME:-$HOME/.hermes}/skills"
DEST="${TARGET_BASE}/neon-genie"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --target) [[ $# -ge 2 ]] || { printf 'Missing target\n' >&2; exit 2; }; DEST="$2"; shift 2 ;;
    --target=*) DEST="${1#--target=}"; shift ;;
    -h|--help) printf 'Usage: install.sh [--target DIR] [--dry-run]\n'; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
  python3 - "$DEST" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1]).expanduser().absolute()
if not sys.argv[1].strip() or any(q.is_symlink() for q in (p, *p.parents)):
    raise SystemExit("refusing empty or symlinked target path")
PY
echo "Installing Neon Genie to: ${DEST}"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "DRY RUN: no files changed"
  exit 0
fi
exec python3 "${ROOT}/scripts/install_transaction.py" "$ROOT" "$DEST" neon-genie
