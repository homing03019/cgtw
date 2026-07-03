# -*- coding: utf-8 -*-
"""Restore vanilla 超强魔法 (skills 4 / 27-30) after contract isolation over-patch.

The contract work should ADD skills 991-995 for summon-contract pets only.
It must NOT redirect all players/pets from vanilla AOE magic to 992-995.

Usage (Windows, on machine with cgmsv):
  python tools/fix_restore_vanilla_aoe_magic.py
  python tools/fix_restore_vanilla_aoe_magic.py --lua C:/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua
  python tools/fix_restore_vanilla_aoe_magic.py --tech C:/cgmsv_26.5c/gmsv/data/tech.txt --vanilla C:/cgmsv/gmsv/data/tech.txt
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "luaUI" / "scripts" / "verify_gbk.py"

LUA_CANDIDATES = [
    ROOT / "server_mirror" / "lua" / "modules" / "petSummonContract.lua",
    Path(r"C:/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua"),
    Path(r"/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua"),
]

TECH_CANDIDATES = [
    Path(r"C:/cgmsv_26.5c/gmsv/data/tech.txt"),
    Path(r"/cgmsv_26.5c/gmsv/data/tech.txt"),
]

VANILLA_TECH_CANDIDATES = [
    Path(r"C:/cgmsv/gmsv/data/tech.txt"),
    Path(r"C:/Users/User/AppData/Local/Temp/tech_vanilla_ref.txt"),
]


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("gbk", "utf-8", "utf-8-sig"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("gbk", errors="replace")


def write_gbk(path: Path, text: str) -> None:
    backup = path.with_suffix(path.suffix + ".bak_magic")
    if not backup.exists():
        backup.write_bytes(path.read_bytes())
    path.write_bytes(text.encode("gbk"))


def parse_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        rows.append(line.split("\t"))
    return rows


def skill_rows_from_vanilla(vanilla_text: str, skill_id: str) -> list[str]:
    """All tech rows for a skill id (not only group 1300xxx)."""
    out = []
    for p in parse_rows(vanilla_text):
        if len(p) > 6 and p[5] == skill_id:
            out.append("\t".join(p))
    return out


def patch_tech_file(vanilla_text: str, current_text: str) -> tuple[str, dict[str, int]]:
    """Ensure vanilla rows for skills 4,27-30 exist; keep contract 991-995 rows."""
    stats = {"removed": 0, "restored": 0, "contract_kept": 0}
    keep: list[str] = []
    for line in current_text.splitlines():
        if not line.strip():
            keep.append(line)
            continue
        p = line.split("\t")
        if len(p) > 5 and p[5] in {"4", "27", "28", "29", "30"}:
            stats["removed"] += 1
            continue
        if "契约" in line:
            stats["removed"] += 1
            continue
        if len(p) > 5 and p[5] in {"991", "992", "993", "994", "995"}:
            stats["contract_kept"] += 1
        keep.append(line)

    restored: list[str] = []
    for sid in ["4", "27", "28", "29", "30"]:
        rows = skill_rows_from_vanilla(vanilla_text, sid)
        restored.extend(rows)
        stats["restored"] += len(rows)

    out = "\n".join(keep + restored)
    if current_text.endswith("\n"):
        out += "\n"
    return out, stats


def patch_lua(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    def sub_once(pattern: str, repl: str, label: str, flags: int = 0) -> None:
        nonlocal text
        new_text, n = re.subn(pattern, repl, text, count=1, flags=flags)
        if n:
            changes.append(label)
            text = new_text

    # Element mapping must stay vanilla for normal play.
    sub_once(
        r"local MAGIC_AOE_BY_ELEMENT = \{[^}]+\}",
        "local MAGIC_AOE_BY_ELEMENT = { earth = 27, water = 28, fire = 29, wind = 30 }",
        "restore MAGIC_AOE_BY_ELEMENT -> 27-30",
    )

    sub_once(
        r"local pool = \{ 992, 993, 994, 995 \}",
        "local pool = { 27, 28, 29, 30 }",
        "restore pet magic pool -> 27-30",
    )

    if "tryAddPetCombatSkill(charIndex, petIndex, 991," in text:
        text = text.replace(
            "tryAddPetCombatSkill(charIndex, petIndex, 991,",
            "tryAddPetCombatSkill(charIndex, petIndex, 4,",
        )
        changes.append("restore tryAddPetCombatSkill phys 991 -> 4")

    if "table.insert(picked, 991)" in text:
        text = text.replace("table.insert(picked, 991)", "table.insert(picked, 4)", 1)
        changes.append("restore table.insert(picked, 991) -> 4")

    if "local desired = { 2600, 199100, 199200, 199210, 199220, 199230 }" in text:
        text = text.replace(
            "local desired = { 2600, 199100, 199200, 199210, 199220, 199230 }",
            "local desired = { 2600, 400, 2700, 2800, 2900, 3000 }",
        )
        changes.append("restore CHAZ desired tech ids")

    # Undo blind global return replacements from fix_contract_isolated.patch_lua
    # Only in typical element-default helper blocks.
    for bad, good, label in [
        (r"(\bwind\b[^\n]{0,40}\breturn\s+)995\b", r"\g<1>30", "restore wind default 995->30"),
        (r"(\bfire\b[^\n]{0,40}\breturn\s+)994\b", r"\g<1>29", "restore fire default 994->29"),
        (r"(\breturn\s+)995(\s*--\s*wind)", r"\g<1>30\2", "restore comment wind return"),
        (r"(\breturn\s+)994(\s*--\s*fire)", r"\g<1>29\2", "restore comment fire return"),
    ]:
        new_text, n = re.subn(bad, good, text, count=1, flags=re.I)
        if n:
            changes.append(label)
            text = new_text

    # Keep contract skills listed, but vanilla must remain available.
    if "aoe_magic = { 992, 993, 994, 995, 27, 28, 29, 30 }" not in text:
        sub_once(
            r"aoe_magic\s*=\s*\{[^}]+\}",
            "aoe_magic = { 992, 993, 994, 995, 27, 28, 29, 30 }",
            "ensure aoe_magic includes both contract + vanilla",
        )

    if "aoe_phys = { 991, 4 }" not in text and "aoe_phys" in text:
        sub_once(
            r"aoe_phys\s*=\s*\{[^}]+\}",
            "aoe_phys = { 991, 4 }",
            "ensure aoe_phys includes both 991 + 4",
        )

    return text, changes


def verify_gbk(path: Path) -> bool:
    if not VERIFY.is_file():
        return True
    r = subprocess.run([sys.executable, str(VERIFY), str(path)], capture_output=True, text=True)
    print(r.stdout.strip())
    return r.returncode == 0


def pick_first(candidates: list[Path]) -> Path | None:
    for p in candidates:
        if p.is_file():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lua", type=Path)
    ap.add_argument("--tech", type=Path)
    ap.add_argument("--vanilla", type=Path, help="vanilla tech.txt reference")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    lua_path = args.lua or pick_first(LUA_CANDIDATES)
    tech_path = args.tech or pick_first(TECH_CANDIDATES)
    vanilla_path = args.vanilla or pick_first(VANILLA_TECH_CANDIDATES)

    if not lua_path:
        print("ERROR: petSummonContract.lua not found")
        return 1

    print(f"lua: {lua_path}")
    lua = read_text(lua_path)
    patched_lua, lua_changes = patch_lua(lua)
    if lua_changes:
        print("\n[lua fixes]")
        for c in lua_changes:
            print(f"  - {c}")
    else:
        print("WARN: no lua pattern fixes matched (file may already be ok or layout changed)")

    if args.dry_run:
        print("\n--dry-run: not writing")
        return 0

    write_gbk(lua_path, patched_lua)
    print(f"written lua: {lua_path}")
    verify_gbk(lua_path)

    if tech_path and vanilla_path:
        print(f"\ntech: {tech_path}")
        print(f"vanilla ref: {vanilla_path}")
        patched_tech, stats = patch_tech_file(read_text(vanilla_path), read_text(tech_path))
        print(f"tech stats: {stats}")
        write_gbk(tech_path, patched_tech)
        print(f"written tech: {tech_path}")
    elif tech_path:
        print("\nSKIP tech.txt (no vanilla reference found). Pass --vanilla")

    print("\nRestart cgmsv and test 超强魔法 on player + normal pet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
