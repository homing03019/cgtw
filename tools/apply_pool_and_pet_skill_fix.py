#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deploy: pet skill learn filter + silent battle pool + bag pool status."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:/cgtw")
REMOTE = "cgmsv-server"
GMSV = "/cgmsv_26.5c/gmsv"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")

PET_SUMMON = ROOT / "server_mirror/lua/modules/petSummonContract.lua"
MANA_POOL = TEMP / "heroesBattleOver.lua"
BAG_SWITCH = TEMP / "bagSwitch.lua"

REMOTE_PET = f"{GMSV}/lua/Modules/petSummonContract.lua"
REMOTE_MANA = f"{GMSV}/lua/Modules/heroesBattleOver.lua"
REMOTE_BAG = f"{GMSV}/lua/Modules/bagSwitch.lua"

# --- petSummonContract patches (ASCII-safe markers + GBK via bytes) ---

PET_SKILL_BLOCK = """local PET_SKILL_LEARN_COL = 10
local PET_SKILL_FIELD_COL = 6

function Module:loadPetSkillLearnFlags()
  self.petSkillLearnFlags = {}
  local path = './data/skill.txt'
  local f = io.open(path, 'r')
  if f == nil then
    self:logInfo('skill.txt missing, pet skill filter disabled')
    return
  end
  local text = f:read('*a')
  f:close()
  for line in string.gmatch(text, '[^\\r\\n]+') do
    local parts = {}
    for part in string.gmatch(line, '[^\\t]+') do
      table.insert(parts, part)
    end
    if #parts >= PET_SKILL_LEARN_COL then
      local skillId = tonumber(parts[2])
      local fieldFlag = tonumber(parts[PET_SKILL_FIELD_COL]) or 0
      local learnFlag = tonumber(parts[PET_SKILL_LEARN_COL]) or 0
      if skillId ~= nil then
        -- 0/2: 战斗或宠物共用; 4: 补血/辅助; 排除 3 玩家专用与 field>=5
        if (learnFlag == 0 or learnFlag == 2 or learnFlag == 4) and fieldFlag < 5 then
          self.petSkillLearnFlags[skillId] = true
        end
      end
    end
  end
end

function Module:isPetLearnableSkill(skillId)
  skillId = tonumber(skillId)
  if skillId == nil then
    return false
  end
  if skillId >= 991 and skillId <= 995 then
    return true
  end
  if skillId == 73 or skillId == 74 then
    return true
  end
  if self.petSkillLearnFlags == nil then
    self:loadPetSkillLearnFlags()
  end
  return self.petSkillLearnFlags[skillId] == true
end
"""

PET_ONLOAD_OLD = "  self:buildEnemyMaps()"
PET_ONLOAD_NEW = """  self:loadPetSkillLearnFlags()
  self:buildEnemyMaps()"""

BUILD_CAND_OLD = """        if not seen[skillId] then
          seen[skillId] = true
          table.insert(candidates, skillId)
        end"""

BUILD_CAND_NEW = """        if not seen[skillId] and self:isPetLearnableSkill(skillId) then
          seen[skillId] = true
          table.insert(candidates, skillId)
        end"""

TRY_ADD_OLD = """  skillId = tonumber(skillId)
  if skillId == nil then
    return nil
  end
  local level"""

TRY_ADD_NEW = """  skillId = tonumber(skillId)
  if skillId == nil then
    return nil
  end
  if not self:isPetLearnableSkill(skillId) then
    return nil
  end
  local level"""


def patch_pet_summon(text: str) -> str:
    if "function Module:isPetLearnableSkill" not in text:
        anchor = "local CONTRACT_PROXY_TO_TECH = {"
        if anchor not in text:
            raise SystemExit("petSummonContract anchor missing")
        text = text.replace(anchor, PET_SKILL_BLOCK + "\n" + anchor, 1)
    if PET_ONLOAD_OLD in text and "loadPetSkillLearnFlags" not in text.split("onLoad")[1][:400]:
        text = text.replace(PET_ONLOAD_OLD, PET_ONLOAD_NEW, 1)
    if BUILD_CAND_OLD in text:
        text = text.replace(BUILD_CAND_OLD, BUILD_CAND_NEW, 1)
    if TRY_ADD_OLD in text:
        text = text.replace(TRY_ADD_OLD, TRY_ADD_NEW, 1)
    # trim archetype pools that only grant player skills
    text = text.replace(
        "self:appendUnique(names, 'heal', 'clean', 'def_magic', 'elem_def')",
        "self:appendUnique(names, 'def_magic', 'earth', 'water', 'fire', 'wind')",
        1,
    )
    text = text.replace(
        "self:appendUnique(names, 'aoe_magic', 'curse', 'elem_attack', 'earth', 'water', 'fire', 'wind')",
        "self:appendUnique(names, 'aoe_magic', 'curse', 'earth', 'water', 'fire', 'wind')",
        1,
    )
    text = text.replace(
        "self:appendUnique(names, 'aoe_magic', 'elem_attack', 'earth', 'water', 'fire', 'wind', 'atk_buff', 'elem_def')",
        "self:appendUnique(names, 'aoe_magic', 'earth', 'water', 'fire', 'wind', 'atk_buff', 'def_magic')",
        1,
    )
    text = text.replace(
        "self:appendUnique(names, 'heal', 'def_magic', 'clean', 'elem_def')",
        "self:appendUnique(names, 'def_magic', 'earth', 'water', 'fire', 'wind')",
        1,
    )
    text = text.replace(
        "self:appendUnique(names, 'heal', 'def_magic', 'elem_def', 'clean')",
        "self:appendUnique(names, 'def_magic', 'earth', 'water', 'fire', 'wind')",
        1,
    )
    return text


def patch_mana_pool(text: str) -> str:
    if "function Module:getPoolStatusText" not in text:
        insert = """

function Module:getPoolStatusText(charIndex)
  local lpPool = tonumber(Field.Get(charIndex, 'LpPool')) or 0
  local fpPool = tonumber(Field.Get(charIndex, 'FpPool')) or 0
  return string.format('[血魔池] 血池剩余: %d LP | 魔池剩余: %d FP', lpPool, fpPool)
end

function Module:showPoolStatus(charIndex)
  NLG.SystemMessage(charIndex, self:getPoolStatusText(charIndex))
end
"""
        text = text.replace("function Module:heal(charIndex,targetIndex)", insert + "function Module:heal(charIndex,targetIndex)", 1)

    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_heal = False
    for line in lines:
        if line.startswith("function Module:heal("):
            in_heal = True
        elif in_heal and line.startswith("function Module:"):
            in_heal = False
        if in_heal and "NLG.SystemMessage(charIndex, '[血魔池]" in line:
            if "不够" in line:
                out.append("    return\n")
            continue
        out.append(line)
    return "".join(out)


def patch_bag_switch(text: str) -> str:
    if "血魔池状态" in text and "selection == 3" in text:
        return text
    text = text.replace("\r\n", "\n")
    if "血魔池状态" not in text:
        lines = text.split("\n")
        out: list[str] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.strip() == '"移动物品"' and i + 1 < len(lines) and lines[i + 1].strip() == "})":
                out.append(line + ",")
                out.append('        NLG.c("血魔池状态"),')
                out.append(lines[i + 1])
                i += 2
                continue
            out.append(line)
            i += 1
        text = "\n".join(out)
    if "selection == 3" not in text:
        text = text.replace(
            """    if selection == 2 then
        ch[CONST.对象_WindowBuffer2] = 0;
        self:onMoveItem(ch, 10, -1);
    end
end

---@param ch CharaWrapper
---@param selection number
---@param buttonClick number
function BagSwitch:onSwitchBag""",
            """    if selection == 2 then
        ch[CONST.对象_WindowBuffer2] = 0;
        self:onMoveItem(ch, 10, -1);
        return
    end
    if selection == 3 then
        local pool = getModule('manaPool')
        if pool and pool.showPoolStatus then
            pool:showPoolStatus(ch.charaIndex)
        else
            NLG.SystemMessage(ch.charaIndex, '[血魔池] 模块未加载')
        end
    end
end

---@param ch CharaWrapper
---@param selection number
---@param buttonClick number
function BagSwitch:onSwitchBag""",
            1,
        )
    return text


def fetch_remote() -> None:
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_MANA}", str(MANA_POOL)], check=True)
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_BAG}", str(BAG_SWITCH)], check=True)


def deploy(path: Path, remote: str) -> None:
    subprocess.run(["scp", str(path), f"{REMOTE}:{remote}"], check=True)


def restart_server() -> None:
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
    fetch_remote()

    pet = PET_SUMMON.read_bytes().decode("gbk")
    pet = patch_pet_summon(pet)
    pet_out = TEMP / "petSummonContract.patched.lua"
    pet_out.write_bytes(pet.encode("gbk") + b"\n")
    PET_SUMMON.write_bytes(pet_out.read_bytes())

    mana = MANA_POOL.read_bytes().decode("gbk")
    mana = patch_mana_pool(mana)
    mana_out = TEMP / "heroesBattleOver.patched.lua"
    mana_out.write_bytes(mana.encode("gbk") + b"\n")

    bag = BAG_SWITCH.read_bytes().decode("gbk")
    bag = patch_bag_switch(bag)
    bag_out = TEMP / "bagSwitch.patched.lua"
    bag_out.write_bytes(bag.encode("gbk") + b"\n")

    deploy(pet_out, REMOTE_PET)
    deploy(mana_out, REMOTE_MANA)
    deploy(bag_out, REMOTE_BAG)
    print("deployed petSummonContract.lua, heroesBattleOver.lua, bagSwitch.lua")
    restart_server()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
