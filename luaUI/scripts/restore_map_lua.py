# -*- coding: utf-8 -*-
"""Restore D:/cgtw/luaUI/modules/map.lua from original UIMAP zip (no patches)."""
import pathlib
import shutil
import sys

ROOT = pathlib.Path(r"D:/cgtw")
DST = ROOT / "luaUI" / "modules" / "map.lua"
SRC = next(pathlib.Path(r"C:/Users/User/Downloads").glob("UIMAP*/map.lua"), None)

if SRC is None:
    SRC = ROOT / "_backup" / "map.lua.original"
if not SRC.exists():
    print("ERROR: source map.lua not found (UIMAP zip or _backup/map.lua.original)", file=sys.stderr)
    sys.exit(1)

shutil.copy2(SRC, DST)
text = DST.read_text(encoding="gbk")

forbidden = [
    "_closeMapAndCopilot",
    "_resolveNavCoords",
    "_dispatchCopilotNav",
    "RUN_BTN_Y - 8",
    "local INPUT_Y = UI.INPUT_Y",
    "OnWindowClose",
    "}))",
]
errors = [name for name in forbidden if name in text]
if errors:
    print("ERROR: restored file still contains patches:", errors, file=sys.stderr)
    sys.exit(1)

required = [
    "local INPUT_Y = PAGE_Y + 50",
    "self:AutoCopilot(targetX, targetY)",
    "return MapModule",
]
missing = [name for name in required if name not in text]
if missing:
    print("ERROR: restored file missing expected original markers:", missing, file=sys.stderr)
    sys.exit(1)

print(f"OK restored {DST} ({DST.stat().st_size} bytes)")
