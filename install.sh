#!/usr/bin/env bash
# ICONIC Command installer. Run on the machine that runs your local model:
#   curl -fsSL https://raw.githubusercontent.com/pbchrist/iconic-intelligence/dashboard/install.sh | bash
# Safe to run again: it updates the app and keeps your files and settings.
set -euo pipefail

REPO="https://github.com/pbchrist/iconic-intelligence"
BRANCH="dashboard"
APP="$HOME/iconic-command"
DATA="$HOME/iconic-command-data"
STATE="$HOME/.local/state/iconic-command"
ENVF="$HOME/.config/iconic-command.env"
say() { printf '\033[1;35m▸\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

command -v python3 >/dev/null || die "python3 is required (sudo apt install python3)"
command -v git >/dev/null || die "git is required (sudo apt install git)"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' || die "Python 3.8 or newer is required"

say "Getting the app"
if [ -d "$APP/.git" ]; then
  git -C "$APP" fetch -q --depth 1 origin "$BRANCH"
  git -C "$APP" reset -q --hard FETCH_HEAD
else
  git clone -q --depth 1 -b "$BRANCH" "$REPO" "$APP"
fi

mkdir -p "$STATE" "$(dirname "$ENVF")"
if [ ! -d "$DATA" ]; then
  say "Adding the two sample workspaces to $DATA"
  cp -r "$APP/data" "$DATA"
fi

# Keep an existing port; otherwise use the first free one from 8770.
PORT=""
[ -f "$ENVF" ] && PORT="$(sed -n 's/^ICONIC_PORT=//p' "$ENVF" | tail -1)"
if [ -z "$PORT" ]; then
  PORT=8770
  while (exec 3<>"/dev/tcp/127.0.0.1/$PORT") 2>/dev/null; do PORT=$((PORT + 1)); done
fi

say "Looking for your local model"
LLM=""
[ -f "$ENVF" ] && LLM="$(sed -n 's/^ICONIC_LLM_URL=//p' "$ENVF" | tail -1)"
if [ -z "$LLM" ]; then
  for p in 8080 8000 8081 8082 8001 5000 1234 11434; do
    if curl -fsS -m 2 "http://127.0.0.1:$p/v1/models" 2>/dev/null | grep -q '"data"'; then LLM="http://127.0.0.1:$p/v1"; break; fi
  done
fi
if [ -n "$LLM" ]; then say "Model server found at $LLM"; else say "No model server answered yet. The dashboard will keep looking every 15 seconds."; fi

{
  echo "ICONIC_PORT=$PORT"
  echo "ICONIC_DATA=$DATA"
  echo "ICONIC_STATE=$STATE"
  [ -n "$LLM" ] && echo "ICONIC_LLM_URL=$LLM"
  grep -E '^ICONIC_(LLM_MODEL|LLM_KEY|RATE_PER_HOUR|SCAN_SECONDS)=' "$ENVF" 2>/dev/null || true
} > "$ENVF.tmp" && mv "$ENVF.tmp" "$ENVF"

say "Starting ICONIC Command on port $PORT"
started=""
if command -v systemctl >/dev/null && systemctl --user show-environment >/dev/null 2>&1; then
  mkdir -p "$HOME/.config/systemd/user"
  cat > "$HOME/.config/systemd/user/iconic-command.service" <<UNIT
[Unit]
Description=ICONIC Command (private intelligence dashboard)
After=network-online.target

[Service]
EnvironmentFile=$ENVF
ExecStart=$(command -v python3) $APP/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
UNIT
  systemctl --user daemon-reload
  systemctl --user enable -q iconic-command
  systemctl --user restart iconic-command
  loginctl enable-linger "$USER" >/dev/null 2>&1 || true
  started="systemd"
else
  pkill -f "$APP/server.py" 2>/dev/null || true
  set -a; . "$ENVF"; set +a
  nohup python3 "$APP/server.py" > "$STATE/server.log" 2>&1 &
  started="background"
fi

for _ in $(seq 1 30); do
  curl -fsS -m 2 "http://127.0.0.1:$PORT/api/status" >/dev/null 2>&1 && break
  sleep 1
done
curl -fsS -m 2 "http://127.0.0.1:$PORT/api/status" >/dev/null 2>&1 || die "It didn't start. Check: journalctl --user -u iconic-command -n 50"

IP="$(command -v tailscale >/dev/null && tailscale ip -4 2>/dev/null | head -1 || true)"
[ -z "$IP" ] && IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo
say "ICONIC Command is running ($started)."
echo "    Open:        http://${IP:-localhost}:$PORT"
echo "    Your files:  $DATA/<workspace>/   (one folder per business; new files are read within 20 seconds)"
echo "    Settings:    $ENVF"
