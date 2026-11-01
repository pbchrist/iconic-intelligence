#!/bin/sh
# Pull the newest ICONIC Command and restart only if something changed. Run by iconic-command-update.timer.
cd "$(dirname "$0")" || exit 0
old=$(git rev-parse HEAD)
git fetch -q --depth 1 origin dashboard && git reset -q --hard FETCH_HEAD || exit 0
[ "$old" != "$(git rev-parse HEAD)" ] && systemctl --user restart iconic-command
exit 0
