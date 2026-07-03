#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix mana pool menu left alignment and toggle not working."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_MODULES = "/cgmsv_26.5c/gmsv/lua/Modules"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
REPO_MIRROR = Path(r"D:/cgtw/server_mirror/lua/modules")

HEROES_REPLACEMENTS = [
    (
        """function Module:getPoolMenuData(charIndex)
  local lpPool = tonumber(Field.Get(charIndex, 'LpPool')) or 0
  local fpPool = tonumber(Field.Get(charIndex, 'FpPool')) or 0
  local enabled = self:isPoolEnabled(charIndex)
  local stateText = enabled and '已开启' or '已关闭'
  local title = string.format('血魔池\\n血池剩余: %d LP\\n魔池剩余: %d FP\\n自动补血魔: %s', lpPool, fpPool, stateText)
  local options = {}
  if enabled then
    table.insert(options, NLG.c('关闭自动补血魔'))
  else
    table.insert(options, NLG.c('开启自动补血魔'))
  end
  table.insert(options, NLG.c('返回'))
  return title, options
end""",
        """function Module:getPoolMenuData(charIndex)
  local lpPool = tonumber(Field.Get(charIndex, 'LpPool')) or 0
  local fpPool = tonumber(Field.Get(charIndex, 'FpPool')) or 0
  local enabled = self:isPoolEnabled(charIndex)
  local stateText = enabled and '已开启' or '已关闭'
  local title = string.format('血池:%d LP  魔池:%d FP  自动补血魔:%s', lpPool, fpPool, stateText)
  local options = {}
  if enabled then
    table.insert(options, '关闭自动补血魔')
  else
    table.insert(options, '开启自动补血魔')
  end
  table.insert(options, '返回')
  return title, options
end""",
    ),
]

BAGSWITCH_REPLACEMENTS = [
    (
        '        NLG.c("血魔池"),',
        '        "血魔池",',
    ),
    (
        """function BagSwitch:onPoolMenu(ch, selection, buttonClick)
    if buttonClick == CONST.BUTTON_关闭 or buttonClick == CONST.BUTTON_否 then
        return
    end
    if selection == 2 then
        return
    end
    local pool = getModule('manaPool')
    if not pool or not pool.handlePoolMenu then
        return
    end
    if pool:handlePoolMenu(ch.charaIndex, selection) then
        self:OpenPoolMenu(ch)
    end
end""",
        """function BagSwitch:onPoolMenu(ch, selection, buttonClick)
    if buttonClick == CONST.BUTTON_关闭 then
        return
    end
    if not selection or selection <= 0 then
        return
    end
    if selection == 2 then
        return
    end
    local pool = getModule('manaPool')
    if not pool or not pool.handlePoolMenu then
        return
    end
    if pool:handlePoolMenu(ch.charaIndex, selection) then
        self:OpenPoolMenu(ch)
    end
end""",
    ),
]


def apply_replacements(text: str, pairs: list[tuple[str, str]], label: str) -> str:
    text = text.replace("\r\n", "\n")
    changed = False
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new, 1)
            changed = True
        elif new in text:
            continue
        else:
            raise SystemExit(f"{label}: expected block not found")
    if not changed:
        print(f"{label}: already patched")
    return text


def write_gbk(path: Path, text: str) -> None:
    path.write_bytes(text.encode("gbk") + b"\n")


def deploy(path: Path, name: str) -> None:
    subprocess.run(["scp", str(path), f"{REMOTE}:{REMOTE_MODULES}/{name}"], check=True)


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
    heroes_in = TEMP / "heroesBattleOver_live.lua"
    bagswitch_in = TEMP / "bagSwitch_live.lua"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_MODULES}/heroesBattleOver.lua", str(heroes_in)], check=True)
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_MODULES}/bagSwitch.lua", str(bagswitch_in)], check=True)

    heroes_text = apply_replacements(heroes_in.read_bytes().decode("gbk"), HEROES_REPLACEMENTS, "heroesBattleOver")
    bagswitch_text = apply_replacements(bagswitch_in.read_bytes().decode("gbk"), BAGSWITCH_REPLACEMENTS, "bagSwitch")

    heroes_out = TEMP / "heroesBattleOver_ui_fix.lua"
    bagswitch_out = TEMP / "bagSwitch_ui_fix.lua"
    write_gbk(heroes_out, heroes_text)
    write_gbk(bagswitch_out, bagswitch_text)

    REPO_MIRROR.mkdir(parents=True, exist_ok=True)
    write_gbk(REPO_MIRROR / "heroesBattleOver.lua", heroes_text)
    write_gbk(REPO_MIRROR / "bagSwitch.lua", bagswitch_text)

    deploy(heroes_out, "heroesBattleOver.lua")
    deploy(bagswitch_out, "bagSwitch.lua")
    print("deployed UI alignment + toggle fix")
    restart()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
