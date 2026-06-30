# -*- coding: utf-8 -*-
"""Restore map.lua from zip + minimal safe patches. GBK only."""
import pathlib
import re
import shutil
import sys

SRC = next(pathlib.Path(r"C:/Users/User/Downloads").glob("UIMAP*/map.lua"))
DST = pathlib.Path(r"D:/cgtw/luaUI/modules/map.lua")
LOG = pathlib.Path(r"D:/cgtw/patch_restore_log.txt")

shutil.copy2(SRC, DST)
text = DST.read_text(encoding="gbk")

helpers = """
function MapModule:_resolveNavCoords()
    local targetX, targetY
    if self.inputX and self.inputX.valid then
        targetX = tonumber(self.inputX.text)
    end
    if self.inputY and self.inputY.valid then
        targetY = tonumber(self.inputY.text)
    end
    if (not targetX or targetX <= 0 or not targetY or targetY <= 0) and self.targetPoint then
        targetX = self.targetPoint.x
        targetY = self.targetPoint.y
    end
    if (not targetX or targetX <= 0 or not targetY or targetY <= 0) and self.selectedWarpIdx then
        local warpData = {}
        if self.warpMode == MODE_SYSTEM then
            warpData = self.warpPoints
        elseif self.warpMode == "NPC" then
            warpData = self.npcPoints
        else
            warpData = self.diyWarpPoints
        end
        local point = warpData[self.selectedWarpIdx]
        if point then
            targetX = point.x
            targetY = point.y
        end
    end
    return targetX, targetY
end

function MapModule:_dispatchCopilotNav(targetX, targetY)
    targetX = tonumber(targetX)
    targetY = tonumber(targetY)
    if not targetX or not targetY or targetX <= 0 or targetY <= 0 then
        return false
    end
    local cmd = string.format('/copilot %d %d', targetX, targetY)
    local copilot = self:getModule('copilot')
    if copilot and copilot.dispatchCommand then
        copilot:dispatchCommand(cmd)
    elseif copilot then
        copilot:autoCopilot(targetX, targetY)
    else
        WinMgr.AutoCopilot(targetX, targetY)
    end
    return true
end

function MapModule:_closeMapAndCopilot(targetX, targetY)
    targetX = tonumber(targetX)
    targetY = tonumber(targetY)
    if not targetX or not targetY or targetX <= 0 or targetY <= 0 then
        self:cliSendMsg('寻路失败：请先选择有效坐标')
        return false
    end

    if self.inputX and self.inputX.valid then
        self.inputX:Set({ text = tostring(targetX) })
    end
    if self.inputY and self.inputY.valid then
        self.inputY:Set({ text = tostring(targetY) })
    end

    if self.map and self.map.valid then
        if self.targetPoint then
            self.map:RemovePoints(self.targetPoint.x, self.targetPoint.y)
        end
        self.targetPoint = { x = targetX, y = targetY }
        self.savedTargetPoint = { x = targetX, y = targetY }
        self.map:AddPoint({
            mapX = targetX,
            mapY = targetY,
            type = 1,
            size = 4,
            color = { 0xffff0000 }
        })
    end

    if self.mapWin and self.mapWin.valid then
        self.mapWin:Close()
    end
    self:closeAddDiyWin()
    self:closeDelConfirm()
    self.mapWin = nil
    self.mapVisible = false
    self:_dispatchCopilotNav(targetX, targetY)
    return true
end

"""

text = text.replace("function MapModule:updateMapPoints()", helpers + "function MapModule:updateMapPoints()", 1)

# remove original run button, re-add on top at end
run_pat = re.compile(r"\t\t\t--执行按钮\n\t\t\twin:AddPngImage\(\{.*?\n\t\t\t\}\)\n", re.DOTALL)
run_match = run_pat.search(text)
if not run_match:
    LOG.write_text("ERROR: run button not found\n", encoding="utf-8")
    sys.exit(1)
text = text[: run_match.start()] + text[run_match.end() :]

run_btn = """\t\t\t--执行按钮
\t\t\twin:AddPngImage({
\t\t\t\tname = '执行',
\t\t\t\tx = UI.RUN_BTN_X - 12,
\t\t\t\ty = UI.RUN_BTN_Y - 8,
\t\t\t\twidth = UI.RUN_BTN_WIDTH + 24,
\t\t\t\theight = UI.RUN_BTN_HEIGHT + 20,
\t\t\t\timage = run_btn,
\t\t\t\timageHover = run_btn_h,
\t\t\t\timagePress = run_btn_p,
\t\t\t\tcolor = -1,
\t\t\t\tvisible = true,
\t\t\t\thitable = true,
\t\t\t\tonClick = function()
                    local targetX, targetY = self:_resolveNavCoords()
                    self:_closeMapAndCopilot(targetX, targetY)
                    return true
                end
\t\t\t})

"""

insert_at = text.find("\n        end\n    end\nend\n\nfunction MapModule:openAddDiy")
if insert_at < 0:
    LOG.write_text("ERROR: insert point not found\n", encoding="utf-8")
    sys.exit(1)
text = text[:insert_at] + "\n" + run_btn + text[insert_at:]

# inputY onEnter via regex (GBK-safe)
input_y_pat = re.compile(
    r"(self\.inputY = win:AddTextInput\(\{.*?hitable = true,\n\t\t\t\})",
    re.DOTALL,
)
m = input_y_pat.search(text)
if m and "onEnter" not in m.group(1):
    block = m.group(1)
    block = block.replace(
        "\t\t\t\thitable = true,\n\t\t\t})",
        "\t\t\t\thitable = true,\n\t\t\t\tonEnter = function()\n                    local targetX, targetY = self:_resolveNavCoords()\n                    self:_closeMapAndCopilot(targetX, targetY)\n                    return true\n                end\n\t\t\t})",
        1,
    )
    text = text[: m.start()] + block + text[m.end() :]

# Enter key in onLoad
old_onload = """    self.addDiyWin = nil
    self.delConfirmWin = nil
end

function MapModule:_sceneStateChanged"""
new_onload = """    self.addDiyWin = nil
    self.delConfirmWin = nil
    self:OnKeyPress(13, {}, 1, function()
        if self.mapVisible and self.mapWin and self.mapWin.valid then
            local targetX, targetY = self:_resolveNavCoords()
            self:_closeMapAndCopilot(targetX, targetY)
        end
    end)
end

function MapModule:_sceneStateChanged"""
if "OnKeyPress(13" not in text:
    text = text.replace(old_onload, new_onload, 1)

# syntax checks before write
if "}))" in text:
    LOG.write_text("ERROR: bad syntax }))\n", encoding="utf-8")
    sys.exit(1)
if ",\n\t\t\t," in text:
    LOG.write_text("ERROR: bad syntax double comma\n", encoding="utf-8")
    sys.exit(1)

DST.write_text(text, encoding="gbk")

# verify round-trip
verify = DST.read_text(encoding="gbk")
assert "function MapModule:_closeMapAndCopilot" in verify
assert "return MapModule" in verify
assert "}))" not in verify
LOG.write_text(f"SUCCESS size={DST.stat().st_size}\n", encoding="utf-8")
