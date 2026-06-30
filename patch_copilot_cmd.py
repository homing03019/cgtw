# -*- coding: utf-8 -*-
"""Make map UI dispatch /copilot x y via copilot module."""
import pathlib
import sys

DST = pathlib.Path(r"D:/cgtw/luaUI/modules/map.lua")
text = DST.read_text(encoding="gbk")

old_run = """function MapModule:_runPendingNavigation()
    local pending = self._navPending
    if not pending then
        return false
    end
    self._navPending = nil

    self:closeAddDiyWin()
    self:closeDelConfirm()
    if self.mapWin and self.mapWin.valid then
        self.mapWin:Close()
    end
    self.mapWin = nil
    self.mapVisible = false

    local copilot = self:getModule('copilot')
    if copilot then
        copilot:autoCopilot(pending.x, pending.y)
    else
        WinMgr.AutoCopilot(pending.x, pending.y)
    end
    return true
end"""

new_run = """function MapModule:_runPendingNavigation()
    local pending = self._navPending
    if not pending then
        return false
    end

    if not pending.ready then
        self:closeAddDiyWin()
        self:closeDelConfirm()
        if self.mapWin and self.mapWin.valid then
            self.mapWin:Close()
        end
        self.mapWin = nil
        self.mapVisible = false
        pending.ready = true
        return true
    end

    self._navPending = nil
    local cmd = string.format('/copilot %d %d', pending.x, pending.y)
    local copilot = self:getModule('copilot')
    if copilot and copilot.dispatchCommand then
        copilot:dispatchCommand(cmd)
    elseif copilot then
        copilot:autoCopilot(pending.x, pending.y)
    else
        WinMgr.AutoCopilot(pending.x, pending.y)
    end
    return true
end"""

if old_run not in text:
    pathlib.Path(r"D:/cgtw/patch_copilot_cmd_log.txt").write_text(
        "ERROR: _runPendingNavigation block not found\n", encoding="utf-8"
    )
    sys.exit(1)
text = text.replace(old_run, new_run, 1)

old_onload = """    self.addDiyWin = nil
    self.delConfirmWin = nil
end

function MapModule:_sceneStateChanged"""
new_onload = """    self.addDiyWin = nil
    self.delConfirmWin = nil
    self._navPending = nil
end

function MapModule:_sceneStateChanged"""
if "self._navPending = nil" not in text:
    text = text.replace(old_onload, new_onload, 1)

# remove duplicate chat tip; copilot module shows its own message
old_msg = """                    WinMgr.CliSendMsg(string.format("寻路开始，目的地：东:%d 南:%d", targetX, targetY))

                    if self.map"""
new_msg = """                    if self.map"""
if old_msg in text:
    text = text.replace(old_msg, new_msg, 1)

DST.write_text(text, encoding="gbk")
pathlib.Path(r"D:/cgtw/patch_copilot_cmd_log.txt").write_text("SUCCESS\n", encoding="utf-8")
