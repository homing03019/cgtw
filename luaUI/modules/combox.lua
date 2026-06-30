---@class ComboxModule : ModuleBase
local ComboxModule = ModuleBase:extend('combox')

local WIN_COMBOX = 201
local WINDOW_LAYER = 4
local DEFAULT_ITEM_HEIGHT = 16
local DEFAULT_FONT = 4
local DEFAULT_COLOR = 0
local HOVER_FONT = 3
local HOVER_COLOR = 1

local function to_number(value, defaultValue)
    local n = tonumber(value)
    if not n then
        return defaultValue
    end
    return n
end

local function to_item_text(item)
    if item == nil then
        return ''
    end
    return tostring(item)
end

local function valid_item_height(value)
    local n = to_number(value, DEFAULT_ITEM_HEIGHT)
    if n <= 0 then
        return DEFAULT_ITEM_HEIGHT
    end
    return n
end

function ComboxModule:_unregisterFocus()
    if self.focusHandle then
        self:unregisterHandle(self.focusHandle)
        self.focusHandle = nil
    end
end

function ComboxModule:_closeCombox()
    self:_unregisterFocus()
    if self.comboxWnd and self.comboxWnd.valid then
        self:releaseWindow(self.comboxWnd)
    end
    self.comboxWnd = nil
    self.comboxState = nil
end

function ComboxModule:_cancelCombox()
    local state = self.comboxState
    if not state or state.closed or state.selected then
        return true
    end

    state.closed = true
    if type(state.onSelectedCallback) == 'function' then
        state.onSelectedCallback(nil, -1)
    end
    self:_closeCombox()
    return true
end

function ComboxModule:_selectItem(item, index)
    local state = self.comboxState
    if not state or state.closed or state.selected then
        return true
    end

    state.selected = true
    state.closed = true
    if type(state.onSelectedCallback) == 'function' then
        state.onSelectedCallback(item, index)
    end
    self:_closeCombox()
    return true
end

function ComboxModule:_addDefaultItem(win, item, index, y, width, parent, clickCallback, itemHeight)
    win:AddText({
        name = 'comboxItem' .. tostring(index),
        parent = parent,
        x = 0,
        y = y,
        width = width,
        height = itemHeight,
        text = to_item_text(item),
        font = DEFAULT_FONT,
        color = DEFAULT_COLOR,
        hitable = true,
        visible = true,
        onClick = function()
            return clickCallback()
        end,
        onHover = function(control)
            control:Set({ color = HOVER_COLOR, font = HOVER_FONT })
            return true
        end,
        onLeave = function(control)
            control:Set({ color = DEFAULT_COLOR, font = DEFAULT_FONT })
            return true
        end,
    })
end

function ComboxModule:OpenComboBox(param)
    param = type(param) == 'table' and param or {}
    self:_closeCombox()

    local itemList = param.itemList
    local onSelectedCallback = param.onSelectedCallback
    if type(itemList) ~= 'table' or #itemList <= 0 then
        if type(onSelectedCallback) == 'function' then
            onSelectedCallback(nil, -1)
        end
        return nil
    end

    local itemHeight = valid_item_height(param.itemHeight)
    local width = to_number(param.width, 0)
    local maxHeight = to_number(param.maxHeight, itemHeight)
    local contentHeight = #itemList * itemHeight
    local status, win = self:newWindow({
        id = WIN_COMBOX,
        x = to_number(param.x, 0),
        y = to_number(param.y, 0),
        width = width,
        height = maxHeight,
        layer = WINDOW_LAYER,
        draw = function(win)
            win:DrawRect({ x = 0, y = 0, width = width, height = maxHeight, color = 0x7f000000 })
        end
    })

    self.status = status
    self.comboxWnd = win
    self.comboxState = {
        selected = false,
        closed = false,
        onSelectedCallback = onSelectedCallback,
    }

    if not win then
        self.comboxState = nil
        return nil
    end

    local parent = nil
    if contentHeight > maxHeight then
        parent = win:AddScrollView({
            x = 0,
            y = 0,
            width = width,
            height = maxHeight,
            contentHeight = contentHeight,
            scrollStep = itemHeight,
            visible = true,
        })
    end

    local createFn = param.itemCreateFn
    for i = 1, #itemList do
        local item = itemList[i]
        local y = (i - 1) * itemHeight
        local clickCallback = function()
            return self:_selectItem(item, i)
        end

        if type(createFn) == 'function' then
            createFn(win, item, i, y, width, parent, clickCallback)
        else
            self:_addDefaultItem(win, item, i, y, width, parent, clickCallback, itemHeight)
        end
    end

    self.focusHandle = self:onWindowFocusChanged(function(focusWinId, blurWinId)
        print("onWindowFocusChanged", focusWinId, blurWinId);
        if blurWinId == WIN_COMBOX and focusWinId ~= WIN_COMBOX then
            print("_cancelCombox", focusWinId, blurWinId);
            return self:_cancelCombox()
        end
    end)

    self:focus(win.id);

    return win
end

function ComboxModule:onUnload()
    self:_closeCombox()
    self.status = nil
end

return ComboxModule
