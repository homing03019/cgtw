# -*- coding: utf-8 -*-
"""Validate map.lua is original GBK and UI layout markers are intact."""
import pathlib
import sys

path = pathlib.Path(r"D:/cgtw/luaUI/modules/map.lua")
text = path.read_text(encoding="gbk")

errors = []

for token in ["}))", ",\n\t\t\t,", "RUN_BTN_Y - 8", "local INPUT_Y = UI.INPUT_Y"]:
    if token in text:
        errors.append(f"forbidden UI/syntax marker: {token}")

# patched build must keep original layout lines
for token in ["local INPUT_Y = PAGE_Y + 50", "local BTN_Y = INPUT_Y + 52", "return MapModule"]:
    if token not in text:
        errors.append(f"missing layout marker: {token}")

for line in text.splitlines():
    if line.startswith("local combox") and "?" in line:
        errors.append("GBK corruption in combox image variable")
        break

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("OK map.lua original layout markers present, GBK intact")
