#!/usr/bin/env python3
"""Offline code recovery from an extracted ICONIC system-rebuild bundle.

Safely stages pinned repositories without requiring GitHub, a local model,
network access, or credentials. Does not start any service or overwrite data.

Usage:
 python3 dr_restore_code.py --bundle-root /path/decrypted-system-kit --output /path/clean-stage

Encrypted bundle extraction should occur only on the Mac where the private
recovery key lives. Never copy the private key to Beastmaster.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as fp:
        for chunk in iter(lambda:fp.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def run(args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                   timeout=240)


def restore(bundle_root, output):
    bundle_root=Path(bundle_root).resolve()
    output=Path(output).resolve()
    manifest=bundle_root/"system"/"inventory.json"
    if not manifest.is_file():
        raise ValueError("Missing system rebuild inventory")
    entries=json.loads(manifest.read_text()).get("git_pins")
    if not isinstance(entries,dict) or len(entries)<5:
        raise ValueError("Incomplete recovery git manifest")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Refusing to overwrite a nonempty target")
    output.mkdir(mode=0o700,parents=True,exist_ok=True)
    completed=[]
    for label,item in sorted(entries.items()):
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,90}",label):
            raise ValueError("Unsafe repository name")
        sha=item.get("sha","")
        if not re.fullmatch(r"[0-9a-f]{40}",sha):
            raise ValueError("Bad pinned commit for "+label)
        bundle=bundle_root/"git-bundles"/(label+".bundle")
        if not bundle.is_file() or bundle.is_symlink():
            raise ValueError("Missing or unsafe bundle for "+label)
        if digest(bundle)!=item.get("bundle_sha256"):
            raise ValueError("Git bundle hash mismatch for "+label)
        target=output/label
        run(["git","clone","--quiet","--no-local",str(bundle),str(target)])
        run(["git","-C",str(target),"cat-file","-e",sha+"^{commit}"])
        run(["git","-C",str(target),"checkout","--detach","--quiet",sha])
        actual=subprocess.check_output(["git","-C",str(target),"rev-parse","HEAD"],
                                       text=True).strip()
        if actual!=sha:raise RuntimeError("Pinned commit mismatch for "+label)
        completed.append({"repository":label,"sha":sha})
        print("RESTORED_PINNED_REPOSITORY",label,sha[:12],flush=True)
    (output/"CODE_RESTORE_VERIFIED.json").write_text(
        json.dumps({"schema":"iconic-offline-code-restore-v1",
                    "restored":completed,"services_started":False,
                    "customer_data_restored":False},indent=2)+"\n")
    print("OFFLINE_RESTORE_STAGED",len(completed),"REPOSITORIES",flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle-root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    restore(args.bundle_root,args.output)


if __name__=="__main__":
    main()
