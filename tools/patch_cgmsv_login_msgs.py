#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Blank out cgmsv.exe login channel announcement strings (GBK)."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(r"D:/cgtw")
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
REMOTE = "cgmsv-server"
REMOTE_EXE = "/cgmsv_26.5c/gmsv/cgmsv.exe"

# Prefixes found in cgmsv.exe; patch full GBK string until null or non-gbk
PREFIXES = [
    "您已进入新手频道".encode("gbk"),
    "您已进入职业频道".encode("gbk"),
    "!内容".encode("gbk"),
    "!内容 ".encode("gbk"),
]


def blank_string_at(data: bytearray, start: int, max_len: int = 120) -> int:
    end = start
    while end < min(len(data), start + max_len):
        b = data[end]
        if b == 0:
            break
        if b < 0x20 and b not in (0x0A, 0x0D):
            break
        end += 1
    length = end - start
    if length <= 0:
        return 0
    for i in range(start, end):
        data[i] = 0x20  # space
    return length


def patch_exe(data: bytearray) -> list[str]:
    log: list[str] = []
    seen: set[int] = set()
    for prefix in PREFIXES:
        off = 0
        while True:
            idx = data.find(prefix, off)
            if idx < 0:
                break
            if idx not in seen:
                n = blank_string_at(data, idx)
                if n:
                    log.append(f"blanked @{idx} len={n} prefix={prefix[:12]!r}")
                    seen.add(idx)
            off = idx + 1
    return log


def main() -> int:
    local = TEMP / "cgmsv.exe"
    if not local.exists():
        subprocess.run(["scp", f"{REMOTE}:{REMOTE_EXE}", str(local)], check=True)
    backup = TEMP / "cgmsv.exe.bak_login_msgs"
    shutil.copy2(local, backup)
    data = bytearray(local.read_bytes())
    log = patch_exe(data)
    out = TEMP / "cgmsv_patched.exe"
    out.write_bytes(data)
    subprocess.run(["scp", str(out), f"{REMOTE}:{REMOTE_EXE}"], check=True)
    print(f"patched {len(log)} strings")
    for line in log:
        print(" ", line)
    print("restart cgmsv required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
