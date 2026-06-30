# -*- coding: utf-8 -*-
"""
Map list click -> close map -> copilot dispatch (same as /copilot x y).
No Enter hook (caused reopen loop). No map.lua Chinese CliSendMsg (GBK garble).
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(r"D:/cgtw")
MAP = ROOT / "luaUI" / "modules" / "map.lua"
RESTORE = ROOT / "luaUI" / "scripts" / "restore_map_lua.py"

subprocess.check_call([sys.executable, str(RESTORE)])
text = MAP.read_text(encoding="gbk")

# --- strip prior nav patches ---
for pat in [
    r"\nfunction MapModule:_resolveNavCoords\(\).*?\nfunction MapModule:updateMapPoints\(\)",
    r"\nfunction MapModule:_beginNav\(targetX, targetY\).*?\nfunction MapModule:updateMapPoints\(\)",
]:
    text = re.sub(pat, "\nfunction MapModule:updateMapPoints()", text, count=1)

text = re.sub(
    r"\n        if self\.warpMode == MODE_SYSTEM or self\.warpMode == \"NPC\" then\n            self:_beginNav\(point\.x, point\.y\)\n        end",
    "",
    text,
)

for pat in [
    r"\n    self\._deferredNav = nil\n    self\._mapCloseNavHandler = self:OnWindowClose\(function\(winId\).*?\n    end\)\n    self\._navEnterHandler = self:OnKeyPress\(CONST\.VK\.ENTER.*?\n    end\)\n",
    r"\n    self\._nextCopilot = nil\n    self\._mapCloseNavHandler = self:OnWindowClose\(function\(winId\).*?\n    end\)\n    self\._navEnterHandler = self:OnKeyPress\(CONST\.VK\.ENTER.*?\n    end\)\n",
    r"\n    self\._navEnterHandler = self:OnKeyPress\(CONST\.VK\.ENTER.*?\n    end\)\n",
    r"\n    self\._deferredNav = nil\n(?=end\n\nfunction MapModule:_sceneStateChanged)",
]:
    text = re.sub(pat, "\n", text, count=1)

text = text.replace(
    """            update = function(window)
                if self._deferredNav and not self.mapVisible then
                    self:_flushDeferredNav()
                end
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
                self:updateMapPoints()
                return false
            end,""",
)

text = text.replace(
    """    if self._mapCloseNavHandler and self._mapCloseNavHandler.valid then
        self._mapCloseNavHandler:Unregister()
    end
    if self._navEnterHandler and self._navEnterHandler.valid then
        self._navEnterHandler:Unregister()
    end
    self._mapCloseNavHandler = nil
    self._navEnterHandler = nil
    self._deferredNav = nil
    self.warpEvent = nil""",
    "    self.warpEvent = nil",
)

text = text.replace("    self._deferredNav = nil\n    self.warpEvent = nil", "    self.warpEvent = nil")

# --- insert helpers (messages via copilot.lua only) ---
helpers = """
function MapModule:_flushDeferredNav()
    local pending = self._deferredNav
    if not pending then
        return false
    end
    if self.mapVisible then
        return false
    end
    self._deferredNav = nil
    local cmd = string.format('/copilot %d %d', pending.x, pending.y)
    local copilot = self:getModule('copilot')
    if copilot and copilot.dispatchCommand then
        copilot:dispatchCommand(cmd)
    else
        self:AutoCopilot(pending.x, pending.y)
    end
    return true
end

function MapModule:_beginNav(targetX, targetY)
    targetX = tonumber(targetX)
    targetY = tonumber(targetY)
    if not targetX or not targetY or targetX <= 0 or targetY <= 0 then
        return false
    end
    self._deferredNav = { x = targetX, y = targetY }
    if self.mapWin and self.mapWin.valid then
        self.mapWin:Close()
    end
    self:closeAddDiyWin()
    self:closeDelConfirm()
    self.mapWin = nil
    self.mapVisible = false
    self:_flushDeferredNav()
    return true
end

function MapModule:_runNavFromInputs()
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
    return self:_beginNav(targetX, targetY)
end

"""

if "_beginNav" not in text:
    text = text.replace("function MapModule:updateMapPoints()", helpers + "function MapModule:updateMapPoints()", 1)

# onWarpItemClick: select + nav (system/NPC)
warp_tail_old = """        self.selectedWarpIdx = actualIdx
        self:refreshWarpList()
    end
end

function split(str,split_char)"""
warp_tail_new = """        self.selectedWarpIdx = actualIdx
        self.targetPoint = { x = point.x, y = point.y }
        self:refreshWarpList()
        if self.warpMode == MODE_SYSTEM or self.warpMode == "NPC" then
            self:_beginNav(point.x, point.y)
        end
    end
end

function split(str,split_char)"""

if "_beginNav(point.x, point.y)" not in text:
    if "self.targetPoint = { x = point.x, y = point.y }" in text:
        text = text.replace(
            """        self.targetPoint = { x = point.x, y = point.y }
        self:refreshWarpList()
    end
end

function split(str,split_char)""",
            """        self.targetPoint = { x = point.x, y = point.y }
        self:refreshWarpList()
        if self.warpMode == MODE_SYSTEM or self.warpMode == "NPC" then
            self:_beginNav(point.x, point.y)
        end
    end
end

function split(str,split_char)""",
            1,
        )
    else:
        text = text.replace(warp_tail_old, warp_tail_new, 1)

# onLoad: init deferred only
if "self._deferredNav = nil" not in text.split("function MapModule:onLoad")[1].split("function MapModule:_sceneStateChanged")[0]:
    text = text.replace(
        "    self.addDiyWin = nil\n    self.delConfirmWin = nil\nend\n\nfunction MapModule:_sceneStateChanged",
        "    self.addDiyWin = nil\n    self.delConfirmWin = nil\n    self._deferredNav = nil\nend\n\nfunction MapModule:_sceneStateChanged",
        1,
    )

# ToggleMap open: clear pending nav
if "self._deferredNav = nil" not in text.split("function MapModule:ToggleMap")[1][:800]:
    text = text.replace(
        "    else\n        self.warpPoints = {}",
        "    else\n        self._deferredNav = nil\n        self.warpPoints = {}",
        1,
    )

# onUnload
if "self._deferredNav = nil" not in text.split("function MapModule:onUnload")[1][:400]:
    text = text.replace(
        "    self.warpEvent = nil\n    self.sceneHandler = nil\nend",
        "    self._deferredNav = nil\n    self.warpEvent = nil\n    self.sceneHandler = nil\nend",
        1,
    )

# fix chat handler
text = re.sub(
    r"(self:onChatMessage\(function\(text\)\s+if text == COMMAND then.*?return 1\s+end)\s+(?:return true\s+)?end\)",
    r"\1\n    end)",
    text,
    count=1,
    flags=re.DOTALL,
)

# list hit area
old_geom = "\t\t\t\tlocal textCtrl = win:AddText({\n\t\t\t\t\tx = UI.LIST_START_X,\n\t\t\t\t\ty = UI.LIST_START_Y + (i-1) * UI.LIST_ITEM_STEP_Y,\n\t\t\t\t\twidth = UI.LIST_WIDTH,\n\t\t\t\t\theight = UI.LIST_HEIGHT,"
new_geom = "\t\t\t\tlocal textCtrl = win:AddText({\n\t\t\t\t\tx = UI.LIST_START_X + UI.LIST_BG_X,\n\t\t\t\t\ty = UI.LIST_START_Y + (i-1) * UI.LIST_ITEM_STEP_Y + UI.LIST_BG_Y,\n\t\t\t\t\twidth = UI.LIST_BG_WIDTH,\n\t\t\t\t\theight = UI.LIST_BG_HEIGHT,"
if "LIST_BG_WIDTH" not in text.split("warpPageTexts[i]")[0].split("LIST_ITEM_COUNT")[1]:
    text = text.replace(old_geom, new_geom, 1)

# run button
while text.count("image = run_btn,") > 1:
    text = re.sub(
        r"\t\t\t--执行按钮\n\t\t\twin:AddPngImage\(\{.*?image = run_btn,.*?\n\t\t\t\}\)\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )

run_handlers = "\t\t\t\tonClick = function()\n\t\t\t\t\tself:_runNavFromInputs()\n\t\t\t\t\treturn true\n\t\t\t\tend\n"
run_pat = re.compile(
    r"(\t\t\t--执行按钮\n\t\t\twin:AddPngImage\(\{.*?image = run_btn,.*?)\t\t\t\ton(?:Click|Event) = function\(.*?\n(?:\t\t\t\t.*?\n)*?\t\t\t\tend(?:,\n\t\t\t\t\ton(?:Click|Event) = function\(.*?\n(?:\t\t\t\t.*?\n)*?\t\t\t\tend)?\n(\t\t\t\}\)\n)",
    re.DOTALL,
)
m = run_pat.search(text)
if not m:
    run_pat = re.compile(
        r"(\t\t\t--执行按钮\n\t\t\twin:AddPngImage\(\{.*?image = run_btn,.*?)\t\t\t\tonClick = function\(\).*?\n                end\n(\t\t\t\}\)\n)",
        re.DOTALL,
    )
    m = run_pat.search(text)
if not m:
    print("ERROR: run button not found", file=sys.stderr)
    sys.exit(1)

block = m.group(1) + run_handlers + m.group(2)
block = block.replace("y = UI.RUN_BTN_Y,", "y = BTN_Y,")
text = text[: m.start()] + block + text[m.end() :]

# move run button to top z-order
run_block_pat = re.compile(
    r"\t\t\t--执行按钮\n\t\t\twin:AddPngImage\(\{.*?image = run_btn,.*?\n\t\t\t\}\)\n",
    re.DOTALL,
)
rm = run_block_pat.search(text)
if rm:
    rb = rm.group(0)
    text = run_block_pat.sub("", text, count=1)
    anchor = "\t\t\tif self:GetAutoCopliotState() == 1 then"
    if anchor in text:
        text = text.replace(anchor, rb + anchor, 1)

# upgrade existing _flushDeferredNav if old patch left AutoCopilot-only version
if "copilot:dispatchCommand" not in text:
    text = text.replace(
        """    self._deferredNav = nil
    self:AutoCopilot(pending.x, pending.y)
    return true
end

function MapModule:_runNavFromInputs()""",
        """    self._deferredNav = nil
    local cmd = string.format('/copilot %d %d', pending.x, pending.y)
    local copilot = self:getModule('copilot')
    if copilot and copilot.dispatchCommand then
        copilot:dispatchCommand(cmd)
    else
        self:AutoCopilot(pending.x, pending.y)
    end
    return true
end

function MapModule:_runNavFromInputs()""",
        1,
    )

# remove map.lua CliSendMsg nav lines if still present
text = re.sub(
    r"\n    WinMgr\.CliSendMsg\([^)]+\)\n    self\._deferredNav",
    "\n    self._deferredNav",
    text,
    count=2,
)

for token in ["_navEnterHandler", "_mapCloseNavHandler", "WinMgr.CliSendMsg('寻路", "WinMgr.CliSendMsg('开始"]:
    if token in text:
        print(f"WARN: stale token remains: {token}", file=sys.stderr)

for need in ["_beginNav", "_flushDeferredNav", "copilot:dispatchCommand", "_beginNav(point.x, point.y)", "_runNavFromInputs()"]:
    if need not in text:
        print(f"ERROR: missing {need}", file=sys.stderr)
        sys.exit(1)
if text.count("image = run_btn,") != 1:
    print("ERROR: run button count", text.count("image = run_btn,"), file=sys.stderr)
    sys.exit(1)

MAP.write_text(text, encoding="gbk")
print(f"OK patched {MAP} ({MAP.stat().st_size} bytes)")
