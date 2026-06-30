local PATH_SEP = string.char(92)
local LUAUI_BASE = rawget(_G, 'LUAUI_BASE') or ('luaUI' .. PATH_SEP)
if LUAUI_BASE ~= '' then
    local tail = string.sub(LUAUI_BASE, -1)
    if tail ~= PATH_SEP and tail ~= '/' then
        LUAUI_BASE = LUAUI_BASE .. PATH_SEP
    end
end
_G.LUAUI_BASE = LUAUI_BASE

dofile(LUAUI_BASE .. 'CONST.lua')
local ModuleBase = dofile(LUAUI_BASE .. 'ModuleBase.lua')
local GlobalEvent = dofile(LUAUI_BASE .. 'GlobalEvent.lua')

_G.ModuleBase = ModuleBase
_G.GlobalEvent = GlobalEvent

local ModuleSystem = dofile(LUAUI_BASE .. 'ModuleSystem.lua')
_G.ModuleSystem = ModuleSystem

ModuleSystem:init({ basePath = LUAUI_BASE })

assert(pcall(dofile, LUAUI_BASE .. 'ModuleConfig.lua'))