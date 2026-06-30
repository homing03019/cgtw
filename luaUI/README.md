# LuaUI

CrossGate LuaUI 模块化入口项目。

## 路径基准

运行期 Lua 基础目录为 luaUI\\。入口和模块加载都会使用该前缀，避免从上级目录启动时加载失败。

## 当前结构

- `init.lua`：唯一入口，只负责加载架构和配置。
- `CONST.lua`：运行常量。
- `GlobalEvent.lua`：通用事件列表。
- `ModuleBase.lua`：模块基类，提供生命周期、资源释放、WinMgr 代理。
- `ModuleSystem.lua`：模块加载、卸载、重载、列表，默认从 `luaUI\\` 下解析模块路径。
- `ModuleConfig.lua`：模块启动配置，默认不加载任何模块。
- `luaUI\modules\`：业务模块目录。
- `luaUI\doc\`：接口文档与架构说明。

## 启用模块

编辑 `luaUI\ModuleConfig.lua`：

```lua
ModuleSystem:loadModule('demo')
```

## 新建模块

在 `luaUI\modules\` 目录新增 `<name>.lua`：

```lua
local MyModule = ModuleBase:extend('myModule')

function MyModule:onLoad()
end

function MyModule:onUnload()
end

return MyModule
```

## 约束

- 所有文件使用 GBK 编码。
- 不直接引入外部依赖。
- 默认不编译、不调试。
- 每次改动保持最小化。
- 不确定的业务逻辑先澄清，不自行扩展。

更多说明见 `luaUI\doc\README.md`。