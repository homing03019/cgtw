---@class HelpBarModule : ModuleBase
local HelpBarModule = ModuleBase:extend('help_bar')

local WIN_HELP_BAR = 21001
local WIN_HELP_TAB = 21002
local WINDOW_WIDTH = 90
local TAB_WIDTH = 18
local WINDOW_TOP = 80
local WINDOW_RIGHT = 20
local BUTTON_WIDTH = 80
local BUTTON_HEIGHT = 32
local BUTTON_PADDING_X = 5
local BUTTON_PADDING_Y = 4
local BUTTON_PITCH = 36
local KEY_DOWN = 1

local VK_1 = 0x31
local VK_2 = 0x32
local VK_3 = 0x33
local VK_4 = 0x34
local VK_5 = 0x35
local VK_CTRL = 0x11
local VK_SHIFT = 0x10

local BACKGROUND = {
    image = 'images/help_bar_bg.png',
    width = 90,
    sourceHeight = 124,
    topHeight = 15,
    bottomHeight = 15,
}

local DEFAULT_BUTTON_IMAGES = {
    normal = 'images/help_bar_button.png',
    hover = 'images/help_bar_button_hover.png',
    press = 'images/help_bar_button_press.png',
}

local BUTTONS = {
    { text = '内挂', color = 0, packet = 'HBMenu', images = nil },
    { text = '佣兵', color = 0, packet = 'HBHero', images = nil },
    { text = '背包', color = 0, packet = 'HBBag', images = nil },
    { text = '收起', color = 0, packet = nil, images = nil, action = 'collapse' },
}

local function button_images(button)
    local images = button.images or DEFAULT_BUTTON_IMAGES
    return images.normal or DEFAULT_BUTTON_IMAGES.normal,
        images.hover or images.normal or DEFAULT_BUTTON_IMAGES.hover,
        images.press or images.normal or DEFAULT_BUTTON_IMAGES.press
end

function HelpBarModule:sendAction(packet)
    if packet ~= nil and packet ~= '' then
        self:sendPacket(packet)
    end
end

function HelpBarModule:closeWindows()
    if self.win and self.win.valid then
        self.win:Close()
    end
    if self.tabWin and self.tabWin.valid then
        self.tabWin:Close()
    end
    self.win = nil
    self.tabWin = nil
end

function HelpBarModule:buildPanel()
    if self.collapsed then
        self:buildTab()
        return
    end

    local windowHeight = #BUTTONS * (BUTTON_HEIGHT + 4) + 30
    local x = CONST.Screen.Width - WINDOW_RIGHT - WINDOW_WIDTH
    local status, win = self:newWindow({
        id = WIN_HELP_BAR,
        x = x,
        y = WINDOW_TOP,
        width = WINDOW_WIDTH,
        height = windowHeight,
        layer = 4,
    })
    self.win = win
    if not win then
        return
    end

    local topHeight = BACKGROUND.topHeight
    local bottomHeight = BACKGROUND.bottomHeight
    local middleSourceHeight = BACKGROUND.sourceHeight - topHeight - bottomHeight
    local middleHeight = windowHeight - topHeight - bottomHeight

    win:AddPngImage({
        name = 'helpBarBgTop',
        x = 0, y = 0,
        width = BACKGROUND.width, height = topHeight,
        image = BACKGROUND.image,
        imageRect = { x = 0, y = 0, width = BACKGROUND.width, height = topHeight },
        visible = true, hitable = false,
    })

    if middleHeight > 0 and middleSourceHeight > 0 then
        win:AddPngImage({
            name = 'helpBarBgMiddle',
            x = 0, y = topHeight,
            width = BACKGROUND.width, height = middleHeight,
            image = BACKGROUND.image,
            imageRect = { x = 0, y = topHeight, width = BACKGROUND.width, height = middleSourceHeight },
            visible = true, hitable = false,
        })
    end

    win:AddPngImage({
        name = 'helpBarBgBottom',
        x = 0, y = windowHeight - bottomHeight,
        width = BACKGROUND.width, height = bottomHeight,
        image = BACKGROUND.image,
        imageRect = { x = 0, y = BACKGROUND.sourceHeight - bottomHeight, width = BACKGROUND.width, height = bottomHeight },
        visible = true, hitable = false,
    })

    for i = 1, #BUTTONS do
        local button = BUTTONS[i]
        local y = BUTTON_PADDING_Y / 2 + (i - 1) * BUTTON_PITCH + 15
        local image, imageHover, imagePress = button_images(button)
        local module = self

        win:AddPngImage({
            name = 'helpBarButton' .. tostring(i),
            x = BUTTON_PADDING_X, y = y,
            width = BUTTON_WIDTH, height = BUTTON_HEIGHT,
            image = image, imageHover = imageHover, imagePress = imagePress,
            visible = true,
            onClick = function()
                if button.action == 'collapse' then
                    module.collapsed = true
                    module:closeWindows()
                    module:buildPanel()
                    return true
                end
                module:sendAction(button.packet)
                return true
            end,
        })

        win:AddText({
            name = 'helpBarButtonText' .. tostring(i),
            x = BUTTON_PADDING_X + 8, y = y + 8,
            width = BUTTON_WIDTH, height = BUTTON_HEIGHT,
            text = button.text or '', font = 0, color = button.color or 0,
            hitable = false, visible = true,
        })
    end
end

function HelpBarModule:buildTab()
    local x = CONST.Screen.Width - WINDOW_RIGHT - TAB_WIDTH
    local status, win = self:newWindow({
        id = WIN_HELP_TAB, x = x, y = WINDOW_TOP + 40,
        width = TAB_WIDTH, height = 48, layer = 4,
    })
    self.tabWin = win
    if not win then return end

    local module = self
    win:AddText({
        name = 'helpBarTabText',
        x = 2, y = 16, width = TAB_WIDTH, height = 20,
        text = '<<', font = 0, color = 0,
        hitable = true, visible = true,
        onClick = function()
            module.collapsed = false
            module:closeWindows()
            module:buildPanel()
            return true
        end,
    })
end

function HelpBarModule:registerHotkeys()
    local module = self
    self:OnKeyPress(VK_1, KEY_DOWN, function() module:sendAction('HBMenu') end)
    self:OnKeyPress(VK_2, KEY_DOWN, function() module:sendAction('HBHero') end)
    self:OnKeyPress(VK_3, KEY_DOWN, function() module:sendAction('HBBag') end)
    self:OnKeyPress(VK_1, { VK_CTRL }, KEY_DOWN, function() module:sendAction('HBMenu') end)
    self:OnKeyPress(VK_2, { VK_CTRL }, KEY_DOWN, function() module:sendAction('HBHero') end)
    self:OnKeyPress(VK_3, { VK_CTRL }, KEY_DOWN, function() module:sendAction('HBBag') end)
    for i = 1, 3 do
        local packet = 'HBBag' .. tostring(i)
        local vk = 0x30 + i
        self:OnKeyPress(vk, { VK_SHIFT }, KEY_DOWN, function()
            module:sendAction(packet)
        end)
    end
end

function HelpBarModule:onLoad()
    self.collapsed = false
    self:registerHotkeys()
    self:onSceneStateChanged(function(sceneType, sceneState)
        if sceneType ~= 9 then
            self:closeWindows()
            return
        end
        self:closeWindows()
        self:buildPanel()
    end)
end

function HelpBarModule:onUnload()
    self:closeWindows()
    self.collapsed = nil
end

return HelpBarModule
