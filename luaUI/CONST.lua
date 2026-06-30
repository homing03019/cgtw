---@class CONST_UIControl_TYPE
---@field NONE integer @0
---@field IMAGE integer @1
---@field TEXT integer @2
---@field PNG_IMAGE integer @3
---@field TEXT_INPUT integer @4

---@class CONST_UIControl_MOUSE_STATE
---@field NONE integer @0
---@field HOVER integer @1
---@field PRESS integer @2

---@class CONST_UIControl
---@field TYPE CONST_UIControl_TYPE
---@field MOUSE_STATE CONST_UIControl_MOUSE_STATE

---@class CONST_MouseFlags
---@field NONE integer @0x0
---@field HOVER integer @0x1
---@field L_DOWN_EVENT integer @0x2
---@field R_DOWN_EVENT integer @0x4
---@field L_HOLD_PHYSICAL integer @0x8
---@field R_HOLD_PHYSICAL integer @0x10
---@field DRAGGING integer @0x20
---@field DRAG_FINISH integer @0x40
---@field L_DBL_CLICK_EVENT integer @0x100
---@field R_DBL_CLICK_EVENT integer @0x200
---@field L_REPEAT_DOWN integer @0x400
---@field R_REPEAT_DOWN integer @0x800

---@class CONST_KeyStateFlag
---@field UP_EDGE integer @0x01，WM_KEYUP 本帧发生
---@field DOWN integer @0x02，当前按住
---@field DOWN_EDGE integer @0x04，首次按下，不含按住重复
---@field DOWN_LATCH integer @0x08，已进入按下周期，防止重复触发 DOWN_EDGE
---@field DOWN_MESSAGE integer @0x10，WM_KEYDOWN 本帧发生，含按住重复

---@class CONST_VK
---@field [integer] string @VK 数值到名称
---@field [string] integer @名称到 VK 数值

---@class CONST
---@field UIControl CONST_UIControl
---@field MouseFlags CONST_MouseFlags
---@field KeyStateFlag CONST_KeyStateFlag
---@field VK CONST_VK

---@type CONST
CONST = CONST or {}

CONST.UIControl = CONST.UIControl or {}
CONST.UIControl.TYPE = CONST.UIControl.TYPE or {
    NONE = 0,
    IMAGE = 1,
    TEXT = 2,
    PNG_IMAGE = 3,
    TEXT_INPUT = 4,
}

CONST.UIControl.MOUSE_STATE = CONST.UIControl.MOUSE_STATE or {
    NONE = 0,
    HOVER = 1,
    PRESS = 2,
}

CONST.MouseFlags = CONST.MouseFlags or {
    NONE = 0x0,
    HOVER = 0x1,
    L_DOWN_EVENT = 0x2,
    R_DOWN_EVENT = 0x4,
    L_HOLD_PHYSICAL = 0x8,
    R_HOLD_PHYSICAL = 0x10,
    DRAGGING = 0x20,
    DRAG_FINISH = 0x40,
    L_DBL_CLICK_EVENT = 0x100,
    R_DBL_CLICK_EVENT = 0x200,
    L_REPEAT_DOWN = 0x400,
    R_REPEAT_DOWN = 0x800,
}

CONST.KeyStateFlag = CONST.KeyStateFlag or {
    UP_EDGE = 0x01,
    DOWN = 0x02,
    DOWN_EDGE = 0x04,
    DOWN_LATCH = 0x08,
    DOWN_MESSAGE = 0x10,
}

CONST.VK = CONST.VK or {}

local function addVk(code, name)
    CONST.VK[code] = name
    CONST.VK[name] = code
end

-- 鼠标
addVk(0x01, "LBUTTON")
addVk(0x02, "RBUTTON")
addVk(0x03, "CANCEL")
addVk(0x04, "MBUTTON")
addVk(0x05, "XBUTTON1")
addVk(0x06, "XBUTTON2")

-- 控制键
addVk(0x08, "BACK")
addVk(0x09, "TAB")
addVk(0x0D, "ENTER")
addVk(0x10, "SHIFT")
addVk(0x11, "CTRL")
addVk(0x12, "ALT")
addVk(0x13, "PAUSE")
addVk(0x14, "CAPSLOCK")
addVk(0x1B, "ESC")

-- 空白 / 导航
addVk(0x20, "SPACE")
addVk(0x21, "PGUP")
addVk(0x22, "PGDN")
addVk(0x23, "END")
addVk(0x24, "HOME")
addVk(0x25, "LEFT")
addVk(0x26, "UP")
addVk(0x27, "RIGHT")
addVk(0x28, "DOWN")

-- 插入删除
addVk(0x2D, "INS")
addVk(0x2E, "DEL")

-- 数字 0-9
for i = 0, 9 do
    local code = 0x30 + i
    local name = tostring(i)
    addVk(code, name)
end

-- 字母 A-Z
for i = 65, 90 do
    local c = string.char(i)
    addVk(i, c)
end

-- Win 键
addVk(0x5B, "LWIN")
addVk(0x5C, "RWIN")
addVk(0x5D, "APPS")

-- 小键盘
addVk(0x60, "NUMPAD0")
addVk(0x61, "NUMPAD1")
addVk(0x62, "NUMPAD2")
addVk(0x63, "NUMPAD3")
addVk(0x64, "NUMPAD4")
addVk(0x65, "NUMPAD5")
addVk(0x66, "NUMPAD6")
addVk(0x67, "NUMPAD7")
addVk(0x68, "NUMPAD8")
addVk(0x69, "NUMPAD9")

addVk(0x6A, "MULTIPLY")
addVk(0x6B, "ADD")
addVk(0x6C, "SEPARATOR")
addVk(0x6D, "SUBTRACT")
addVk(0x6E, "DECIMAL")
addVk(0x6F, "DIVIDE")

-- F1-F24
for i = 1, 24 do
    local code = 0x70 + (i - 1)
    addVk(code, "F" .. i)
end

-- 锁
addVk(0x90, "NUMLOCK")
addVk(0x91, "SCROLLLOCK")

-- 左右修饰键
addVk(0xA0, "LSHIFT")
addVk(0xA1, "RSHIFT")
addVk(0xA2, "LCTRL")
addVk(0xA3, "RCTRL")
addVk(0xA4, "LALT")
addVk(0xA5, "RALT")

-- 浏览器键
addVk(0xA6, "BROWSER_BACK")
addVk(0xA7, "BROWSER_FORWARD")
addVk(0xA8, "BROWSER_REFRESH")
addVk(0xA9, "BROWSER_STOP")
addVk(0xAA, "BROWSER_SEARCH")
addVk(0xAB, "BROWSER_FAVORITES")
addVk(0xAC, "BROWSER_HOME")

-- 音量
addVk(0xAD, "VOLUME_MUTE")
addVk(0xAE, "VOLUME_DOWN")
addVk(0xAF, "VOLUME_UP")

-- 多媒体
addVk(0xB0, "MEDIA_NEXT")
addVk(0xB1, "MEDIA_PREV")
addVk(0xB2, "MEDIA_STOP")
addVk(0xB3, "MEDIA_PLAY")

-- 启动
addVk(0xB4, "LAUNCH_MAIL")
addVk(0xB5, "LAUNCH_MEDIA")
addVk(0xB6, "LAUNCH_APP1")
addVk(0xB7, "LAUNCH_APP2")

-- OEM / 标点键
addVk(0xBA, "OEM_1")
addVk(0xBB, "OEM_PLUS")
addVk(0xBC, "OEM_COMMA")
addVk(0xBD, "OEM_MINUS")
addVk(0xBE, "OEM_PERIOD")
addVk(0xBF, "OEM_2")
addVk(0xC0, "OEM_3")
addVk(0xDB, "OEM_4")
addVk(0xDC, "OEM_5")
addVk(0xDD, "OEM_6")
addVk(0xDE, "OEM_7")
addVk(0xDF, "OEM_8")
addVk(0xE2, "OEM_102")

---@type CONST_VK
VK = CONST.VK
