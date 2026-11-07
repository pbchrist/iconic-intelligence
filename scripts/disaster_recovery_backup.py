#!/usr/bin/env python3
"""Encrypted, recoverable Beastmaster critical-state backup to external disk + Mac.

No secrets are sent to GitHub. Keypair is generated on the *Mac*; only the
public certificate exists on Beastmaster. Source services are never stopped.
SQLite databases use the online SQLite backup API, not a live file copy.

This is a best-effort, point-in-time *per-database* backup. It is not an
atomic distributed snapshot across all live services. Inspect the manifest
and complete a restore drill before declaring full disaster recovery.
"""
from __future__ import annotations

from datetime import datetime,timezone
import fnmatch
import hashlib
import json
import os
import shlex
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time

HOME=Path("/home/patrick")
DEST=Path("/run/media/patrick/2067738214reward/ICONIC-RECOVERY")
CERT=HOME/".local/share/iconic-recovery/recovery-public.crt"
MAC="user@100.78.33.125"
MAC_HOME="/Users/user"
WORK=HOME/".local/state/iconic-recovery"
SELECTED=[
    ".config/mempalace",
    ".config/systemd/user",
    ".config/iconic-command.env",
    ".config/gh",
    ".ssh",
    ".hermes",
    "hermes-instance2",
    ".open-webui",
    ".local/state/iconic-command",
    "iconic-command-data",
    "services/iconic-intelligence-reserve/data",
    "experiments/beastmaster-training/checkpoints",
    "experiments/beastmaster-adversarial-harness/logs",
]
EXCLUDED_DIRS={
    ".git",".cache","node_modules","__pycache__","venv",".venv",
    "backups","state-snapshots","cache","tools","installs",
    "hermes-agent-venv","tests","test-results","hf-cache",
    "logs","tmp","temp","build","dist",
    "chroma-cache","browser-cache","uv",
}
# Retain essential documents and runtime config; skip reproducible dependencies.
SQLITE_EXT={".db",".sqlite",".sqlite3"}
RUN_DATE=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
CURRENT_VERSION="iconic-critical-dr-v1"


def run(args, **kw):
    return subprocess.run(args,check=True,**kw)


def digest(path,chunk=4*1024*1024):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for part in iter(lambda:f.read(chunk),b""):
            h.update(part)
    return h.hexdigest()


def walk_sqlite(src):
    if src.is_file():
        return [src] if src.suffix.lower() in SQLITE_EXT else []
    dbs=[]
    for root,dirs,files in os.walk(src,followlinks=False):
        dirs[:]=[d for d in dirs if d not in EXCLUDED_DIRS and
                 ".retired" not in d and ".rollback-broken" not in d]
        for file in files:
            candidate=Path(root)/file
            if candidate.suffix.lower() in SQLITE_EXT and not candidate.is_symlink():
                dbs.append(candidate)
    return dbs


def copy_state(stage):
    root=stage/"home/patrick"
    root.mkdir(parents=True,exist_ok=True)
    db_list=[]
    for rel in SELECTED:
        src=HOME/rel
        if not src.exists():
            continue
        target=root/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        if src.is_file():
            if src.suffix.lower() not in SQLITE_EXT:
                shutil.copy2(src,target,follow_symlinks=False)
            else:
                db_list.append((src,target))
            continue
        target.mkdir(parents=True,exist_ok=True)
        # Rsync regular files, never follow symlinks; exclude cache/dependency
        # directories and SQLite files copied consistently below.
        excludes=["--exclude="+p+"/" for p in sorted(EXCLUDED_DIRS)]
        excludes += ["--exclude=*.retired*/","--exclude=*.rollback-broken*/"]
        excludes += ["--exclude=*"+e for e in sorted(SQLITE_EXT)]
        excludes += ["--exclude=*-wal","--exclude=*-shm"]
        print("COPY_STATE",rel,flush=True)
        run(["rsync","-a","--safe-links",*excludes,str(src)+"/",str(target)+"/"])
        for db in walk_sqlite(src):
            dest=root/db.relative_to(HOME)
            db_list.append((db,dest))
    copied=[]
    for source,dest in db_list:
        dest.parent.mkdir(parents=True,exist_ok=True)
        print("SQLITE_ONLINE_BACKUP",str(source.relative_to(HOME)),flush=True)
        src=sqlite3.connect("file:"+str(source)+"?mode=ro",uri=True,timeout=60)
        try:
            dst=sqlite3.connect(str(dest),timeout=60)
            try:
                src.backup(dst,pages=10000,sleep=0.2)
                check=dst.execute("PRAGMA quick_check").fetchone()[0]
                if check!="ok":
                    raise RuntimeError("SQLite quick_check failed")
            finally:
                dst.close()
        finally:
            src.close()
        copied.append({"relative":str(source.relative_to(HOME)),
                       "bytes":dest.stat().st_size,"sha256":digest(dest)})
    return copied


def safely_remove_staging(stage):
    # rsync -a retains read-only source-directory modes. We may relax
    # permissions only inside a precisely checked disposable staging path.
    stage=Path(stage).resolve()
    expected=WORK.resolve()
    if stage.parent != expected or not stage.name.startswith("staging-"):
        raise RuntimeError("Refusing to remove an unexpected staging path")
    for root, dirs, files in os.walk(stage, topdown=False, followlinks=False):
        for dirname in dirs:
            item=Path(root)/dirname
            if not item.is_symlink():
                os.chmod(item,0o700)
        os.chmod(root,0o700)
    shutil.rmtree(stage)


def manifest(stage,sqlite_files):
    repos={
        "iconic-intelligence":"iconic-command",
        "iconic-intelligence-reserve":"services/iconic-intelligence-reserve",
        "beastmaster-adversarial-harness":"experiments/beastmaster-adversarial-harness",
        "beastmaster-training":"experiments/beastmaster-training",
        "iconic-reserve-website":"services/iconic-reserve-website",
    }
    versions={}
    for name,rel in repos.items():
        path=HOME/rel
        if not path.exists():continue
        sha=subprocess.check_output(["git","-C",str(path),"rev-parse","HEAD"],text=True).strip()
        remote=subprocess.check_output(["git","-C",str(path),"remote","get-url","origin"],text=True).strip()
        if "@" in remote and "github.com" in remote and remote.startswith("https:"):
            remote="https://github.com/"+remote.split("github.com/",1)[1]
        versions[name]={"sha":sha,"remote":remote}
    payload={
        "schema":CURRENT_VERSION,
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "host":"patrick-beastmaster",
        "selected_relative_roots":SELECTED,
        "excluded_directory_names":sorted(EXCLUDED_DIRS),
        "sqlite_snapshots":sqlite_files,
        "git_versions":versions,
        "model_blobs_included":False,
        "model_inventory_location":"model_inventory.json",
        "recovery_key_private_location":"Mac FileVault-protected ~/.iconic-recovery/keys/iconic-dr-2026-private.pem",
        "recovery_key_public_fingerprint":"62:9A:E3:8B:68:3F:8A:45:9E:58:A3:3D:3D:A4:23:38:02:C0:4D:06:88:26:A4:98:25:E8:96:C9:1D:8C:19:AC",
        "sqlite_backup_type":"online per-database backup API; cross-DB consistency not guaranteed",
        "exclusion_note":"No model weights, caches, dependencies, or archival backups in critical archive.",
    }
    (stage/"recovery-manifest.json").write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    os.chmod(stage/"recovery-manifest.json",0o600)
    return payload


def model_inventory(stage):
    models=[]
    for directory in (HOME/"models",HOME/"ai-review/bonsai2/models"):
        if not directory.exists():continue
        for item in directory.rglob("*.gguf"):
            if item.is_file():
                models.append({"relative":str(item.relative_to(HOME)),"size":item.stat().st_size})
    (stage/"model_inventory.json").write_text(json.dumps(models,indent=2)+"\n",encoding="utf-8")


def encrypt_snapshot(stage):
    DEST.mkdir(parents=True,exist_ok=True)
    output=DEST/("critical-state-"+RUN_DATE+".tar.zst.cms")
    temp=output.with_suffix(".partial")
    tar=subprocess.Popen(["tar","-C",str(stage),"-cf","-","."],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    compressor=subprocess.Popen(["zstd","-T2","-3","-q"],stdin=tar.stdout,stdout=subprocess.PIPE)
    tar.stdout.close()
    try:
        crypt=subprocess.run(["openssl","cms","-encrypt","-binary","-stream",
                             "-outform","DER","-aes256","-recip",str(CERT),
                             "-out",str(temp)],stdin=compressor.stdout,
                             capture_output=True)
        compressor.stdout.close()
        code=compressor.wait()
        tarcode=tar.wait()
        if tarcode!=0 or code!=0 or crypt.returncode!=0:
            raise RuntimeError("Critical archive pipeline failed")
        temp.replace(output)
        return output
    finally:
        if tar.poll() is None:tar.kill()
        if compressor.poll() is None:compressor.kill()


def copy_offhost(archive):
    filename=archive.name
    macdir=MAC_HOME+"/.iconic-recovery/archives"
    cmd=["ssh","-oBatchMode=yes","-oConnectTimeout=8",MAC,
         "mkdir -p "+macdir]
    run(cmd)
    print("COPY_TO_MAC_ENCRYPTED",filename,flush=True)
    run(["scp","-q","-oBatchMode=yes",str(archive),
         MAC+":"+macdir+"/"+filename])
    expected=digest(archive)
    actual=subprocess.check_output(["ssh","-oBatchMode=yes",MAC,
          "shasum -a 256 "+macdir+"/"+filename],text=True).split()[0]
    if expected!=actual:
        raise RuntimeError("Mac copy checksum mismatch")
    print("MAC_ENCRYPTED_SHA256_VERIFIED",expected,flush=True)
    # Also request OneDrive upload by placing an encrypted file into the
    # sync folder. That does NOT prove the cloud has finished syncing it.
    # Shell is restricted to our fixed timestamped, internally generated name.
    remote=(
      "set -e; cloud=\"$HOME/Library/CloudStorage/OneDrive-Personal/ICONIC-Recovery\"; "
      "mkdir -p \"$cloud\"; "
      "cp \""+macdir+"/"+filename+"\" \"$cloud/"+filename+"\"; "
      "shasum -a 256 \"$cloud/"+filename+"\""
    )
    result=subprocess.check_output(["ssh","-oBatchMode=yes",MAC,remote],text=True).split()[0]
    if result!=expected:raise RuntimeError("Mac OneDrive-folder copy checksum mismatch")
    print("ONEDRIVE_LOCAL_SYNC_FOLDER_COPY_VERIFIED_UPLOAD_UNCONFIRMED",flush=True)
    # Verify cryptographic readability on the Mac without exposing plaintext.
    decrypt=(
      "set -o pipefail; "
      "openssl cms -decrypt -inform DER "
      "-in "+macdir+"/"+filename+" "
      "-recip "+MAC_HOME+"/.iconic-recovery/keys/iconic-dr-2026-public.crt "
      "-inkey "+MAC_HOME+"/.iconic-recovery/keys/iconic-dr-2026-private.pem "
      "| zstd -t -q"
    )
    # Quote one full remote shell command so the pipe reaches bash intact.
    run(["ssh","-oBatchMode=yes",MAC,"bash -lc "+shlex.quote(decrypt)])
    print("MAC_DECRYPT_AND_DECOMPRESS_VERIFIED",flush=True)
    return expected


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execute",action="store_true")
    p.add_argument("--skip-offhost",action="store_true")
    args=p.parse_args()
    if not args.execute:
        print("DRY_RUN_NO_WRITES")
        print("Selected",len(SELECTED),"critical data roots, including encrypted credentials")
        print("Encryption certificate",CERT.exists())
        print("External drive",DEST.parent.is_mount() if hasattr(DEST.parent,"is_mount") else DEST.parent.exists())
        print("Run --execute to take snapshot")
        return
    if not CERT.is_file():
        raise RuntimeError("Recovery public cert missing")
    if not Path("/run/media/patrick/2067738214reward").is_mount():
        raise RuntimeError("Expected external disk not mounted")
    # Never create an unencrypted snapshot directly on an external disk.
    WORK.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(WORK,0o700)
    stage=WORK/("staging-"+RUN_DATE)
    if stage.exists():
        raise RuntimeError("Staging path already exists")
    stage.mkdir(mode=0o700)
    try:
        files=copy_state(stage)
        model_inventory(stage)
        payload=manifest(stage,files)
        print("DATABASE_SNAPSHOTS",len(files),flush=True)
        archive=encrypt_snapshot(stage)
        sha=digest(archive)
        sidecar=DEST/(archive.name+".sha256")
        sidecar.write_text(sha+"  "+archive.name+"\n",encoding="utf-8")
        print("ENCRYPTED_EXTERNAL_ARCHIVE",str(archive),"BYTES",archive.stat().st_size,flush=True)
        print("ARCHIVE_SHA256",sha,flush=True)
        if not args.skip_offhost:
            copy_offhost(archive)
        print("DISASTER_RECOVERY_CRITICAL_SNAPSHOT_COMPLETE",flush=True)
    finally:
        # Do not leave a second plaintext copy of private credentials/stores
        # in the staging directory. SSD remanence still depends on hardware.
        safely_remove_staging(stage)


if __name__=="__main__":
    raise SystemExit(
        "Single-file CMS backups over 2 GiB are NOT recoverable on the Mac. "
        "Use disaster_recovery_backup_split.py instead.")
