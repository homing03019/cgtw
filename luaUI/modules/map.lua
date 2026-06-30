--首发bbs.cnmlb.com
--M佬前端版本：0.4.4
--lua：老王298582478、小黑396750012
--M佬牛B！！！！！！
local MapModule = ModuleBase:extend('mapmodule')
local WIN_MAP = 2002
local add_diy = 2003
local del_diy = 2004
local COMMAND = 'map'
local MODE_SYSTEM = 1
local MODE_CUSTOM = 2

-- ====================== UI坐标配置（800分辨率）======================
local UI_800 = {
	BG_IMG = 'images/map/bg.png',
    -- 窗口
    WIN_X = 0,
    WIN_Y = -30,
	WIN_WIDTH = 760,
	WIN_HEIGHT = 472,
	
    -- 地图
    MAP_X = 19,
    MAP_Y = 39,
    MAP_WIDTH = 522,
    MAP_HEIGHT = 400,

    -- 鼠标坐标标签
    MOUSE_LABEL_X = 0,
    MOUSE_LABEL_Y = 0,

    -- 模式切换按钮
    BTN_START_X = 551,
    BTN_START_Y = 39,
    BTN_WIDTH = 56,
    BTN_HEIGHT = 25,
    BTN_GAP = 2,
    BTN_TEXT_Y = 7,
    BTN_TEXT1_X = 10,
    BTN_TEXT2_X = 16,
    BTN_TEXT3_X = 4,

    -- 列表
    LIST_START_X = 560,
    LIST_START_Y = 75,
    LIST_ITEM_COUNT = 9,
    LIST_ITEM_STEP_Y = 26,
    LIST_WIDTH = 130,
    LIST_HEIGHT = 20,
    LIST_BG_X = -5,
    LIST_BG_Y = -5,
    LIST_BG_WIDTH = 164,
    LIST_BG_HEIGHT = 22,

    -- 页码和翻页
    PAGE_X = 625,
    PAGE_Y = 283,
    L_ARROW_X = 595,
    R_ARROW_X = 675,
    ARROW_WIDTH = 11,
    ARROW_HEIGHT = 13,

    -- 坐标输入区
    COORD_IMG_X = 553,
    INPUT_X_X = 590,
    INPUT_Y_X = 655,
    INPUT_Y = 333,
    INPUT_Y_OFFSET = 2,
    INPUT_WIDTH = 60,
    INPUT_HEIGHT = 18,

    -- 搜索
    SEARCH_X = 555,
    SEARCH_BTN_X = 652,
    SEARCH_BTN_Y_OFFSET = 26,
    SEARCH_WIDTH = 94,
    SEARCH_HEIGHT = 20,
    SEARCH_BTN_WIDTH = 65,
    SEARCH_BTN_HEIGHT = 23,

    -- 执行按钮
    RUN_BTN_X = 605,
    RUN_BTN_Y = 385,
    RUN_BTN_WIDTH = 65,
    RUN_BTN_HEIGHT = 23,

    -- 添加删除按钮
    ADD_BTN_X = 580,
    ADD_BTN_Y_OFFSET = 23,
    DEL_BTN_X = 650,
    DEL_BTN_WIDTH = 54,
    DEL_BTN_HEIGHT = 17,

    -- 关闭按钮
    CLOSE_X = 710,
    CLOSE_Y = 8,
    CLOSE_WIDTH = 15,
    CLOSE_HEIGHT = 15,
}


-- ====================== UI坐标配置（640分辨率）======================
local UI_640 = {
	BG_IMG = 'images/map/bg2.png',
    -- 窗口
    WIN_X = 0,
    WIN_Y = -25,
    WIN_WIDTH = 562,
    WIN_HEIGHT = 400,

    -- 地图
    MAP_X = 19,
    MAP_Y = 39,
    MAP_WIDTH = 325,
    MAP_HEIGHT = 343,

    -- 鼠标坐标标签
    MOUSE_LABEL_X = 0,
    MOUSE_LABEL_Y = 0,

    -- 模式切换按钮
    BTN_START_X = 350,
    BTN_START_Y = 38,
    BTN_WIDTH = 56,
    BTN_HEIGHT = 25,
    BTN_GAP = 2,
    BTN_TEXT_Y = 7,
    BTN_TEXT1_X = 10,
    BTN_TEXT2_X = 16,
    BTN_TEXT3_X = 4,

    -- 列表
    LIST_START_X = 360,    
    LIST_START_Y = 75,
    LIST_ITEM_STEP_Y = 25,
	LIST_ITEM_COUNT = 7, 
    LIST_WIDTH = 130,
    LIST_HEIGHT = 20,
    LIST_BG_X = -5,
    LIST_BG_Y = -5,
    LIST_BG_WIDTH = 164,
    LIST_BG_HEIGHT = 22,

    -- 页码和翻页
    PAGE_X = 425,          
    PAGE_Y = 283,
    L_ARROW_X = 395,       
    R_ARROW_X = 475,       
    ARROW_WIDTH = 11,
    ARROW_HEIGHT = 13,

    -- 坐标输入区
    COORD_IMG_X = 353,     
    INPUT_X_X = 390,       
    INPUT_Y_X = 455,       
    INPUT_Y = 333,
    INPUT_Y_OFFSET = 2,
    INPUT_WIDTH = 60,
    INPUT_HEIGHT = 18,

    -- 搜索
    SEARCH_X = 355,        
    SEARCH_BTN_X = 452,    
    SEARCH_BTN_Y_OFFSET = 26,
    SEARCH_WIDTH = 94,
    SEARCH_HEIGHT = 20,
    SEARCH_BTN_WIDTH = 65,
    SEARCH_BTN_HEIGHT = 23,

    -- 执行按钮
    RUN_BTN_X = 405,       
    RUN_BTN_Y = 385,
    RUN_BTN_WIDTH = 65,
    RUN_BTN_HEIGHT = 23,

    -- 添加删除按钮
    ADD_BTN_X = 380,       
    ADD_BTN_Y_OFFSET = 23,
    DEL_BTN_X = 450,      
    DEL_BTN_WIDTH = 52,
    DEL_BTN_HEIGHT = 17,

    -- 关闭按钮
    CLOSE_X = 510,      
    CLOSE_Y = 8,
    CLOSE_WIDTH = 15,
    CLOSE_HEIGHT = 15,
	
}



-- ======================素材设置======================
local l_arrow = 'images/map/245066.png'
local l_arrow_h = 'images/map/245068.png'
local l_arrow_p = 'images/map/245067.png'
local r_arrow = 'images/map/245063.png'
local r_arrow_h = 'images/map/245065.png'
local r_arrow_p = 'images/map/245064.png'
local run_btn = 'images/map/244273.png'
local run_btn_h = 'images/map/244275.png'
local run_btn_p = 'images/map/244274.png'
local close_btn = 'images/map/640016.png'
local close_btn_h = 'images/map/640017.png'
local close_btn_p = 'images/map/640018.png'
local ok_btn = 'images/map/640022.png'
local ok_btn_h = 'images/map/640023.png'
local ok_btn_p = 'images/map/640024.png'
local add_btn = 'images/map/640025.png'
local add_btn_h = 'images/map/640026.png'
local add_btn_p = 'images/map/640027.png'
local del_btn = 'images/map/245072.png'
local del_btn_h ='images/map/245074.png'
local del_btn_p = 'images/map/245073.png'
local add_warp = 'images/map/new_warp.png'
local del_warp = 'images/map/del_warp.png'
local warp_select = 'images/map/warp_select.png'
local warp_select_h = 'images/map/warp_select_h.png'
local warp_select_p = 'images/map/warp_select_p.png'
local combox背景框 = 'images/map/combox背景框.png'
local 文本背景框 = 'images/map/文本背景框.png'
local 坐标图 = 'images/map/坐标.png'
local 关闭按钮 = 'images/map/关闭按钮.png'
local 关闭按下 = 'images/map/关闭按下.png'
local 关闭高亮 = 'images/map/关闭高亮.png'
local 搜索按钮 = 'images/map/搜索按钮.png'
local 搜索按下 = 'images/map/搜索按下.png'
local 搜索高亮 = 'images/map/搜索高亮.png'




function MapModule:onLoad()
	print('加载map完成')
    self.mapWin = nil
    self.mapVisible = false
    self.mouseLabel = nil
    self.inputX = nil
    self.inputY = nil
    self.warpPoints = {}
	self.diyWarpPoints = {}
    self.npcPoints = {}
    self.warpPage = 1
    self.warpPageTexts = {}
    self.warpMode = MODE_SYSTEM
    self.selectedWarpIdx = nil
    self.playerPoint = nil
    self.targetPoint = nil
    self.savedTargetPoint = nil
    self.searchMatchIndex = 0
    self.currentUI = nil
    self.warpEvent = WinMgr.OnPacketRecv("allwarp", function(header, params) self:warp_event(header, params) end)
	self.diyWarp = WinMgr.OnPacketRecv('diywarp',function(header, params) self:diy_warp(header, params) end)
    self.npcEvent = WinMgr.OnPacketRecv("allnpc", function(header, params) self:npc_event(header, params) end) -- NPC监听
	self.sceneHandler = self:onSceneStateChanged(function(scene, state) self:_sceneStateChanged(scene, state) end)
    self:onChatMessage(function(text)
        if text == COMMAND then--map触发
            self:ToggleMap()
			return 1
        end
    end)
    -- Shift+M 触发
    self:OnKeyPress(77, {16}, 1, function()
        self:ToggleMap()
    end)
    -- M+Shift 触发
    self:OnKeyPress(16, {77}, 1, function()
        self:ToggleMap()
    end)
    self.addDiyWin = nil
    self.delConfirmWin = nil
    self._deferredNav = nil
end

function MapModule:_sceneStateChanged(scene, state)
    if scene == 9 then
        if self.mapWin and self.mapWin.valid then
			self.warpMode = MODE_SYSTEM
            self.mapWin:Close()
        end
		self:closeAddDiyWin()
		self:closeDelConfirm()
        self.mapWin = nil
        self.mapVisible = false
        self.selectedWarpIdx = nil
        self.warpPage = 1
        self.warpPoints = {}
        self.diyWarpPoints = {}
        self.npcPoints = {}
    end
end

function MapModule:npc_event(header, params)
    self.warpPage = 1
    self.npcPoints = {}
    local parts = split(params[1], "|")
    for i = 1, #parts, 3 do
        if parts[i] and parts[i] ~= "" then
            table.insert(self.npcPoints, {
                name = parts[i],
                x = tonumber(parts[i + 1]) or 0,
                y = tonumber(parts[i + 2]) or 0
            })
        end
    end
    if self.warpMode == "NPC" then
        self:refreshWarpList()
    end
end

function MapModule:diy_warp(header, params)
	self.warpPage = 1
	self.diyWarpPoints = {}
	local parts = split(params[1], "|")
	for i = 1, #parts, 3 do
		if parts[i] and parts[i] ~= "" then
			table.insert(self.diyWarpPoints, {
				name = parts[i],
				x = tonumber(parts[i + 1]) or 0,
				y = tonumber(parts[i + 2]) or 0
			})
		end
	end

	if self.warpMode == MODE_CUSTOM then
		self:refreshWarpList()
	end
end

function MapModule:warp_event(header, params)
	self.warpPoints = {}
	local parts = split(params[1], "|")
	for i = 1, #parts, 3 do
		if parts[i] and parts[i] ~= "" then
			table.insert(self.warpPoints, {
				name = parts[i],
				x = tonumber(parts[i + 1]) or 0,
				y = tonumber(parts[i + 2]) or 0
			})
		end
	end
	self:refreshWarpList()
end

function MapModule:onWarpModeBtnClick(index)
    if not self.mapWin or not self.mapWin.valid then
        return
    end
    
    if index == 1 then
        self.warpMode = MODE_SYSTEM
        self.warpPage = 1
        self.selectedWarpIdx = nil
        self.searchMatchIndex = 0
        self:refreshWarpModeButtons()
        self:refreshWarpList()
    elseif index == 2 then
        self.warpMode = "NPC"
        self.warpPage = 1
        self.selectedWarpIdx = nil
        self.searchMatchIndex = 0
        WinMgr.SendPacket("get_npc", "all")
        self:refreshWarpModeButtons()
        self:refreshWarpList()
    elseif index == 3 then
        self.warpMode = MODE_CUSTOM
        self.warpPage = 1
        self.selectedWarpIdx = nil
        self.searchMatchIndex = 0
        self:refreshWarpModeButtons()
        self:refreshWarpList()
    end
end

function MapModule:refreshWarpModeButtons()
    for i = 1, 3 do
        local imgCtrl = self.warpModeBtnImages[i]
        local txtCtrl = self.warpModeBtnTexts[i]
        local isSelected = false
        if i == 1 and self.warpMode == MODE_SYSTEM then
            isSelected = true
        elseif i == 2 and self.warpMode == "NPC" then
            isSelected = true
        elseif i == 3 and self.warpMode == MODE_CUSTOM then
            isSelected = true
        end

        if imgCtrl and imgCtrl.valid then
            imgCtrl:Set({ image = isSelected and warp_select_p or warp_select })
        end

        if txtCtrl and txtCtrl.valid then
            txtCtrl:Set({ color = isSelected and 5 or 0 })
        end
    end
end

function MapModule:refreshWarpList()
    if not self.mapWin or not self.mapWin.valid then return end
    local perPage = self.currentUI.LIST_ITEM_COUNT
    local startIdx = (self.warpPage - 1) * perPage + 1
    
    local warpData = {}
    if self.warpMode == MODE_SYSTEM then
        warpData = self.warpPoints
    elseif self.warpMode == "NPC" then
        warpData = self.npcPoints
    else
        warpData = self.diyWarpPoints
    end

    for i = 1, perPage do
        local idx = startIdx + i - 1
        local textCtrl = self.warpPageTexts[i]
        
        if textCtrl and textCtrl.valid then
            if idx <= #warpData then
                local displayName = string.gsub(warpData[idx].name, "\\S", " ")
                local isSelected = (idx == self.selectedWarpIdx)
                textCtrl:Set({
                    text = displayName,
                    color = isSelected and 5 or 0,
                    visible = true,
                    hitable = true
                })
            else
                textCtrl:Set({ text = "", visible = false, hitable = false })
            end
        end
    end
    
    if self.warpPageText and self.warpPageText.valid then
        local totalPage = math.ceil(#warpData / perPage)
        if totalPage <= 0 then totalPage = 1 end
        self.warpPageText:Set({ text = string.format("%d/%d", self.warpPage, totalPage) })
    end
end

function MapModule:prevWarpPage()
    local perPage = self.currentUI.LIST_ITEM_COUNT
    
    local warpData = {}
    if self.warpMode == MODE_SYSTEM then
        warpData = self.warpPoints
    elseif self.warpMode == "NPC" then
        warpData = self.npcPoints
    else
        warpData = self.diyWarpPoints
    end

    local maxPage = math.ceil(#warpData / perPage)
    if maxPage <= 0 then maxPage = 1 end
    
    if self.warpPage > 1 then
        self.warpPage = self.warpPage - 1
        self:refreshWarpList()
    end
end

function MapModule:nextWarpPage()
    local perPage = self.currentUI.LIST_ITEM_COUNT
    
    local warpData = {}
    if self.warpMode == MODE_SYSTEM then
        warpData = self.warpPoints
    elseif self.warpMode == "NPC" then
        warpData = self.npcPoints
    else
        warpData = self.diyWarpPoints
    end

    local maxPage = math.ceil(#warpData / perPage)
    if maxPage <= 0 then maxPage = 1 end
    
    if self.warpPage < maxPage then
        self.warpPage = self.warpPage + 1
        self:refreshWarpList()
    end
end

function MapModule:onWarpItemClick(idx)
    local perPage = self.currentUI.LIST_ITEM_COUNT
    local actualIdx = (self.warpPage - 1) * perPage + idx
    
    local warpData = {}
    if self.warpMode == MODE_SYSTEM then
        warpData = self.warpPoints
    elseif self.warpMode == "NPC" then
        warpData = self.npcPoints
    else
        warpData = self.diyWarpPoints
    end
    
    if actualIdx <= #warpData then
        local point = warpData[actualIdx]
        if self.inputX and self.inputX.valid then
            self.inputX:Set({ text = tostring(point.x) })
        end
        if self.inputY and self.inputY.valid then
            self.inputY:Set({ text = tostring(point.y) })
        end
        
        self.selectedWarpIdx = actualIdx
        self.targetPoint = { x = point.x, y = point.y }
        self:refreshWarpList()
    end
end

function split(str,split_char)
    local sub_str_tab = {}
    while (true) do
		local pos = string.find(str, split_char)
		if (not pos) then
			sub_str_tab[#sub_str_tab + 1] = str
			break
		end
		local sub_str = string.sub(str, 1, pos - 1)
		sub_str_tab[#sub_str_tab + 1] = sub_str
		str = string.sub(str, pos + 1, #str)
    end
    return sub_str_tab
end



function MapModule:_isDblClick(flags)
    flags = tonumber(flags) or 0
    local bitFlag = CONST.MouseFlags.L_DBL_CLICK_EVENT
    return (flags % (bitFlag * 2)) >= bitFlag
end

function MapModule:onWarpListClick(idx, flags)
    self:onWarpItemClick(idx)
    if not self:_isDblClick(flags) then
        return
    end
    if self.warpMode ~= MODE_SYSTEM and self.warpMode ~= "NPC" then
        return
    end
    local perPage = self.currentUI.LIST_ITEM_COUNT
    local actualIdx = (self.warpPage - 1) * perPage + idx
    local warpData = {}
    if self.warpMode == MODE_SYSTEM then
        warpData = self.warpPoints
    else
        warpData = self.npcPoints
    end
    if actualIdx > #warpData then
        return
    end
    local point = warpData[actualIdx]
    if point then
        self:_beginNav(point.x, point.y)
    end
end

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

function MapModule:updateMapPoints()
    if not self.map or not self.map.valid then
        return
    end
    
    self.map:Set({ mapX = -1, mapY = -1, floor = -1, mapId = -1 })
    
    for index, value in ipairs(self.map:GetPoints()) do
        self.map:RemovePoints(value.mapX, value.mapY)
    end
    
    local playerX = Player.mapX
    local playerY = Player.mapY
    
    self.playerPoint = { x = playerX, y = playerY }
    self.map:AddPoint({
        mapX = playerX,
        mapY = playerY,
        type = 1,
        size = 2,
        color = { 0xffff0000, 0xffff0000, 0xffff0000, 0xffff0000, 0xffff0000, 0xffff0000, 0xffff0000, 0xffff0000, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff, 0xffffffff }
    })
    
    if self.targetPoint then
        self.map:AddPoint({
            mapX = self.targetPoint.x,
            mapY = self.targetPoint.y,
            type = 0,
            size = 4,
            color = { 0xffff0000 }
        })
    end
    
    if self:GetAutoCopliotState() == 1 then
        local route = WinMgr.GetAutoCopliotRoute()
        for key, value in ipairs(route) do
            if key % 3 == 0 then
                self.map:AddPoint({
                mapX = value.x,
                mapY = value.y,
                type = 0,
                size = 2,
                color = { 0xffff0000 }
                })
            end
        end
    end
end

function MapModule:ToggleMap()
    if self.mapVisible then
        if self.mapWin and self.mapWin.valid then
			self.warpMode = MODE_SYSTEM
            self.mapWin:Close()
        end
		self:closeAddDiyWin()
		self:closeDelConfirm()
        self.mapWin = nil
        self.mapVisible = false
        self.selectedWarpIdx = nil
        self.warpPage = 1
        self.warpPoints = {}
        self.diyWarpPoints = {}
    else
        self._deferredNav = nil
        self.warpPoints = {}
        self.diyWarpPoints = {}
		self.warpMode = MODE_SYSTEM
		WinMgr.SendPacket("get_warp", "all")
        WinMgr.SendPacket("get_npc", "all")
        
        local screenWidth = CONST.Screen.Width
        local UI = nil
        if screenWidth < 800 then
            UI = UI_640
        elseif screenWidth >= 800 then
            UI = UI_800
        else
            UI = UI_800
        end
        
        self.currentUI = UI
        
        local winWidth = UI.WIN_WIDTH
        local winHeight = UI.WIN_HEIGHT
        local x = (CONST.Screen.Width - winWidth) / 2
        local y = (CONST.Screen.Height - winHeight) / 2 + UI.WIN_Y

        local PAGE_Y = UI.LIST_START_Y + (UI.LIST_ITEM_COUNT - 1) * UI.LIST_ITEM_STEP_Y + 25
        local INPUT_Y = PAGE_Y + 50
        local BTN_Y = INPUT_Y + 52

        local status, win = self:newWindow({
            id = WIN_MAP,
            x = (CONST.Screen.Width - winWidth) / 2 + UI.WIN_X,
            y = (CONST.Screen.Height - winHeight) / 2 + UI.WIN_Y,
            width = winWidth,
            height = winHeight,
            layer = 4,
            dragMove = 1,
            update = function(window)
                if not window.valid then
                    return false
                end
                self:updateMapPoints()
                return false
            end,
        })

        self.mapWin = win
        self.mapVisible = true

        if win then
            self.map_bg = win:AddPngImage({
				name = '背景',
                x = 0,
                y = 0,
                width = UI.WIN_WIDTH,
                height = UI.WIN_HEIGHT,
                image = UI.BG_IMG,
                color = -1,
                visible = true,
                hitable = false,
            })

            self.map = win:AddMap({
                width = UI.MAP_WIDTH,
                height = UI.MAP_HEIGHT,
                x = UI.MAP_X,
                y = UI.MAP_Y,
                onClick = function(c)
                    local mapX = c.clickX
                    local mapY = c.clickY

                    if self.inputX and self.inputX.valid then
                        self.inputX:Set({ text = tostring(mapX) })
                    end
                    if self.inputY and self.inputY.valid then
                        self.inputY:Set({ text = tostring(mapY) })
                    end

                    if self.map and self.map.valid then
                        if self.targetPoint then
                            self.map:RemovePoints(self.targetPoint.x, self.targetPoint.y)
                        end
                        self.targetPoint = { x = mapX, y = mapY }
                        self.savedTargetPoint = { x = mapX, y = mapY }
                        self.map:AddPoint({
                            mapX = mapX,
                            mapY = mapY,
                            type = 1,
                            size = 4,
                            color = { 0xffff0000 }
                        })
                    end
                end,
                onHover = function(c)
                    if c.mouseX and c.mouseY then
                        local displayX = c.mouseX
                        local displayY = c.mouseY
                        local mouseInWinX = CONST.Mouse.x - win.x
                        local mouseInWinY = CONST.Mouse.y - win.y
                        
                        if self.mouseLabel and self.mouseLabel.valid then
                            self.mouseLabel:Set({ 
                                x = mouseInWinX -  45,
                                y = mouseInWinY - 25,
                                text = string.format("东:%d 南:%d", displayX, displayY),
                                visible = true
                            })
                        end
                    end
                    return false
                end,
                onLeave = function(c)
                    if self.mouseLabel and self.mouseLabel.valid then
                        self.mouseLabel:Set({ visible = false })
                    end
                    return false
                end,
            })

            self.mouseLabel = win:AddText({
				name = '鼠标坐标',
                x = UI.MOUSE_LABEL_X,
                y = UI.MOUSE_LABEL_Y,
                width = 100,
                height = 18,
                text = '',
                font = 1,
                color = 0,
                hitable = false,
                visible = false,
            })

			-- 模式切换按钮
            self.warpModeBtnImages = {}
            self.warpModeBtnTexts = {}

            local btn1Img = win:AddPngImage({
                x = UI.BTN_START_X,
                y = UI.BTN_START_Y,
                width = UI.BTN_WIDTH,
                height = UI.BTN_HEIGHT,
                image = warp_select_p,
                imageHover = warp_select_h,
                imagePress = warp_select_p,
                color = -1,
                visible = true,
                hitable = true,
                onClick = function()
                    self:onWarpModeBtnClick(1)
                    return true
                end
            })
            self.warpModeBtnImages[1] = btn1Img

            local btn2Img = win:AddPngImage({
                x = UI.BTN_START_X + UI.BTN_WIDTH + UI.BTN_GAP,
                y = UI.BTN_START_Y,
                width = UI.BTN_WIDTH,
                height = UI.BTN_HEIGHT,
                image = warp_select,
                imageHover = warp_select_h,
                imagePress = warp_select_p,
                color = -1,
                visible = true,
                hitable = true,
                onClick = function()
                    self:onWarpModeBtnClick(2)
                    return true
                end
            })
            self.warpModeBtnImages[2] = btn2Img

            local btn3Img = win:AddPngImage({
                x = UI.BTN_START_X + (UI.BTN_WIDTH + UI.BTN_GAP) * 2,
                y = UI.BTN_START_Y,
                width = UI.BTN_WIDTH,
                height = UI.BTN_HEIGHT,
                image = warp_select,
                imageHover = warp_select_h,
                imagePress = warp_select_p,
                color = -1,
                visible = true,
                hitable = true,
                onClick = function()
                    self:onWarpModeBtnClick(3)
                    return true
                end
            })
            self.warpModeBtnImages[3] = btn3Img

            -- 按钮上的文字
            local text1 = win:AddText({
                x = UI.BTN_START_X + UI.BTN_TEXT1_X,
                y = UI.BTN_START_Y + UI.BTN_TEXT_Y,
                width = UI.BTN_WIDTH,
                height = 16,
                text = "系统",
                font = 1,
                color = 5,
                hitable = false,
                visible = true,
            })
            self.warpModeBtnTexts[1] = text1

            local text2 = win:AddText({
                x = UI.BTN_START_X + UI.BTN_WIDTH + UI.BTN_GAP + UI.BTN_TEXT2_X,
                y = UI.BTN_START_Y + UI.BTN_TEXT_Y,
                width = UI.BTN_WIDTH,
                height = 16,
                text = "NPC",
                font = 1,
                color = 0,
                hitable = false,
                visible = true,
            })
            self.warpModeBtnTexts[2] = text2

            local text3 = win:AddText({
                x = UI.BTN_START_X + (UI.BTN_WIDTH + UI.BTN_GAP) * 2 + UI.BTN_TEXT3_X,
                y = UI.BTN_START_Y + UI.BTN_TEXT_Y,
                width = UI.BTN_WIDTH,
                height = 16,
                text = "自定义",
                font = 1,
                color = 0,
                hitable = false,
                visible = true,
            })
            self.warpModeBtnTexts[3] = text3

			-- 自动生成列表

			self.warpPageTexts = {}
			for i = 1, UI.LIST_ITEM_COUNT do
                win:AddPngImage({
                    name = "单行背景",
                    x = UI.LIST_START_X + UI.LIST_BG_X,
                    y = UI.LIST_START_Y + (i-1) * UI.LIST_ITEM_STEP_Y + UI.LIST_BG_Y,
                    width = UI.LIST_BG_WIDTH,
                    height = UI.LIST_BG_HEIGHT,
                    image = 文本背景框,
                    color = -1,
                    visible = true,
                    hitable = false,
                })
				local textCtrl = win:AddText({
					x = UI.LIST_START_X,
					y = UI.LIST_START_Y + (i-1) * UI.LIST_ITEM_STEP_Y,
					width = UI.LIST_WIDTH,
					height = UI.LIST_HEIGHT,
					text = "",
					font = 1,
					color = 0,
					hitable = true,
					visible = true,
					onClick = function(control, flags)
						self:onWarpListClick(i, flags)
						return true
					end
				})
				self.warpPageTexts[i] = textCtrl
			end

            self.warpPageText = win:AddText({
				name = '页码',
                x = UI.PAGE_X,
                y = PAGE_Y,
                width = 30,
                height = 20,
                text = "1/1",
                font = 1,
                color = 0,
                hitable = false,
                visible = true,
            })
            --左箭头
            win:AddPngImage({
				name = '左翻页',
                x = UI.L_ARROW_X,
                y = PAGE_Y,
                width = UI.ARROW_WIDTH,
                height = UI.ARROW_HEIGHT,
                image = l_arrow,
                imageHover = l_arrow_h ,
                imagePress = l_arrow_p ,
                color = -1,
                visible = true,
                onClick = function()
                    self:prevWarpPage()
                    return true
                end
            })
            --右边箭头
            win:AddPngImage({
				name = '右翻页',
                x = UI.R_ARROW_X,
                y = PAGE_Y,
                width = UI.ARROW_WIDTH,
                height = UI.ARROW_HEIGHT,
                image = r_arrow ,
                imageHover = r_arrow_h ,
                imagePress = r_arrow_p ,
                color = -1,
                visible = true,
                onClick = function()
                    self:nextWarpPage()
                    return true
                end
            })
            
            self:refreshWarpList()
            
            if self.savedTargetPoint and self.map and self.map.valid then
                local state = WinMgr.GetAutoCopliotState()
                if state == 1 then
                    self.targetPoint = self.savedTargetPoint
                    self.map:AddPoint({
                        mapX = self.targetPoint.x,
                        mapY = self.targetPoint.y,
                        type = 1,
                        size = 4,
                        color = { 0xffff0000 }
                    })
                end
            end
		
            win:AddPngImage({
				name = '坐标',
				x = UI.COORD_IMG_X,
				y = INPUT_Y,
				width = 34,
				height = 19,
				image = 坐标图,
				color = -1,
				visible = true,
                hitable = false,
			})

			--input x
			self.inputX = win:AddTextInput({
				name = '输入x',
				x = UI.INPUT_X_X,
				y = INPUT_Y + UI.INPUT_Y_OFFSET,
				width = UI.INPUT_WIDTH,
				height = UI.INPUT_HEIGHT,
				text = '0',
				font = 1,
				color = 5,
				maxLength = 10,
				visible = true,
				hitable = true,
			})
			--input y
			self.inputY = win:AddTextInput({
				name = '输入y',
				x = UI.INPUT_Y_X,
				y = INPUT_Y + UI.INPUT_Y_OFFSET,
				width = UI.INPUT_WIDTH,
				height = UI.INPUT_HEIGHT,
				text = '0',
				font = 1,
				color = 5,
				maxLength = 10,
				visible = true,
				hitable = true,
			})

			self.searchInput = win:AddTextInput({
				name = '搜索框',
				x = UI.SEARCH_X,
				y = INPUT_Y + UI.SEARCH_BTN_Y_OFFSET+2,
				width = UI.SEARCH_WIDTH,
				height = UI.SEARCH_HEIGHT,
				text = '',
				font = 1,
				color = 5,
				maxLength = 50,
				visible = true,
				hitable = true,
			})

			--执行按钮
			win:AddPngImage({
				name = '执行',
				x = UI.RUN_BTN_X,
				y = BTN_Y,
				width = UI.RUN_BTN_WIDTH,
				height = UI.RUN_BTN_HEIGHT,
				image = run_btn,
				imageHover = run_btn_h,
				imagePress = run_btn_p,
				color = -1,
				visible = true,
				onClick = function()
					self:_runNavFromInputs()
					return true
				end
			})
			if self:GetAutoCopliotState() == 1 then
				local route = WinMgr.GetAutoCopliotRoute()
				if route and #route > 0 then
					local lastPoint = route[#route]
					self.inputX:Set({ text = tostring(lastPoint.x) })
					self.inputY:Set({ text = tostring(lastPoint.y) })
				end
			end			
        end
    end
end

function MapModule:openAddDiy()
    if self.addDiyWin and self.addDiyWin.valid then
		WinMgr.Focus(add_diy)
        return
    end
    local winW = 149
    local winH = 128
    local screenW = CONST.Screen.Width
    local screenH = CONST.Screen.Height
    local winX = (screenW - winW) / 2
    local winY = (screenH - winH) / 2
    local status, win = self:newWindow({
        id = add_diy,
        x = winX,
        y = winY,
        width = winW,
        height = winH,
        layer = 4,
        dragMove = 1,
    })
    self.addDiyWin = win
    WinMgr.Focus(add_diy)
    -- 背景图
    win:AddPngImage({
        x = 0, y = 0,
        width = winW, height = winH,
        image = add_warp,
        color = -1,
        hitable = false,
    })

    -- 输入框
    self.addDiyName = win:AddTextInput({ x = 43, y = 26, width = 95, height = 18, text = "", font=1, color=0, maxLength=32 })
    self.addDiyX = win:AddTextInput({ x = 43, y = 50, width = 95, height = 18, text = "", font=1, color=0, maxLength=10 })
    self.addDiyY = win:AddTextInput({ x = 43, y = 74, width = 95, height = 18, text = "", font=1, color=0, maxLength=10 })

    -- 确定
    win:AddPngImage({
        x = 20, y = 100, width=52, height=17,
        image = ok_btn, imageHover=ok_btn_h, imagePress=ok_btn_p,
        onClick = function()
            local name = self.addDiyName.text
            local x = tonumber(self.addDiyX.text)
            local y = tonumber(self.addDiyY.text)
            if name and x and y and x>0 and y>0 then
                WinMgr.SendPacket('input_diy', name.."|"..x.."|"..y)
            end
            self:closeAddDiyWin()
            return true
        end
    })

    -- 取消
    win:AddPngImage({
        x = 82, y = 100, width=52, height=17,
        image = close_btn, imageHover=close_btn_h, imagePress=close_btn_p,
        onClick = function()
            self:closeAddDiyWin()
            return true
        end
    })
end

function MapModule:closeAddDiyWin()
    if self.addDiyWin and self.addDiyWin.valid then
        self.addDiyWin:Close()
    end
    self.addDiyWin = nil
    self.addDiyName = nil
    self.addDiyX = nil
    self.addDiyY = nil
end

function MapModule:openDelConfirm()
    if self.delConfirmWin and self.delConfirmWin.valid then
		WinMgr.Focus(del_diy)
        return
    end

    local winW = 149
    local winH = 77
    local screenW = CONST.Screen.Width
    local screenH = CONST.Screen.Height
    local winX = (screenW - winW) / 2
    local winY = (screenH - winH) / 2
    local status, win = self:newWindow({
        id = del_diy,
        x = winX,
        y = winY,
        width = winW,
        height = winH,
        layer = 4,
        dragMove = 1,
    })
    self.delConfirmWin = win
    WinMgr.Focus(del_diy)
    -- 背景
    win:AddPngImage({
        x = 0, y = 0,
        width = winW, height = winH,
        image = del_warp,
        color = -1,
        hitable = false,
    })

    win:AddPngImage({
        x = 15, y = 50, width=52, height=17,
        image = ok_btn, imageHover=ok_btn_h, imagePress=ok_btn_p,
        onClick = function()
            if self.selectedWarpIdx then
                WinMgr.SendPacket("del_diy", tostring(self.selectedWarpIdx))
                self.selectedWarpIdx = nil
            end
            self:closeDelConfirm()
            return true
        end
    })

    -- 取消
    win:AddPngImage({
        x = 82, y = 50, width=52, height=17,
        image = close_btn, imageHover=close_btn_h, imagePress=close_btn_p,
        onClick = function()
            self:closeDelConfirm()
            return true
        end
    })
end

function MapModule:closeDelConfirm()
    if self.delConfirmWin and self.delConfirmWin.valid then
        self.delConfirmWin:Close()
    end
    self.delConfirmWin = nil
end

function MapModule:onUnload()
    self.playerPoint = nil
    self.targetPoint = nil
    if self.map and self.map.valid then
        if self.playerPoint then
            self.map:RemovePoints(self.playerPoint.x, self.playerPoint.y)
        end
        if self.targetPoint then
            self.map:RemovePoints(self.targetPoint.x, self.targetPoint.y)
        end
    end
    
    if self.warpEvent and self.warpEvent.valid then
        self.warpEvent:Unregister()
		self.diyWarp:Unregister()
        self.npcEvent:Unregister()
    end
    if self.sceneHandler and self.sceneHandler.valid then
        self.sceneHandler:Unregister()
    end
    self.warpEvent = nil
    self.sceneHandler = nil
    if self.mapWin and self.mapWin.valid then
        self.mapWin:Close()
    end
    self.mapWin = nil
    self.mapVisible = false
    self.mouseLabel = nil
    self.inputX = nil
    self.inputY = nil
    self.selectedWarpIdx = nil
    self.diyWarpPoints = {}
    self.npcPoints = {}
end

return MapModule