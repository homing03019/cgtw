#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheme A: proxy tech ids (409/2700...) + effect ids 901-905.
- Client bin: anime 110901-110905 (patch if missing)
- Server tech.txt: proxy rows effect column -> 901-905

WARNING: Do NOT run this on production without client bins 901-905 deployed.
It overwrites VANILLA proxy rows (409/2700/2800/2900/3000) and breaks player/pet
super magic. Use tools/fix_super_magic_tech_effects.py to revert.
"""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:/cgtw")
TOOLS = ROOT / "tools"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
REMOTE = "cgmsv-server"
REMOTE_TECH = "/cgmsv_26.5c/gmsv/data/tech.txt"

# tech_id (col index 3) -> contract effect id
PROXY_EFFECT = {
    "409": 901,
    "2700": 902,
    "2800": 903,
    "2900": 904,
    "3000": 905,
}

# contract skill_id (col 5) -> effect (keep 199xxx rows aligned)
SKILL_EFFECT = {
    "991": 901,
    "992": 902,
    "993": 903,
    "994": 904,
    "995": 905,
}

REQUIRED_ANIME = {
    "base": (ROOT / "bin" / "AnimeInfo_4.bin", 110901),
    "puk2": (ROOT / "bin" / "Puk2" / "AnimeInfo_PUK2_4.bin", 110902),
}


def bins_have_effects() -> bool:
    ok = True
    for label, (path, need_id) in REQUIRED_ANIME.items():
        if not path.exists():
            print(f"MISSING {label} {path}")
            ok = False
            continue
        raw = path.read_bytes()
        found = any(
            struct.unpack_from("<i", raw, off)[0] == need_id
            for off in range(0, len(raw) - 11, 12)
        )
        print(f"bin {label} anime {need_id}: {'OK' if found else 'MISSING'}")
        ok = ok and found
    return ok


def patch_server_tech() -> tuple[int, list[str]]:
    local = TEMP / "tech_proxy_effects.txt"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_TECH}", str(local)], check=True)
    text = local.read_bytes().decode("gbk")
    log: list[str] = []
    changed = 0
    out_lines: list[str] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 9:
            out_lines.append(line)
            continue
        tid = parts[3]
        sid = parts[5]
        new_eff = PROXY_EFFECT.get(tid) or SKILL_EFFECT.get(sid)
        if new_eff is not None:
            old = parts[8]
            parts[8] = str(new_eff)
            if old != parts[8]:
                changed += 1
                log.append(f"tech={tid} skill={sid} effect {old}->{parts[8]}")
        out_lines.append("\t".join(parts))
    out = TEMP / "tech_proxy_effects.bin"
    out.write_bytes("\n".join(out_lines).encode("gbk") + b"\n")
    subprocess.run(["scp", str(out), f"{REMOTE}:{REMOTE_TECH}"], check=True)
    return changed, log


def main() -> int:
    print("=== Scheme A: effects 901-905 on proxy tech ===")
    if not bins_have_effects():
        print("Patching client bins (901-905)...")
        subprocess.run([sys.executable, str(TOOLS / "patch_contract_effects.py")], check=True)
        if not bins_have_effects():
            print("ERROR: client bins still missing 901-905 animes")
            return 1
    else:
        print("Client bins already contain 901-905 animes.")

    n, log = patch_server_tech()
    print(f"Server tech.txt: {n} rows updated")
    for row in log[:20]:
        print(" ", row)
    if len(log) > 20:
        print(f"  ... +{len(log) - 20} more")

    print(
        "\nDone. Restart cgmsv (reload tech.txt) + restart cg2d.\n"
        "Pets still use proxy ids 409/2700...; battle should play effect 901-905."
    )
    print("Applying client AnimeInfo redirect (117->110901 etc.)...")
    subprocess.run([sys.executable, str(TOOLS / "deploy_contract_effects_client.py")], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
