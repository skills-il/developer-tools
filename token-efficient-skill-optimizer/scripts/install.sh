#!/bin/sh
# Install token-efficient-skill-optimizer into ~/.claude/skills/ (copy, not symlink).
# Idempotent: re-running overwrites the installed copy with this package.
set -eu

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${HOME}/.claude/skills/token-efficient-skill-optimizer"

if [ ! -f "${SRC}/SKILL.md" ]; then
  echo "ERROR: SKILL.md not found next to scripts/ - run from inside the package" >&2
  exit 1
fi

mkdir -p "${DEST}"
# copy package contents; exclude caches/venvs if any snuck in
rsync -a --delete \
  --exclude '__pycache__' --exclude '.venv' --exclude 'venv' \
  "${SRC}/" "${DEST}/"

echo "installed -> ${DEST}"
echo "version:   $(cat "${DEST}/VERSION")"
echo "notes:     optional venv for exact-ish token counts:"
echo "           python3 -m venv ~/.claude/skills/token-efficient-skill-optimizer/.venv"
echo "           ~/.claude/skills/token-efficient-skill-optimizer/.venv/bin/pip install tiktoken pyyaml"
