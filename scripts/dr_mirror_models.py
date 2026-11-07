#!/usr/bin/env python3
"""Safely mirror local GGUF weights to external USB and verify each SHA-256.

No model is stopped or modified. Uses low process priority and rsync with
resumable partial files. Avoids Cyberpunk, game files, and any other filesystem
not explicitly listed here. The USB drive is not an offsite backup.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime,timezone

ROOT=Path("/run/media/patrick/2067738214reward/ICONIC-RECOVERY")
SRC=Path("/home/patrick")
DIRECTORIES=[
    Path("models"),
    Path("ai-review/bonsai2/models"),
]


def checksum(path):
    h=hashlib.sha256()
    with path.open("rb") as fp:
        while True:
            chunk=fp.read(8*1024*1024)
            if not chunk:break
            h.update(chunk)
    return h.hexdigest()


def main():
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--execute",action="store_true")
    args=a.parse_args()
    if not args.execute:
        print("DRY_RUN explicit GGUF model directories only; --execute to copy")
        return
    if not ROOT.parent.is_mount():
        raise RuntimeError("Expected external drive not mounted")
    out=ROOT/"model-blobs"
    out.mkdir(parents=True,exist_ok=True)
    assets=[]
    for rel in DIRECTORIES:
        origin=SRC/rel
        if not origin.exists():continue
        target=out/rel
        target.mkdir(parents=True,exist_ok=True)
        print("MIRROR_MODEL_DIRECTORY",rel,flush=True)
        subprocess.run([
            "rsync","-rtl","--size-only","--partial","--no-perms","--no-owner","--no-group",
            "--exclude=*.tmp","--exclude=*.partial","--exclude=.git/",
            str(origin)+"/",str(target)+"/"
        ],check=True,timeout=7200)
        for original in origin.rglob("*.gguf"):
            if not original.is_file():continue
            relative=original.relative_to(SRC)
            copied=out/relative
            if not copied.is_file() or copied.stat().st_size!=original.stat().st_size:
                raise RuntimeError("Model copy incomplete "+str(relative))
            print("VERIFY_MODEL_HASHES",relative,flush=True)
            local=checksum(original)
            remote=checksum(copied)
            if local!=remote:raise RuntimeError("Model checksum mismatch "+str(relative))
            assets.append({"relative":str(relative),"bytes":original.stat().st_size,
                           "sha256":local})
    manifest={"schema":"iconic-dr-model-mirror-v1","verified_utc":datetime.now(timezone.utc).isoformat(),
              "files":assets,"total_bytes":sum(x["bytes"] for x in assets),
              "file_count":len(assets),"all_hashes_match":True,
              "offsite_independent_copy_verified":False}
    temp=ROOT/"model-mirror-verification.json.tmp"
    temp.write_text(json.dumps(manifest,indent=2)+"\n")
    temp.replace(ROOT/"model-mirror-verification.json")
    print("MODEL_MIRROR_VERIFIED",len(assets),"FILES",manifest["total_bytes"],"BYTES",flush=True)


if __name__=="__main__":main()
