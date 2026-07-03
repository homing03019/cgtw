#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Disable all lua login announcements + patch cgmsv channel strings."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
GMSV = "/cgmsv_26.5c/gmsv"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
TOOLS = Path(r"D:/cgtw/tools")

WELCOME = f"{GMSV}/lua/Modules/welcome.lua"
PET = f"{GMSV}/lua/Modules/petSummonContract.lua"
MODULE_CFG = f"{GMSV}/lua/ModuleConfig.lua"


def fetch() -> None:
    subprocess.run(["scp", f"{REMOTE}:{WELCOME}", str(TEMP / "welcome.lua")], check=True)
    subprocess.run(["scp", f"{REMOTE}:{PET}", str(TEMP / "petSummonContract.lua")], check=True)
    subprocess.run(["scp", f"{REMOTE}:{MODULE_CFG}", str(TEMP / "ModuleConfig.lua")], check=True)


def patch_welcome(text: str) -> str:
    if "function Welcome:onLogin(player)\n  return\nend" in text.replace("\r\n", "\n"):
        return text
    text = text.replace("\r\n", "\n")
    # Replace entire welcome block
    old = """local announceflg = true;  --对首次进入游戏玩家全副公告
local WelcomeMessage = {}; --欢迎词
table.insert(WelcomeMessage, "欢迎使用cgmsv引擎");
table.insert(WelcomeMessage, "自定义欢迎信息,请在gmsv\\\\lua\\\\Modules\\\\welcome.lua内修改!");

function Welcome:onLogin(player)
  if (WelcomeMessage ~= nil) then   --欢迎词
    for _, text in ipairs(WelcomeMessage) do
      NLG.TalkToCli(player, -1, text, CONST.颜色_黄色, CONST.字体_中);
    end
    if (announceflg == true and Char.GetData(player, CONST.对象_登陆次数) == 1) then
      NLG.SystemMessage(-1, "欢迎[" .. Char.GetData(player, CONST.对象_原名) .. "]来到了游戏.")
    end
  end
end"""
    new = """local announceflg = false;
local WelcomeMessage = {};

function Welcome:onLogin(player)
  return
end"""
    if old not in text:
        raise SystemExit("welcome.lua pattern missing")
    return text.replace(old, new)


def patch_pet(text: str) -> str:
    text = text.replace("\r\n", "\n")
    # Stop Chaz test spam every login
    text = text.replace(
        """  NLG.SystemMessage(charIndex, string.format('[契约] 宠技已换客户端ID x%d，第三招=活杀气功弹', learned))
  return true
end""",
        """  return true
end""",
        1,
    )
    # Only run fix once
    needle = "function Module:fixChazPetSkillsOnce(charIndex)\n  local cdkey"
    if "CHAZ_PET_SKILL_FIX_FLAG" in text and "if io.open(CHAZ_PET_SKILL_FIX_FLAG, 'r') then" not in text:
        text = text.replace(
            needle,
            """function Module:fixChazPetSkillsOnce(charIndex)
  if io.open(CHAZ_PET_SKILL_FIX_FLAG, 'r') then
    return false
  end
  local cdkey""",
            1,
        )
    # Remove test contract on login
    text = text.replace(
        """    if self:isChazChar(charIndex) then
      self:giveChazContractPending(charIndex)
      self:giveRandomTestContractToChaz()
      self:fixChazCharm(charIndex)
    end""",
        """    if self:isChazChar(charIndex) then
      self:fixChazCharm(charIndex)
    end""",
        1,
    )
    text = text.replace("  self:giveRandomTestContractToChaz()\n", "", 1)
    # Silence test contract message
    text = text.replace(
        """          NLG.SystemMessage(charIndex, string.format(
            '[测试] 已发放随机宠物契约(%s)。', self:getEnemyName(enemyId) or '?'))""",
        "",
        1,
    )
    return text


def patch_module_config(text: str) -> str:
    # keep welcome loaded but silent; optional comment
    return text


def deploy(path: Path, remote: str) -> None:
    subprocess.run(["scp", str(path), f"{REMOTE}:{remote}"], check=True)


def stop_server() -> None:
    subprocess.run(
        [
            "ssh",
            REMOTE,
            "powershell -NoProfile -ExecutionPolicy Bypass -File C:/cgmsv_26.5c/tools/stop-cgmsv-server.ps1",
        ],
        check=True,
    )


def restart() -> None:
    trigger = Path(r"C:/Users/User/.cursor/skills/cgmsv-restart/scripts/trigger_desktop_restart.ps1")
    subprocess.run(["scp", str(trigger), f"{REMOTE}:/cgmsv_26.5c/tools/trigger_desktop_restart.ps1"], check=True)
    subprocess.run(
        [
            "ssh",
            REMOTE,
            "powershell -NoProfile -ExecutionPolicy Bypass -File C:/cgmsv_26.5c/tools/trigger_desktop_restart.ps1",
        ],
        check=True,
    )


def main() -> int:
    fetch()
    w = patch_welcome((TEMP / "welcome.lua").read_bytes().decode("gbk"))
    p = patch_pet((TEMP / "petSummonContract.lua").read_bytes().decode("gbk"))
    w_out = TEMP / "welcome.patched.lua"
    p_out = TEMP / "petSummonContract.patched.lua"
    w_out.write_bytes(w.encode("gbk") + b"\n")
    p_out.write_bytes(p.encode("gbk") + b"\n")
    deploy(w_out, WELCOME)
    deploy(p_out, PET)
    print("lua login announcements disabled")
    stop_server()
    subprocess.run(["python", str(TOOLS / "patch_cgmsv_login_msgs.py")], check=True)
    restart()
    print("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
