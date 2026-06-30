# -*- coding: utf-8 -*-
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(r"D:/cgtw")
DST = ROOT / "luaUI" / "modules" / "map.lua"
SRC = next(pathlib.Path(r"C:/Users/User/Downloads").glob("UIMAP*/map.lua"))
LOG = ROOT / "patch_log.txt"

def log(msg):
    LOG.write_text((LOG.read_text(encoding="utf-8") if LOG.exists() else "") + str(msg) + "\n", encoding="utf-8")

LOG.write_text("", encoding="utf-8")
shutil.copy2(SRC, DST)
log(f"restored bytes={DST.stat().st_size}")

text = DST.read_text(encoding="gbk")

text = text.replace(
    "        local INPUT_Y = PAGE_Y + 50\n        local BTN_Y = INPUT_Y + 52",
    "        local INPUT_Y = UI.INPUT_Y\n        local BTN_Y = UI.RUN_BTN_Y",
    1,
)

nav_block = """
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
    if (not targetX or targetX <= 0 or not targetY or targetY <= 0) and self.savedTargetPoint then
        targetX = self.savedTargetPoint.x
        targetY = self.savedTargetPoint.y
    end
    return targetX, targetY
end

function MapModule:_queueNavigation(targetX, targetY)
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

    self._navPending = { x = targetX, y = targetY }
    self:cliSendMsg(string.format('寻路开始，目的地：东:%d 南:%d', targetX, targetY))
    return true
end

function MapModule:_runPendingNavigation()
    local pending = self._navPending
    if not pending then
        return false
    end
    self._navPending = nil

    local copilot = self:getModule('copilot')
    if copilot then
        copilot:autoCopilot(pending.x, pending.y)
    else
        WinMgr.AutoCopilot(pending.x, pending.y)
    end

    self:closeAddDiyWin()
    self:closeDelConfirm()
    if self.mapWin and self.mapWin.valid then
        self.mapWin:Close()
    end
    self.mapWin = nil
    self.mapVisible = false
    return true
end

"""

text = text.replace("function MapModule:updateMapPoints()", nav_block + "function MapModule:updateMapPoints()", 1)

text = text.replace(
    "    self.addDiyWin = nil\n    self.delConfirmWin = nil\nend\n\nfunction MapModule:_sceneStateChanged",
    "    self.addDiyWin = nil\n    self.delConfirmWin = nil\n    self._navPending = nil\n    self:OnKeyPress(13, {}, 1, function()\n        if self.mapVisible and self.mapWin and self.mapWin.valid then\n            local x, y = self:_resolveNavCoords()\n            self:_queueNavigation(x, y)\n        end\n    end)\nend\n\nfunction MapModule:_sceneStateChanged",
    1,
)

text = text.replace(
    """            update = function(window)
                if not window.valid then
                    return false
                end
                self:updateMapPoints()
                return false
            end,""",
    """            update = function(window)
                if not window.valid then
                    return false
                end
                if self._navPending then
                    self:_runPendingNavigation()
                end
                self:updateMapPoints()
                return false
            end,""",
    1,
)

text = text.replace(
    """        self.selectedWarpIdx = actualIdx
        self:refreshWarpList()
    end
end""",
    """        self.selectedWarpIdx = actualIdx
        self:refreshWarpList()
        self:_queueNavigation(point.x, point.y)
    end
end""",
    1,
)

text = text.replace(
    """                        self.map:AddPoint({
                            mapX = mapX,
                            mapY = mapY,
                            type = 1,
                            size = 4,
                            color = { 0xffff0000 }
                        })
                    end
                end,""",
    """                        self.map:AddPoint({
                            mapX = mapX,
                            mapY = mapY,
                            type = 1,
                            size = 4,
                            color = { 0xffff0000 }
                        })
                    end
                    self:_queueNavigation(mapX, mapY)
                end,""",
    1,
)

old_run = """				onClick = function()
                    local targetX = 0
                    local targetY = 0
                    if self.inputX and self.inputX.valid then
                        targetX = tonumber(self.inputX.text) or 0
                    end
                    if self.inputY and self.inputY.valid then
                        targetY = tonumber(self.inputY.text) or 0
                    end
                    if targetX <= 0 or targetY <= 0 then
                        return true
                    end
                    WinMgr.CliSendMsg(string.format("寻路开始，目的地：东:%d 南:%d", targetX, targetY))

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

                    self:AutoCopilot(targetX, targetY)
                    return true
                end"""
new_run = """				onClick = function()
                    local x, y = self:_resolveNavCoords()
                    self:_queueNavigation(x, y)
                    return true
                end"""
text = text.replace(old_run, new_run, 1)

run_pat = re.compile(r"\t\t\t--执行按钮\n\t\t\twin:AddPngImage\(\{.*?\n\t\t\t\}\)\n", re.DOTALL)
run_match = run_pat.search(text)
if run_match:
    run_block = run_match.group(0)
    text = text[: run_match.start()] + text[run_match.end() :]
    run_block = run_block.replace("x = UI.RUN_BTN_X,\n\t\t\t\ty = BTN_Y,", "x = UI.RUN_BTN_X - 8,\n\t\t\t\ty = UI.RUN_BTN_Y - 6,")
    run_block = run_block.replace("width = UI.RUN_BTN_WIDTH,\n\t\t\t\theight = UI.RUN_BTN_HEIGHT,", "width = UI.RUN_BTN_WIDTH + 16,\n\t\t\t\theight = UI.RUN_BTN_HEIGHT + 12,")
    if "hitable = true" not in run_block:
        run_block = run_block.replace("visible = true,\n", "visible = true,\n\t\t\t\thitable = true,\n", 1)
    insert_at = text.find("\n        end\n    end\nend\n\nfunction MapModule:openAddDiy")
    if insert_at > 0:
        text = text[:insert_at] + "\n" + run_block.rstrip() + text[insert_at:]
        log("moved run button")

input_y_old = """\t\t\t--input y
\t\t\tself.inputY = win:AddTextInput({
\t\t\t\tname = '坐标y',
\t\t\t\tx = UI.INPUT_Y_X,
\t\t\t\ty = INPUT_Y + UI.INPUT_Y_OFFSET,
\t\t\t\twidth = UI.INPUT_WIDTH,
\t\t\t\theight = UI.INPUT_HEIGHT,
\t\t\t\ttext = '0',
\t\t\t\tfont = 1,
\t\t\t\tcolor = 5,
\t\t\t\tmaxLength = 10,
\t\t\t\tvisible = true,
\t\t\t\thitable = true,
\t\t\t})"""
input_y_new = input_y_old.replace(
    "\t\t\t\thitable = true,\n\t\t\t})",
    "\t\t\t\thitable = true,\n\t\t\t\tonEnter = function()\n                    local x, y = self:_resolveNavCoords()\n                    self:_queueNavigation(x, y)\n                    return true\n                end\n\t\t\t})",
)
if input_y_old in text:
    text = text.replace(input_y_old, input_y_new, 1)
    log("patched inputY onEnter")

DST.write_text(text, encoding="gbk")
final = DST.read_text(encoding="gbk")

# validation
errors = []
if "?" in final[final.find("local combox"):final.find("local combox")+40]:
    errors.append("combox var corrupted")
if "function MapModule:_queueNavigation" not in final:
    errors.append("missing _queueNavigation")
if "return MapModule" not in final:
    errors.append("missing return")
# extract combox line
for line in final.splitlines():
    if line.startswith("local combox"):
        log("combox_line_ok=" + str("?" not in line))
        break

log(f"final_bytes={DST.stat().st_size}")
if errors:
    log("ERRORS: " + ", ".join(errors))
    sys.exit(1)
log("SUCCESS")
