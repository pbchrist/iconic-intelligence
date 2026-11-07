#!/usr/bin/env python3
"""Read-only ICONIC disaster-recovery health: snapshot age, verified off-host status.

No credentials or archive plaintext are read. Nonzero exit when a required
backup is missing or too old. Intended for a systemd service/timer with logs.
"""
from __future__ import annotations
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import sys

EXTERNAL=Path("/run/media/patrick/2067738214reward/ICONIC-RECOVERY")
STATE=Path("/home/patrick/.local/state/iconic-recovery")


def inspect(max_age_hours=36):
    if not EXTERNAL.parent.is_mount():
        return {"status":"FAIL","reason":"external_not_mounted"}
    snapshots=sorted(
        (x for x in EXTERNAL.glob("critical-state-*")
         if x.is_dir() and (x/"manifest.json").is_file() and
         (x/"SHA256SUMS").is_file()),
        key=lambda x:x.name)
    verified=[x for x in snapshots if (x/"VERIFIED_ON_MAC").is_file()]
    result={
        "schema":"iconic-recovery-health-v1",
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "encrypted_external_snapshots":len(snapshots),
        "mac_verified_snapshots":len(verified),
        "pending_offhost_snapshots":len(snapshots)-len(verified),
        "most_recent_encrypted":snapshots[-1].name if snapshots else None,
        "most_recent_mac_verified":verified[-1].name if verified else None,
        "model_mirror_verified":(EXTERNAL/"model-mirror-verification.json").is_file(),
    }
    if not verified:
        result.update(status="FAIL",reason="no_verified_offhost_backup")
        return result
    date_string=verified[-1].name[len("critical-state-"):]
    timestamp=datetime.strptime(date_string,"%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    hours=(datetime.now(timezone.utc)-timestamp).total_seconds()/3600
    result["last_verified_age_hours"]=round(hours,2)
    result["max_verified_age_hours"]=max_age_hours
    result["status"]="PASS" if hours<=max_age_hours else "FAIL"
    result["reason"]="fresh" if hours<=max_age_hours else "offhost_backup_stale"
    return result


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--max-age-hours",type=int,default=36)
    args=p.parse_args()
    info=inspect(args.max_age_hours)
    STATE.mkdir(exist_ok=True,parents=True,mode=0o700)
    temp=STATE/"recovery-health.json.tmp"
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
    try:
        os.write(fd,(json.dumps(info,indent=2)+"\n").encode("utf-8"))
        os.fsync(fd)
    finally:os.close(fd)
    os.replace(temp,STATE/"recovery-health.json")
    print(json.dumps(info,indent=2))
    if info["status"]!="PASS":
        sys.exit(1)


if __name__=="__main__":
    main()
