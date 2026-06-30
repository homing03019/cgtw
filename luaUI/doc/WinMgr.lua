---@class LuaWindow
---@field valid boolean @窗口引用是否仍有效
---@field id integer @窗口 ID
---@field winId integer @窗口 ID，同 id
---@field state integer @窗口状态
---@field visible boolean @窗口是否可见
---@field count integer @子控件数量
---@field x integer
---@field y integer
---@field width integer
---@field height integer
---@field layer integer

---@class NativeWindow
---@field valid boolean @窗口是否仍存在
---@field winId integer @窗口 ID
---@field x integer
---@field y integer
---@field width integer
---@field height integer
---@field layer integer

---@class LuaControl
---@field valid boolean @控件引用是否仍有效
---@field id integer @控件 ID
---@field controlId integer @控件 ID，同 id
---@field name string
---@field x integer
---@field y integer
---@field width integer
---@field height integer
---@field visible boolean
---@field type integer @见 CONST.UIControl.TYPE
---@field mouseState integer @见 CONST.UIControl.MOUSE_STATE
---@field parentId integer @父 ScrollView 控件 ID；0 表示直属窗口
---@field image integer|string|nil @图片控件返回图号，PNG 图片控件返回路径
---@field imageHover string|nil @仅 PNG 图片控件
---@field imagePress string|nil @仅 PNG 图片控件
---@field imageRect LuaPngRect|nil @仅 PNG 图片控件
---@field imageHoverRect LuaPngRect|nil @仅 PNG 图片控件
---@field imagePressRect LuaPngRect|nil @仅 PNG 图片控件
---@field color integer|nil @仅 PNG 图片控件
---@field text string|nil @文本或输入框控件
---@field maxLength integer|nil @仅输入框控件
---@field animeNo integer|nil @仅动画控件
---@field action integer|nil @仅动画控件
---@field dir integer|nil @仅动画控件
---@field revertPlay integer|nil @仅动画控件
---@field scrollY integer|nil @仅 ScrollView；当前垂直滚动偏移
---@field contentHeight integer|nil @仅 ScrollView；内容高度
---@field maxScrollY integer|nil @仅 ScrollView；最大垂直滚动偏移
---@field barWidth integer|nil @仅 ScrollView；滚动条宽度
---@field scrollStep integer|nil @仅 ScrollView；最小滚动单位
---@field mapX integer|nil @仅地图控件；中心地图 X
---@field mapY integer|nil @仅地图控件；中心地图 Y
---@field mapId integer|nil @仅地图控件；地图 ID
---@field floor integer|nil @仅地图控件；楼层
---@field mapWidth integer|nil @仅地图控件；已加载地图宽度
---@field mapHeight integer|nil @仅地图控件；已加载地图高度
---@field mouseX integer|nil @仅地图控件；当前鼠标所在地图 X
---@field mouseY integer|nil @仅地图控件；当前鼠标所在地图 Y
---@field clickX integer|nil @仅地图控件；最近一次点击地图 X
---@field clickY integer|nil @仅地图控件；最近一次点击地图 Y
---@field lastClickX integer|nil @clickX 别名
---@field lastClickY integer|nil @clickY 别名

---@class LuaEventHandle
---@field valid boolean @事件是否仍有效；false 表示已反注册
---@field active boolean @事件是否仍有效，同 valid

---@return boolean success @成功反注册返回 true；重复反注册返回 false
function LuaEventHandle:Unregister() end


---@alias LuaUIEvent fun(control: LuaControl, flags: integer): boolean|nil
---@alias LuaUITextEvent fun(control: LuaControl, text: string): boolean|nil
---@alias LuaWindowCallback fun(window: LuaWindow): boolean|nil
---@alias LuaPacketRecvCallback fun(packetHeader: string, params: string[])
---@alias LuaPacketSendCallback fun(packetHeader: string, data: string, len: integer)
---@alias LuaPacketData string|integer
---@alias LuaKeyPressCallback fun()
---@alias LuaSceneStateChangedCallback fun(sceneType: integer, sceneState: integer)

---@alias LuaVkList integer|integer[]

---@class LuaWindowParam
---@field id integer @必须大于 100
---@field x integer
---@field y integer
---@field width integer
---@field height integer
---@field layer integer|nil @仅新建窗口时生效，默认 4
---@field visible boolean|nil @默认 true；false 时创建隐藏窗口
---@field update LuaWindowCallback|nil
---@field draw LuaWindowCallback|nil

---@class LuaControlBaseParam
---@field name string|nil
---@field x integer|nil @默认 0
---@field y integer|nil @默认 0
---@field width integer|nil @默认 0
---@field height integer|nil @默认 0
---@field visible boolean|nil @默认 true；false 时不绘制、不响应 process
---@field hitable boolean|nil @图片/PNG/动画/输入框默认 true，文本默认 false
---@field parent LuaControl|nil @父 ScrollView；未填则直属窗口
---@field parentId integer|nil @父 ScrollView 控件 ID；parent 优先
---@field onEvent LuaUIEvent|nil
---@field onClick LuaUIEvent|nil
---@field onPress LuaUIEvent|nil
---@field onHover LuaUIEvent|nil
---@field onLeave LuaUIEvent|nil
---@field onDrag LuaUIEvent|nil
---@field onDrop LuaUIEvent|nil

---@class LuaImageParam: LuaControlBaseParam
---@field image integer|nil @图号；未填时读 id，默认 -1
---@field id integer|nil @image 未填时使用
---@field imageHover integer|nil @默认 image
---@field imagePress integer|nil @默认 image
---@field color integer|nil @默认 0xffffffff

---@class LuaPngRect
---@field x integer
---@field y integer
---@field width integer|nil @未填时读 w
---@field height integer|nil @未填时读 h
---@field w integer|nil @width 别名，仅参数可用
---@field h integer|nil @height 别名，仅参数可用

---@class LuaPngImageParam: LuaControlBaseParam
---@field image string|nil
---@field imageRect LuaPngRect|nil
---@field imageHover string|nil
---@field imageHoverRect LuaPngRect|nil
---@field imagePress string|nil
---@field imagePressRect LuaPngRect|nil
---@field color integer|nil @默认 0xffffffff

---@class LuaAnimeParam: LuaControlBaseParam
---@field animeNo integer|nil @动画编号
---@field action integer|nil @动画动作
---@field dir integer|nil @动画方向
---@field revert integer|nil @倒序播放：1，正序播放：0

---@class LuaTextParam: LuaControlBaseParam
---@field text string|nil @默认空字符串
---@field font integer|nil @默认 0
---@field fontType integer|nil @font 未填时使用
---@field color integer|nil @默认 0，仅低 8 位生效

---@class LuaTextInputParam: LuaControlBaseParam
---@field text string|nil @默认空字符串
---@field font integer|nil @默认 0
---@field fontType integer|nil @font 未填时使用
---@field color integer|nil @默认 0，仅低 8 位生效
---@field maxLength integer|nil @默认 287；<=0 或 >287 时重置为 287
---@field onChange LuaUITextEvent|nil
---@field onEnter LuaUITextEvent|nil

---@class LuaScrollViewParam: LuaControlBaseParam
---@field contentHeight integer|nil @默认 height；小于 height 时不显示滚动条
---@field scrollY integer|nil @默认 0；自动限制到 0..maxScrollY，并按 scrollStep 对齐
---@field barWidth integer|nil @默认 8；仅垂直滚动条
---@field scrollStep integer|nil @默认 1；<=0 时重置为 1

---@class LuaMapParam: LuaControlBaseParam
---@field mapX integer|nil @中心地图 X；未填或 -1 时使用角色当前地图 X
---@field mapY integer|nil @中心地图 Y；未填或 -1 时使用角色当前地图 Y
---@field mapId integer|nil @未填或 -1 时使用当前地图 ID
---@field floor integer|nil @未填或 -1 时使用当前楼层

---@class LuaControlSetParam
---@field name string|nil
---@field x integer|nil
---@field y integer|nil
---@field width integer|nil
---@field height integer|nil
---@field visible boolean|nil @false 时不绘制、不响应 process，并清理鼠标/输入状态
---@field hitable boolean|nil
---@field image integer|string|nil @图片控件为图号，PNG 图片控件为路径
---@field id integer|nil @图片控件 image 未填时使用
---@field imageHover integer|string|nil
---@field imageHoverRect LuaPngRect|nil
---@field imagePress integer|string|nil
---@field imagePressRect LuaPngRect|nil
---@field imageRect LuaPngRect|nil
---@field color integer|nil
---@field text string|nil
---@field font integer|nil
---@field fontType integer|nil @font 未填时使用
---@field maxLength integer|nil @仅输入框控件
---@field animeNo integer|nil @仅动画控件；只接受数值型
---@field action integer|nil @仅动画控件；只接受数值型，对应 YobiAction.actionState
---@field dir integer|nil @仅动画控件；只接受数值型，对应 YobiAction.dir
---@field revertPlay integer|nil @仅动画控件；非 0 时传给 UIElementData_2.revertPlay
---@field revert integer|nil @revertPlay 别名，仅参数可用
---@field scrollY integer|nil @仅 ScrollView；自动限制到 0..maxScrollY，并按 scrollStep 对齐
---@field contentHeight integer|nil @仅 ScrollView
---@field barWidth integer|nil @仅 ScrollView；<=0 时重置为 8
---@field scrollStep integer|nil @仅 ScrollView；<=0 时重置为 1
---@field mapX integer|nil @仅地图控件；未填保持原值；-1 时使用角色当前地图 X
---@field mapY integer|nil @仅地图控件；未填保持原值；-1 时使用角色当前地图 Y
---@field mapId integer|nil @仅地图控件；未填保持原值；-1 时使用当前地图 ID
---@field floor integer|nil @仅地图控件；未填保持原值；-1 时使用当前楼层

---@class LuaWindowSetParam
---@field x integer|nil
---@field y integer|nil
---@field width integer|nil
---@field height integer|nil
---@field visible boolean|nil @false 时隐藏窗口并清理控件鼠标状态、拖动状态和输入框焦点
---@field update LuaWindowCallback|nil
---@field draw LuaWindowCallback|nil

---@class LuaDrawRectParam
---@field x integer|nil @默认 0
---@field y integer|nil @默认 0
---@field width integer|nil @未填时读 w
---@field height integer|nil @未填时读 h
---@field w integer|nil @width 别名
---@field h integer|nil @height 别名
---@field color integer|nil @默认 0

---@param param LuaImageParam
---@return LuaControl|nil control
function LuaWindow:AddImage(param) end

---@param param LuaAnimeParam
---@return LuaControl|nil control
function LuaWindow:AddAnime(param) end

---@param param LuaPngImageParam
---@return LuaControl|nil control
function LuaWindow:AddPngImage(param) end

---@param param LuaTextParam
---@return LuaControl|nil control
function LuaWindow:AddText(param) end

---@param param LuaTextInputParam
---@return LuaControl|nil control
function LuaWindow:AddTextInput(param) end

---@param param LuaScrollViewParam
---@return LuaControl|nil control
function LuaWindow:AddScrollView(param) end

---@param param LuaMapParam
---@return LuaControl|nil control
function LuaWindow:AddMap(param) end

---@param param LuaWindowSetParam
---@return boolean success
function LuaWindow:Set(param) end

---@return boolean success
function LuaWindow:Close() end

---@param vkMain integer @0..255
---@param stateMask integer @1..255，见 CONST.KeyStateFlag
---@return boolean pressed
function LuaWindow:CheckKeyState(vkMain, stateMask) end

---@param vkMain integer @0..255
---@param vkList LuaVkList @附加按住键；可为单个 VK 或数组
---@param stateMask integer @1..255，见 CONST.KeyStateFlag
---@return boolean pressed
function LuaWindow:CheckKeyState(vkMain, vkList, stateMask) end

---@return boolean success
function LuaWindow:ClearChildren() end

---@param text string|nil @nil 时按空字符串处理
---@return boolean success
function LuaWindow:ShowTips(text) end

---@param param LuaDrawRectParam
---@return boolean success @窗口隐藏时返回 false
---@return integer|nil index
function LuaWindow:DrawRect(param) end

---@param param LuaControlSetParam
---@return boolean success
function LuaControl:Set(param) end

---@class WinMgrModule
WinMgr = WinMgr or {}

---@param param LuaWindowParam
---@return integer status @0 新建窗口，1 已存在并更新位置/尺寸/回调
---@return LuaWindow window
function WinMgr.NewWindow(param) end

---@param id integer
---@return LuaWindow|NativeWindow|nil window
function WinMgr.FindWindow(id) end

---@param id integer
---@return integer success @1 成功，0 失败
function WinMgr.Focus(id) end

---@param id integer
function WinMgr.Close(id) end

---开始自动导航到地图坐标；会持续分段移动直到到达或调用 StopCopilot
---@param x integer @目标地图 X
---@param y integer @目标地图 Y
function WinMgr.AutoCopilot(x, y) end

---停止当前自动导航
function WinMgr.StopCopilot() end
---获取当前自动导航状态
---@return integer state @1 导航中，0 未导航
function WinMgr.GetAutoCopliotState() end

---@param callback LuaSceneStateChangedCallback
---@return LuaEventHandle handle @调用 handle:Unregister() 反注册
function WinMgr.OnSceneStateChanged(callback) end

---@param callback fun(focusWinId: integer, blurWinId: integer) @-1 表示无焦点窗口
---@return LuaEventHandle handle @调用 handle:Unregister() 反注册
function WinMgr.OnWindowFocusChanged(callback) end

---@param callback fun(winId: integer)
---@return LuaEventHandle handle @调用 handle:Unregister() 反注册
function WinMgr.OnWindowClose(callback) end

---@param callback LuaChatMessageCallback
---@return LuaEventHandle handle @callback 返回 1 时拦截发送事件
function WinMgr.OnChatMessage(callback) end

---@param header string
---@param callback LuaPacketRecvCallback
---@return LuaEventHandle handle
function WinMgr.OnPacketRecv(header, callback) end

---@param header string
---@param callback LuaPacketSendCallback
---@return LuaEventHandle handle
function WinMgr.OnPacketSend(header, callback) end

---@param vkMain integer @0..255
---@param stateMask integer @1..255，见 CONST.KeyStateFlag
---@param callback LuaKeyPressCallback
---@return LuaEventHandle handle
function WinMgr.OnKeyPress(vkMain, stateMask, callback) end

---@param vkMain integer @0..255
---@param vkList LuaVkList @附加按住键；可为单个 VK 或数组
---@param stateMask integer @1..255，见 CONST.KeyStateFlag
---@param callback LuaKeyPressCallback
---@return LuaEventHandle handle
function WinMgr.OnKeyPress(vkMain, vkList, stateMask, callback) end

---@param fullPacket string @完整封包；未以 \n 结尾时自动补齐
---@return integer result
function WinMgr.SendPacket(fullPacket) end

---@param head string @协议头
---@param ... LuaPacketData @按空格拼接；integer 使用 62 进制编码，string 使用 nrproto 字符串转义；末尾自动补 \n
---@return integer result
function WinMgr.SendPacket(head, ...) end

---@param seNo integer @0..500
---@param panX integer @默认 320
---@return integer result @0 成功，-1 失败
function WinMgr.PlaySe(seNo, panX) end

---@param bgmNo integer @bin\bgm\bgm.cf 第二列 BGM 号
---@return integer result @1 成功，非 1 失败
function WinMgr.LoadAndPlayBGM(bgmNo) end

---@param type integer @固定 BGM 类型：0 或 1
---@param repeats integer @重复次数，传给原客户端
---@return integer result @1 成功，非 1 失败
function WinMgr.PlayFixedBGM(type, repeats) end

---@param msg string
function WinMgr.CliSendMsg(msg) end

---@param msg string
---@param color integer @默认 0
function WinMgr.CliSendMsg(msg, color) end

---@param msg string
---@param color integer @默认 0
---@param font integer @默认 0
function WinMgr.CliSendMsg(msg, color, font) end

---@param msg string
---@param color integer @默认 0
---@param font integer @默认 0
---@param sender string|nil
function WinMgr.CliSendMsg(msg, color, font, sender) end

---@param value integer
---@return string encoded
function WinMgr.NrEncode62(value) end

---@param value string
---@return integer decoded
function WinMgr.NrDecode62(value) end

---@param value integer
---@return string encoded
function WinMgr.NrEncode16(value) end

---@param value string
---@return integer decoded
function WinMgr.NrDecode16(value) end

---@param value string
---@return string encoded
function WinMgr.NrEncodeString(value) end

---@param value string
---@return string decoded
function WinMgr.NrDecodeString(value) end
