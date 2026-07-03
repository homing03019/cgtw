#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch contract summon: skill count 1-4, AOE by str/mag, random slots 6-10, display fix."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_LUA = "/cgmsv_26.5c/gmsv/lua/Modules/petSummonContract.lua"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
LOCAL = TEMP / "petSummonContract.lua"
OUT = TEMP / "petSummonContract.patched.lua"

# --- insert slot constants after BOSS_SKILL_LEVEL_MAX block ---
SLOT_CONST_OLD = """local BOSS_SKILL_LEVEL_MAX = 10
local BOW_ATTACK_STYLE = 4"""

SLOT_CONST_NEW = """local BOSS_SKILL_LEVEL_MAX = 10
local SUMMON_SKILL_SLOT_MIN = 6
local SUMMON_SKILL_SLOT_MAX = 10
local BOW_ATTACK_STYLE = 4"""

COMMENT_OLD = "-- 召唤自带 0-3 个战斗宠技（普通 Lv3-8 / Boss Lv4-10），依五围分配"
COMMENT_NEW = "-- 召唤自带 1-4 个战斗宠技（普通 Lv3-8 / Boss Lv4-10），依五围分配；技能栏 6-10 随机"

ASSIGN_SLOTS_FN = """
function Module:assignRandomSkillSlots(petIndex)
  local slots = math.random(SUMMON_SKILL_SLOT_MIN, SUMMON_SKILL_SLOT_MAX)
  Char.SetData(petIndex, CONST.PET_技能栏, slots)
  return slots
end

function Module:getContractSkillDisplayName(skillId, techId, level)
  skillId = tonumber(skillId)
  local contractNames = {
    [991] = '契约震波',
    [992] = '契约秘法·陨石',
    [993] = '契约秘法·冰冻',
    [994] = '契约秘法·火焰',
    [995] = '契约秘法·风刃',
  }
  if skillId and contractNames[skillId] then
    return string.format('%s Lv%d', contractNames[skillId], level)
  end
  local techName = self:getAdvancedPetTechName(techId)
  if string.find(techName, 'LV') or string.find(techName, 'Lv') or string.find(techName, '活杀') then
    return techName
  end
  return string.format('%s Lv%d', techName, level)
end

function Module:petUsesProxyTech(petIndex)
  local maxSlots = self:getPetSkillSlotCount(petIndex)
  for s = 0, maxSlots - 1 do
    local techId = Pet.GetSkill(petIndex, s)
    if techId >= 0 and CONTRACT_PROXY_TO_TECH[techId] then
      return true
    end
  end
  return false
end
"""

APPLY_GROWTH_OLD = """function Module:applyRandomGrowth(charIndex, petIndex, enemyId, isBoss)
  local arts = {
    CONST.PET_体成, CONST.PET_力成, CONST.PET_强成, CONST.PET_敏成, CONST.PET_魔成,
  }
  local targetTotal = self:rollSummonTotal(isBoss == true)
  if targetTotal <= 0 then return end
  local values = self:splitTotalRandom(targetTotal)
  for i, artType in ipairs(arts) do
    Pet.SetArtRank(petIndex, artType, values[i])
  end
  Pet.ReBirth(charIndex, petIndex)
end"""

APPLY_GROWTH_NEW = APPLY_GROWTH_OLD.replace(
    "  Pet.ReBirth(charIndex, petIndex)\nend",
    "  Pet.ReBirth(charIndex, petIndex)\n  self:assignRandomSkillSlots(petIndex)\nend",
)

PICK_ELEMENT_FN = """
function Module:pickMagicAoeSkillIdByElement(enemyId)
  local baseId = self:getEnemyBaseId(enemyId)
  if baseId == nil then
    local pool = { 992, 993, 994, 995 }
    return pool[math.random(1, #pool)]
  end
  local baseIndex = Data.EnemyBaseGetDataIndex(baseId)
  if baseIndex == nil or baseIndex < 0 then
    local pool = { 992, 993, 994, 995 }
    return pool[math.random(1, #pool)]
  end
  local attrs = {
    earth = tonumber(Data.EnemyBaseGetData(baseIndex, CONST.DATA_ENEMYBASE_EARTHAT)) or 0,
    water = tonumber(Data.EnemyBaseGetData(baseIndex, CONST.DATA_ENEMYBASE_WATERAT)) or 0,
    fire = tonumber(Data.EnemyBaseGetData(baseIndex, CONST.DATA_ENEMYBASE_FIREAT)) or 0,
    wind = tonumber(Data.EnemyBaseGetData(baseIndex, CONST.DATA_ENEMYBASE_WINDAT)) or 0,
  }
  local best = -1
  for _, val in pairs(attrs) do
    if val > best then best = val end
  end
  if best <= 0 then
    local pool = { 992, 993, 994, 995 }
    return pool[math.random(1, #pool)]
  end
  local tied = {}
  for name, val in pairs(attrs) do
    if val == best then
      table.insert(tied, MAGIC_AOE_BY_ELEMENT[name])
    end
  end
  return tied[math.random(1, #tied)]
end
"""

ENSURE_AOE_OLD = """function Module:ensureMandatoryAoeSkills(charIndex, petIndex, enemyId, isBoss, parts, granted, picked)
  local role = self:getPetAttackRole(parts)
  local bpTotal = parts[1] + parts[2] + parts[3] + parts[4] + parts[5]
  if role == 'none' then
    local total = bpTotal
    if total > 0 then
      local magicShare = parts[5] / total
      local physShare = (parts[2] + parts[4]) / total
      if physShare >= magicShare then
        role = 'physical'
      else
        role = 'magic'
      end
    end
  end
  if role == 'physical' or role == 'magic' then
    if role == 'physical' and not self:grantedHasAoeSkill(granted, self.isAoePhysicalSkillId) then
      local entry = self:tryAddPetCombatSkill(charIndex, petIndex, 991, isBoss, bpTotal)
      if entry then
        table.insert(granted, entry)
        table.insert(picked, 991)
      end
    end
    if role == 'magic' and not self:grantedHasAoeSkill(granted, self.isAoeMagicSkillId) then
      local skillId = self:pickMandatoryMagicAoeSkillId(enemyId, parts)
      if not self:skillAlreadyPicked(picked, skillId) then
        local entry = self:tryAddPetCombatSkill(charIndex, petIndex, skillId, isBoss, bpTotal)
        if entry then
          table.insert(granted, entry)
          table.insert(picked, skillId)
        end
      end
    end
  end
  if #granted > 0 then
    Pet.UpPet(charIndex, petIndex)
  end
  return granted
end"""

ENSURE_AOE_NEW = """function Module:ensureMandatoryAoeSkills(charIndex, petIndex, enemyId, isBoss, parts, granted, picked)
  local bpTotal = parts[1] + parts[2] + parts[3] + parts[4] + parts[5]
  local strength = parts[2] or 0
  local magic = parts[5] or 0
  local skillId
  if strength > magic then
    skillId = 991
  elseif magic > strength then
    skillId = self:pickMagicAoeSkillIdByElement(enemyId)
  else
    if math.random(0, 1) == 0 then
      skillId = 991
    else
      skillId = self:pickMagicAoeSkillIdByElement(enemyId)
    end
  end
  if skillId == 991 then
    if not self:grantedHasAoeSkill(granted, self.isAoePhysicalSkillId) then
      local entry = self:tryAddPetCombatSkill(charIndex, petIndex, 991, isBoss, bpTotal)
      if entry then
        table.insert(granted, entry)
        table.insert(picked, 991)
      end
    end
  else
    if not self:skillAlreadyPicked(picked, skillId)
        and not self:grantedHasAoeSkill(granted, self.isAoeMagicSkillId) then
      local entry = self:tryAddPetCombatSkill(charIndex, petIndex, skillId, isBoss, bpTotal)
      if entry then
        table.insert(granted, entry)
        table.insert(picked, skillId)
      end
    end
  end
  if #granted > 0 then
    Pet.UpPet(charIndex, petIndex)
  end
  return granted
end"""

TRY_ADD_RETURN_OLD = """  return {
    skillId = skillId,
    techId = techId,
    level = level,
    name = self:getAdvancedPetTechName(techId),
  }
end"""

TRY_ADD_RETURN_NEW = """  return {
    skillId = skillId,
    techId = techId,
    level = level,
    name = self:getContractSkillDisplayName(skillId, techId, level),
  }
end"""

GRANT_COUNT_OLD = "  local skillCount = math.random(0, 3)"
GRANT_COUNT_NEW = "  local skillCount = math.random(1, 4)"

GRANT_END_OLD = """  granted = self:ensureMandatoryAoeSkills(
    charIndex, petIndex, enemyId, isBoss, parts, granted, picked)
  return granted
end"""

GRANT_END_NEW = """  granted = self:ensureMandatoryAoeSkills(
    charIndex, petIndex, enemyId, isBoss, parts, granted, picked)
  if self:petUsesProxyTech(petIndex) then
    self:markContractSummonPet(petIndex)
  end
  Pet.UpPet(charIndex, petIndex)
  Pet.UpPet(charIndex, petIndex)
  return granted
end"""

FORMAT_SKILLS_OLD = """function Module:formatGrantedSkills(granted)
  if granted == nil or #granted == 0 then
    return ''
  end
  local parts = {}
  for i = 1, #granted do
    local g = granted[i]
    table.insert(parts, string.format('【%s】Lv%d', g.name, g.level))
  end
  return table.concat(parts, ' ')
end"""

FORMAT_SKILLS_NEW = """function Module:formatGrantedSkills(granted)
  if granted == nil or #granted == 0 then
    return ''
  end
  local parts = {}
  for i = 1, #granted do
    local g = granted[i]
    table.insert(parts, string.format('【%s】', g.name))
  end
  return table.concat(parts, ' ')
end"""

FORCE_PET_OLD = """  local grantedSkills = self:grantSummonCombatSkills(charIndex, petIndex, enemyId, isBoss)
  self:refreshPetLoyalty(charIndex, petIndex, true)
  return true, petIndex, grantedSkills
end"""

FORCE_PET_NEW = """  local grantedSkills = self:grantSummonCombatSkills(charIndex, petIndex, enemyId, isBoss)
  self:refreshPetLoyalty(charIndex, petIndex, true)
  Pet.UpPet(charIndex, petIndex)
  NLG.UpChar(charIndex)
  return true, petIndex, grantedSkills
end"""


def patch(text: str) -> str:
    text = text.replace("\r\n", "\n")
    replacements = [
        (SLOT_CONST_OLD, SLOT_CONST_NEW),
        (COMMENT_OLD, COMMENT_NEW),
        (APPLY_GROWTH_OLD, APPLY_GROWTH_NEW),
        (ENSURE_AOE_OLD, ENSURE_AOE_NEW),
        (TRY_ADD_RETURN_OLD, TRY_ADD_RETURN_NEW),
        (GRANT_COUNT_OLD, GRANT_COUNT_NEW),
        (GRANT_END_OLD, GRANT_END_NEW),
        (FORMAT_SKILLS_OLD, FORMAT_SKILLS_NEW),
        (FORCE_PET_OLD, FORCE_PET_NEW),
    ]
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f"patch anchor missing: {old[:60]!r}...")
        text = text.replace(old, new, 1)
    if "function Module:assignRandomSkillSlots" not in text:
        anchor = "function Module:applyRandomGrowth(charIndex, petIndex, enemyId, isBoss)"
        text = text.replace(anchor, ASSIGN_SLOTS_FN + "\n" + anchor, 1)
    if "function Module:pickMagicAoeSkillIdByElement" not in text:
        anchor = "function Module:ensureMandatoryAoeSkills"
        text = text.replace(anchor, PICK_ELEMENT_FN + "\n" + anchor, 1)
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
    restart()
    Path(TEMP / "patch_contract_summon_ok.txt").write_text("ok", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
