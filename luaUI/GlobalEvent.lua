local GlobalEvent = {}
GlobalEvent.__index = GlobalEvent
GlobalEvent.STOP = {}

local function to_name(value)
    if value == nil then
        return nil
    end
    if type(value) == 'table' then
        return value.name or tostring(value)
    end
    return tostring(value)
end

local function sort_handlers(list)
    table.sort(list, function(a, b)
        if a.priority ~= b.priority then
            return a.priority > b.priority
        end
        return a.order < b.order
    end)
end

function GlobalEvent.new(name)
    local self = setmetatable({}, GlobalEvent)
    self.name = name or 'GlobalEvent'
    self.handlers = {}
    self.handler_by_id = {}
    self.next_id = 0
    self.next_order = 0
    return self
end

function GlobalEvent:add(owner, fn, opt)
    if type(fn) ~= 'function' then
        return nil, 'callback must be function'
    end
    opt = opt or {}
    self.next_id = self.next_id + 1
    self.next_order = self.next_order + 1
    local handle = {
        id = self.next_id,
        owner = owner,
        owner_name = to_name(owner),
        fn = fn,
        priority = tonumber(opt.priority) or 0,
        order = self.next_order,
        tag = opt.tag,
    }
    self.handlers[#self.handlers + 1] = handle
    self.handler_by_id[handle.id] = handle
    sort_handlers(self.handlers)
    return handle
end

function GlobalEvent:remove(handle)
    if type(handle) == 'number' then
        handle = self.handler_by_id[handle]
    end
    if not handle then
        return false
    end
    for i = #self.handlers, 1, -1 do
        if self.handlers[i] == handle then
            table.remove(self.handlers, i)
            self.handler_by_id[handle.id] = nil
            return true
        end
    end
    return false
end

function GlobalEvent:remove_owner(owner)
    local removed = 0
    for i = #self.handlers, 1, -1 do
        local handle = self.handlers[i]
        if handle.owner == owner then
            table.remove(self.handlers, i)
            self.handler_by_id[handle.id] = nil
            removed = removed + 1
        end
    end
    return removed
end

function GlobalEvent:dispatch(...)
    for i = 1, #self.handlers do
        local handle = self.handlers[i]
        local ok, ret = pcall(handle.fn, handle.owner, ...)
        if ok and (ret == false or ret == GlobalEvent.STOP) then
            return ret
        end
    end
    return nil
end

return GlobalEvent