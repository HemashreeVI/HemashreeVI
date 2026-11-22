#!/usr/bin/env python3
"""Adds ?v=<content hash> to every local image in README.md, so GitHub's image cache
fetches a fresh copy whenever a picture changes (same name, new content).
Run after rebuilding cards:  python3 scripts/stamp_readme.py
"""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
readme = ROOT / "README.md"
text = readme.read_text()

def stamp(m):
    attr, path = m.group(1), m.group(2)
    f = ROOT / path.lstrip("./")
    if not f.is_file():
        return m.group(0)
    v = hashlib.sha1(f.read_bytes()).hexdigest()[:8]
    return f'{attr}="{path}?v={v}"'

new = re.sub(r'(src|srcset)="(\./[^"?]+\.(?:svg|webp|png|gif|jpe?g))(?:\?v=[\w]+)?"', stamp, text)
readme.write_text(new)
print(len(re.findall(r'\?v=', new)), "images stamped")
