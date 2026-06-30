# -*- coding: utf-8 -*-
"""Restore vanilla bins, add isolated contract effects 901-905, separate contract tech rows."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\cgtw")
TOOLS = ROOT / "tools"
BACKUP = ROOT / "_backup" / "contract_effects_bins"
BIN = ROOT / "bin"
PUK2 = BIN / "Puk2"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
REMOTE = "cgmsv-server"
REMOTE_TECH = "/cgmsv_26.5c/gmsv/data/tech.txt"
REMOTE_LUA = "/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua"

# clone templates: skill_id -> (effect_id, name_prefix, tech_base, group, tpl_skill)
CONTRACT = {
    991: (901, "契约震波", 199100, 139981, "4"),
    992: (902, "契约秘法·陨石", 199200, 139991, "27"),
    993: (903, "契约秘法·冰冻", 199210, 139992, "28"),
    994: (904, "契约秘法·火焰", 199220, 139993, "29"),
    995: (905, "契约秘法·风刃", 199230, 139994, "30"),
}

SPIRACLE = [
    (1, "AS:0,AN:1,AM:1,DD:125,", 5),
    (2, "AS:0,AN:1,AM:2,DD:125,", 10),
    (3, "AS:0,AN:2,AM:2,DD:125,", 15),
    (4, "AS:0,AN:2,AM:3,DD:125,", 20),
    (5, "AS:0,AN:3,AM:3,DD:125,", 25),
    (6, "AS:0,AN:3,AM:4,DD:125,", 30),
    (7, "AS:0,AN:3,AM:5,DD:125,", 35),
    (8, "AS:0,AN:4,AM:5,DD:125,", 40),
    (9, "AS:0,AN:4,AM:6,DD:125,", 45),
    (10, "AS:0,AN:5,AM:7,DD:125,", 50),
]

MAGIC_AR = [
    (1, 38, 40),
    (2, 68, 80),
    (3, 96, 120),
    (4, 121, 160),
    (5, 147, 200),
    (6, 173, 240),
    (7, 199, 280),
    (8, 228, 320),
    (9, 258, 360),
    (10, 289, 400),
]


def restore_bins():
    mapping = [
        (BACKUP / "Anime_4.bin", BIN / "Anime_4.bin"),
        (BACKUP / "AnimeInfo_4.bin", BIN / "AnimeInfo_4.bin"),
        (BACKUP / "Graphic_66.bin", BIN / "Graphic_66.bin"),
        (BACKUP / "GraphicInfo_66.bin", BIN / "GraphicInfo_66.bin"),
        (BACKUP / "puk2_Anime_PUK2_4.bin", PUK2 / "Anime_PUK2_4.bin"),
        (BACKUP / "puk2_AnimeInfo_PUK2_4.bin", PUK2 / "AnimeInfo_PUK2_4.bin"),
        (BACKUP / "puk2_Graphic_PUK2_2.bin", PUK2 / "Graphic_PUK2_2.bin"),
        (BACKUP / "puk2_GraphicInfo_PUK2_2.bin", PUK2 / "GraphicInfo_PUK2_2.bin"),
    ]
    patched = ROOT / "bin_patched"
    patched.mkdir(parents=True, exist_ok=True)
    inplace = ROOT / "_backup" / "contract_effects_inplace"
    for src, dst in mapping:
        if not src.exists():
            alt = inplace / src.name
            if alt.exists():
                src = alt
            else:
                raise SystemExit(f"missing backup {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
            print("restored", dst)
        except PermissionError:
            alt = patched / dst.name if dst.parent == BIN else patched / f"puk2_{dst.name}"
            shutil.copy2(src, alt)
            print("restored to", alt, "(game locking bin/)")


def parse_rows(text):
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rows.append(line.split("\t"))
    return rows


def vanilla_skill_rows(vanilla_text, skill_id):
    out = []
    for p in parse_rows(vanilla_text):
        if len(p) > 6 and p[5] == skill_id and p[4].startswith("1300"):
            out.append("\t".join(p))
    return out


def build_contract_rows(vanilla_text):
    by_skill = {}
    for p in parse_rows(vanilla_text):
        if len(p) < 8:
            continue
        try:
            sid = int(p[5])
            lv = int(p[6])
        except ValueError:
            continue
        by_skill.setdefault(str(sid), {})[lv] = p

    lines = []
    for new_sid, (effect, prefix, base, group, tpl) in CONTRACT.items():
        tpl_map = by_skill.get(tpl, {})
        for lv in range(1, 11):
            if tpl == "4":
                opt, mp = SPIRACLE[lv - 1][1], SPIRACLE[lv - 1][2]
                row = [
                    f"{prefix}LV{lv}",
                    "TECH_SpiracleShot",
                    opt,
                    str(base + lv - 1),
                    str(group),
                    str(new_sid),
                    str(lv),
                    "1",
                    str(effect),
                    "",
                    "",
                    str(mp),
                    "1",
                    "",
                    "",
                ]
            else:
                ar, mp = MAGIC_AR[lv - 1][1], MAGIC_AR[lv - 1][2]
                row = [
                    f"{prefix}LV{lv}",
                    "TECH_Attack_Magic",
                    f"AR:{ar},",
                    str(base + lv - 1),
                    str(group),
                    str(new_sid),
                    str(lv),
                    "1",
                    str(effect),
                    "",
                    "",
                    str(mp),
                    "1",
                    "",
                    "",
                ]
            lines.append("\t".join(row))
    return lines


def patch_tech(vanilla_path: Path, current_path: Path):
    vanilla = vanilla_path.read_bytes().decode("gbk")
    current = current_path.read_bytes().decode("gbk")
    keep = []
    removed = 0
    for line in current.splitlines():
        if not line.strip():
            keep.append(line)
            continue
        p = line.split("\t")
        if len(p) > 5 and p[5] in {"4", "27", "28", "29", "30", "991", "992", "993", "994", "995"}:
            removed += 1
            continue
        if "契约" in line:
            removed += 1
            continue
        keep.append(line)
    restored = []
    for sid in ["4", "27", "28", "29", "30"]:
        restored.extend(vanilla_skill_rows(vanilla, sid))
    contract = build_contract_rows(vanilla)
    out = "\n".join(keep + restored + contract) + "\n"
    return out, removed, len(restored), len(contract)


def patch_lua(text: str) -> str:
    import re

    text = re.sub(
        r"  aoe_phys = \{ 4 \},",
        "  aoe_phys = { 991, 4 },",
        text,
    )
    text = re.sub(
        r"  aoe_magic = \{ 27, 28, 29, 30 \},",
        "  aoe_magic = { 992, 993, 994, 995, 27, 28, 29, 30 },",
        text,
    )
    if "CUSTOM_AOE_TECH_BASE" not in text:
        block = """
local CUSTOM_AOE_TECH_BASE = {
  [991] = 199100,
  [992] = 199200,
  [993] = 199210,
  [994] = 199220,
  [995] = 199230,
}

"""
        text = text.replace(
            "local AOE_PHYSICAL_SKILL_IDS",
            block + "local AOE_PHYSICAL_SKILL_IDS",
        )
    if "[991] = true" not in text:
        text = text.replace(
            "local AOE_PHYSICAL_SKILL_IDS = { [4] = true }",
            "local AOE_PHYSICAL_SKILL_IDS = { [4] = true, [991] = true }",
        )
    text = re.sub(
        r"local AOE_MAGIC_SKILL_IDS = \{.*?\}\nlocal MAGIC_AOE_BY_ELEMENT = \{ earth = 27, water = 28, fire = 29, wind = 30 \}",
        "local AOE_MAGIC_SKILL_IDS = {\n"
        "  [23] = true, [24] = true, [25] = true, [26] = true,\n"
        "  [27] = true, [28] = true, [29] = true, [30] = true,\n"
        "  [992] = true, [993] = true, [994] = true, [995] = true,\n"
        "}\n"
        "local MAGIC_AOE_BY_ELEMENT = { earth = 992, water = 993, fire = 994, wind = 995 }",
        text,
        flags=re.S,
    )
    if "customBase = CUSTOM_AOE_TECH_BASE" not in text:
        text = text.replace(
            "  level = math.max(1, math.min(10, tonumber(level) or 1))\n"
            "  return skillId * 100 + (level - 1)",
            "  level = math.max(1, math.min(10, tonumber(level) or 1))\n"
            "  local customBase = CUSTOM_AOE_TECH_BASE[skillId]\n"
            "  if customBase then\n"
            "    return customBase + (level - 1)\n"
            "  end\n"
            "  return skillId * 100 + (level - 1)",
        )
    text = text.replace(
        "tryAddPetCombatSkill(charIndex, petIndex, 4, isBoss, bpTotal)",
        "tryAddPetCombatSkill(charIndex, petIndex, 991, isBoss, bpTotal)",
    )
    text = text.replace("table.insert(picked, 4)", "table.insert(picked, 991)", 1)
    text = text.replace(
        "local pool = { 27, 28, 29, 30 }",
        "local pool = { 992, 993, 994, 995 }",
    )
    text = text.replace("return 30", "return 995")
    text = text.replace("return 29", "return 994")
    text = text.replace(
        "local CHAZ_PET_SKILL_FIX_FLAG = './lua/fix_chaz_pet_skills_v2.done'",
        "local CHAZ_PET_SKILL_FIX_FLAG = './lua/fix_chaz_pet_skills_v3.done'",
    )
    text = text.replace(
        "local desired = { 2600, 400, 2700, 2800, 2900, 3000 }",
        "local desired = { 2600, 199100, 199200, 199210, 199220, 199230 }",
    )
    if "calcAdvancedPetTechId" in text and "customBase = CUSTOM_AOE_TECH_BASE" not in text:
        pass
    return text


def main():
    restore_bins()
    sys.path.insert(0, str(TOOLS))
    import patch_contract_effects as pce

    print("adding isolated contract animes 901-905...")
    work = ROOT / "bin_patched"
    work.mkdir(parents=True, exist_ok=True)
    work_puk2 = work / "Puk2"
    work_puk2.mkdir(parents=True, exist_ok=True)
    base_files = [
        (BACKUP / "Anime_4.bin", work / "Anime_4.bin"),
        (BACKUP / "AnimeInfo_4.bin", work / "AnimeInfo_4.bin"),
        (BACKUP / "Graphic_66.bin", work / "Graphic_66.bin"),
        (BACKUP / "GraphicInfo_66.bin", work / "GraphicInfo_66.bin"),
    ]
    puk2_files = [
        (BACKUP / "puk2_Anime_PUK2_4.bin", work_puk2 / "Anime_PUK2_4.bin"),
        (BACKUP / "puk2_AnimeInfo_PUK2_4.bin", work_puk2 / "AnimeInfo_PUK2_4.bin"),
        (BACKUP / "puk2_Graphic_PUK2_2.bin", work_puk2 / "Graphic_PUK2_2.bin"),
        (BACKUP / "puk2_GraphicInfo_PUK2_2.bin", work_puk2 / "GraphicInfo_PUK2_2.bin"),
    ]
    inplace = ROOT / "_backup" / "contract_effects_inplace"
    for src, dst in base_files + puk2_files:
        if not src.exists():
            if dst.parent == work_puk2:
                src = inplace / f"puk2_{dst.name}"
            else:
                src = inplace / f"base_{dst.name}"
        if not src.exists():
            live = dst if dst.exists() else (PUK2 / dst.name if dst.parent == work_puk2 else BIN / dst.name)
            src = live
        shutil.copy2(src, dst)
    pce.BASE_A = work / "Anime_4.bin"
    pce.BASE_AI = work / "AnimeInfo_4.bin"
    pce.BASE_G = work / "Graphic_66.bin"
    pce.BASE_GI = work / "GraphicInfo_66.bin"
    pce.PUK2_A = work_puk2 / "Anime_PUK2_4.bin"
    pce.PUK2_AI = work_puk2 / "AnimeInfo_PUK2_4.bin"
    pce.PUK2_G = work_puk2 / "Graphic_PUK2_2.bin"
    pce.PUK2_GI = work_puk2 / "GraphicInfo_PUK2_2.bin"
    pce.SET_PATHS["base"] = (pce.BASE_AI, pce.BASE_A, pce.BASE_GI, pce.BASE_G)
    pce.SET_PATHS["puk2"] = (pce.PUK2_AI, pce.PUK2_A, pce.PUK2_GI, pce.PUK2_G)
    pce.PATCH_DIR = work
    pce.patch_base_bins()
    print(f"patched client bins in {work} (copy to bin/ when game closed)")

    vanilla = TEMP / "tech_vanilla_ref.txt"
    if not vanilla.exists():
        subprocess.run(
            ["scp", f"{REMOTE}:{REMOTE_TECH}", str(TEMP / "tech_broken.txt")],
            check=True,
        )
        subprocess.run(
            ["scp", "cgmsv-server:C:/cgmsv/gmsv/data/tech.txt", str(vanilla)],
            check=True,
        )
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_TECH}", str(TEMP / "tech_broken.txt")], check=True)
    patched, rem, rst, con = patch_tech(vanilla, TEMP / "tech_broken.txt")
    out = TEMP / "tech_isolated.bin"
    out.write_bytes(patched.encode("gbk"))
    subprocess.run(["scp", str(out), f"{REMOTE}:{REMOTE_TECH}"], check=True)
    print(f"tech: removed={rem} restored_vanilla={rst} contract={con}")

    subprocess.run(["scp", f"{REMOTE}:{REMOTE_LUA}", str(TEMP / "pet_live.lua")], check=True)
    lua = patch_lua((TEMP / "pet_live.lua").read_bytes().decode("gbk"))
    lua_out = TEMP / "pet_isolated.lua"
    lua_out.write_bytes(lua.encode("gbk"))
    subprocess.run(["scp", str(lua_out), f"{REMOTE}:{REMOTE_LUA}"], check=True)
    print("petSummonContract updated")


if __name__ == "__main__":
    main()
