#!/bin/sh
# Pull the newest ICONIC Command and restart only if something changed. Run by iconic-command-update.timer.
cd "$(dirname "$0")" || exit 0
old=$(git rev-parse HEAD)
git fetch -q --depth 1 origin dashboard && git reset -q --hard FETCH_HEAD || exit 0
# Keep the two fictional sample businesses identical to the repo.
DATA=$(sed -n 's/^ICONIC_DATA=//p' "$HOME/.config/iconic-command.env" 2>/dev/null)
if [ -n "$DATA" ] && [ -d "$DATA" ]; then
  for ws in data/*/; do
    name=$(basename "$ws")
    grep -q '"sample": *true' "$ws/workspace.json" 2>/dev/null || continue
    # Fictional sample folders mirror the repo exactly (renamed or removed files go away too).
    if ! diff -rq "$ws" "$DATA/$name" >/dev/null 2>&1; then
      rm -rf "$DATA/$name.new" && cp -r "$ws" "$DATA/$name.new" && rm -rf "$DATA/$name" && mv "$DATA/$name.new" "$DATA/$name"
    fi
  done
fi
[ "$old" != "$(git rev-parse HEAD)" ] && systemctl --user restart iconic-command
exit 0
