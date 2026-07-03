#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore client AnimeInfo bins from pre-contract-redirect backup."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(r"D:/cgtw")
BACKUP = ROOT / "_backup" / "client_tech" / "20260701_084115_before_exe_re" / "client" / "bin"

PAIRS = [
    (BACKUP / "AnimeInfo_4.bin", ROOT / "bin" / "AnimeInfo_4.bin"),
    (BACKUP / "Puk2" / "AnimeInfo_PUK2_4.bin", ROOT / "bin" / "Puk2" / "AnimeInfo_PUK2_4.bin"),
]


def main() -> int:
    for src, dst in PAIRS:
        if not src.exists():
            raise SystemExit(f"missing backup {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"restored {dst.name} from vanilla backup")
    print("Restart cg2d completely.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
