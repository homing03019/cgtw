# -*- coding: utf-8 -*-
"""Save copilot.lua as GBK so CliSendMsg Chinese displays correctly in cg2d."""
import pathlib

path = pathlib.Path(r"D:/cgtw/luaUI/modules/copilot.lua")
text = """---@class CopilotModule : ModuleBase
local CopilotModule = ModuleBase:extend('copilot')

local COMMAND_STOP = '^%s*/copilot%s+stop%s*$'
local COMMAND_NAV = '^%s*/copilot%s+(%-?%d+)%s+(%-?%d+)%s*$'
local TIP_START = '开始自动导航: '
local TIP_STOP = '结束自动导航'

function CopilotModule:dispatchCommand(text)
    if type(text) ~= 'string' then
        return false
    end

    if string.match(text, COMMAND_STOP) then
        self:stopCopilot()
        self:cliSendMsg(TIP_STOP)
        return true
    end

    local x, y = string.match(text, COMMAND_NAV)
    if x and y then
        self:autoCopilot(tonumber(x), tonumber(y))
        self:cliSendMsg(TIP_START .. x .. ', ' .. y)
        return true
    end

    return false
end

function CopilotModule:onLoad()
    self:onChatMessage(function(text)
        if self:dispatchCommand(text) then
            return 1
        end
        return nil
    end)
end

return CopilotModule
"""
path.write_text(text, encoding="gbk")
# verify
path.read_text(encoding="gbk")
print(f"OK {path} GBK ({path.stat().st_size} bytes)")
