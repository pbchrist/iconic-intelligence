#!/usr/bin/env bash
# ICONIC Command installer. Run on the machine that runs your local model:
#   curl -fsSL https://raw.githubusercontent.com/pbchrist/iconic-intelligence/dashboard/install.sh | bash
# Add "-s -- --public" after bash to also put it on the internet with Tailscale Funnel.
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

{
  echo "ICONIC_PORT=$PORT"
  echo "ICONIC_DATA=$DATA"
  echo "ICONIC_STATE=$STATE"
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
  # Self-update: every 10 minutes, pull the newest version and restart only if it changed.
  cat > "$HOME/.config/systemd/user/iconic-command-update.service" <<UNIT
[Unit]
Description=Update ICONIC Command

[Service]
Type=oneshot
ExecStart=/bin/sh $APP/update.sh
UNIT
  cat > "$HOME/.config/systemd/user/iconic-command-update.timer" <<UNIT
[Unit]
Description=Check for ICONIC Command updates every 10 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=10min

[Install]
WantedBy=timers.target
UNIT
  systemctl --user daemon-reload
  systemctl --user enable -q iconic-command
  systemctl --user enable -q --now iconic-command-update.timer
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

sleep 3
MODEL_LINE="$(curl -fsS -m 5 "http://127.0.0.1:$PORT/api/status" | python3 -c 'import json,sys; m=json.load(sys.stdin)["model"]; print(("Model: " + m["model"] + " at " + m["endpoint"]) if m["online"] else ("NO MODEL: " + m["error"]))' 2>/dev/null || true)"

PUBLIC_URL=""
if [ "${1:-}" = "--public" ]; then
  command -v tailscale >/dev/null || die "--public needs Tailscale installed"
  say "Opening it to the internet with Tailscale Funnel (port $PORT only)"
  sudo tailscale funnel --bg "$PORT" || die "Funnel didn't start. If it printed a link, open it to allow Funnel for this machine, then run this again."
  # Pick the public address that points at THIS app's port (other Funnels may already exist).
  PUBLIC_URL="$(tailscale funnel status 2>/dev/null | awk -v p=":$PORT" '/^https:\/\//{u=$1} index($0,p) && u {print u; exit}')"
fi

IP="$(command -v tailscale >/dev/null && tailscale ip -4 2>/dev/null | head -1 || true)"
[ -z "$IP" ] && IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo
say "ICONIC Command is running ($started)."
echo "    Open:        http://${IP:-localhost}:$PORT"
echo "    Your files:  $DATA/<workspace>/   (one folder per business; new files are read within 20 seconds)"
echo "    Settings:    $ENVF"
[ "$started" = "systemd" ] && echo "    Updates:     automatic, checked every 10 minutes"
echo "    $MODEL_LINE"
[ -n "$PUBLIC_URL" ] && echo "    Public link: $PUBLIC_URL   (visitors see only the sample businesses, with an hourly limit)"
case "$MODEL_LINE" in NO\ MODEL*)
  echo
  echo "    Start your chat model (llama-server with Qwen) and the dashboard connects on its own within 15 seconds."
  echo "    Model servers running right now:"
  (ps -eo pid,args | grep -E "llama-server|llama_cpp|ollama|vllm|lmstudio" | grep -v grep | cut -c1-160 | sed 's/^/      /') || echo "      none"
  ;;
esac
