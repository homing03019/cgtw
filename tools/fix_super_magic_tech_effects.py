#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restore vanilla battle effect ids for super magic / spiracle skills.

Scheme A (deploy_contract_effects_A.py) wrongly set proxy tech rows
409 / 2700 / 2800 / 2900 / 3000 to effects 901-905. The cg2d client only
understands vanilla effects 117 / 317-320, so player AND pet super magic break.

Also maps contract skill rows (991-995) back to vanilla effects.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REMOTE = "cgmsv-server"
REMOTE_TECH = "/cgmsv_26.5c/gmsv/data/tech.txt"
TEMP = Path(r"C:/Users/User/AppData/Local/Temp")
VANILLA = Path(r"D:/cgtw/_backup/client_tech/20260701_084115_before_exe_re/server/tech.txt")

# tech id (col 3) -> vanilla effect from backup
PROXY_TECH = {"409", "2700", "2800", "2900", "3000"}

# contract skill id (col 5) -> client-known effect
CONTRACT_SKILL_EFFECT = {
    "991": "117",
    "992": "317",
    "993": "318",
    "994": "319",
    "995": "320",
}


def load_vanilla_proxy_effects() -> dict[str, str]:
    if not VANILLA.exists():
        raise SystemExit(f"vanilla tech backup missing: {VANILLA}")
    text = VANILLA.read_bytes().decode("gbk")
    out: dict[str, str] = {}
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 9:
            continue
        tid = parts[3]
        if tid in PROXY_TECH:
            out[tid] = parts[8]
    missing = PROXY_TECH - set(out)
    if missing:
        raise SystemExit(f"vanilla backup missing proxy rows: {sorted(missing)}")
    return out


def main() -> int:
    proxy_eff = load_vanilla_proxy_effects()
    local = TEMP / "tech_super_magic_fix.txt"
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_TECH}", str(local)], check=True)
    text = local.read_bytes().decode("gbk")
    changed = 0
    log: list[str] = []
    out_lines: list[str] = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 9:
            out_lines.append(line)
            continue
        tid = parts[3]
        sid = parts[5]
        old = parts[8]
        new_eff = None
        if tid in proxy_eff:
            new_eff = proxy_eff[tid]
        elif sid in CONTRACT_SKILL_EFFECT:
            new_eff = CONTRACT_SKILL_EFFECT[sid]
        if new_eff is not None and old != new_eff:
            parts[8] = new_eff
            changed += 1
            log.append(f"tech={tid} skill={sid} effect {old}->{new_eff}")
        out_lines.append("\t".join(parts))
    out = TEMP / "tech_super_magic_fix.bin"
    out.write_bytes("\n".join(out_lines).encode("gbk") + b"\n")
    subprocess.run(["scp", str(out), f"{REMOTE}:{REMOTE_TECH}"], check=True)
    print(f"tech.txt restored vanilla effects ({changed} rows)")
    for row in log[:25]:
        print(" ", row)
    if len(log) > 25:
        print(f"  ... +{len(log) - 25} more")
    print("restart cgmsv to reload tech.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
