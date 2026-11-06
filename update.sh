#!/bin/sh
# Validate a candidate without touching the running release; only install after tests pass.
set -eu
cd "$(dirname "$0")"
old=$(git rev-parse HEAD)
candidate=$(mktemp -d)
trap 'rm -rf "$candidate"' EXIT
git fetch -q --depth 1 origin dashboard
git archive FETCH_HEAD | tar -x -C "$candidate"
(cd "$candidate" && python3 -m unittest discover -s tests -q)
# Only after candidate passes do we replace the running checkout.
git reset -q --hard FETCH_HEAD
DATA=$(sed -n 's/^ICONIC_DATA=//p' "$HOME/.config/iconic-command.env" 2>/dev/null || true)
if [ -n "$DATA" ] && [ -d "$DATA" ]; then
  for ws in data/*/; do
    name=$(basename "$ws")
    grep -q '"sample": *true' "$ws/workspace.json" 2>/dev/null || continue
    if ! diff -rq "$ws" "$DATA/$name" >/dev/null 2>&1; then
      rm -rf "$DATA/$name.new"
      cp -r "$ws" "$DATA/$name.new"
      rm -rf "$DATA/$name"
      mv "$DATA/$name.new" "$DATA/$name"
    fi
  done
fi
if [ "$old" != "$(git rev-parse HEAD)" ]; then
  systemctl --user restart iconic-command
fi
