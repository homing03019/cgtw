#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""List contract summon pet learnable skills from pools + skill.txt filter."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

SKILL_TXT = Path(r"C:/Users/User/AppData/Local/Temp/skill.txt")

SUMMON_SKILL_POOLS = {
    "combo": [0, 1, 3, 4, 5, 6],
    "zhuren": [7, 8, 9, 10, 11, 12],
    "status_phys": [],
    "earth": [19, 20, 21, 22],
    "water": [23, 24, 25, 26],
    "fire": [27, 28, 29, 30],
    "wind": [31],
    "abnormal": [32, 33, 34, 35, 36, 37],
    "def_magic": [38, 39, 40, 41, 42, 43],
    "atk_buff": [44, 45, 46, 47, 48, 49],
    "elem_attack": [50, 51, 52, 53, 54],
    "elem_def": [55, 56, 57, 58, 59, 60],
    "heal": [61, 62, 63],
    "clean": [64, 65, 66, 67, 68],
    "curse": [75, 76, 77, 78, 79, 80],
    "assassin": [74],
    "shoot": [73],
    "aoe_phys": [991],
    "aoe_magic": [992, 993, 994, 995, 27, 28, 29, 30],
}

PET_SKILL_WHITELIST = {67, 68, 73, 74}

LEARN_COL = 10  # 1-based column index in skill.txt
FIELD_COL = 6


def load_skills() -> dict[int, dict]:
    text = SKILL_TXT.read_bytes().decode("gbk", errors="replace")
    out: dict[int, dict] = {}
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < LEARN_COL:
            continue
        try:
            sid = int(parts[1])
        except ValueError:
            continue
        out[sid] = {
            "name": parts[0],
            "field": int(parts[FIELD_COL - 1]) if parts[FIELD_COL - 1].isdigit() else 0,
            "learn": int(parts[LEARN_COL - 1]) if parts[LEARN_COL - 1].isdigit() else -1,
        }
    return out


def is_learnable(sid: int, skills: dict[int, dict], allow_heal: bool = True) -> tuple[bool, str]:
    if sid in PET_SKILL_WHITELIST:
        extra = "弓宠/洁净白名单" if sid in (73, 74) else "洁净/气绝白名单"
        return True, extra
    if 991 <= sid <= 995:
        return True, "契约专属AOE"
    s = skills.get(sid)
    if not s:
        return False, "skill.txt 无此ID"
    learn = s["learn"]
    field = s["field"]
    if field >= 5:
        return False, f"Boss专用 field={field}"
    allowed = {0, 2}
    if allow_heal:
        allowed.add(4)
    if learn == 3:
        return False, f"玩家专用 learn=3（如元素祈祷）"
    if learn not in allowed:
        return False, f"不可学 learn={learn}"
    tag = {0: "宠物/抗性", 2: "战斗共用", 4: "补血/辅助"}.get(learn, str(learn))
    return True, tag


def main() -> None:
    skills = load_skills()
    out = Path(r"C:/Users/User/AppData/Local/Temp/contract_pet_skill_list.md")
    lines = [
        "# 契约召唤宠 — 可学技能清单",
        "",
        "规则（当前）：",
        "- **可学**：skill.txt 学习栏 `0` / `2` / `4`，或白名单 67/68/73/74",
        "- **不可学**：`3`（玩家专用祈祷等，67/68 除外）、`field≥5`（Boss技）",
        "- **诅咒池**：仅状态攻击 75–80（已移除金钱攻击等）",
        "- **抗性 13–18**：已取消",
        "- **等级**：普通宠 Lv3–8，Boss Lv4–10",
        "- 五围流派会决定从哪些**技能池**抽取；每场随机 0–3 招 + 可能强制 AOE",
        "",
    ]

    all_pool_ids: set[int] = set()
    for ids in SUMMON_SKILL_POOLS.values():
        all_pool_ids.update(ids)

    lines.append("## 按技能池分类")
    lines.append("")
    for pool, ids in SUMMON_SKILL_POOLS.items():
        lines.append(f"### {pool}")
        lines.append("")
        lines.append("| ID | 技能名 | 可学 | 说明 |")
        lines.append("|----|--------|------|------|")
        for sid in ids:
            name = skills.get(sid, {}).get("name", "?")
            ok, reason = is_learnable(sid, skills, allow_heal=True)
            mark = "✅" if ok else "❌"
            lines.append(f"| {sid} | {name} | {mark} | {reason} |")
        lines.append("")

    learnable = []
    blocked = []
    for sid in sorted(all_pool_ids):
        name = skills.get(sid, {}).get("name", f"#{sid}")
        ok, reason = is_learnable(sid, skills, allow_heal=True)
        (learnable if ok else blocked).append((sid, name, reason))

    lines.append("## 汇总：池内可学（✅）")
    lines.append("")
    for sid, name, reason in learnable:
        pools = [p for p, ids in SUMMON_SKILL_POOLS.items() if sid in ids]
        lines.append(f"- **{sid}** {name} — {reason}（池: {', '.join(pools)}）")
    lines.append("")
    lines.append("## 汇总：池内不可学（❌）")
    lines.append("")
    for sid, name, reason in blocked:
        pools = [p for p, ids in SUMMON_SKILL_POOLS.items() if sid in ids]
        lines.append(f"- **{sid}** {name} — {reason}（池: {', '.join(pools)}）")
    lines.append("")

    by_cat: dict[str, list] = defaultdict(list)
    for sid, name, reason in learnable:
        by_cat[reason.split("（")[0]].append(f"{name}(ID{sid})")
    lines.append("## 按类型速览（仅可学）")
    lines.append("")
    for cat in ["战斗共用", "补血/辅助", "宠物/抗性", "契约专属AOE", "固定（弓宠射击/通用）"]:
        if cat in by_cat:
            lines.append(f"**{cat}**：{', '.join(by_cat[cat])}")
            lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
