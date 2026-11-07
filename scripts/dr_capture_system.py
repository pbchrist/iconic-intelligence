#!/usr/bin/env python3
"""Capture reproducible system configuration + Git bundles, encrypt to Mac key.

Runs online without restarting any services; never publishes credentials or
service unit contents. The archive includes nonsecret package manifests,
privileged readable service configuration, and offline git bundles.
"""
from __future__ import annotations

from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HOME=Path("/home/patrick")
RECOVERY=HOME/".local/share/iconic-recovery"
EXTERNAL=Path("/run/media/patrick/2067738214reward/ICONIC-RECOVERY")
CERT=RECOVERY/"recovery-public.crt"
UTC=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

REPOS={
    "iconic-intelligence":HOME/"iconic-command",
    "iconic-intelligence-reserve":HOME/"services/iconic-intelligence-reserve",
    "beastmaster-adversarial-harness":HOME/"experiments/beastmaster-adversarial-harness",
    "beastmaster-training":HOME/"experiments/beastmaster-training",
    "iconic-reserve-website-working-tree":HOME/"services/iconic-reserve-website",
}
SYSTEM_FILES=[
    Path("/etc/systemd/system/llama-server-qwen38.service"),
    Path("/etc/nut/ups.conf"),
    Path("/etc/nut/upsmon.conf"),
    Path("/etc/nut/upsd.conf"),
    Path("/etc/nut/nut.conf"),
    Path("/etc/docker/daemon.json"),
]


def safe_output(args):
    p=subprocess.run(args,text=True,capture_output=True,timeout=75)
    if p.returncode:
        return "UNAVAILABLE "+str(args[:2])+"\n"
    return p.stdout


def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(4*1024*1024),b""):
            h.update(b)
    return h.hexdigest()


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--execute",action="store_true")
    args=ap.parse_args()
    if not args.execute:
        print("DRY_RUN: would capture root service units where readable, repo git bundles, "
              "package/service inventory, and encrypted Mac/external archive")
        return
    if not CERT.is_file() or not EXTERNAL.parent.is_mount():
        raise RuntimeError("Missing certificate or detached external drive")
    EXTERNAL.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="iconic-system-capture-",dir=HOME/".local/state") as tmp:
        root=Path(tmp)
        bundles=root/"git-bundles"
        bundles.mkdir()
        pins={}
        for label,path in REPOS.items():
            if safe_output(["git","-C",str(path),"rev-parse","--is-shallow-repository"]).strip()=="true":
                print("FETCH_COMPLETE_GIT_HISTORY",label,flush=True)
                subprocess.run(["git","-C",str(path),"fetch","--unshallow","origin"],check=True,timeout=180)
            commit=safe_output(["git","-C",str(path),"rev-parse","HEAD"]).strip()
            pins[label]={"path":str(path),"sha":commit}
            target=bundles/(label+".bundle")
            print("BUNDLE",label,flush=True)
            subprocess.run(["git","-C",str(path),"bundle","create",str(target),"--all"],
                           check=True,timeout=120)
            subprocess.run(["git","bundle","verify",str(target)],cwd=path,
                           stdout=subprocess.DEVNULL,check=True,timeout=60)
            pins[label]["bundle_sha256"]=sha(target)
        sysdir=root/"system"
        sysdir.mkdir()
        system={"kernel":safe_output(["uname","-r"]).strip(),
                "gpu":safe_output(["nvidia-smi","--query-gpu=index,name,memory.total,driver_version","--format=csv,noheader"]),
                "repos":pins,
                "files_copied":[],
                "files_not_readable":[]}
        for path in SYSTEM_FILES:
            if path.is_file() and os.access(path,os.R_OK):
                dst=root/"root-config"/path.relative_to("/")
                dst.parent.mkdir(exist_ok=True,parents=True)
                shutil.copy2(path,dst)
                system["files_copied"].append(str(path))
            else:
                system["files_not_readable"].append(str(path))
        inventory={
            "os_release":Path("/etc/os-release").read_text(),
            "nvidia_gpus":system["gpu"],
            "dpkg_packages":safe_output(["dpkg-query","-W","-f=${binary:Package}\t${Version}\n"]),
            "python_version":safe_output(["python3","--version"]),
            "systemctl_user_services":safe_output(
                ["systemctl","--user","list-unit-files","--type=service","--no-pager"]),
            "systemctl_user_timers":safe_output(
                ["systemctl","--user","list-timers","--all","--no-pager"]),
            "systemctl_root_units":safe_output(
                ["systemctl","list-unit-files","--type=service","--no-pager"]),
            "model_listing":safe_output(["find",str(HOME/"models"),"-type","f","-name","*.gguf","-printf","%p %s\\n"]),
            "git_pins":pins,
        }
        (sysdir/"inventory.json").write_text(json.dumps(inventory,indent=2)+"\n")
        (sysdir/"system-files.json").write_text(json.dumps(system,indent=2)+"\n")
        out=EXTERNAL/("system-rebuild-"+UTC+".tar.zst.cms")
        pending=out.with_suffix(".partial")
        # Never store unencrypted final archives on the USB drive.
        tar=subprocess.Popen(["tar","-C",str(root),"-cf","-","."],stdout=subprocess.PIPE)
        compressor=subprocess.Popen(["zstd","-T2","-3","-q"],stdin=tar.stdout,stdout=subprocess.PIPE)
        tar.stdout.close()
        with pending.open("wb") as file:
            crypt=subprocess.Popen(["openssl","cms","-encrypt","-binary","-stream",
                                    "-outform","DER","-aes256","-recip",str(CERT)],
                                   stdin=compressor.stdout,stdout=file)
            compressor.stdout.close()
            rc=crypt.wait()
        if tar.wait() or compressor.wait() or rc:
            raise RuntimeError("System-capture encryption pipeline failed")
        pending.replace(out)
        digest=sha(out)
        (EXTERNAL/(out.name+".sha256")).write_text(digest+"  "+out.name+"\n")
        print("ENCRYPTED_SYSTEM_BUNDLE",out,"SHA256",digest,"BYTES",out.stat().st_size,flush=True)
        # Reuse same off-Mac encrypted-copy/decryption verification as critical snapshot.
        import importlib.util
        script=Path(__file__).resolve().with_name("disaster_recovery_backup.py")
        spec=importlib.util.spec_from_file_location("dr",script)
        dr=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dr)
        dr.copy_offhost(out)
        print("SYSTEM_REBUILD_ARCHIVE_COMPLETE")


if __name__=="__main__":
    main()
