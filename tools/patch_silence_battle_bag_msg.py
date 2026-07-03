#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Silence battle-end auto bag cleanup popup/messages in manaPool."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_LUA = "/cgmsv_26.5c/gmsv/lua/Modules/heroesBattleOver.lua"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
REPO_MIRROR = Path(r"D:/cgtw/server_mirror/lua/modules")

REPLACEMENTS = [
    (
        '      NLG.Say(charIndex,-1,"检测到你开启了交易，战斗后包包自动清理完毕。",1,3);',
        "      -- auto bag cleanup notice silenced",
    ),
    (
        '      NLG.SystemMessage(charIndex, targetName.."魔石已售出，获得【" .. price*soldrate .. "】魔币。");',
        "      -- magic stone sold notice silenced",
    ),
    (
        '      NLG.SystemMessage(charIndex, "钱包满了！");',
        "      -- wallet full notice silenced",
    ),
]


def patch(text: str) -> str:
    text = text.replace("\r\n", "\n")
    changed = False
    for old, new in REPLACEMENTS:
        if old in text:
            text = text.replace(old, new, 1)
            changed = True
    if not changed:
        if "auto bag cleanup notice silenced" in text:
            print("already patched")
        else:
            raise SystemExit("expected message lines not found")
    return text


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
    local = TEMP / "heroesBattleOver_live.lua"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_LUA}", str(local)], check=True)
    text = patch(local.read_bytes().decode("gbk"))
    out = TEMP / "heroesBattleOver_silent.lua"
    write_gbk(out, text)
    REPO_MIRROR.mkdir(parents=True, exist_ok=True)
    write_gbk(REPO_MIRROR / "heroesBattleOver.lua", text)
    deploy(out)
    print("deployed heroesBattleOver.lua (silenced battle bag notices)")
    restart()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
