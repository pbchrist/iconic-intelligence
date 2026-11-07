#!/usr/bin/env python3
"""Recoverable split-CMS encrypted snapshot; each part is <256 MiB.

Previous single 2.97 GB CMS file was NOT restorable by Mac OpenSSL. This
version encrypts compressed stream in independently decryptable chunks.
Source data and the snapshot are never uploaded in plaintext.
"""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime,timezone

SOURCE=Path(__file__).resolve().with_name("disaster_recovery_backup.py")
spec=importlib.util.spec_from_file_location("legacy_dr_source",SOURCE)
dr=importlib.util.module_from_spec(spec);spec.loader.exec_module(dr)
ROOT=Path("/home/patrick")
MAC="user@100.78.33.125"
MACDIR="/Users/user/.iconic-recovery/archives"
CHUNK_BYTES=128*1024*1024


def encrypt_split(stage,identifier):
    output=dr.DEST/identifier
    output.mkdir(parents=True,exist_ok=False)
    tar=subprocess.Popen(["tar","-C",str(stage),"-cf","-","."],
                         stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    zstd=subprocess.Popen(["zstd","-T2","-3","-q"],stdin=tar.stdout,
                          stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    tar.stdout.close()
    parts=[]
    try:
        i=0
        while True:
            payload=zstd.stdout.read(CHUNK_BYTES)
            if not payload:break
            i+=1
            raw=dr.WORK/("encrypted-input-"+identifier+".tmp")
            out=output/("part-%04d.cms"%i)
            pending=out.with_suffix(".partial")
            try:
                fd=os.open(raw,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
                with os.fdopen(fd,"wb") as handle:
                    handle.write(payload)
                    handle.flush()
                    os.fsync(handle.fileno())
                # Deliberately omit -stream and keep the DER envelope below
                # OpenSSL's large-ASN.1-buffer limit.
                subprocess.run(["openssl","cms","-encrypt","-binary",
                    "-outform","DER","-aes256",
                    "-recip",str(dr.CERT),"-in",str(raw),"-out",str(pending)],
                    check=True,timeout=160)
                pending.replace(out)
                parts.append({"file":out.name,"sha256":dr.digest(out),
                              "bytes":out.stat().st_size})
                print("ENCRYPTED_RECOVERABLE_CHUNK",i,"bytes",out.stat().st_size,flush=True)
            finally:
                raw.unlink(missing_ok=True)
                pending.unlink(missing_ok=True)
        zstd.stdout.close()
        errors=(tar.wait(),zstd.wait())
        if errors!=(0,0) or not parts:raise RuntimeError("Tar/zstd stream failed")
        metadata={"schema":"iconic-recovery-split-cms-v2","id":identifier,
                  "created_utc":datetime.now(timezone.utc).isoformat(),
                  "chunk_limit_bytes":CHUNK_BYTES,"encrypted_parts":parts,
                  "archived_contents":"home/patrick critical state, source manifests and sqlite online backups",
                  "restore_requirement":"Mac private RSA key; concatenate decrypted parts then zstd -d | tar",
                  "status":"ENCRYPTED_UNVERIFIED_UNTIL_MAC_DECRYPT_TEST"}
        (output/"manifest.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
        (output/"SHA256SUMS").write_text("".join(x["sha256"]+"  "+x["file"]+"\n" for x in parts))
        return output
    except Exception:
        # A partial archive is never a verified backup.
        (output/"INCOMPLETE_DO_NOT_RESTORE").write_text("Archive failed; do not use.\n")
        raise
    finally:
        if tar.poll() is None:tar.kill()
        if zstd.poll() is None:zstd.kill()


def copy_and_verify_on_mac(encrypted_directory):
    ident=encrypted_directory.name
    print("TRANSFER_ENCRYPTED_PARTS_TO_MAC",ident,flush=True)
    subprocess.run(["ssh","-oBatchMode=yes",MAC,"mkdir -p "+MACDIR],
                   check=True,timeout=20)
    subprocess.run(["scp","-q","-r","-oBatchMode=yes",str(encrypted_directory),
                    MAC+":"+MACDIR+"/"],check=True,timeout=1800)
    print("VERIFY_MAC_DECRYPTABLE_SEGMENTS",flush=True)
    subprocess.run(["ssh","-oBatchMode=yes",MAC,
                    "/Users/user/.iconic-recovery/verify-recovery-archive.sh "+ident],
                    check=True,timeout=600)
    # Only after crypto/decompression verification, copy to local OneDrive sync.
    # This proves that a local sync-folder copy exists, NOT that cloud uploaded.
    remote=(
      "set -e; cloud=\"$HOME/Library/CloudStorage/OneDrive-Personal/ICONIC-Recovery\"; "
      "mkdir -p \"$cloud\"; "
      "cp -R \""+MACDIR+"/"+ident+"\" \"$cloud/\"; "
      "cd \"$cloud/"+ident+"\"; "
      "shasum -a 256 -c SHA256SUMS"
    )
    subprocess.run(["ssh","-oBatchMode=yes",MAC,remote],check=True,timeout=600)
    print("MAC_AND_ONEDRIVE_LOCAL_FILES_VERIFIED_CLOUD_UPLOAD_NOT_PROVEN",flush=True)
    path=encrypted_directory/"VERIFIED_ON_MAC"
    path.write_text(datetime.now(timezone.utc).isoformat()+"\n")
    print("RECOVERABLE_ENCRYPTED_SNAPSHOT_VERIFIED",ident,flush=True)


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execute",action="store_true")
    args=p.parse_args()
    if not args.execute:
        print("Dry-run: safe split-CMS snapshot to mounted external disk and Mac")
        print("No model files included. Never stage secrets on public GitHub.")
        return
    if not dr.CERT.is_file() or not dr.DEST.parent.is_mount():
        raise RuntimeError("Required cert or external mount missing")
    dr.DEST.mkdir(exist_ok=True)
    dr.WORK.mkdir(exist_ok=True,mode=0o700)
    identifier="critical-state-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stage=dr.WORK/("staging-"+identifier)
    stage.mkdir(mode=0o700)
    try:
        sqlites=dr.copy_state(stage)
        dr.model_inventory(stage)
        dr.manifest(stage,sqlites)
        print("ONLINE_SQLITE_SNAPSHOT_COUNT",len(sqlites),flush=True)
        directory=encrypt_split(stage,identifier)
        copy_and_verify_on_mac(directory)
    finally:
        dr.safely_remove_staging(stage)


if __name__=="__main__":main()
