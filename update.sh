#!/bin/sh
# Safe auto-deploy: test first, restart, verify health, roll back on failure.
# The model service is never restarted; only this dashboard process is.
set -eu
cd "$(dirname "$0")"

STATE="${ICONIC_STATE:-$HOME/.local/state/iconic-command}"
mkdir -p "$STATE"
exec 9>"$STATE/deploy.lock"
flock -n 9 || exit 0

GOOD="$STATE/last-known-good.sha"
PENDING="$STATE/pending-deploy.sha"
BLOCKED="$STATE/blocked-candidate.sha"
HEALTH_URL="${ICONIC_UPDATE_HEALTH_URL:-http://127.0.0.1:8771/api/status}"

log() { printf '%s ICONIC deploy: %s\n' "$(date '+%F %T')" "$*" >&2; }
atomic_sha() { printf '%s\n' "$2" > "$1.new"; mv -f "$1.new" "$1"; }

health_once() {
    python3 - "$HEALTH_URL" <<'PY'
import json, sys, urllib.request
try:
    with urllib.request.urlopen(sys.argv[1], timeout=3) as r:
        d = json.load(r)
    assert d["model"]["online"] is True
    assert d["model"]["model"]
except (Exception):
    sys.exit(1)
PY
}
healthy() {
    i=0
    while [ "$i" -lt 15 ]; do
        if health_once; then return 0; fi
        i=$((i + 1))
        sleep 1
    done
    return 1
}
sync_samples() {
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
}
rollback() {
    good="$1"
    bad="$2"
    log "health failed; rolling back $bad -> $good"
    git reset -q --hard "$good"
    sync_samples
    if ! systemctl --user restart iconic-command || ! healthy; then
        log "CRITICAL: rollback attempted but last-known-good is not healthy"
    else
        log "rollback restored healthy last-known-good $good"
    fi
    atomic_sha "$BLOCKED" "$bad"
    rm -f "$PENDING"
}

# Recovery after power loss or an interrupted update.
if [ -s "$PENDING" ]; then
    bad=$(cat "$PENDING")
    good=$(cat "$GOOD")
    if [ "$(git rev-parse HEAD)" = "$bad" ] && healthy; then
        atomic_sha "$GOOD" "$bad"
        git update-ref refs/iconic/last-known-good "$bad"
        rm -f "$PENDING" "$BLOCKED"
        log "recovered healthy deployment $bad"
    else
        rollback "$good" "$bad"
        exit 1
    fi
fi

old=$(git rev-parse HEAD)
git fetch -q --depth 1 origin dashboard
next=$(git rev-parse FETCH_HEAD)
[ "$old" != "$next" ] || exit 0
if [ -s "$BLOCKED" ] && [ "$(cat "$BLOCKED")" = "$next" ]; then
    log "skipping previously failed candidate $next"
    exit 1
fi

candidate=$(mktemp -d)
trap 'rm -rf "$candidate"' EXIT
git archive "$next" | tar -x -C "$candidate"
# No production files change until these tests all pass.
if ! (cd "$candidate" && python3 -m py_compile server.py &&
    sh -n update.sh && python3 -m unittest discover -s tests -q); then
    atomic_sha "$BLOCKED" "$next"
    log "candidate $next failed tests; production untouched"
    exit 1
fi

atomic_sha "$GOOD" "$old"
git update-ref refs/iconic/last-known-good "$old"
atomic_sha "$PENDING" "$next"
log "candidate passed: deploying $next"
if ! git reset -q --hard "$next" || ! sync_samples ||
    ! systemctl --user restart iconic-command || ! healthy; then
    rollback "$old" "$next"
    exit 1
fi

atomic_sha "$GOOD" "$next"
git update-ref refs/iconic/last-known-good "$next"
rm -f "$PENDING" "$BLOCKED"
log "deployed and health-verified $next"
