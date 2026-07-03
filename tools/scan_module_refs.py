#!/usr/bin/env python3
from pathlib import Path

mods = Path(r"C:/Users/User/AppData/Local/Temp/srv_modules")
for f in mods.glob("*.lua"):
    t = f.read_bytes().decode("gbk", "replace")
    for i, l in enumerate(t.splitlines(), 1):
        if "heroesBattleOver" in l or "manaPool" in l:
            print(f"{f.name}:{i}:{l.strip()[:120]}")
