#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix manaPool module key, restore/safely silence login msgs, fix CONST corruption."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
GMSV = "/cgmsv_26.5c/gmsv"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")

REMOTE_EXE = f"{GMSV}/cgmsv.exe"
REMOTE_MODULES = f"{GMSV}/lua/Modules"
REMOTE_CFG = f"{GMSV}/lua/ModuleConfig.lua"

CONST_FIXES = {
    "%对象_交易开关%": "CONST.对象_交易开关",
    "%道具_价格%": "CONST.道具_价格",
    "%道具_序%": "CONST.道具_序",
}
CORRUPT_RE = re.compile(r"%([\u4e00-\u9fff_][\u4e00-\u9fff0-9_]*)%")

# Login channel hints embedded in cgmsv.exe (GBK)
SILENCE_MSGS = [
    "您已进入新手频道,可以使用 /n 内容 的方式来发言.",
    "您已进入职业频道,可以使用 /j 内容 的方式来发言.",
    "您并不在职业频道中,所以无法发言.",
    "您并不在新手频道中,所以无法发言.",
    "您已进入新手频道,可以使用!",
    "您已进入职业频道,可以使用!",
    "!内容 的方式来进行发言.",
    "欢迎使用cgmsv引擎.",
    "自定义欢迎信息,请在gmsv\\lua\\Modules\\welcome.lua内修改!",
]


def fetch_modules() -> Path:
    local = TEMP / "srv_modules_fix"
    local.mkdir(exist_ok=True)
    subprocess.run(["scp", "-r", f"{REMOTE}:{REMOTE_MODULES}/*.lua", str(local)], check=True)
    return local


def fix_lua_corruption(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    for old, new in CONST_FIXES.items():
        if old in text:
            text = text.replace(old, new)
            changes.append(f"{old} -> {new}")

    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        if name.startswith(("对象_", "道具_", "CHAR_")):
            changes.append(f"%{name}% -> CONST.{name}")
            return f"CONST.{name}"
        return m.group(0)

    return CORRUPT_RE.sub(repl, text), changes


def patch_heroes_battle_over(text: str) -> str:
    text, _ = fix_lua_corruption(text)
    text = text.replace("    return\n    return\n", "    return\n", 1)
    old = """      if randValue>=min and randValue<=max then
        if Char.GetEmptyItemSlot(charIndex) < 0 then
          NLG.Say(charIndex,-1,"背包满了", CONST.颜色_红色, 0)
          return
        end
        local itemIndex = Char.GiveItem(charIndex, itemId, 1)
        if itemIndex < 0 then
          self:logInfo("battle drop skipped", charIndex, itemId)
          return
        end
        Item.SetData(itemIndex, CONST.道具_已鉴定, 1)
        goto continue;
      end
      ::continue::"""
    new = """      if randValue>=min and randValue<=max then
        if Char.GetEmptyItemSlot(charIndex) < 0 then
          NLG.Say(charIndex,-1,"背包满了", CONST.颜色_红色, 0)
          return
        end
        local itemIndex = Char.GiveItem(charIndex, itemId, 1)
        if itemIndex < 0 then
          self:logInfo("battle drop skipped", charIndex, itemId)
          return
        end
        Item.SetData(itemIndex, CONST.道具_已鉴定, 1)
        break
      end"""
    if old in text:
        text = text.replace(old, new, 1)
    return text


def patch_module_config(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    old = "loadModule('heroesBattleOver')"
    new = "loadModule('manaPool', { path = 'heroesBattleOver.lua' })"
    if old in text:
        text = text.replace(old, new, 1)
        changes.append("register manaPool under correct module key")
    boot = """
if getModule('manaPool') == nil then
  logError('BOOT', 'manaPool NOT LOADED')
else
  logInfo('BOOT', 'manaPool OK')
end"""
    if "manaPool NOT LOADED" not in text:
        text = text.rstrip() + boot + "\n"
        changes.append("added manaPool boot check")
    return text, changes


def null_out_messages(data: bytearray) -> list[str]:
    log: list[str] = []
    for msg in SILENCE_MSGS:
        b = msg.encode("gbk")
        off = 0
        while True:
            idx = data.find(b, off)
            if idx < 0:
                break
            for i in range(idx, idx + len(b)):
                data[i] = 0
            log.append(f"nulled @{idx} len={len(b)} {msg[:24]}...")
            off = idx + len(b)
    return log


def restore_and_patch_exe() -> list[str]:
    bak = TEMP / "cgmsv.exe.bak_login_msgs"
    if not bak.exists():
        subprocess.run(["scp", f"{REMOTE}:{REMOTE_EXE}", str(bak)], check=True)
    data = bytearray(bak.read_bytes())
    log = null_out_messages(data)
    out = TEMP / "cgmsv_silenced.exe"
    out.write_bytes(data)
    subprocess.run(["scp", str(out), f"{REMOTE}:{REMOTE_EXE}"], check=True)
    return ["restored cgmsv.exe from backup"] + log


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
    report: list[str] = []
    mods = fetch_modules()

    for f in sorted(mods.glob("*.lua")):
        try:
            text = f.read_bytes().decode("gbk")
        except UnicodeDecodeError:
            report.append(f"GBK_DECODE_FAIL: {f.name}")
            continue
        fixed, changes = fix_lua_corruption(text)
        if f.name == "heroesBattleOver.lua":
            fixed = patch_heroes_battle_over(fixed)
        if fixed != text:
            out = TEMP / f"fixed_{f.name}"
            out.write_bytes(fixed.encode("gbk") + b"\n")
            deploy(out, f"{REMOTE_MODULES}/{f.name}")
            report.append(f"FIXED {f.name}: {changes}")

    cfg_local = TEMP / "ModuleConfig.lua"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_CFG}", str(cfg_local)], check=True)
    cfg, cfg_changes = patch_module_config(cfg_local.read_bytes().decode("gbk"))
    if cfg_changes:
        cfg_out = TEMP / "ModuleConfig.patched.lua"
        cfg_out.write_bytes(cfg.encode("gbk") + b"\n")
        deploy(cfg_out, REMOTE_CFG)
        report.append(f"FIXED ModuleConfig.lua: {cfg_changes}")

    stop_server()
    report.extend(restore_and_patch_exe())
    restart()

    out = TEMP / "fix_login_garble_report.txt"
    out.write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
