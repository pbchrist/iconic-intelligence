#!/bin/bash
# Independently decrypt and validate ICONIC's encrypted state archive on Mac.
# No private recovery key ever leaves the Mac. Plaintext is transient by default.
set -euo pipefail
umask 077
id="${1:-}"
keep="${2:-}"
if [[ ! "$id" =~ ^critical-state-[0-9]{8}T[0-9]{6}Z$ ]]; then
  echo "Expected critical-state-YYYYMMDDTHHMMSSZ archive ID" >&2
  exit 2
fi
if [[ -n "$keep" && "$keep" != "--keep" ]]; then
  echo "Optional second argument is --keep (leaves plaintext in protected Mac folder)" >&2
  exit 2
fi
root="$HOME/.iconic-recovery/archives/$id"
test -f "$root/SHA256SUMS"
cd "$root"
shasum -a 256 -c SHA256SUMS
shopt -s nullglob
parts=(part-*.cms)
test "${#parts[@]}" -ge 1
key="$HOME/.iconic-recovery/keys/iconic-dr-2026-private.pem"
cert="$HOME/.iconic-recovery/keys/iconic-dr-2026-public.crt"
mkdir -p "$HOME/.iconic-recovery/restore-tests"
scratch=$(mktemp -d "$HOME/.iconic-recovery/restore-tests/$id.XXXXXX")
chmod 700 "$scratch"
cleanup(){
  if [[ "$keep" != "--keep" ]]; then
    # Only remove an auto-generated, tightly scoped disposable restore path.
    case "$scratch" in
      "$HOME/.iconic-recovery/restore-tests/$id."*)
        # GNU rsync preserved read-only Linux folder modes in the archive.
        # Relax permissions only in this private disposable restore subtree.
        find "$scratch" -type d -exec chmod u+rwx {} +
        rm -rf -- "$scratch"
        ;;
      *) echo "Refusing unsafe cleanup path" >&2 ;;
    esac
  fi
}
trap cleanup EXIT
(
  for item in "${parts[@]}"; do
    openssl cms -decrypt -inform DER -in "$item" -recip "$cert" -inkey "$key"
  done
) | /usr/local/bin/zstd -d -q | tar -xf - -C "$scratch"
python3 - "$scratch" <<'PY'
import hashlib,json,pathlib,sqlite3,sys
root=pathlib.Path(sys.argv[1])
meta=root/'recovery-manifest.json'
if not meta.is_file():raise SystemExit('MISSING_RECOVERY_MANIFEST')
manifest=json.loads(meta.read_text())
verified=0
for entry in manifest.get('sqlite_snapshots',[]):
    file=root/'home/patrick'/entry['relative']
    if not file.is_file():raise SystemExit('MISSING_SQLITE_FILE')
    h=hashlib.sha256()
    with file.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    if h.hexdigest()!=entry['sha256']:raise SystemExit('SQLITE_HASH_MISMATCH')
    con=sqlite3.connect('file:'+str(file)+'?mode=ro',uri=True)
    try:
        if con.execute('PRAGMA quick_check').fetchone()[0]!='ok':
            raise SystemExit('SQLITE_QUICK_CHECK_FAILED')
    finally:con.close()
    verified+=1
print('CLEAN_MAC_RESTORE_DRILL_PASS')
print('SQLITE_DATABASES_VERIFIED',verified)
print('RECOVERY_MANIFEST_SCHEMA',manifest.get('schema'))
PY
if [[ "$keep" == "--keep" ]]; then
  echo "WARNING: plaintext recovery data and credentials remain at $scratch"
else
  echo "MAC_RESTORE_VERIFIED_PLAINTEXT_CLEANUP_REQUESTED"
fi
