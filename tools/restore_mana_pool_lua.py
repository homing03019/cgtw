#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore heroesBattleOver.lua (manaPool) from pre-patch baseline + minimal safe edits."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_LUA = "/cgmsv_26.5c/gmsv/lua/Modules/heroesBattleOver.lua"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")

# Original heal() empty-pool guard (before silent-heal patch broke syntax)
HEAL_BROKEN = """  if lpPool <= 0 and fpPool <= 0 then
    return
    return
  end"""

HEAL_FIXED = """  if lpPool <= 0 and fpPool <= 0 then
    return
  end"""

# Optional: restore original message instead of silent (uncomment if preferred)
# HEAL_FIXED = """  if lpPool <= 0 and fpPool <= 0 then
#     NLG.SystemMessage(charIndex, '[血魔池] 血池或魔池余量不足。')
#     return
#   end"""

POOL_STATUS = """

function Module:getPoolStatusText(charIndex)
  local lpPool = tonumber(Field.Get(charIndex, 'LpPool')) or 0
  local fpPool = tonumber(Field.Get(charIndex, 'FpPool')) or 0
  return string.format('[血魔池] 血池剩余: %d LP | 魔池剩余: %d FP', lpPool, fpPool)
end

function Module:showPoolStatus(charIndex)
  NLG.SystemMessage(charIndex, self:getPoolStatusText(charIndex))
end
"""


def patch(text: str) -> str:
    text = text.replace("\r\n", "\n")
    broken = """  if lpPool <= 0 and fpPool <= 0 then
    return
    return
  end"""
    fixed = """  if lpPool <= 0 and fpPool <= 0 then
    return
  end"""
    if broken in text:
        text = text.replace(broken, fixed, 1)
    elif "    return\n    return\n" in text:
        text = text.replace("    return\n    return\n", "    return\n", 1)

    # Ensure bag menu helpers exist (minimal addition on top of original module)
    if "function Module:getPoolStatusText" not in text:
        anchor = "function Module:heal(charIndex,targetIndex)"
        if anchor not in text:
            raise SystemExit("heal() anchor missing")
        text = text.replace(anchor, POOL_STATUS + anchor, 1)

    # Fix any CONST template corruption if present
    for old, new in {
        "%对象_交易开关%": "CONST.对象_交易开关",
        "%道具_价格%": "CONST.道具_价格",
    }.items():
        text = text.replace(old, new)

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
    local = TEMP / "heroesBattleOver_broken.lua"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_LUA}", str(local)], check=True)
    text = local.read_bytes().decode("gbk")
    fixed = patch(text)
    out = TEMP / "heroesBattleOver_restored.lua"
    out.write_bytes(fixed.encode("gbk") + b"\n")
    deploy(out)
    restart()
    (TEMP / "restore_mana_pool.txt").write_text("deployed heroesBattleOver restored heal syntax\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
