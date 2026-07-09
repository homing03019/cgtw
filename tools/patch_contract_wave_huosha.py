#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contract physical AOE: fixed 活杀气功弹, 10 targets, 110% damage (tech 199100)."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
GMSV = "/cgmsv_26.5c/gmsv"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")

TECH_ROW = (
    "活杀气功弹\tTECH_SpiracleShot\tAS:0,AN:10,AM:10,DD:110,\t"
    "199100\t130004\t4\t1\t1\t117\t\t\t50\t1\t\t"
)

LUA_REPLACEMENTS = [
    (
        """  local contractNames = {
    [991] = '契约震波',
    [992] = '契约秘法·陨石',""",
        """  if skillId == 991 then
    return '活杀气功弹'
  end
  local contractNames = {
    [992] = '契约秘法·陨石',""",
    ),
    (
        """    level = self:rollSummonSkillLevel(isBoss, bpTotal)
    techId = self:calcAdvancedPetTechId(skillId, level)
  end
  if not self:isAdvancedPetTechValid(techId) then""",
        """    level = self:rollSummonSkillLevel(isBoss, bpTotal)
    techId = self:calcAdvancedPetTechId(skillId, level)
    if skillId == 991 then
      level = 1
      techId = CONTRACT_TECH_LV1[991]
    end
  end
  if not self:isAdvancedPetTechValid(techId) then""",
    ),
    (
        """  for i = 1, #granted do
    local g = granted[i]
    table.insert(parts, string.format('【%s】', g.name))
  end""",
        """  for i = 1, #granted do
    local g = granted[i]
    if g.skillId == 991 then
      table.insert(parts, string.format('【%s】', g.name))
    else
      table.insert(parts, string.format('【%s】Lv%d', g.name, g.level))
    end
  end""",
    ),
]


def patch_lua(text: str) -> str:
    text = text.replace("\r\n", "\n")
    for old, new in LUA_REPLACEMENTS:
        if old not in text:
            if new.split("\n")[0] in text:
                continue
            raise SystemExit(f"lua anchor missing: {old[:60]!r}")
        text = text.replace(old, new, 1)
    return text


def patch_tech(text: str) -> str:
    text = text.replace("\r\n", "\n").rstrip("\n")
    if "\t199100\t" in text or text.endswith("199100"):
        # update params if row exists
        lines = []
        for line in text.split("\n"):
            if "\t199100\t" in f"\t{line}\t" or line.split("\t")[3:4] == ["199100"]:
                parts = line.split("\t")
                if len(parts) > 2:
                    parts[0] = "活杀气功弹"
                    parts[2] = "AS:0,AN:10,AM:10,DD:110,"
                line = "\t".join(parts)
            lines.append(line)
        return "\n".join(lines) + "\n"
    return text + "\n" + TECH_ROW + "\n"


def write_gbk(path: Path, text: str) -> None:
    path.write_bytes(text.encode("gbk") + b"\n")


def deploy(local: Path, remote: str) -> None:
    subprocess.run(["scp", str(local), f"{REMOTE}:{remote}"], check=True)


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
    lua_in = TEMP / "petSummonContract_live.lua"
    tech_in = TEMP / "tech_live.txt"
    subprocess.run(["scp", f"{REMOTE}:{GMSV}/lua/Modules/petSummonContract.lua", str(lua_in)], check=True)
    subprocess.run(["scp", f"{REMOTE}:{GMSV}/data/tech.txt", str(tech_in)], check=True)

    lua_out = TEMP / "petSummonContract_wave.lua"
    tech_out = TEMP / "tech_wave.txt"
    write_gbk(lua_out, patch_lua(lua_in.read_bytes().decode("gbk")))
    write_gbk(tech_out, patch_tech(tech_in.read_bytes().decode("gbk")))

    deploy(lua_out, f"{GMSV}/lua/Modules/petSummonContract.lua")
    deploy(tech_out, f"{GMSV}/data/tech.txt")
    print("deployed contract wave huosha fix (10 targets, DD110)")
    restart()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
