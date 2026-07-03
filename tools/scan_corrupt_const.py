#!/usr/bin/env python3
import re
import subprocess
from pathlib import Path

TEMP = Path(r"C:/Users/User/AppData/Local/Temp/srv_modules_fix")
subprocess.run(["scp", "-r", "cgmsv-server:/cgmsv_26.5c/gmsv/lua/Modules/*.lua", str(TEMP)], check=True)
pat = re.compile(r"(?<![\"'])%([\u4e00-\u9fff\w_]+%)")
bad = []
for f in TEMP.glob("*.lua"):
    t = f.read_bytes().decode("gbk", "replace")
    for i, l in enumerate(t.splitlines(), 1):
        if pat.search(l):
            bad.append(f"{f.name}:{i}:{l.strip()[:100]}")
Path(r"C:/Users/User/AppData/Local/Temp/corrupt_after.txt").write_text(
    "\n".join(bad) if bad else "none", encoding="utf-8"
)
print(len(bad))
