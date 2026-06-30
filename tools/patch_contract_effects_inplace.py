# -*- coding: utf-8 -*-
"""Tint original pet-skill effect animes in-place (117 / 317-320) for contract look."""
from __future__ import annotations

import shutil
import struct
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(r"D:\cgtw")
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from export_anime_dir6_gif import (  # noqa: E402
    GRAPHIC_INFO_SIZE,
    GraphicInfo,
    header_size,
    load_anime_infos,
    load_cgp_palette,
    load_graphic_infos,
    read_anime_header,
    read_frames,
    render_graphic,
)

PALETTE = ROOT / "bin" / "pal" / "palet_00.cgp"
BACKUP = ROOT / "_backup" / "contract_effects_inplace"

# anime_id -> (bin set, tint rgb)
TARGETS = [
    (110117, "base", (1.25, 0.95, 0.35)),
    (110317, "puk2", (1.15, 0.75, 1.35)),
    (110318, "puk2", (0.55, 0.85, 1.45)),
    (110319, "puk2", (1.45, 0.55, 0.35)),
    (110320, "puk2", (0.65, 1.25, 0.75)),
]

SETS = {
    "base": {
        "ai": ROOT / "bin" / "AnimeInfo_4.bin",
        "a": ROOT / "bin" / "Anime_4.bin",
        "gi": ROOT / "bin" / "GraphicInfo_66.bin",
        "g": ROOT / "bin" / "Graphic_66.bin",
    },
    "puk2": {
        "ai": ROOT / "bin" / "Puk2" / "AnimeInfo_PUK2_4.bin",
        "a": ROOT / "bin" / "Puk2" / "Anime_PUK2_4.bin",
        "gi": ROOT / "bin" / "Puk2" / "GraphicInfo_PUK2_2.bin",
        "g": ROOT / "bin" / "Puk2" / "Graphic_PUK2_2.bin",
    },
}


def tint_image(img: Image.Image, rgb: tuple[float, float, float]) -> Image.Image:
    base = img.convert("RGBA")
    r, g, b, a = base.split()
    rgb_img = ImageEnhance.Color(Image.merge("RGB", (r, g, b))).enhance(1.35)
    tr, tg, tb = rgb_img.split()
    tr = tr.point(lambda p: min(255, int(p * rgb[0])))
    tg = tg.point(lambda p: min(255, int(p * rgb[1])))
    tb = tb.point(lambda p: min(255, int(p * rgb[2])))
    out = Image.merge("RGBA", (tr, tg, tb, a))
    return ImageEnhance.Brightness(out).enhance(1.12)


def encode_graphic_rd(img: Image.Image, template: bytes, info: GraphicInfo) -> bytes:
    if template[:2] != b"RD" or (template[2] & 1):
        return template
    w, h = info.width, info.height
    px = img.load()
    pixels = []
    for y in range(h, 0, -1):
        for x in range(w):
            c = px[x - 1, y - 1]
            pixels.append(0 if c[3] < 20 else min(15, max(1, (c[0] + c[1] + c[2]) // 48)))
    return template[:16] + bytes(pixels)


def find_anime(anime_info: bytes, anime_id: int):
    for off in range(0, len(anime_info) - 11, 12):
        aid, addr, act, _ = struct.unpack_from("<iiHH", anime_info, off)
        if aid == anime_id:
            return addr, act
    return None


def collect_gids(anime: bytes, addr: int, act_cnt: int) -> list[int]:
    hsz = header_size(anime, addr)
    offset = addr
    gids = []
    for _ in range(act_cnt):
        header, offset = read_anime_header(anime, offset, hsz)
        frames, offset = read_frames(anime, offset, header.frame_cnt)
        for fr in frames:
            gids.append(fr.graphic_id)
    return gids


def patch_set(set_name: str, anime_id: int, tint) -> int:
    paths = SETS[set_name]
    ai = bytearray(paths["ai"].read_bytes())
    a = paths["a"].read_bytes()
    gi = bytearray(paths["gi"].read_bytes())
    g = bytearray(paths["g"].read_bytes())
    palette = load_cgp_palette(PALETTE)
    ginfos = load_graphic_infos(paths["gi"])
    found = find_anime(ai, anime_id)
    if found is None:
        print(f"skip missing anime {anime_id} in {set_name}")
        return 0
    addr, act = found
    gids = sorted(set(collect_gids(a, addr, act)))
    n = 0
    for gid in gids:
        info = ginfos.get(gid)
        if info is None:
            continue
        raw = g[info.addr : info.addr + info.length]
        try:
            img = tint_image(render_graphic(g, info, palette), tint)
            payload = encode_graphic_rd(img, raw, info)
        except Exception:
            continue
        if len(payload) != info.length:
            continue
        g[info.addr : info.addr + info.length] = payload
        n += 1
    paths["g"].write_bytes(g)
    print(f"{set_name} anime {anime_id}: tinted {n} graphics")
    return n


def main():
    BACKUP.mkdir(parents=True, exist_ok=True)
    for set_name, paths in SETS.items():
        for key, path in paths.items():
            if path.exists():
                shutil.copy2(path, BACKUP / f"{set_name}_{path.name}")
    total = 0
    for anime_id, set_name, tint in TARGETS:
        total += patch_set(set_name, anime_id, tint)
    print(f"done, tinted {total} graphic blobs")


if __name__ == "__main__":
    main()
