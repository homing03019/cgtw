#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add mana pool on/off toggle and backpack sub-page UI (bagSwitch + manaPool)."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_MODULES = "/cgmsv_26.5c/gmsv/lua/Modules"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
REPO_MIRROR = Path(r"D:/cgtw/server_mirror/lua/modules")

POOL_TOGGLE_BLOCK = """
local POOL_ENABLED_FIELD = 'PoolEnabled'

function Module:isPoolEnabled(charIndex)
  local v = Field.Get(charIndex, POOL_ENABLED_FIELD)
  if v == nil or v == '' then
    return true
  end
  return v == '1'
end

function Module:setPoolEnabled(charIndex, enabled)
  Field.Set(charIndex, POOL_ENABLED_FIELD, enabled and '1' or '0')
end

"""

POOL_STATUS_OLD = """function Module:getPoolStatusText(charIndex)
  local lpPool = tonumber(Field.Get(charIndex, 'LpPool')) or 0
  local fpPool = tonumber(Field.Get(charIndex, 'FpPool')) or 0
  return string.format('[血魔池] 血池剩余: %d LP | 魔池剩余: %d FP', lpPool, fpPool)
end

function Module:showPoolStatus(charIndex)
  NLG.SystemMessage(charIndex, self:getPoolStatusText(charIndex))
end"""

POOL_STATUS_NEW = """function Module:getPoolStatusText(charIndex)
  local lpPool = tonumber(Field.Get(charIndex, 'LpPool')) or 0
  local fpPool = tonumber(Field.Get(charIndex, 'FpPool')) or 0
  local state = self:isPoolEnabled(charIndex) and '开启' or '关闭'
  return string.format('[血魔池] 血池剩余: %d LP | 魔池剩余: %d FP | 自动补血魔: %s', lpPool, fpPool, state)
end

function Module:showPoolStatus(charIndex)
  NLG.SystemMessage(charIndex, self:getPoolStatusText(charIndex))
end

function Module:getPoolMenuData(charIndex)
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
end

function Module:handlePoolMenu(charIndex, selection)
  if selection == 1 then
    local enabled = self:isPoolEnabled(charIndex)
    self:setPoolEnabled(charIndex, not enabled)
    local msg = (not enabled) and '开启' or '关闭'
    NLG.SystemMessage(charIndex, '[血魔池] 自动补血魔已' .. msg)
    return true
  end
  return false
end"""

HEAL_ANCHOR = "function Module:heal(charIndex,targetIndex)\n  local name = Char.GetData(targetIndex,CONST.CHAR_名字)"
HEAL_GUARD = """function Module:heal(charIndex,targetIndex)
  if not self:isPoolEnabled(charIndex) then
    return
  end
  local name = Char.GetData(targetIndex,CONST.CHAR_名字)"""


def patch_heroes(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if "function Module:isPoolEnabled" not in text:
        anchor = "function Module:getPoolStatusText(charIndex)"
        if anchor not in text:
            raise SystemExit("getPoolStatusText anchor missing in heroesBattleOver.lua")
        text = text.replace(anchor, POOL_TOGGLE_BLOCK + anchor, 1)

    if "function Module:getPoolMenuData" not in text:
        if POOL_STATUS_OLD in text:
            text = text.replace(POOL_STATUS_OLD, POOL_STATUS_NEW, 1)
        elif "function Module:getPoolMenuData" not in text:
            raise SystemExit("pool status block not found for replacement")

    if "if not self:isPoolEnabled(charIndex)" not in text:
        if HEAL_ANCHOR not in text:
            raise SystemExit("heal() anchor missing")
        text = text.replace(HEAL_ANCHOR, HEAL_GUARD, 1)

    for old, new in {
        "%对象_交易开关%": "CONST.对象_交易开关",
        "%道具_价格%": "CONST.道具_价格",
        "    return\n    return\n": "    return\n",
    }.items():
        text = text.replace(old, new)

    return text


def patch_bagswitch(text: str) -> str:
    text = text.replace("\r\n", "\n")

    text = text.replace(
        'local POOL_STATUS = 3;',
        'local POOL_MENU = 3;',
        1,
    )

    text = text.replace(
        'NLG.c("血魔池状态"),',
        'NLG.c("血魔池"),',
        1,
    )

    old_onmenu_pool = """    if selection == 3 then
        local pool = getModule('manaPool')
        if pool and pool.showPoolStatus then
            pool:showPoolStatus(ch.charaIndex)
        else
            NLG.SystemMessage(ch.charaIndex, '[血魔池] 模块未加载')
        end
    end"""

    new_onmenu_pool = """    if selection == 3 then
        self:OpenPoolMenu(ch)
        return
    end"""

    if old_onmenu_pool in text:
        text = text.replace(old_onmenu_pool, new_onmenu_pool, 1)
    elif "function BagSwitch:OpenPoolMenu" not in text:
        raise SystemExit("bagSwitch onMenu pool block not found")

    if "function BagSwitch:OpenPoolMenu" not in text:
        insert_after = """function BagSwitch:OpenMenu(charIndex)
    local ch = self:Chara(charIndex);
    ch[CONST.对象_WindowBuffer2] = 1;
    local menu = self:NPC_buildSelectionText("背包管理", {
        "切换背包",
        "移动物品",
        NLG.c("血魔池"),
    })
    NLG.ShowWindowTalked(charIndex, self.dummyNPC,
        CONST.窗口_选择框, CONST.BUTTON_确定关闭,
        0, menu);
end"""

        pool_menu_funcs = """

function BagSwitch:OpenPoolMenu(ch)
    local pool = getModule('manaPool')
    if not pool or not pool.getPoolMenuData then
        NLG.SystemMessage(ch.charaIndex, '[血魔池] 模块未加载')
        return
    end
    local title, options = pool:getPoolMenuData(ch.charaIndex)
    ch:ShowWindowTalked(self.dummyNPC,
        self:NPC_buildSelectionText(title, options),
        {
            button = CONST.BUTTON_关闭,
            type = CONST.窗口_选择框,
            seqNo = POOL_MENU,
        })
end

function BagSwitch:onPoolMenu(ch, selection, buttonClick)
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
end
"""
        if insert_after not in text:
            raise SystemExit("OpenMenu block not found in bagSwitch.lua")
        text = text.replace(insert_after, insert_after + pool_menu_funcs, 1)

    window_handler = """    if seqNo == BAG_LIST2 then
        self:onSelectedMoveBag(ch, line, btnClick);
    end
end"""

    new_window_handler = """    if seqNo == BAG_LIST2 then
        self:onSelectedMoveBag(ch, line, btnClick);
    end
    if seqNo == POOL_MENU then
        self:onPoolMenu(ch, line, btnClick);
    end
end"""

    if "if seqNo == POOL_MENU then" not in text:
        if window_handler not in text:
            raise SystemExit("onWindowTalked handler anchor missing")
        text = text.replace(window_handler, new_window_handler, 1)

    return text


def write_gbk(path: Path, text: str) -> None:
    path.write_bytes(text.encode("gbk") + b"\n")


def deploy(local: Path, remote_name: str) -> None:
    subprocess.run(
        ["scp", str(local), f"{REMOTE}:{REMOTE_MODULES}/{remote_name}"],
        check=True,
    )


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
    heroes_local = TEMP / "heroesBattleOver_live.lua"
    bagswitch_local = TEMP / "bagSwitch_live.lua"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_MODULES}/heroesBattleOver.lua", str(heroes_local)], check=True)
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_MODULES}/bagSwitch.lua", str(bagswitch_local)], check=True)

    heroes_out = TEMP / "heroesBattleOver_pool_toggle.lua"
    bagswitch_out = TEMP / "bagSwitch_pool_toggle.lua"

    heroes_text = patch_heroes(heroes_local.read_bytes().decode("gbk"))
    bagswitch_text = patch_bagswitch(bagswitch_local.read_bytes().decode("gbk"))

    write_gbk(heroes_out, heroes_text)
    write_gbk(bagswitch_out, bagswitch_text)

    REPO_MIRROR.mkdir(parents=True, exist_ok=True)
    write_gbk(REPO_MIRROR / "heroesBattleOver.lua", heroes_text)
    write_gbk(REPO_MIRROR / "bagSwitch.lua", bagswitch_text)

    deploy(heroes_out, "heroesBattleOver.lua")
    deploy(bagswitch_out, "bagSwitch.lua")
    print("deployed heroesBattleOver.lua + bagSwitch.lua")
    restart()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
