#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Disable redundant battle-end packagesort chat notice; sort kept in manaPool."""
from __future__ import annotations

import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
GMSV = "/cgmsv_26.5c/gmsv"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")

PACKAGESORT_OLD = '\t\t\tNLG.SystemMessage(player,"背包整理完毕。");'
PACKAGESORT_NEW = "\t\t\t-- bag sort notice silenced"

MODULECONFIG_OLD = "useModule('packagesort')"
MODULECONFIG_NEW = "-- useModule('packagesort')  -- disabled: duplicate SortItem; manaPool handles battle sort"


def patch_packagesort(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if PACKAGESORT_OLD in text:
        return text.replace(PACKAGESORT_OLD, PACKAGESORT_NEW, 1)
    if "bag sort notice silenced" in text:
        return text
    raise SystemExit("packagesort.lua message line not found")


def patch_module_config(text: str) -> str:
    text = text.replace("\r\n", "\n")
    if MODULECONFIG_OLD in text and MODULECONFIG_NEW not in text:
        return text.replace(MODULECONFIG_OLD, MODULECONFIG_NEW, 1)
    if MODULECONFIG_NEW in text or "disabled: duplicate SortItem" in text:
        return text
    raise SystemExit("ModuleConfig packagesort line not found")


def write_gbk(path: Path, text: str) -> None:
    path.write_bytes(text.encode("gbk") + b"\n")


def deploy(local: Path, remote: str) -> None:
    subprocess.run(["scp", str(local), f"{REMOTE}:{remote}"], check=True)


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
    pkg_local = TEMP / "packagesort_live.lua"
    cfg_local = TEMP / "ModuleConfig_live.lua"
    subprocess.run(["scp", f"{REMOTE}:{GMSV}/lua/Module/packagesort.lua", str(pkg_local)], check=True)
    subprocess.run(["scp", f"{REMOTE}:{GMSV}/lua/ModuleConfig.lua", str(cfg_local)], check=True)

    pkg_text = patch_packagesort(pkg_local.read_bytes().decode("gbk"))
    cfg_text = patch_module_config(cfg_local.read_bytes().decode("gbk"))

    pkg_out = TEMP / "packagesort_silent.lua"
    cfg_out = TEMP / "ModuleConfig_no_packagesort.lua"
    write_gbk(pkg_out, pkg_text)
    write_gbk(cfg_out, cfg_text)

    deploy(pkg_out, f"{GMSV}/lua/Module/packagesort.lua")
    deploy(cfg_out, f"{GMSV}/lua/ModuleConfig.lua")
    print("disabled packagesort module + silenced legacy message")
    restart()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
