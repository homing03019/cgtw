#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Silence battle-end '背包整理完毕' message from packagesort.lua."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_LUA = "/cgmsv_26.5c/gmsv/lua/Module/packagesort.lua"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")

OLD = '\t\t\tNLG.SystemMessage(player,"背包整理完毕。");'
NEW = "\t\t\t-- bag sort notice silenced"


def patch(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if OLD in text:
        return text.replace(OLD, NEW, 1)
    if "bag sort notice silenced" in text:
        print("already patched")
        return text
    raise SystemExit("packagesort message line not found")


def write_gbk(path: Path, text: str) -> None:
    path.write_bytes(text.encode("gbk") + b"\n")


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
    local = TEMP / "packagesort_live.lua"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_LUA}", str(local)], check=True)
    text = patch(local.read_bytes().decode("gbk"))
    out = TEMP / "packagesort_silent.lua"
    write_gbk(out, text)
    deploy(out)
    print("deployed packagesort.lua (silenced bag sort notice)")
    restart()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
