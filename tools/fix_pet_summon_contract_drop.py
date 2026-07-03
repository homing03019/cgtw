# -*- coding: utf-8 -*-
"""Fix petSummonContract.lua: remove test drop notification + repair GBK card info strings.

Usage (on Windows, from D:\\cgtw):
  python tools/fix_pet_summon_contract_drop.py
  python tools/fix_pet_summon_contract_drop.py --lua C:/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua
  python tools/fix_pet_summon_contract_drop.py --dry-run

Reads/writes server Lua as GBK bytes (never UTF-8).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "luaUI" / "scripts" / "verify_gbk.py"

# Candidate locations (first existing file wins unless --lua given)
LUA_CANDIDATES = [
    ROOT / "server_mirror" / "lua" / "modules" / "petSummonContract.lua",
    Path(r"C:/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua"),
    Path(r"/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua"),
    Path(r"C:/Users/User/AppData/Local/Temp/pet_live.lua"),
]

# Canonical GBK user-visible strings for summon cards (simplified Chinese)
STRINGS = {
    "card_name_fmt": "召唤卡(%s)",
    "card_name_contract": "契约召唤卡(%s)",
    "tip_hover": "$0封印着$5%s$0的契约灵魂\n$7双击可召唤为宠物伙伴",
    "tip_detail": "$0契约宠物：$5%s$0\n等级：$3%d$0  档次：$3%d$0\n$7双击使用可召唤",
    "tip_detail_skills": "$0契约宠物：$5%s$0\n等级：$3%d$0  档次：$3%d$0\n技能：$3%s$0\n$7双击使用可召唤",
    "drop_notify": "获得召唤卡：%s",
}

GARBLED_MARKERS = ("锟斤拷", "\ufffd", "ï¿½", "鍙", "鍗", "鍙琚", "濂戠害", "鍙¬", "瀵勫€")

# Whole-line removals: debug/test notifications left in drop path
TEST_LINE_PATTERNS = [
    re.compile(
        r"^\s*(?:NLG\.(?:SystemMessage|TalkToCli|Say)|char\.TalkToCli|Char\.TalkToCli)"
        r"\([^)]*(?:测试|測試|\[test\]|\[debug\]|test\s*drop|debug\s*drop)[^)]*\)\s*;?\s*$",
        re.I,
    ),
    re.compile(
        r"^\s*self:log(?:Info|Debug|Warn)\([^)]*(?:测试|測試|test\s*drop|summon\s*card\s*test)[^)]*\)\s*;?\s*$",
        re.I,
    ),
    re.compile(r"^\s*print\([^)]*(?:测试|測試|test\s*drop)[^)]*\)\s*;?\s*$", re.I),
]

# Replace garbled / UTF-8-mangled literals with canonical GBK strings
LITERAL_REPLACEMENTS: list[tuple[re.Pattern[str], str | object]] = [
    (
        re.compile(r'string\.format\(\s*["\'][^"\']*?(?:鍙|å|鍙琚)[^"\']*?\(%s\)\s*["\']\s*,'),
        f'string.format("{STRINGS["card_name_fmt"]}",',
    ),
    (
        re.compile(
            r'return\s+["\']\$0[^"\']*?\.\.\s*name\s*\.\.\s*["\'][^"\']*?["\']',
        ),
        f'return "{STRINGS["tip_hover"]}" .. name',
    ),
]

# If file still has mojibake inside quoted strings, map by function context (reserved)
FUNCTION_STRING_PATCHES = {}


def apply_literal_replacements(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    for pat, repl in LITERAL_REPLACEMENTS:
        if callable(repl):
            new_text, n = pat.subn(repl, text)
        else:
            new_text, n = pat.subn(repl, text)
        if n:
            changes.append(f"literal pattern {pat.pattern[:50]!r} x{n}")
            text = new_text
    return text, changes

def find_lua(explicit: Path | None) -> Path | None:
    if explicit:
        return explicit if explicit.is_file() else None
    for p in LUA_CANDIDATES:
        if p.is_file():
            return p
    return None


def has_garbled(s: str) -> bool:
    return any(m in s for m in GARBLED_MARKERS)


def try_recover_utf8_mojibake(s: str) -> str | None:
    """Recover UTF-8 Chinese that was wrongly interpreted as latin1/cp1252."""
    for enc in ("latin1", "cp1252"):
        try:
            raw = s.encode(enc)
            recovered = raw.decode("utf-8")
            if recovered != s and not has_garbled(recovered):
                # sanity: should contain CJK
                if re.search(r"[\u4e00-\u9fff]", recovered):
                    return recovered
        except (UnicodeDecodeError, UnicodeEncodeError):
            continue
    return None


def remove_test_lines(text: str) -> tuple[str, list[str]]:
    removed: list[str] = []
    out_lines: list[str] = []
    for line in text.splitlines():
        drop = False
        for pat in TEST_LINE_PATTERNS:
            if pat.search(line):
                drop = True
                removed.append(line.strip())
                break
        if not drop:
            out_lines.append(line)
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else ""), removed


def patch_quoted_strings(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []

    def repl(m: re.Match[str]) -> str:
        quote, body = m.group(1), m.group(2)
        if not has_garbled(body) and "å" not in body and "Ã" not in body:
            return m.group(0)
        recovered = try_recover_utf8_mojibake(body)
        if recovered:
            changes.append(f"recover: {body[:40]!r} -> {recovered[:40]!r}")
            return quote + recovered + quote
        # keyword-based fallback for summon card tooltips
        if any(k in body for k in ("召唤", "鍙", "契约", "濂", "封印", "双击", "宠物")):
            if "双击" in body or "double" in body.lower():
                fixed = STRINGS["tip_hover"]
            elif "等级" in body or "LV" in body.upper():
                fixed = STRINGS["tip_detail"]
            elif "%s" in body:
                fixed = STRINGS["card_name_fmt"]
            else:
                fixed = STRINGS["card_name_contract"]
            changes.append(f"replace garbled literal: {body[:40]!r}")
            return quote + fixed + quote
        return m.group(0)

    patched = re.sub(r'(["\'])((?:\\.|(?!\1).)*)\1', repl, text)
    return patched, changes


def patch_item_expansion_returns(text: str) -> tuple[str, list[str]]:
    """Normalize ItemExpansionEvent return strings for summon cards."""
    changes: list[str] = []
    if "onItemExpansionEvent" not in text and "ItemExpansionEvent" not in text:
        return text, changes

    # type == 1 hover line
    pat_hover = re.compile(
        r"(if\s+type\s*==\s*1\s+then\s+return\s+)(['\"])(.*?)\2",
        re.S,
    )

    def fix_hover(m: re.Match[str]) -> str:
        body = m.group(3)
        if has_garbled(body) or "å" in body or "鍙" in body:
            changes.append("fix ItemExpansion type==1 hover string")
            return m.group(1) + '"' + STRINGS["tip_hover"] + '"'
        return m.group(0)

    text = pat_hover.sub(fix_hover, text)

    # type == 2 detail: keep structure but fix garbled template prefix
    pat_detail = re.compile(
        r"(if\s+type\s*==\s*2\s+then\s+return\s+)(.*?)(\n\s+end)",
        re.S,
    )

    def fix_detail(m: re.Match[str]) -> str:
        block = m.group(2)
        if has_garbled(block) or "å" in block:
            changes.append("fix ItemExpansion type==2 detail block")
            # preserve concatenation with name/level if present
            if "level" in block.lower() or "等级" in block or "lv" in block.lower():
                new_block = (
                    'string.format("' + STRINGS["tip_detail"] + '", name, level, rank)'
                )
            else:
                new_block = '"' + STRINGS["tip_detail"] + '" .. name'
            return m.group(1) + new_block + m.group(3)
        return m.group(0)

    return pat_detail.sub(fix_detail, text), changes


def patch_card_name_setdata(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    pat = re.compile(
        r'(Item\.SetData\(\s*itemIndex\s*,\s*CONST\.道具_名字\s*,\s*)'
        r'string\.format\(\s*["\'][^"\']+["\']\s*,',
    )

    def fix(m: re.Match[str]) -> str:
        changes.append("fix Item.SetData card name format")
        return m.group(1) + f'string.format("{STRINGS["card_name_fmt"]}",'

    return pat.sub(fix, text), changes


def patch_lua(text: str) -> tuple[str, dict[str, list[str]]]:
    report: dict[str, list[str]] = {}
    text, removed = remove_test_lines(text)
    report["removed_test_lines"] = removed

    text, exp_changes = patch_item_expansion_returns(text)
    report["item_expansion_fixes"] = exp_changes

    text, lit_changes = apply_literal_replacements(text)
    report["literal_replacements"] = lit_changes

    text, qchanges = patch_quoted_strings(text)
    report["quoted_string_fixes"] = qchanges

    text, name_changes = patch_card_name_setdata(text)
    report["card_name_fixes"] = name_changes

    return text, report


def verify_gbk(path: Path) -> bool:
    if not VERIFY.is_file():
        return True
    r = subprocess.run([sys.executable, str(VERIFY), str(path)], capture_output=True, text=True)
    print(r.stdout.strip())
    if r.stderr:
        print(r.stderr.strip())
    return r.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lua", type=Path, help="path to petSummonContract.lua")
    ap.add_argument("--dry-run", action="store_true", help="print changes only")
    ap.add_argument("--restart", action="store_true", help="restart cgmsv after patch (Windows)")
    args = ap.parse_args()

    lua_path = find_lua(args.lua)
    if not lua_path:
        print("ERROR: petSummonContract.lua not found.")
        print("Copy server file to one of:")
        for p in LUA_CANDIDATES:
            print(f"  - {p}")
        print("Or pass --lua <path>")
        return 1

    print(f"patching: {lua_path}")
    raw = lua_path.read_bytes()
    text = None
    for enc in ("gbk", "utf-8", "utf-8-sig"):
        try:
            text = raw.decode(enc)
            if enc != "gbk":
                print(f"NOTE: decoded as {enc} (will rewrite as GBK)")
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        text = raw.decode("gbk", errors="replace")
        print("WARN: GBK decode used replacement characters")

    patched, report = patch_lua(text)
    total = sum(len(v) for v in report.values())
    if total == 0:
        print("No automatic fixes applied. Searching for suspicious lines...")
        for i, line in enumerate(text.splitlines(), 1):
            if any(k in line for k in ("测试", "測試", "TalkToCli", "SystemMessage")):
                if "召唤" in line or "契" in line or "drop" in line.lower() or "测试" in line:
                    print(f"  L{i}: {line.strip()[:100]}")
            if has_garbled(line) or "å" in line:
                print(f"  garble L{i}: {line.strip()[:100]}")
        return 2

    for key, items in report.items():
        if items:
            print(f"\n[{key}]")
            for item in items:
                print(f"  - {item}")

    if args.dry_run:
        print("\n--dry-run: not writing file")
        return 0

    backup = lua_path.with_suffix(lua_path.suffix + ".bak")
    backup.write_bytes(raw)
    lua_path.write_bytes(patched.encode("gbk"))
    print(f"\nbackup: {backup}")
    print(f"written: {lua_path} ({lua_path.stat().st_size} bytes)")

    if not verify_gbk(lua_path):
        print("WARN: verify_gbk reported issues; review backup before restart")

    if args.scp:
        remote = "cgmsv-server:/cgmsv_26.5c/gmsv/lua/modules/petSummonContract.lua"
        subprocess.run(["scp", str(lua_path), remote], check=True)
        print(f"uploaded -> {remote}")

    print("\nRestart cgmsv and test monster drop + card tooltip.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
