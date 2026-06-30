# -*- coding: utf-8 -*-
"""Fix map nav: close window first, then /copilot on OnWindowClose."""
import pathlib
import re
import sys

DST = pathlib.Path(r"D:/cgtw/luaUI/modules/map.lua")
text = DST.read_text(encoding="gbk")
LOG = []

def must_contain(needle, msg):
    if needle not in text:
        LOG.append("ERROR: " + msg)
        pathlib.Path(r"D:/cgtw/patch_fix_log.txt").write_text("\n".join(LOG), encoding="utf-8")
        sys.exit(1)

# remove old deferred navigation if present
text = re.sub(
    r"\nfunction MapModule:_runPendingNavigation\(\).*?\nend\n",
    "\n",
    text,
    count=1,
    flags=re.DOTALL,
)

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
    if (not targetX or targetX <= 0 or not targetY or targetY <= 0) and self.savedTargetPoint then
        targetX = self.savedTargetPoint.x
        targetY = self.savedTargetPoint.y
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

function MapModule:_beginCopilotNav(targetX, targetY)
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

    self._navAfterClose = { x = targetX, y = targetY }
    self:closeAddDiyWin()
    self:closeDelConfirm()

    if self.mapWin and self.mapWin.valid then
        self.mapWin:Close()
        return true
    end

    self.mapWin = nil
    self.mapVisible = false
    local pending = self._navAfterClose
    self._navAfterClose = nil
    self:_dispatchCopilotNav(pending.x, pending.y)
    return true
end

"""

if "function MapModule:_beginCopilotNav" not in text:
    text = text.replace("function MapModule:updateMapPoints()", helpers + "function MapModule:updateMapPoints()", 1)

# onLoad: window close handler
old_onload = """    self.addDiyWin = nil
    self.delConfirmWin = nil
    self._navPending = nil
end

function MapModule:_sceneStateChanged"""
new_onload = """    self.addDiyWin = nil
    self.delConfirmWin = nil
    self._navAfterClose = nil
    self.closeNavHandler = self:OnWindowClose(function(winId)
        if winId ~= WIN_MAP then
            return
        end
        local pending = self._navAfterClose
        if not pending then
            return
        end
        self._navAfterClose = nil
        self.mapWin = nil
        self.mapVisible = false
        self:_dispatchCopilotNav(pending.x, pending.y)
    end)
end

function MapModule:_sceneStateChanged"""
if "self.closeNavHandler" not in text:
    if old_onload in text:
        text = text.replace(old_onload, new_onload, 1)
    else:
        text = text.replace(
            "    self.addDiyWin = nil\n    self.delConfirmWin = nil\nend\n\nfunction MapModule:_sceneStateChanged",
            new_onload.replace("    self._navPending = nil\n", ""),
            1,
        )

# window update: remove pending nav hook
text = text.replace(
    """                if self._navPending then
                    self:_runPendingNavigation()
                end
                self:updateMapPoints()""",
    "                self:updateMapPoints()",
)

# layout alignment
text = text.replace(
    "        local INPUT_Y = PAGE_Y + 50\n        local BTN_Y = INPUT_Y + 52",
    "        local INPUT_Y = UI.INPUT_Y\n        local BTN_Y = UI.RUN_BTN_Y",
)

# run button handler
run_old = """				onClick = function()
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
                    return true
                end"""
run_new = """				onClick = function()
                    local targetX, targetY = self:_resolveNavCoords()
                    self:_beginCopilotNav(targetX, targetY)
                    return true
                end"""
must_contain("onClick = function()", "run button")
if run_old in text:
    text = text.replace(run_old, run_new, 1)
elif "self:_beginCopilotNav" not in text:
    LOG.append("WARN: exact run button block not found")

# move run button to end + larger hit area
run_pat = re.compile(r"\t\t\t--执行按钮\n\t\t\twin:AddPngImage\(\{.*?\n\t\t\t\}\)\n", re.DOTALL)
run_match = run_pat.search(text)
if run_match and text.find("self.searchInput = win:AddTextInput", run_match.start()) > 0:
    run_block = run_match.group(0)
    text = text[: run_match.start()] + text[run_match.end() :]
    run_block = run_block.replace("x = UI.RUN_BTN_X,\n\t\t\t\ty = BTN_Y,", "x = UI.RUN_BTN_X - 8,\n\t\t\t\ty = UI.RUN_BTN_Y - 6,")
    run_block = run_block.replace("width = UI.RUN_BTN_WIDTH,\n\t\t\t\theight = UI.RUN_BTN_HEIGHT,", "width = UI.RUN_BTN_WIDTH + 16,\n\t\t\t\theight = UI.RUN_BTN_HEIGHT + 12,")
    insert_at = text.find("\n        end\n    end\nend\n\nfunction MapModule:openAddDiy")
    if insert_at > 0:
        text = text[:insert_at] + "\n" + run_block.rstrip() + text[insert_at:]

# onUnload cleanup
if "self.closeNavHandler" not in text.split("function MapModule:onUnload")[1][:800]:
    text = text.replace(
        "    if self.sceneHandler and self.sceneHandler.valid then\n        self.sceneHandler:Unregister()\n    end\n    self.warpEvent = nil\n    self.sceneHandler = nil",
        "    if self.sceneHandler and self.sceneHandler.valid then\n        self.sceneHandler:Unregister()\n    end\n    if self.closeNavHandler and self.closeNavHandler.valid then\n        self.closeNavHandler:Unregister()\n    end\n    self.warpEvent = nil\n    self.sceneHandler = nil\n    self.closeNavHandler = nil\n    self._navAfterClose = nil",
        1,
    )

DST.write_text(text, encoding="gbk")
pathlib.Path(r"D:/cgtw/patch_fix_log.txt").write_text("SUCCESS\n" + "\n".join(LOG), encoding="utf-8")
