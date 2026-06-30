from pathlib import Path
import re

t = Path(r"D:/cgtw/luaUI/modules/map.lua").read_text(encoding="gbk")
checks = [
    "_queueNavigation",
    "_runPendingNavigation",
    "_resolveNavCoords",
    "_navPending",
    "getModule('copilot')",
    "copilot:autoCopilot",
    "if self._navPending then",
    "OnKeyPress(13",
    "onEnter = function",
    "RUN_BTN_X - 8",
    "_startNavigation",
]
for c in checks:
    print(f"{c}: {c in t}")

# onLoad nav pending
if "self._navPending = nil" not in t:
    print("MISSING onLoad _navPending init")

Path(r"D:/cgtw/_verify.txt").write_text(
    t[t.find("function MapModule:_queueNavigation"):t.find("function MapModule:updateMapPoints")],
    encoding="utf-8",
)
