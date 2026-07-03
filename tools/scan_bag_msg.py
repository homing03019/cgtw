#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

KEYWORDS = ["背包整理", "整理完毕", "整理完畢", "包包自动", "清理完毕", "/zl"]
ROOT = Path(r"C:/Users/User/AppData/Local/Temp/cgmsv_scan")
ROOT.mkdir(parents=True, exist_ok=True)
OUT = Path(r"C:/Users/User/AppData/Local/Temp/bag_msg_hits.txt")

subprocess.run(
    ["scp", "-r", "cgmsv-server:/cgmsv_26.5c/gmsv/lua/", str(ROOT / "lua")],
    check=True,
)

lines_out = []
for path in (ROOT / "lua").rglob("*"):
    if path.suffix.lower() not in {".lua", ".txt"}:
        continue
    raw = path.read_bytes()
    for enc in ("gbk", "utf-8", "big5"):
        try:
            text = raw.decode(enc)
            break
        except Exception:
            text = ""
    for kw in KEYWORDS:
        if kw in text:
            rel = path.relative_to(ROOT)
            for i, line in enumerate(text.splitlines(), 1):
                if kw in line:
                    lines_out.append(f"{rel}:{i}: {line.strip()}")

OUT.write_text("\n".join(sorted(set(lines_out))), encoding="utf-8")
print(f"wrote {len(lines_out)} hits to {OUT}")
