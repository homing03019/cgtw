#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clone battle effect anime into BASE bin with tint, patch server tech effects, export GIF preview."""
from __future__ import annotations

import shutil
import struct
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(r"D:\cgtw")
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from export_anime_dir6_gif import (  # noqa: E402
    ANIME_FRAME_SIZE,
    ANIME_INFO_SIZE,
    GRAPHIC_INFO_SIZE,
    GraphicInfo,
    header_size,
    load_anime_infos,
    load_cgp_palette,
    load_graphic_infos,
    read_anime_header,
    read_frames,
    render_graphic,
    save_gif,
)

CLIENT = ROOT
OUT_GIF = ROOT / "export_gif_dir6" / "contract_effects"
BACKUP = ROOT / "_backup" / "contract_effects_bins"

BASE_AI = CLIENT / "bin" / "AnimeInfo_4.bin"
BASE_A = CLIENT / "bin" / "Anime_4.bin"
BASE_GI = CLIENT / "bin" / "GraphicInfo_66.bin"
BASE_G = CLIENT / "bin" / "Graphic_66.bin"
PATCH_DIR = CLIENT / "bin_patched"
PUK2_AI = CLIENT / "bin" / "Puk2" / "AnimeInfo_PUK2_4.bin"
PUK2_A = CLIENT / "bin" / "Puk2" / "Anime_PUK2_4.bin"
PUK2_GI = CLIENT / "bin" / "Puk2" / "GraphicInfo_PUK2_2.bin"
PUK2_G = CLIENT / "bin" / "Puk2" / "Graphic_PUK2_2.bin"
PALETTE = CLIENT / "bin" / "pal" / "palet_00.cgp"

REMOTE = "cgmsv-server"
REMOTE_TECH = "/cgmsv_26.5c/gmsv/data/tech.txt"

# server effect id -> (source anime id, source set, tint rgb multiplier)
CONTRACT_EFFECTS = [
    (901, 110117, "base", (1.25, 0.95, 0.35), "contract_wave"),
    (902, 110317, "puk2", (1.15, 0.75, 1.35), "contract_magic_earth"),
    (903, 110318, "puk2", (0.55, 0.85, 1.45), "contract_magic_water"),
    (904, 110319, "puk2", (1.45, 0.55, 0.35), "contract_magic_fire"),
    (905, 110320, "puk2", (0.65, 1.25, 0.75), "contract_magic_wind"),
]

SET_PATHS = {
    "base": (BASE_AI, BASE_A, BASE_GI, BASE_G),
    "puk2": (PUK2_AI, PUK2_A, PUK2_GI, PUK2_G),
}


@dataclass
class SourceSet:
    anime_info: bytes
    anime: bytes
    graphic_info: bytes
    graphic: bytes
    infos: dict
    ginfos: dict


def load_set(name: str) -> SourceSet:
    ai, a, gi, g = SET_PATHS[name]
    anime_info = ai.read_bytes()
    anime = a.read_bytes()
    graphic_info = gi.read_bytes()
    graphic = g.read_bytes()
    infos = {x.id: x for x in load_anime_infos(ai)}
    ginfos = load_graphic_infos(gi)
    return SourceSet(anime_info, anime, graphic_info, graphic, infos, ginfos)


def find_anime_info_entry(anime_info: bytes, anime_id: int) -> tuple[int, int, int] | None:
    for off in range(0, len(anime_info) - 11, 12):
        aid, addr, act, _ = struct.unpack_from("<iiHH", anime_info, off)
        if aid == anime_id:
            return off, addr, act
    return None


def slice_anime_blob(anime: bytes, addr: int, act_cnt: int) -> bytes:
    hsz = header_size(anime, addr)
    offset = addr
    start = addr
    for _ in range(act_cnt):
        header, offset = read_anime_header(anime, offset, hsz)
        _, offset = read_frames(anime, offset, header.frame_cnt)
    return anime[start:offset]


def collect_graphic_ids(blob: bytes, act_cnt: int) -> list[int]:
    hsz = header_size(blob, 0)
    offset = 0
    gids: list[int] = []
    for _ in range(act_cnt):
        header, offset = read_anime_header(blob, offset, hsz)
        frames, offset = read_frames(blob, offset, header.frame_cnt)
        for fr in frames:
            gids.append(fr.graphic_id)
    return gids


def remap_blob_graphic_ids(blob: bytes, act_cnt: int, mapping: dict[int, int]) -> bytes:
    hsz = header_size(blob, 0)
    out = bytearray()
    offset = 0
    for _ in range(act_cnt):
        header, offset = read_anime_header(blob, offset, hsz)
        frames, next_offset = read_frames(blob, offset, header.frame_cnt)
        out.extend(struct.pack("<hhii", header.direct, header.action, header.duration, header.frame_cnt))
        if hsz == 20:
            out.extend(blob[offset - 20 + 12 : offset - 20 + 20])
        for fr in frames:
            gid = mapping.get(fr.graphic_id, fr.graphic_id)
            out.extend(struct.pack("<ihhh", gid, fr.off_x, fr.off_y, fr.flag))
        offset = next_offset
    return bytes(out)


def tint_image(img: Image.Image, rgb: tuple[float, float, float]) -> Image.Image:
    base = img.convert("RGBA")
    r, g, b, a = base.split()
    rgb_img = Image.merge("RGB", (r, g, b))
    tinted = ImageEnhance.Color(rgb_img).enhance(1.35)
    tr, tg, tb = tinted.split()
    tr = tr.point(lambda p: min(255, int(p * rgb[0])))
    tg = tg.point(lambda p: min(255, int(p * rgb[1])))
    tb = tb.point(lambda p: min(255, int(p * rgb[2])))
    out = Image.merge("RGBA", (tr, tg, tb, a))
    glow = ImageEnhance.Brightness(out).enhance(1.12)
    return glow


def rgba_to_palette_index(r: int, g: int, b: int, a: int, palette) -> int:
    if a < 20:
        return 0
    best_i = 1
    best_d = 10**9
    for i, (pr, pg, pb, _pa) in enumerate(palette):
        if i == 0:
            continue
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def encode_graphic_from_rgba(img: Image.Image, info: GraphicInfo, palette) -> bytes:
    """Write an uncompressed RD graphic (version 0) from tinted RGBA pixels."""
    w, h = info.width, info.height
    if img.size != (w, h):
        img = img.resize((w, h), Image.Resampling.NEAREST)
    px = img.convert("RGBA").load()
    body = bytearray()
    for y in range(h, 0, -1):
        for x in range(w):
            c = px[x - 1, y - 1]
            body.append(rgba_to_palette_index(c[0], c[1], c[2], c[3], palette))
    header = struct.pack("<2sBBiii", b"RD", 0, 0, w, h, len(body))
    return header + bytes(body)


def clone_graphic(
    src: SourceSet,
    gid: int,
    new_gid: int,
    tint: tuple[float, float, float],
    palette,
    target_g: bytearray,
    target_gi: bytearray,
) -> None:
    info = src.ginfos.get(gid)
    if info is None:
        raise SystemExit(f"missing graphic {gid}")
    raw = src.graphic[info.addr : info.addr + info.length]
    try:
        img = render_graphic(src.graphic, info, palette)
        img = tint_image(img, tint)
        payload = encode_graphic_from_rgba(img, info, palette)
    except Exception:
        payload = raw
    new_addr = len(target_g)
    target_g.extend(payload)
    new_len = len(payload)
    chunk = bytearray(GRAPHIC_INFO_SIZE)
    struct.pack_into(
        "<iiiiiiiBBB5xi",
        chunk,
        0,
        new_gid,
        new_addr,
        new_len,
        info.off_x,
        info.off_y,
        info.width,
        info.height,
        0,
        0,
        0,
        info.map_id,
    )
    target_gi.extend(chunk)


def make_gid_allocator(ginfos: dict):
    used = set(ginfos.keys())
    cursor = max(used) + 1 if used else 1

    def alloc() -> int:
        nonlocal cursor
        while cursor in used:
            cursor += 1
        gid = cursor
        used.add(gid)
        cursor += 1
        return gid

    return alloc


def verify_graphic_info(path: Path, label: str) -> None:
    from collections import Counter

    raw = path.read_bytes()
    ids = [struct.unpack_from("<i", raw, i * GRAPHIC_INFO_SIZE)[0] for i in range(len(raw) // GRAPHIC_INFO_SIZE)]
    dup = sum(1 for v in Counter(ids).values() if v > 1)
    print(f"{label}: entries={len(ids)} unique={len(set(ids))} dup_ids={dup} max_id={max(ids) if ids else 0}")
    if dup > 34:
        raise SystemExit(f"{label} has {dup} duplicate graphic ids (expected <=34 legacy dups)")


def patch_effect_bins(
    effects: list[tuple],
    target_ai: Path,
    target_a: Path,
    target_gi: Path,
    target_g: Path,
    patch_dir: Path,
    backup_prefix: str,
) -> dict[int, int]:
    palette = load_cgp_palette(PALETTE)
    target_g_b = bytearray(target_g.read_bytes())
    target_gi_b = bytearray(target_gi.read_bytes())
    target_a_b = bytearray(target_a.read_bytes())
    target_ai_b = bytearray(target_ai.read_bytes())
    ginfos = load_graphic_infos(target_gi)
    effect_to_anime: dict[int, int] = {}
    alloc_gid = make_gid_allocator(ginfos)

    for effect_id, src_anime_id, set_name, tint, _label in effects:
        src = load_set(set_name)
        entry = find_anime_info_entry(src.anime_info, src_anime_id)
        if entry is None:
            raise SystemExit(f"source anime {src_anime_id} missing in {set_name}")
        _, addr, act_cnt = entry
        blob = slice_anime_blob(src.anime, addr, act_cnt)
        gids = collect_graphic_ids(blob, act_cnt)
        mapping: dict[int, int] = {}
        for gid in sorted(set(gids)):
            new_gid = alloc_gid()
            mapping[gid] = new_gid
            clone_graphic(src, gid, new_gid, tint, palette, target_g_b, target_gi_b)
        new_blob = remap_blob_graphic_ids(blob, act_cnt, mapping)
        new_addr = len(target_a_b)
        target_a_b.extend(new_blob)
        new_anime_id = 110000 + effect_id
        target_ai_b.extend(struct.pack("<iiHH", new_anime_id, new_addr, act_cnt, 0))
        effect_to_anime[effect_id] = new_anime_id
        print(
            f"[{backup_prefix}] effect {effect_id} -> anime {new_anime_id} "
            f"({act_cnt} actions, {len(set(gids))} graphics)"
        )

    BACKUP.mkdir(parents=True, exist_ok=True)
    patch_dir.mkdir(parents=True, exist_ok=True)
    out_a = patch_dir / target_a.name
    out_ai = patch_dir / target_ai.name
    out_g = patch_dir / target_g.name
    out_gi = patch_dir / target_gi.name
    for src in (target_a, target_ai, target_g, target_gi):
        shutil.copy2(src, BACKUP / f"{backup_prefix}_{src.name}")
    out_g.write_bytes(target_g_b)
    out_gi.write_bytes(target_gi_b)
    out_a.write_bytes(target_a_b)
    out_ai.write_bytes(target_ai_b)
    verify_graphic_info(out_gi, f"{backup_prefix} GraphicInfo")
    for src, dst in ((out_a, target_a), (out_ai, target_ai), (out_g, target_g), (out_gi, target_gi)):
        try:
            shutil.copy2(src, dst)
            print(f"deployed {dst}")
        except PermissionError:
            print(f"WARN: could not overwrite {dst}; patched copy at {src}")
    return effect_to_anime


def patch_base_bins() -> dict[int, int]:
    base_effects = [e for e in CONTRACT_EFFECTS if e[2] == "base"]
    return patch_effect_bins(
        base_effects,
        BASE_AI,
        BASE_A,
        BASE_GI,
        BASE_G,
        PATCH_DIR,
        "base",
    )


def patch_puk2_bins() -> dict[int, int]:
    puk2_effects = [e for e in CONTRACT_EFFECTS if e[2] == "puk2"]
    puk2_patch = PATCH_DIR / "Puk2"
    puk2_patch.mkdir(parents=True, exist_ok=True)
    return patch_effect_bins(
        puk2_effects,
        PUK2_AI,
        PUK2_A,
        PUK2_GI,
        PUK2_G,
        puk2_patch,
        "puk2",
    )


def _effect_asset_paths(effect_id: int, set_name: str) -> tuple[Path, Path, Path, Path]:
    if set_name == "puk2":
        root = PATCH_DIR / "Puk2"
        return (
            root / PUK2_AI.name if (root / PUK2_AI.name).exists() else PUK2_AI,
            root / PUK2_A.name if (root / PUK2_A.name).exists() else PUK2_A,
            root / PUK2_GI.name if (root / PUK2_GI.name).exists() else PUK2_GI,
            root / PUK2_G.name if (root / PUK2_G.name).exists() else PUK2_G,
        )
    return (
        PATCH_DIR / BASE_AI.name if (PATCH_DIR / BASE_AI.name).exists() else BASE_AI,
        PATCH_DIR / BASE_A.name if (PATCH_DIR / BASE_A.name).exists() else BASE_A,
        PATCH_DIR / BASE_GI.name if (PATCH_DIR / BASE_GI.name).exists() else BASE_GI,
        PATCH_DIR / BASE_G.name if (PATCH_DIR / BASE_G.name).exists() else BASE_G,
    )


def export_effect_gifs(effect_to_anime: dict[int, int], direction: int = 6) -> list[Path]:
    OUT_GIF.mkdir(parents=True, exist_ok=True)
    palette = load_cgp_palette(PALETTE)
    exported: list[Path] = []

    for effect_id, _src_id, set_name, _tint, label in CONTRACT_EFFECTS:
        anime_id = effect_to_anime.get(effect_id)
        if anime_id is None:
            continue
        ai_path, a_path, gi_path, g_path = _effect_asset_paths(effect_id, set_name)
        ginfos = load_graphic_infos(gi_path)
        gdata = g_path.read_bytes()
        adata = a_path.read_bytes()
        infos = {x.id: x for x in load_anime_infos(ai_path)}
        ai = infos.get(anime_id)
        if ai is None:
            print(f"WARN: anime {anime_id} missing for effect {effect_id}")
            continue
        hsz = header_size(adata, ai.addr)
        offset = ai.addr
        saved = None
        for _ in range(ai.act_cnt):
            header, offset = read_anime_header(adata, offset, hsz)
            frames, offset = read_frames(adata, offset, header.frame_cnt)
            if header.frame_cnt <= 0:
                continue
            images: list[Image.Image] = []
            ok = True
            for fr in frames:
                info = ginfos.get(fr.graphic_id)
                if info is None:
                    ok = False
                    break
                try:
                    images.append(render_graphic(gdata, info, palette))
                except Exception:
                    ok = False
                    break
            if not ok or not images:
                continue
            item = (header.direct, header.duration, images)
            if header.direct == direction:
                saved = item
                break
            if saved is None:
                saved = item
        if saved is None:
            print(f"WARN: no frames exported for effect {effect_id}")
            continue
        direct, duration, images = saved
        safe = label
        out_path = OUT_GIF / f"effect{effect_id:03d}_{anime_id}_{safe}_dir{direct}.gif"
        save_gif(images, duration, out_path)
        exported.append(out_path)
        print(f"GIF -> {out_path.name}")
    return exported


def patch_server_tech_effects():
    local = Path(r"C:/Users/User/AppData/Local/Temp/tech_265c_live.txt")
    subprocess.run(["scp", f"{REMOTE}:{REMOTE_TECH}", str(local)], check=True)
    raw = local.read_bytes()
    text = raw.decode("gbk")
    replacements = {
        991: 901,
        992: 902,
        993: 903,
        994: 904,
        995: 905,
    }
    old_effects = {991: 118, 992: 318, 993: 319, 994: 320, 995: 321}
    lines = text.splitlines()
    out_lines = []
    changed = 0
    for line in lines:
        if "契约" not in line:
            out_lines.append(line)
            continue
        parts = line.split("\t")
        if len(parts) < 9:
            out_lines.append(line)
            continue
        try:
            skill_id = int(parts[5])
        except ValueError:
            out_lines.append(line)
            continue
        if skill_id in replacements:
            parts[8] = str(replacements[skill_id])
            changed += 1
        out_lines.append("\t".join(parts))
    if changed == 0:
        print("WARN: no contract tech lines updated; check effect columns manually")
    out = Path(r"C:/Users/User/AppData/Local/Temp/tech_contract_effects.bin")
    out.write_bytes("\n".join(out_lines).encode("gbk") + b"\n")
    subprocess.run(["scp", str(out), f"{REMOTE}:{REMOTE_TECH}"], check=True)
    print(f"tech.txt updated ({changed} contract lines -> effects 901-905)")


def export_effect_sequence_gifs(
    effect_to_anime: dict[int, int],
    direction: int = 6,
) -> list[Path]:
    """Export every action on a direction (full magic sequence)."""
    OUT_GIF.mkdir(parents=True, exist_ok=True)
    seq_dir = OUT_GIF / "sequences"
    seq_dir.mkdir(parents=True, exist_ok=True)
    palette = load_cgp_palette(PALETTE)
    exported: list[Path] = []

    for effect_id, _src_id, set_name, _tint, label in CONTRACT_EFFECTS:
        if set_name != "puk2":
            continue
        anime_id = effect_to_anime.get(effect_id)
        if anime_id is None:
            continue
        ai_path, a_path, gi_path, g_path = _effect_asset_paths(effect_id, set_name)
        ginfos = load_graphic_infos(gi_path)
        gdata = g_path.read_bytes()
        adata = a_path.read_bytes()
        infos = {x.id: x for x in load_anime_infos(ai_path)}
        ai = infos.get(anime_id)
        if ai is None:
            continue
        hsz = header_size(adata, ai.addr)
        offset = ai.addr
        act_idx = 0
        for _ in range(ai.act_cnt):
            header, offset = read_anime_header(adata, offset, hsz)
            frames, offset = read_frames(adata, offset, header.frame_cnt)
            if header.direct != direction or header.frame_cnt <= 0:
                act_idx += 1
                continue
            images: list[Image.Image] = []
            ok = True
            for fr in frames:
                info = ginfos.get(fr.graphic_id)
                if info is None:
                    ok = False
                    break
                try:
                    images.append(render_graphic(gdata, info, palette))
                except Exception:
                    ok = False
                    break
            if ok and images:
                out_path = seq_dir / f"effect{effect_id:03d}_{anime_id}_{label}_act{act_idx:02d}_dir{direction}.gif"
                save_gif(images, header.duration, out_path)
                exported.append(out_path)
            act_idx += 1
        print(f"sequence {label}: {sum(1 for p in exported if label in p.name)} clips dir{direction}")
    return exported


def main() -> int:
    print("Patching BASE bin (901 契约震波)...")
    effect_map = patch_base_bins()
    print("Patching PUK2 bins (902-905 契约秘法)...")
    effect_map.update(patch_puk2_bins())
    print("Exporting GIF previews...")
    gifs = export_effect_gifs(effect_map, direction=6)
    print("Exporting full magic sequences...")
    seq = export_effect_sequence_gifs(effect_map, direction=6)
    print(f"Done. preview={len(gifs)} sequence={len(seq)} in {OUT_GIF}")
    return 0


def main_with_server() -> int:
    effect_map = main()
    print("Updating server tech.txt effect ids...")
    patch_server_tech_effects()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
