#!/usr/bin/env python3
"""Check style-guide.yaml against the site's live color tokens.

The site loads styles.css, then mobile-first.css; the later :root wins.
Exit 1 and list every token whose YAML value no longer matches.
Run: python3 scripts/check-style-guide.py
"""
import re, sys, pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
tokens = {}
for css in ("styles.css", "mobile-first.css"):
    text = (ROOT / css).read_text()
    block = re.search(r":root\s*\{([^}]*)\}", text)
    if block:
        for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block.group(1)):
            tokens[name] = value.strip()

def resolve(v, depth=0):
    m = re.fullmatch(r"var\((--[\w-]+)\)", v)
    return resolve(tokens.get(m.group(1), v), depth + 1) if m and depth < 5 else v

def norm(v):
    return re.sub(r"\s+", "", v.lower()).replace("0.", ".")

guide = yaml.safe_load((ROOT / "style-guide.yaml").read_text())
bad = 0
for t in guide["colors"]["tokens"]:
    live = resolve(tokens.get(t["name"], "(missing)"))
    if norm(live) != norm(t["hex"]):
        bad += 1
        print(f"MISMATCH {t['name']}: yaml {t['hex']} / css {live}")
print(f"{len(guide['colors']['tokens']) - bad} of {len(guide['colors']['tokens'])} color tokens match.")
sys.exit(1 if bad else 0)
