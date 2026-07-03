#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set ground item/pet/gold despawn to 10 minutes in setup.cf."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_SETUP = "/cgmsv_26.5c/gmsv/setup.cf"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
TARGET_SECONDS = 600

REPLACEMENTS = {
    "Petdeletetime": TARGET_SECONDS,
    "Itemdeletetime": TARGET_SECONDS,
    "golddeletetime": TARGET_SECONDS,
}


def patch(text: str) -> str:
    text = text.replace("\r\n", "\n")
    for key, value in REPLACEMENTS.items():
        pattern = re.compile(rf"^({re.escape(key)}=)\d+\s*$", re.MULTILINE)
        if not pattern.search(text):
            raise SystemExit(f"{key} not found in setup.cf")
        text = pattern.sub(rf"\g<1>{value}", text, count=1)
    return text


def deploy(path: Path) -> None:
    subprocess.run(["scp", str(path), f"{REMOTE}:{REMOTE_SETUP}"], check=True)


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
    local = TEMP / "setup.cf"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_SETUP}", str(local)], check=True)
    text = local.read_bytes().decode("gbk")
    fixed = patch(text)
    out = TEMP / "setup_drop_10min.cf"
    out.write_bytes(fixed.encode("gbk") + b"\n")
    deploy(out)
    print("deployed setup.cf (Pet/Item/Gold deletetime=600)")
    restart()
    print("cgmsv restart triggered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
