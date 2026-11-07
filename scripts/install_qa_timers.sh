#!/bin/sh
# Install independent user timers. Does not touch the model or restart ICONIC Command.
set -eu
cd "$(dirname "$0")/.."
dest="$HOME/.config/systemd/user"
mkdir -p "$dest"
cp systemd/iconic-qa-inbox.service systemd/iconic-qa-inbox.timer "$dest/"
cp systemd/iconic-qa-monitor.service systemd/iconic-qa-monitor.timer "$dest/"
systemctl --user daemon-reload
systemctl --user enable --now iconic-qa-inbox.timer iconic-qa-monitor.timer
systemctl --user list-timers --all --no-pager | grep -E 'iconic-qa-(inbox|monitor)' || true
