#!/usr/bin/env python3
from pathlib import Path

text = Path(r"C:/Users/User/AppData/Local/Temp/tech.txt").read_bytes().decode("gbk", "replace")
lines = [l for l in text.splitlines() if "气功" in l or "活杀" in l]
Path(r"C:/Users/User/AppData/Local/Temp/qigong_all.txt").write_text("\n".join(lines[:40]), encoding="utf-8")
# tech index = line number? print first few cols
for line in lines[:15]:
    parts = line.split("\t")
    print("|".join(parts[:8]))
