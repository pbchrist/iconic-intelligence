#!/bin/sh
# Pull the newest ICONIC Command and restart only if something changed. Run by iconic-command-update.timer.
cd "$(dirname "$0")" || exit 0
old=$(git rev-parse HEAD)
git fetch -q --depth 1 origin dashboard && git reset -q --hard FETCH_HEAD || exit 0
# Keep the two fictional sample businesses in step with the repo (new or updated files only).
DATA=$(sed -n 's/^ICONIC_DATA=//p' "$HOME/.config/iconic-command.env" 2>/dev/null)
if [ -n "$DATA" ] && [ -d "$DATA" ]; then
  for ws in data/*/; do
    name=$(basename "$ws")
    grep -q '"sample": *true' "$ws/workspace.json" 2>/dev/null && mkdir -p "$DATA/$name" && cp -ru "$ws." "$DATA/$name/"
  done
fi
[ "$old" != "$(git rev-parse HEAD)" ] && systemctl --user restart iconic-command
exit 0
