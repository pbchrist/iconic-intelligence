#!/bin/bash
# Verify an encrypted multi-part ICONIC backup without exposing the key.
set -euo pipefail
id="${1:-}"
if [[ ! "$id" =~ ^(critical-state|system-rebuild)-[0-9]{8}T[0-9]{6}Z$ ]]; then
  echo "Invalid backup ID" >&2; exit 3
fi
root="$HOME/.iconic-recovery/archives/$id"
test -d "$root"
test -f "$root/SHA256SUMS"
cd "$root"
shasum -a 256 -c SHA256SUMS
shopt -s nullglob
parts=(part-*.cms)
test "${#parts[@]}" -ge 1
echo "ENCRYPTED_PARTS_CHECKSUM_PASS ${#parts[@]}"
key="$HOME/.iconic-recovery/keys/iconic-dr-2026-private.pem"
cert="$HOME/.iconic-recovery/keys/iconic-dr-2026-public.crt"
(
  for item in "${parts[@]}"; do
    openssl cms -decrypt -inform DER -in "$item" -recip "$cert" -inkey "$key"
  done
) | /usr/local/bin/zstd -t -q
echo "INDEPENDENT_MAC_DECRYPT_AND_ZSTD_PASS $id"
