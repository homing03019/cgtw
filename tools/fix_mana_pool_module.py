#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix corrupted CONST refs in heroesBattleOver.lua (manaPool module)."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_LUA = "/cgmsv_26.5c/gmsv/lua/Modules/heroesBattleOver.lua"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
LOCAL = TEMP / "heroesBattleOver.lua"
OUT = TEMP / "heroesBattleOver.fixed.lua"

REPLACEMENTS = [
    ("%对象_交易开关%", "CONST.对象_交易开关"),
    ("%道具_价格%", "CONST.道具_价格"),
]


def patch(text: str) -> str:
    changed = False
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new)
            changed = True
    if not changed and "CONST.对象_交易开关" in text:
        print("already fixed")
        return text
    if not changed:
        raise SystemExit("expected corruption patterns not found")
    # remove duplicate return left from prior silent-heal patch
    text = text.replace("    return\n    return\n", "    return\n", 1)
    return text


def deploy(path: Path) -> None:
    subprocess.run(["scp", str(path), f"{REMOTE}:{REMOTE_LUA}"], check=True)


def restart() -> None:
    trigger = Path(r"C:/Users/User/.cursor/skills/cgmsv-restart/scripts/trigger_desktop_restart.ps1")
    subprocess.run(["scp", str(trigger), f"{REMOTE}:/cgmsv_26.5c/tools/trigger_desktop_restart.ps1"], check=True)
    subprocess.run(
        [
            "ssh",
            REMOTE,
            "powershell -NoProfile -ExecutionPolicy Bypass -File C:/cgmsv_26.5c/tools/trigger_desktop_restart.ps1",
        ],
        check=True,
    )


def main() -> int:
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_LUA}", str(LOCAL)], check=True)
    text = LOCAL.read_bytes().decode("gbk")
    fixed = patch(text)
    OUT.write_bytes(fixed.encode("gbk") + b"\n")
    deploy(OUT)
    print("deployed heroesBattleOver.lua")
    restart()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
