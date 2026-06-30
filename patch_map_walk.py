# -*- coding: utf-8 -*-
"""Minimal GBK-safe fix: defer AutoCopilot to next frame (same path as /copilot)."""
import pathlib
import sys

DST = pathlib.Path(r"D:/cgtw/luaUI/modules/map.lua")
LOG = pathlib.Path(r"D:/cgtw/patch_walk_log.txt")
text = DST.read_text(encoding="gbk")

helper = """
function MapModule:_runPendingNavigation()
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
end

"""

marker = "function MapModule:updateMapPoints()"
if "function MapModule:_runPendingNavigation" not in text:
    text = text.replace(marker, helper + marker, 1)

old_update = """            update = function(window)
                if not window.valid then
                    return false
                end
                self:updateMapPoints()
                return false
            end,"""
new_update = """            update = function(window)
                if not window.valid then
                    return false
                end
                if self._navPending then
                    self:_runPendingNavigation()
                end
                self:updateMapPoints()
                return false
            end,"""
if old_update in text:
    text = text.replace(old_update, new_update, 1)

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

old_autopilot = """                    self:AutoCopilot(targetX, targetY)
                    return true
                end"""
new_autopilot = """                    self._navPending = { x = targetX, y = targetY }
                    return true
                end"""
if old_autopilot not in text:
    LOG.write_text("ERROR: run button block not found\n", encoding="utf-8")
    sys.exit(1)
text = text.replace(old_autopilot, new_autopilot, 1)

DST.write_text(text, encoding="gbk")
LOG.write_text("SUCCESS minimal walk patch applied\n", encoding="utf-8")
