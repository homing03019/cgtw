# -*- coding: utf-8 -*-
from pathlib import Path
import sys

MAP = Path(r"D:/cgtw/luaUI/modules/map.lua")
text = MAP.read_text(encoding="gbk")

text2 = text.replace(
    """        if self.warpMode == MODE_SYSTEM or self.warpMode == "NPC" then
            self:_beginNav(point.x, point.y)
        end
    end
end

function split(str,split_char)""",
    """    end
end

function split(str,split_char)""",
    1,
)
if text2 == text:
    print("WARN: beginNav block not removed", file=sys.stderr)
else:
    text = text2

helpers = """
function MapModule:_isDblClick(flags)
    flags = tonumber(flags) or 0
    local bitFlag = CONST.MouseFlags.L_DBL_CLICK_EVENT
    return (flags % (bitFlag * 2)) >= bitFlag
end

function MapModule:onWarpListClick(idx, flags)
    self:onWarpItemClick(idx)
    if not self:_isDblClick(flags) then
        return
    end
    if self.warpMode ~= MODE_SYSTEM and self.warpMode ~= "NPC" then
        return
    end
    local perPage = self.currentUI.LIST_ITEM_COUNT
    local actualIdx = (self.warpPage - 1) * perPage + idx
    local warpData = {}
    if self.warpMode == MODE_SYSTEM then
        warpData = self.warpPoints
    else
        warpData = self.npcPoints
    end
    if actualIdx > #warpData then
        return
    end
    local point = warpData[actualIdx]
    if point then
        self:_beginNav(point.x, point.y)
    end
end

"""

if "onWarpListClick" not in text:
    text = text.replace("function MapModule:_flushDeferredNav()", helpers + "function MapModule:_flushDeferredNav()", 1)

text = text.replace(
    "self:onWarpItemClick(i)\n\t\t\t\t\t\treturn true",
    "self:onWarpListClick(i, flags)\n\t\t\t\t\t\treturn true",
    1,
)
text = text.replace(
    "onClick = function()\n\t\t\t\t\t\tself:onWarpListClick(i, flags)",
    "onClick = function(control, flags)\n\t\t\t\t\t\tself:onWarpListClick(i, flags)",
    1,
)

if "onWarpListClick" not in text:
    sys.exit("patch failed")

import re
warp_fn = re.search(r"function MapModule:onWarpItemClick\(idx\).*?end\nend\n\nfunction split", text, re.DOTALL)
if warp_fn and "_beginNav" in warp_fn.group(0):
    sys.exit("single click nav remains in onWarpItemClick")

MAP.write_text(text, encoding="gbk")
print("OK", MAP.stat().st_size)
