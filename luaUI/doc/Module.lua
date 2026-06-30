---@class ModuleLoadOption
---@field path string|nil @指定模块文件路径；相对路径默认基于 luaUI\\
---@field forceReload boolean|nil @是否强制重载
---@field globals table|nil @注入模块环境的额外全局对象

---@class ModuleSpec
---@field name string|nil @模块名
---@field path string|nil @模块文件路径
---@field env table|nil @模块运行环境
---@field id string|nil @模块实例 ID
---@field opt ModuleLoadOption|nil @加载参数

---@class ModuleInfo
---@field name string @模块名
---@field id string @模块实例 ID
---@field loaded boolean @是否已加载

---@class ModuleCleanupItem
---@field name string
---@field fn fun(module: ModuleBase)

---@class ModuleOwnedItem
---@field resource any
---@field disposer fun(resource: any, module: ModuleBase)
---@field name string

---@class GlobalEventHandle
---@field id integer
---@field owner any
---@field owner_name string|nil
---@field fn function
---@field priority integer
---@field order integer
---@field tag any

---@alias ModuleCleanupCallback fun(module: ModuleBase)
---@alias ModuleDisposer fun(resource: any, module: ModuleBase)
---@alias ModuleSceneStateChangedCallback fun(sceneType: integer, sceneState: integer)
---@alias ModuleWindowFocusChangedCallback fun(focusWinId: integer, blurWinId: integer)
---@alias ModuleWindowCloseCallback fun(winId: integer)
---@alias ModulePacketRecvCallback fun(packetHeader: string, params: string[])
---@alias ModulePacketSendCallback fun(packetHeader: string, data: string, len: integer)
---@alias ModuleChatMessageCallback fun(text: string): integer|nil
---@alias ModuleKeyPressCallback fun()

---@class GlobalEvent
---@field STOP table @事件停止标记
---@field name string
---@field handlers GlobalEventHandle[]
---@field handler_by_id table<integer, GlobalEventHandle>
---@field next_id integer
---@field next_order integer
GlobalEvent = GlobalEvent or {}

---@param name string|nil
---@return GlobalEvent event
function GlobalEvent.new(name) end

---@param owner any
---@param fn function
---@param opt table|nil @可选字段 priority、tag
---@return GlobalEventHandle|nil handle
---@return string|nil err
function GlobalEvent:add(owner, fn, opt) end

---@param handle GlobalEventHandle|integer
---@return boolean removed
function GlobalEvent:remove(handle) end

---@param owner any
---@return integer removed
function GlobalEvent:remove_owner(owner) end

---@return any result
function GlobalEvent:dispatch(...) end

---@class ModuleSystemModule
---@field modules table<string, ModuleBase>
---@field sequence integer
---@field opt table
---@field basePath string @Lua 基础目录，默认 luaUI\\
---@field events table
ModuleSystem = ModuleSystem or {}

---@param opt table|nil @可选字段 basePath，默认 luaUI\\
---@return ModuleSystemModule self
function ModuleSystem:init(opt) end

---@param name string
---@param opt ModuleLoadOption|nil
---@return ModuleBase|nil module
---@return string|nil err
function ModuleSystem:loadModule(name, opt) end

---@param name string
---@param opt ModuleLoadOption|nil
---@return ModuleBase|nil module
---@return string|nil err
function ModuleSystem:reloadModule(name, opt) end

---@param name string
---@return boolean success
function ModuleSystem:unloadModule(name) end

---@param name string
---@return ModuleBase|nil module
function ModuleSystem:getModule(name) end

---@return ModuleInfo[] modules
function ModuleSystem:listModules() end

function ModuleSystem:close() end

---@class ModuleBase
---@field class table
---@field spec ModuleSpec
---@field name string
---@field id string
---@field env table|nil
---@field loaded boolean
---@field disposed boolean
---@field state table
ModuleBase = ModuleBase or {}

---@param class table
---@return ModuleBase instance
function ModuleBase.__call(class, ...) end

---@param self ModuleBase
---@return string text
function ModuleBase.__tostring(self) end

---@param class_name string|nil
---@return table class
function ModuleBase:extend(class_name) end

---@param spec ModuleSpec|nil
---@return ModuleBase instance
function ModuleBase:new(spec) end

---@param name string|nil
---@param fn ModuleCleanupCallback
---@return ModuleCleanupItem item
function ModuleBase:addCleanup(name, fn) end

---@param fn ModuleCleanupCallback
---@param name string|nil
---@return ModuleCleanupItem item
function ModuleBase:defer(fn, name) end

---@param resource any
---@param disposer ModuleDisposer
---@param name string|nil
---@return any resource
---@return string|nil err
function ModuleBase:own(resource, disposer, name) end

---@param handle LuaEventHandle|GlobalEventHandle|nil
---@return LuaEventHandle|GlobalEventHandle|nil handle
function ModuleBase:ownEvent(handle) end

---@param handle LuaEventHandle|GlobalEventHandle|nil
---@return boolean success
function ModuleBase:unregisterHandle(handle) end

---@param window LuaWindow|nil
---@return LuaWindow|nil window
function ModuleBase:ownWindow(window) end

---@param window LuaWindow|nil
---@return boolean success
function ModuleBase:releaseWindow(window) end

---@param name string
---@return ModuleBase|nil module
function ModuleBase:getModule(name) end

---@param name string
---@param opt ModuleLoadOption|nil
---@return ModuleBase|nil module
---@return string|nil err
function ModuleBase:loadModule(name, opt) end

---@param name string
---@param opt ModuleLoadOption|nil
---@return ModuleBase|nil module
---@return string|nil err
function ModuleBase:reloadModule(name, opt) end

---@param name string
---@return boolean success
function ModuleBase:unloadModule(name) end

---@return ModuleInfo[] modules
function ModuleBase:listModules() end

---@param param LuaWindowParam
---@return integer status @0 新建窗口，1 已存在并更新位置/尺寸/回调
---@return LuaWindow window
function ModuleBase:newWindow(param) end

---@param param LuaWindowParam
---@return integer status
---@return LuaWindow window
function ModuleBase:NewWindow(param) end

---@param id integer
---@return LuaWindow|NativeWindow|nil window
function ModuleBase:findWindow(id) end

---@param id integer
---@return LuaWindow|NativeWindow|nil window
function ModuleBase:FindWindow(id) end

---@param id integer
---@return integer success @1 成功，0 失败
function ModuleBase:focus(id) end

---@param id integer
---@return integer success
function ModuleBase:Focus(id) end

---@param id integer
function ModuleBase:closeWindow(id) end

---@param id integer
function ModuleBase:Close(id) end

---开始自动导航到地图坐标；会持续分段移动直到到达或调用 StopCopilot
---@param x integer @目标地图 X
---@param y integer @目标地图 Y
function ModuleBase:autoCopilot(x, y) end

---开始自动导航到地图坐标；会持续分段移动直到到达或调用 StopCopilot
---@param x integer @目标地图 X
---@param y integer @目标地图 Y
function ModuleBase:AutoCopilot(x, y) end

---停止当前自动导航
function ModuleBase:stopCopilot() end

---停止当前自动导航
function ModuleBase:StopCopilot() end

---获取当前自动导航状态
---@return integer state @1 导航中，0 未导航
function ModuleBase:getAutoCopliotState() end

---获取当前自动导航状态
---@return integer state @1 导航中，0 未导航
function ModuleBase:GetAutoCopliotState() end

---@param callback ModuleSceneStateChangedCallback
---@return LuaEventHandle handle
function ModuleBase:onSceneStateChanged(callback) end

---@param callback ModuleSceneStateChangedCallback
---@return LuaEventHandle handle
function ModuleBase:OnSceneStateChanged(callback) end

---@param callback ModuleWindowFocusChangedCallback @-1 表示无焦点窗口
---@return LuaEventHandle handle @调用 handle:Unregister() 反注册
function ModuleBase:onWindowFocusChanged(callback) end

---@param callback ModuleWindowFocusChangedCallback @-1 表示无焦点窗口
---@return LuaEventHandle handle @调用 handle:Unregister() 反注册
function ModuleBase:OnWindowFocusChanged(callback) end

---@param callback ModuleWindowCloseCallback
---@return LuaEventHandle handle @调用 handle:Unregister() 反注册
function ModuleBase:onWindowClose(callback) end

---@param callback ModuleWindowCloseCallback
---@return LuaEventHandle handle @调用 handle:Unregister() 反注册
function ModuleBase:OnWindowClose(callback) end

---@param callback ModuleChatMessageCallback
---@return LuaEventHandle handle @callback 返回 1 时拦截发送事件
function ModuleBase:onChatMessage(callback) end

---@param callback ModuleChatMessageCallback
---@return LuaEventHandle handle @callback 返回 1 时拦截发送事件
function ModuleBase:OnChatMessage(callback) end

---@param header string
---@param callback ModulePacketRecvCallback
---@return LuaEventHandle handle
function ModuleBase:onPacketRecv(header, callback) end

---@param header string
---@param callback ModulePacketRecvCallback
---@return LuaEventHandle handle
function ModuleBase:OnPacketRecv(header, callback) end

---@param header string
---@param callback ModulePacketSendCallback
---@return LuaEventHandle handle
function ModuleBase:onPacketSend(header, callback) end

---@param header string
---@param callback ModulePacketSendCallback
---@return LuaEventHandle handle
function ModuleBase:OnPacketSend(header, callback) end

---@param vkMain integer @0..255
---@param stateMask integer @1..255，见 CONST.KeyStateFlag
---@param callback ModuleKeyPressCallback
---@return LuaEventHandle handle
function ModuleBase:onKeyPress(vkMain, stateMask, callback) end

---@param vkMain integer @0..255
---@param vkList LuaVkList @附加按住键；可为单个 VK 或数组
---@param stateMask integer @1..255，见 CONST.KeyStateFlag
---@param callback ModuleKeyPressCallback
---@return LuaEventHandle handle
function ModuleBase:onKeyPress(vkMain, vkList, stateMask, callback) end

---@param vkMain integer
---@param stateMask integer
---@param callback ModuleKeyPressCallback
---@return LuaEventHandle handle
function ModuleBase:OnKeyPress(vkMain, stateMask, callback) end

---@param vkMain integer
---@param vkList LuaVkList
---@param stateMask integer
---@param callback ModuleKeyPressCallback
---@return LuaEventHandle handle
function ModuleBase:OnKeyPress(vkMain, vkList, stateMask, callback) end

---@param fullPacket string @完整封包；未以 \n 结尾时自动补齐
---@return integer result
function ModuleBase:sendPacket(fullPacket) end

---@param head string @协议头
---@param ... LuaPacketData @按空格拼接；integer 使用 62 进制编码，string 使用 nrproto 字符串转义；末尾自动补 \n
---@return integer result
function ModuleBase:sendPacket(head, ...) end

---@param fullPacket string @完整封包；未以 \n 结尾时自动补齐
---@return integer result
function ModuleBase:SendPacket(fullPacket) end

---@param head string @协议头
---@param ... LuaPacketData @按空格拼接；integer 使用 62 进制编码，string 使用 nrproto 字符串转义；末尾自动补 \n
---@return integer result
function ModuleBase:SendPacket(head, ...) end

---@param seNo integer @0..500
---@param panX integer @默认 320
---@return integer result @0 成功，-1 失败
function ModuleBase:playSe(seNo, panX) end

---@param seNo integer @0..500
---@param panX integer @默认 320
---@return integer result @0 成功，-1 失败
function ModuleBase:PlaySe(seNo, panX) end

---@param bgmNo integer @bin\bgm\bgm.cf 第二列 BGM 号
---@return integer result @1 成功，非 1 失败
function ModuleBase:loadAndPlayBGM(bgmNo) end

---@param bgmNo integer @bin\bgm\bgm.cf 第二列 BGM 号
---@return integer result @1 成功，非 1 失败
function ModuleBase:LoadAndPlayBGM(bgmNo) end

---@param type integer @固定 BGM 类型：0 或 1
---@param repeats integer @重复次数，传给原客户端
---@return integer result @1 成功，非 1 失败
function ModuleBase:playFixedBGM(type, repeats) end

---@param type integer @固定 BGM 类型：0 或 1
---@param repeats integer @重复次数，传给原客户端
---@return integer result @1 成功，非 1 失败
function ModuleBase:PlayFixedBGM(type, repeats) end

---@param msg string
function ModuleBase:cliSendMsg(msg) end

---@param msg string
---@param color integer @默认 0
function ModuleBase:cliSendMsg(msg, color) end

---@param msg string
---@param color integer @默认 0
---@param font integer @默认 0
function ModuleBase:cliSendMsg(msg, color, font) end

---@param msg string
---@param color integer @默认 0
---@param font integer @默认 0
---@param sender string|nil
function ModuleBase:cliSendMsg(msg, color, font, sender) end

---@param msg string
function ModuleBase:CliSendMsg(msg) end

---@param msg string
---@param color integer @默认 0
function ModuleBase:CliSendMsg(msg, color) end

---@param msg string
---@param color integer @默认 0
---@param font integer @默认 0
function ModuleBase:CliSendMsg(msg, color, font) end

---@param msg string
---@param color integer @默认 0
---@param font integer @默认 0
---@param sender string|nil
function ModuleBase:CliSendMsg(msg, color, font, sender) end

---@param value integer
---@return string encoded
function ModuleBase:nrEncode62(value) end

---@param value integer
---@return string encoded
function ModuleBase:NrEncode62(value) end

---@param value string
---@return integer decoded
function ModuleBase:nrDecode62(value) end

---@param value string
---@return integer decoded
function ModuleBase:NrDecode62(value) end

---@param value integer
---@return string encoded
function ModuleBase:nrEncode16(value) end

---@param value integer
---@return string encoded
function ModuleBase:NrEncode16(value) end

---@param value string
---@return integer decoded
function ModuleBase:nrDecode16(value) end

---@param value string
---@return integer decoded
function ModuleBase:NrDecode16(value) end

---@param value string
---@return string encoded
function ModuleBase:nrEncodeString(value) end

---@param value string
---@return string encoded
function ModuleBase:NrEncodeString(value) end

---@param value string
---@return string decoded
function ModuleBase:nrDecodeString(value) end

---@param value string
---@return string decoded
function ModuleBase:NrDecodeString(value) end

---@return boolean success
function ModuleBase:load() end

---@return boolean success
function ModuleBase:unload() end

---@return ModuleBase|nil module
---@return string|nil err
function ModuleBase:reload() end

function ModuleBase:onLoad() end

function ModuleBase:onUnload() end