#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import tempfile
from pathlib import Path

root = Path(tempfile.mkdtemp())
subprocess.run(["scp", "-r", "cgmsv-server:/cgmsv_26.5c/gmsv/lua/", str(root / "lua")], check=True)
kw = "背包整理"
out = Path(r"C:/Users/User/AppData/Local/Temp/bag_sort_all_hits.txt")
lines = []
for p in (root / "lua").rglob("*"):
    if p.suffix.lower() != ".lua":
        continue
    try:
        text = p.read_bytes().decode("gbk")
    except Exception:
        continue
    if kw not in text:
        continue
    rel = p.relative_to(root)
    for i, line in enumerate(text.splitlines(), 1):
        if kw in line:
            lines.append(f"{rel}:{i}: {line.strip()}")
out.write_text("\n".join(lines), encoding="utf-8")
print(len(lines))
