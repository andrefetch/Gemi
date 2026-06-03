#!/usr/bin/env bash
# Launch the Gemi TUI from anywhere.
set -euo pipefail

# Resolve the directory this script lives in (repo root), following symlinks.
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
ROOT="$(cd -P "$(dirname "$SOURCE")" >/dev/null 2>&1 && pwd)"

cd "$ROOT"

if command -v uv >/dev/null 2>&1; then
  exec uv run python -m gemi.tui "$@"
else
  exec python3 -m gemi.tui "$@"
fi
