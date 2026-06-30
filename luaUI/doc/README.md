# LuaUI 架构文档

## 入口

init.lua 是唯一入口，运行期 Lua 基础目录为 luaUI\\，加载顺序固定：

1. `luaUI\\CONST.lua`
2. `luaUI\\ModuleBase.lua`
3. `luaUI\\GlobalEvent.lua`
4. `luaUI\\ModuleSystem.lua`
5. `luaUI\\ModuleConfig.lua`

`ModuleConfig.lua` 默认不加载模块。需要启用模块时，在该文件中调用：

```lua
ModuleSystem:loadModule('demo')
```

## 目录

```text
luaUI/
  init.lua
  CONST.lua
  GlobalEvent.lua
  ModuleBase.lua
  ModuleSystem.lua
  ModuleConfig.lua
  modules/
    demo.lua
  doc/
    README.md
    CONST.lua
    WinMgr.lua
    Global.lua
```

## 模块规范

模块放在 `luaUI\\modules\\<name>.lua`，返回模块类表。

```lua
---@class DemoModule : ModuleBase
local DemoModule = ModuleBase:extend('demo')

function DemoModule:onLoad()
end

function DemoModule:onUnload()
end

return DemoModule
```

`onLoad` 用于注册事件、创建初始状态。`onUnload` 用于模块自定义清理；事件句柄和通过 `newWindow` 持有的窗口会由基类自动释放。

## ModuleSystem

常用接口：

```lua
ModuleSystem:loadModule(name, opt)
ModuleSystem:reloadModule(name, opt)
ModuleSystem:unloadModule(name)
ModuleSystem:getModule(name)
ModuleSystem:listModules()
ModuleSystem:close()
```

模块查找顺序：

1. `luaUI\\modules\\<name>.lua`
2. `luaUI\\modules\\<name>\\init.lua`
3. `luaUI\\<name>.lua`

## ModuleBase

模块内可用接口：

```lua
self:loadModule(name, opt)
self:reloadModule(name, opt)
self:unloadModule(name)
self:getModule(name)
self:listModules()
```

资源管理：

```lua
self:addCleanup(name, fn)
self:defer(fn, name)
self:own(resource, disposer, name)
self:ownEvent(handle)
self:unregisterHandle(handle)
self:ownWindow(window)
self:releaseWindow(window)
```

## WinMgr 代理

`ModuleBase` 封装了 `luaUI\doc\WinMgr.lua` 中列出的全部 `WinMgr` 接口：

```lua
self:newWindow(param)
self:findWindow(id)
self:focus(id)
self:closeWindow(id)
self:autoCopilot(x, y)
self:stopCopilot()
self:getAutoCopliotState()
self:onSceneStateChanged(callback)
self:onWindowFocusChanged(callback)
self:onWindowClose(callback)
self:onChatMessage(callback)
self:onPacketRecv(header, callback)
self:onPacketSend(header, callback)
self:onKeyPress(...)
self:sendPacket(...)
self:playSe(...)
self:loadAndPlayBGM(bgmNo)
self:playFixedBGM(type, repeats)
self:cliSendMsg(...)
self:nrEncode62(value)
self:nrDecode62(value)
self:nrEncode16(value)
self:nrDecode16(value)
self:nrEncodeString(value)
self:nrDecodeString(value)
```

同时保留对应的大写方法名，便于按 `WinMgr` 原名调用。

## 编码

项目所有文件使用 GBK 编码。读写文件必须显式指定 GBK，禁止使用默认编码。

## 示例模块

`luaUI\\modules\\demo.lua` 是旧 `init.lua` demo 迁移结果，默认不加载。需要测试时，在 `luaUI\ModuleConfig.lua` 取消注释：

```lua
ModuleSystem:loadModule('demo')
```