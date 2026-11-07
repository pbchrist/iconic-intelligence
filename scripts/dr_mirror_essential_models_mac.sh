#!/bin/bash
# Mirror ONLY the three essential production inference GGUF files to the Mac.
# Safe to rerun; encrypted Mac filesystem (FileVault); source model untouched.
# Does NOT copy gaming files, arbitrary directories, or confidential customer data.
set -euo pipefail
umask 077
MAC_HOST="user@100.78.33.125"
SRC="/home/patrick/models"
DEST="/Users/user/.iconic-recovery/models"
FILES=(
  "Qwen3.8-27B-Q4_K_M.gguf"
  "nomic-embed-text-v1.5.Q8_0.gguf"
  "failover/Qwen3-8B-Q4_K_M.gguf"
)
ssh -oBatchMode=yes -oConnectTimeout=8 "$MAC_HOST" "mkdir -p '$DEST/failover' && chmod 700 '$DEST'"
for item in "${FILES[@]}"; do
  source="$SRC/$item"
  test -f "$source"
  case "$item" in
    *".."*|/*) echo "Unsafe path" >&2; exit 2 ;;
  esac
  echo "COPY_ESSENTIAL_MODEL $item"
  rsync -a --partial --append-verify --bwlimit=35000 -e "ssh -oBatchMode=yes" "$source" "$MAC_HOST:$DEST/$item"
  expected=$(sha256sum "$source" | awk '{print $1}')
  actual=$(ssh -oBatchMode=yes "$MAC_HOST" "shasum -a 256 '$DEST/$item'" | awk '{print $1}')
  if [[ "$expected" != "$actual" ]]; then
    echo "SHA256_MODEL_COPY_MISMATCH $item" >&2; exit 3
  fi
  echo "ESSENTIAL_MODEL_OFFHOST_SHA256_VERIFIED $item $expected"
done
echo "ALL_THREE_ESSENTIAL_MODELS_INDEPENDENTLY_MIRRORED_TO_MAC"
