local ModuleBase = {}
ModuleBase.__index = ModuleBase

local RESERVED_KEYS = {
    class = true,
    disposed = true,
    env = true,
    id = true,
    loaded = true,
    name = true,
    spec = true,
    state = true,
    _cleanup = true,
    _events = true,
    _windows = true,
    _owned = true,
}

local function as_name(value)
    if value == nil then
        return nil
    end
    if type(value) == 'table' then
        return value.name or tostring(value)
    end
    return tostring(value)
end

local function runtime_system()
    local system = rawget(_G, 'ModuleSystem')
    if type(system) == 'table' then
        return system
    end
    return nil
end

local function winmgr_fn(name)
    local api = rawget(_G, 'WinMgr')
    local fn = api and api[name]
    if type(fn) ~= 'function' then
        error('WinMgr.' .. tostring(name) .. ' is unavailable', 3)
    end
    return fn
end

local function has_method(resource, method_name)
    if resource == nil then
        return false
    end
    local ok, fn = pcall(function()
        return resource[method_name]
    end)
    return ok and type(fn) == 'function'
end

local function clear_table(tbl)
    if type(tbl) ~= 'table' then
        return
    end
    for key in pairs(tbl) do
        tbl[key] = nil
    end
end

function ModuleBase:extend(class_name)
    local class = {}
    class.__index = class
    class.__name = class_name or 'ModuleBase'
    class.__base = self
    return setmetatable(class, self)
end

function ModuleBase.__call(class, ...)
    return class:new(...)
end

function ModuleBase.__tostring(self)
    return string.format('ModuleBase<%s>', as_name(self))
end

function ModuleBase:new(spec)
    local instance = setmetatable({}, self)
    instance.class = self
    instance.spec = spec or {}
    instance.name = instance.spec.name or self.__name or 'ModuleBase'
    instance.id = instance.spec.id or self.__name or instance.name
    instance.env = instance.spec.env
    instance.loaded = false
    instance.disposed = false
    instance.state = {}
    instance._cleanup = {}
    instance._events = {}
    instance._windows = {}
    instance._owned = {}
    return instance
end

function ModuleBase:addCleanup(name, fn)
    if type(fn) ~= 'function' then
        error('cleanup callback must be function', 2)
    end
    local item = {
        name = name or ('cleanup_' .. tostring(#self._cleanup + 1)),
        fn = fn,
    }
    self._cleanup[#self._cleanup + 1] = item
    return item
end

function ModuleBase:defer(fn, name)
    return self:addCleanup(name, fn)
end

function ModuleBase:own(resource, disposer, name)
    if resource == nil then
        return nil
    end
    if type(disposer) ~= 'function' then
        return nil, 'disposer must be function'
    end
    self._owned[#self._owned + 1] = {
        resource = resource,
        disposer = disposer,
        name = name or as_name(resource) or 'resource',
    }
    return resource
end

function ModuleBase:ownEvent(handle)
    if handle then
        self._events[#self._events + 1] = handle
    end
    return handle
end

function ModuleBase:unregisterHandle(handle)
    if not handle then
        return false
    end
    for i = #self._events, 1, -1 do
        if self._events[i] == handle then
            table.remove(self._events, i)
            break
        end
    end
    if has_method(handle, 'Unregister') then
        return handle:Unregister()
    end
    return false
end

function ModuleBase:ownWindow(window)
    if window then
        self._windows[#self._windows + 1] = window
    end
    return window
end

function ModuleBase:releaseWindow(window)
    if not window then
        return false
    end
    for i = #self._windows, 1, -1 do
        if self._windows[i] == window then
            table.remove(self._windows, i)
            break
        end
    end
    if has_method(window, 'Close') then
        return window:Close()
    end
    return false
end

function ModuleBase:getModule(name)
    local system = runtime_system()
    if not system then
        return nil
    end
    return system:getModule(name)
end

function ModuleBase:loadModule(name, opt)
    local system = runtime_system()
    if not system then
        error('ModuleSystem is unavailable', 2)
    end
    return system:loadModule(name, opt)
end

function ModuleBase:reloadModule(name, opt)
    local system = runtime_system()
    if not system then
        error('ModuleSystem is unavailable', 2)
    end
    return system:reloadModule(name, opt)
end

function ModuleBase:unloadModule(name)
    local system = runtime_system()
    if not system then
        error('ModuleSystem is unavailable', 2)
    end
    return system:unloadModule(name)
end

function ModuleBase:listModules()
    local system = runtime_system()
    if not system then
        return {}
    end
    return system:listModules()
end

function ModuleBase:newWindow(param)
    local status, window = winmgr_fn('NewWindow')(param)
    self:ownWindow(window)
    return status, window
end

function ModuleBase:NewWindow(param)
    return self:newWindow(param)
end

function ModuleBase:findWindow(id)
    return winmgr_fn('FindWindow')(id)
end

function ModuleBase:FindWindow(id)
    return self:findWindow(id)
end

function ModuleBase:focus(id)
    return winmgr_fn('Focus')(id)
end

function ModuleBase:Focus(id)
    return self:focus(id)
end

function ModuleBase:closeWindow(id)
    return winmgr_fn('Close')(id)
end

function ModuleBase:Close(id)
    return self:closeWindow(id)
end

function ModuleBase:autoCopilot(x, y)
    return winmgr_fn('AutoCopilot')(x, y)
end

function ModuleBase:AutoCopilot(x, y)
    return self:autoCopilot(x, y)
end

function ModuleBase:stopCopilot()
    return winmgr_fn('StopCopilot')()
end

function ModuleBase:StopCopilot()
    return self:stopCopilot()
end

function ModuleBase:getAutoCopliotState()
    return winmgr_fn('GetAutoCopliotState')()
end

function ModuleBase:GetAutoCopliotState()
    return self:getAutoCopliotState()
end

function ModuleBase:onSceneStateChanged(callback)
    return self:ownEvent(winmgr_fn('OnSceneStateChanged')(callback))
end

function ModuleBase:OnSceneStateChanged(callback)
    return self:onSceneStateChanged(callback)
end

function ModuleBase:onWindowFocusChanged(callback)
    return self:ownEvent(winmgr_fn('OnWindowFocusChanged')(callback))
end

function ModuleBase:OnWindowFocusChanged(callback)
    return self:onWindowFocusChanged(callback)
end

function ModuleBase:onWindowClose(callback)
    return self:ownEvent(winmgr_fn('OnWindowClose')(callback))
end

function ModuleBase:OnWindowClose(callback)
    return self:onWindowClose(callback)
end

function ModuleBase:onChatMessage(callback)
    return self:ownEvent(winmgr_fn('OnChatMessage')(callback))
end

function ModuleBase:OnChatMessage(callback)
    return self:onChatMessage(callback)
end

function ModuleBase:onPacketRecv(header, callback)
    return self:ownEvent(winmgr_fn('OnPacketRecv')(header, callback))
end

function ModuleBase:OnPacketRecv(header, callback)
    return self:onPacketRecv(header, callback)
end

function ModuleBase:onPacketSend(header, callback)
    return self:ownEvent(winmgr_fn('OnPacketSend')(header, callback))
end

function ModuleBase:OnPacketSend(header, callback)
    return self:onPacketSend(header, callback)
end

function ModuleBase:onKeyPress(...)
    return self:ownEvent(winmgr_fn('OnKeyPress')(...))
end

function ModuleBase:OnKeyPress(...)
    return self:onKeyPress(...)
end

function ModuleBase:sendPacket(...)
    return winmgr_fn('SendPacket')(...)
end

function ModuleBase:SendPacket(...)
    return self:sendPacket(...)
end

function ModuleBase:playSe(...)
    return winmgr_fn('PlaySe')(...)
end

function ModuleBase:PlaySe(...)
    return self:playSe(...)
end

function ModuleBase:loadAndPlayBGM(...)
    return winmgr_fn('LoadAndPlayBGM')(...)
end

function ModuleBase:LoadAndPlayBGM(...)
    return self:loadAndPlayBGM(...)
end

function ModuleBase:playFixedBGM(...)
    return winmgr_fn('PlayFixedBGM')(...)
end

function ModuleBase:PlayFixedBGM(...)
    return self:playFixedBGM(...)
end

function ModuleBase:cliSendMsg(...)
    return winmgr_fn('CliSendMsg')(...)
end

function ModuleBase:CliSendMsg(...)
    return self:cliSendMsg(...)
end

function ModuleBase:nrEncode62(value)
    return winmgr_fn('NrEncode62')(value)
end

function ModuleBase:NrEncode62(value)
    return self:nrEncode62(value)
end

function ModuleBase:nrDecode62(value)
    return winmgr_fn('NrDecode62')(value)
end

function ModuleBase:NrDecode62(value)
    return self:nrDecode62(value)
end

function ModuleBase:nrEncode16(value)
    return winmgr_fn('NrEncode16')(value)
end

function ModuleBase:NrEncode16(value)
    return self:nrEncode16(value)
end

function ModuleBase:nrDecode16(value)
    return winmgr_fn('NrDecode16')(value)
end

function ModuleBase:NrDecode16(value)
    return self:nrDecode16(value)
end

function ModuleBase:nrEncodeString(value)
    return winmgr_fn('NrEncodeString')(value)
end

function ModuleBase:NrEncodeString(value)
    return self:nrEncodeString(value)
end

function ModuleBase:nrDecodeString(value)
    return winmgr_fn('NrDecodeString')(value)
end

function ModuleBase:NrDecodeString(value)
    return self:nrDecodeString(value)
end

function ModuleBase:load()
    self.loaded = true
    self.disposed = false
    local ok, err = pcall(function()
        if type(self.onLoad) == 'function' then
            self:onLoad()
        end
    end)
    if not ok then
        error(err, 0)
    end
    return true
end

function ModuleBase:unload()
    if self.disposed then
        return true
    end

    pcall(function()
        if type(self.onUnload) == 'function' then
            self:onUnload()
        end
    end)

    for i = #self._cleanup, 1, -1 do
        local item = self._cleanup[i]
        pcall(item.fn, self)
    end

    for i = #self._owned, 1, -1 do
        local item = self._owned[i]
        pcall(item.disposer, item.resource, self)
    end

    for i = #self._events, 1, -1 do
        local handle = self._events[i]
        if has_method(handle, 'Unregister') then
            pcall(handle.Unregister, handle)
        end
    end

    for i = #self._windows, 1, -1 do
        local window = self._windows[i]
        if has_method(window, 'Close') then
            pcall(window.Close, window)
        end
    end

    clear_table(self._cleanup)
    clear_table(self._owned)
    clear_table(self._events)
    clear_table(self._windows)
    clear_table(self.state)
    self.loaded = false
    self.disposed = true

    for key in pairs(self) do
        if not RESERVED_KEYS[key] then
            self[key] = nil
        end
    end
    self.state = nil
    self.spec = nil
    self.env = nil
    return true
end

function ModuleBase:reload()
    local system = runtime_system()
    if system then
        return system:reloadModule(self.name)
    end
    error('ModuleSystem is unavailable', 2)
end

function ModuleBase:onLoad()
end

function ModuleBase:onUnload()
end

return ModuleBase