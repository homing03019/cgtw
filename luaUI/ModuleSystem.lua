local PATH_SEP = string.char(92)

local function normalize_base(base)
    base = base or ('luaUI' .. PATH_SEP)
    if base == '' then
        return ''
    end
    local tail = string.sub(base, -1)
    if tail ~= PATH_SEP and tail ~= '/' then
        base = base .. PATH_SEP
    end
    return base
end

local LUAUI_BASE = normalize_base(rawget(_G, 'LUAUI_BASE') or ('luaUI' .. PATH_SEP))

local function is_absolute_path(path)
    if type(path) ~= 'string' or path == '' then
        return false
    end
    local first = string.sub(path, 1, 1)
    if first == PATH_SEP or first == '/' then
        return true
    end
    return string.match(path, '^%a:') ~= nil
end

local function has_luaui_prefix(path)
    return string.sub(path, 1, 6) == ('luaUI' .. PATH_SEP)
        or string.sub(path, 1, 6) == 'luaUI/'
end

local function runtime_path(path, base)
    if type(path) ~= 'string' then
        return path
    end
    if path == '' or is_absolute_path(path) or has_luaui_prefix(path) then
        return path
    end
    return normalize_base(base or LUAUI_BASE) .. path
end

local GlobalEvent = rawget(_G, 'GlobalEvent') or dofile(runtime_path('GlobalEvent.lua', LUAUI_BASE))
local ModuleBase = rawget(_G, 'ModuleBase') or dofile(runtime_path('ModuleBase.lua', LUAUI_BASE))

local ModuleSystem = {}
ModuleSystem.__index = ModuleSystem

local function shallow_copy(src, dst)
    dst = dst or {}
    if type(src) ~= 'table' then
        return dst
    end
    for key, value in pairs(src) do
        dst[key] = value
    end
    return dst
end

local function readonly_proxy(source)
    source = source or {}
    return setmetatable({}, {
        __index = source,
        __newindex = function()
            error('read-only API table', 2)
        end,
        __metatable = false,
    })
end

local function make_module_print(module_name)
    local global_print = print
    local prefix = string.format('[%s]', tostring(module_name or 'module'))
    return function(...)
        return global_print(prefix, ...)
    end
end

local function file_exists(path)
    local handle = io.open(path, 'r')
    if handle then
        handle:close()
        return true
    end
    return false
end

local function load_chunk(path, env)
    local chunk, err
    if setfenv then
        chunk, err = loadfile(path)
        if not chunk then
            return nil, err
        end
        setfenv(chunk, env)
        return chunk
    end
    chunk, err = loadfile(path, 't', env)
    if not chunk then
        return nil, err
    end
    return chunk
end

local function make_env(system, name, opt)
    opt = opt or {}
    local base = {
        assert = assert,
        error = error,
        ipairs = ipairs,
        next = next,
        pairs = pairs,
        pcall = pcall,
        select = select,
        tonumber = tonumber,
        tostring = tostring,
        type = type,
        unpack = unpack,
        xpcall = xpcall,
        math = math,
        string = string,
        table = table,
        coroutine = coroutine,
        os = os,
        io = io,
        debug = debug,
        rawget = rawget,
        rawset = rawset,
        getmetatable = getmetatable,
        setmetatable = setmetatable,
        load = load,
        loadfile = loadfile,
        dofile = dofile,
        print = make_module_print(name),
        ModuleBase = ModuleBase,
        ModuleSystem = system,
        GlobalEvent = GlobalEvent,
        CONST = readonly_proxy(rawget(_G, 'CONST')),
        WinMgr = readonly_proxy(rawget(_G, 'WinMgr')),
        Player = readonly_proxy(rawget(_G, 'Player')),
        Graphic = readonly_proxy(rawget(_G, 'Graphic')),
    }

    if system and type(system.opt) == 'table' and type(system.opt.globals) == 'table' then
        shallow_copy(system.opt.globals, base)
    end
    if type(opt.globals) == 'table' then
        shallow_copy(opt.globals, base)
    end

    local env = {}
    env._G = env
    env.__name = name
    env.__system = system
    env.__module_name = name
    env.dofile = function(path)
        local chunk, err = load_chunk(runtime_path(path, system.basePath), env)
        if not chunk then
            error(err, 0)
        end
        return chunk()
    end
    env.loadfile = function(path)
        local chunk, err = load_chunk(runtime_path(path, system.basePath), env)
        if not chunk then
            return nil, err
        end
        return chunk
    end

    return setmetatable(env, {
        __index = base,
        __newindex = function(t, key, value)
            rawset(t, key, value)
        end,
    })
end

function ModuleSystem:init(opt)
    opt = opt or {}
    self.modules = {}
    self.sequence = 0
    self.opt = opt
    self.basePath = normalize_base(opt.basePath or opt.base_path or LUAUI_BASE)
    self.events = {
        module = GlobalEvent.new('ModuleSystem'),
    }
    return self
end

function ModuleSystem:_resolve_path(name, opt)
    local basePath = self.basePath or LUAUI_BASE
    if opt and opt.path then
        return runtime_path(opt.path, basePath)
    end
    return runtime_path(string.format('modules' .. PATH_SEP .. '%s.lua', name), basePath)
end

function ModuleSystem:_load_class(name, path, opt)
    local env = make_env(self, name, opt or {})
    local chunk, err = load_chunk(path, env)
    if not chunk then
        return nil, err, env
    end
    local ok, result = pcall(chunk)
    if not ok then
        return nil, result, env
    end
    return result, nil, env
end

function ModuleSystem:_instantiate(name, path, class, env, opt)
    if type(class) ~= 'table' and type(env[name]) == 'table' then
        class = env[name]
    end
    if type(class) ~= 'table' then
        return nil, 'module chunk must return a module class table'
    end
    if type(class.new) ~= 'function' then
        return nil, 'module class must provide new()'
    end

    self.sequence = self.sequence + 1
    local id = string.format('%s#%d', name, self.sequence)
    local instance = class:new({
        name = name,
        path = path,
        env = env,
        id = id,
        opt = opt or {},
    })
    instance.env = env
    instance.spec = instance.spec or {}
    instance.spec.path = path
    instance.spec.name = name
    instance.spec.env = env
    instance.spec.id = id
    instance.class = class
    instance.name = name
    instance.id = id
    return instance
end

function ModuleSystem:loadModule(name, opt)
    opt = opt or {}
    local existing = self.modules[name]
    if existing and not opt.forceReload then
        return existing
    end

    if existing then
        local ok = self:unloadModule(name)
        if not ok then
            return nil, 'failed to unload existing module'
        end
    end

    local path, path_err = self:_resolve_path(name, opt)
    if not path then
        return nil, path_err
    end

    local class, err, env = self:_load_class(name, path, opt)
    if not class then
        return nil, err
    end

    local instance, inst_err = self:_instantiate(name, path, class, env, opt)
    if not instance then
        return nil, inst_err
    end

    self.modules[name] = instance
    local ok, load_err = pcall(function()
        instance:load()
    end)
    if not ok then
        pcall(function()
            instance:unload()
        end)
        self.modules[name] = nil
        return nil, load_err
    end

    return instance
end

function ModuleSystem:reloadModule(name, opt)
    opt = opt or {}
    local current = self.modules[name]
    if not current then
        return self:loadModule(name, opt)
    end
    return self:loadModule(name, {
        path = opt.path or (current.spec and current.spec.path),
        forceReload = true,
        globals = opt.globals,
    })
end

function ModuleSystem:unloadModule(name)
    local module = self.modules[name]
    if not module then
        return true
    end
    local ok = pcall(function()
        module:unload()
    end)
    self.modules[name] = nil
    return ok
end

function ModuleSystem:getModule(name)
    return self.modules[name]
end

function ModuleSystem:listModules()
    local list = {}
    for name, module in pairs(self.modules) do
        list[#list + 1] = {
            name = name,
            id = module.id,
            loaded = module.loaded,
        }
    end
    table.sort(list, function(a, b)
        return tostring(a.name) < tostring(b.name)
    end)
    return list
end

function ModuleSystem:close()
    local names = {}
    for name in pairs(self.modules) do
        names[#names + 1] = name
    end
    for i = 1, #names do
        pcall(function()
            self:unloadModule(names[i])
        end)
    end
end

return ModuleSystem