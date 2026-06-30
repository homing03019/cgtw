#!/usr/bin/env python3
"""Export Cross Gate anime GIFs for a single direction (default: dir 6)."""

from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image

ANIME_INFO_SIZE = 12
ANIME_FRAME_SIZE = 10
GRAPHIC_INFO_SIZE = 40

PREFIX_PALETTE = [
    (0, 0, 0, 0),
    (0, 0, 128, 255),
    (0, 128, 0, 255),
    (0, 128, 128, 255),
    (128, 0, 0, 255),
    (128, 0, 128, 255),
    (128, 128, 0, 255),
    (192, 192, 192, 255),
    (192, 220, 192, 255),
    (240, 202, 166, 255),
    (0, 0, 222, 255),
    (0, 95, 255, 255),
    (160, 255, 255, 255),
    (210, 95, 0, 255),
    (255, 210, 80, 255),
    (40, 225, 40, 255),
]

SUFFIX_PALETTE = [
    (150, 195, 245, 255),
    (95, 160, 30, 255),
    (70, 125, 195, 255),
    (30, 85, 155, 255),
    (55, 65, 70, 255),
    (30, 35, 40, 255),
    (240, 251, 255, 255),
    (165, 110, 58, 255),
    (128, 128, 128, 255),
    (0, 0, 255, 255),
    (0, 255, 0, 255),
    (0, 255, 255, 255),
    (255, 0, 0, 255),
    (255, 128, 255, 255),
    (255, 255, 0, 255),
    (255, 255, 255, 255),
]


@dataclass
class GraphicInfo:
    id: int
    addr: int
    length: int
    off_x: int
    off_y: int
    width: int
    height: int
    map_id: int


@dataclass
class AnimeInfo:
    id: int
    addr: int
    act_cnt: int


@dataclass
class AnimeHeader:
    direct: int
    action: int
    duration: int
    frame_cnt: int


@dataclass
class AnimeFrame:
    graphic_id: int
    off_x: int
    off_y: int
    flag: int


@dataclass
class AnimeSet:
    name: str
    anime_info: Path
    anime: Path
    graphic_info: Path
    graphic: Path
    palette_graphic_info: Path | None = None
    palette_graphic: Path | None = None


def load_cgp_palette(path: Path) -> list[tuple[int, int, int, int]]:
    raw = path.read_bytes()
    body: list[tuple[int, int, int, int]] = []
    for i in range(0, len(raw), 3):
        b, g, r = raw[i : i + 3]
        if (r, g, b) in ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)):
            body.append((0, 0, 0, 0))
        else:
            body.append((r, g, b, 255))
    return PREFIX_PALETTE + body + SUFFIX_PALETTE


def palette_from_bytes(raw: bytes) -> list[tuple[int, int, int, int]]:
    out: list[tuple[int, int, int, int]] = []
    for i in range(0, len(raw), 3):
        b, g, r = raw[i : i + 3]
        if (r, g, b) in ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255)):
            out.append((0, 0, 0, 0))
        else:
            out.append((r, g, b, 255))
    return out


def decode_rle(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        fb = data[i]
        i += 1
        flag = fb & 0xF0
        if flag in (0x00, 0x10, 0x20):
            data_byte = None
        elif flag in (0x80, 0x90, 0xA0):
            data_byte = data[i]
            i += 1
        elif flag in (0xC0, 0xD0, 0xE0):
            data_byte = 0
        else:
            raise ValueError(f"invalid RLE flag: {fb:#x}")

        if flag in (0x00, 0x80, 0xC0):
            count = fb & 0x0F
        elif flag in (0x10, 0x90, 0xD0):
            count = ((fb & 0x0F) << 8) + data[i]
            i += 1
        elif flag in (0x20, 0xA0, 0xE0):
            count = ((fb & 0x0F) << 16) + (data[i] << 8) + data[i + 1]
            i += 2
        else:
            raise ValueError(f"invalid RLE flag: {fb:#x}")

        if data_byte is None:
            out.extend(data[i : i + count])
            i += count
        else:
            out.extend(bytes([data_byte]) * count)
    return bytes(out)


def load_graphic_infos(path: Path) -> dict[int, GraphicInfo]:
    data = path.read_bytes()
    infos: dict[int, GraphicInfo] = {}
    for off in range(0, len(data), GRAPHIC_INFO_SIZE):
        chunk = data[off : off + GRAPHIC_INFO_SIZE]
        if len(chunk) < GRAPHIC_INFO_SIZE:
            break
        gid, addr, length, off_x, off_y, width, height, grid_w, grid_h, access, map_id = struct.unpack(
            "<iiiiiiiBBB5xi", chunk
        )
        infos[gid] = GraphicInfo(gid, addr, length, off_x, off_y, width, height, map_id)
    return infos


def load_anime_infos(path: Path) -> list[AnimeInfo]:
    data = path.read_bytes()
    infos: list[AnimeInfo] = []
    for off in range(0, len(data), ANIME_INFO_SIZE):
        chunk = data[off : off + ANIME_INFO_SIZE]
        if len(chunk) < ANIME_INFO_SIZE:
            break
        anime_id, addr, act_cnt, _ = struct.unpack("<iiHH", chunk)
        infos.append(AnimeInfo(anime_id, addr, act_cnt))
    return infos


def header_size(anime_data: bytes, addr: int) -> int:
    if addr + 20 > len(anime_data):
        return 12
    sentinel = struct.unpack_from("<i", anime_data, addr + 16)[0]
    return 20 if sentinel == -1 else 12


def read_anime_header(anime_data: bytes, offset: int, size: int) -> tuple[AnimeHeader, int]:
    direct, action, duration, frame_cnt = struct.unpack_from("<hhii", anime_data, offset)
    return AnimeHeader(direct, action, duration, frame_cnt), offset + size


def read_frames(anime_data: bytes, offset: int, count: int) -> tuple[list[AnimeFrame], int]:
    frames: list[AnimeFrame] = []
    for _ in range(count):
        gid, off_x, off_y, flag = struct.unpack_from("<ihhh", anime_data, offset)
        frames.append(AnimeFrame(gid, off_x, off_y, flag))
        offset += ANIME_FRAME_SIZE
    return frames, offset


def render_graphic(
    graphic_data: bytes,
    info: GraphicInfo,
    palette: list[tuple[int, int, int, int]],
) -> Image.Image:
    if info.length < 16:
        raise ValueError(f"graphic {info.id} too short")
    magic = graphic_data[info.addr : info.addr + 2]
    if magic != b"RD":
        raise ValueError(f"graphic {info.id} invalid magic: {magic!r}")

    version = graphic_data[info.addr + 2]
    pos = info.addr + 16
    end = info.addr + info.length
    raw = graphic_data[info.addr + 16 : end]

    palette_size = 0
    if version >= 2:
        palette_size = struct.unpack_from("<i", graphic_data, pos)[0]
        raw = graphic_data[info.addr + 20 : end]

    if version & 1:
        decoded = decode_rle(raw)
    else:
        decoded = raw

    if palette_size:
        pixel_data = decoded[:-palette_size]
        local_palette = palette_from_bytes(decoded[-palette_size:])
    else:
        pixel_data = decoded
        local_palette = palette

    w, h = info.width, info.height
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    for idx, pix in enumerate(pixel_data):
        x = idx % w
        y = h - idx // w
        if y < 0 or y >= h or pix >= len(local_palette):
            continue
        px[x, y] = local_palette[pix]
    return img


def compose_gif(frames: list[Image.Image], duration_ms: int) -> Image.Image:
    if not frames:
        raise ValueError("no frames")
    delay = max(1, int(duration_ms / len(frames) / 10))
    w = max(f.width for f in frames)
    h = max(f.height for f in frames)
    composed: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.paste(frame, (0, 0), frame)
        composed.append(canvas.convert("P", palette=Image.ADAPTIVE, colors=256))
    out = composed[0]
    out.save(
        BytesIO(),
        format="GIF",
        save_all=True,
        append_images=composed[1:],
        duration=delay * 10,
        loop=0,
        disposal=2,
        transparency=0,
    )
    return out


def save_gif(frames: list[Image.Image], duration_ms: int, out_path: Path) -> None:
    delay = max(1, int(duration_ms / len(frames) / 10))
    w = max(f.width for f in frames)
    h = max(f.height for f in frames)
    composed: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.paste(frame, (0, 0), frame)
        composed.append(canvas)
    first = composed[0].convert("RGBA")
    rest = [f.convert("RGBA") for f in composed[1:]]
    first.save(
        out_path,
        format="GIF",
        save_all=True,
        append_images=rest,
        duration=delay * 10,
        loop=0,
        disposal=2,
    )


def discover_sets(client_root: Path) -> list[AnimeSet]:
    sets = [
        AnimeSet("[BASE]", client_root / "bin/AnimeInfo_4.bin", client_root / "bin/Anime_4.bin",
                 client_root / "bin/GraphicInfo_66.bin", client_root / "bin/Graphic_66.bin"),
        AnimeSet("[EX]", client_root / "bin/AnimeInfoEx_1.Bin", client_root / "bin/AnimeEx_1.Bin",
                 client_root / "bin/GraphicInfoEx_5.bin", client_root / "bin/GraphicEx_5.bin"),
        AnimeSet("[V3]", client_root / "bin/AnimeInfoV3_8.bin", client_root / "bin/AnimeV3_8.bin",
                 client_root / "bin/GraphicInfoV3_19.bin", client_root / "bin/GraphicV3_19.bin",
                 client_root / "bin/GraphicInfoV3_19.bin", client_root / "bin/GraphicV3_19.bin"),
        AnimeSet("[Puk2]", client_root / "bin/Puk2/AnimeInfo_PUK2_4.bin", client_root / "bin/Puk2/Anime_PUK2_4.bin",
                 client_root / "bin/Puk2/GraphicInfo_PUK2_2.bin", client_root / "bin/Puk2/Graphic_PUK2_2.bin"),
        AnimeSet("[Puk3]", client_root / "bin/Puk3/AnimeInfo_PUK3_2.bin", client_root / "bin/Puk3/Anime_PUK3_2.bin",
                 client_root / "bin/Puk3/GraphicInfo_PUK3_1.bin", client_root / "bin/Puk3/Graphic_PUK3_1.bin"),
        AnimeSet("[Joy]", client_root / "bin/AnimeInfo_Joy_91.bin", client_root / "bin/Anime_Joy_91.bin",
                 client_root / "bin/GraphicInfo_Joy_125.bin", client_root / "bin/Graphic_Joy_125.bin"),
        AnimeSet("[Joy_EX]", client_root / "bin/AnimeInfo_Joy_EX_93.bin", client_root / "bin/Anime_Joy_EX_93.bin",
                 client_root / "bin/GraphicInfo_Joy_EX_96.bin", client_root / "bin/Graphic_Joy_EX_96.bin"),
        AnimeSet("[Joy_CH1]", client_root / "bin/AnimeInfo_Joy_CH1.Bin", client_root / "bin/Anime_Joy_CH1.bin",
                 client_root / "bin/GraphicInfo_Joy_CH1.bin", client_root / "bin/Graphic_Joy_CH1.bin"),
    ]
    return [s for s in sets if s.anime_info.exists() and s.anime.exists()]


def export_set(
    anime_set: AnimeSet,
    out_dir: Path,
    direction: int,
    palette_path: Path,
    limit: int | None,
    skip_existing: bool,
) -> tuple[int, int]:
    palette = load_cgp_palette(palette_path)
    graphic_infos = load_graphic_infos(anime_set.graphic_info)
    graphic_data = anime_set.graphic.read_bytes()
    anime_data = anime_set.anime.read_bytes()
    anime_infos = load_anime_infos(anime_set.anime_info)

    set_out = out_dir / anime_set.name.strip("[]")
    set_out.mkdir(parents=True, exist_ok=True)

    exported = 0
    skipped = 0
    for idx, ai in enumerate(anime_infos):
        if limit is not None and exported >= limit:
            break
        if ai.addr <= 0 or ai.act_cnt <= 0:
            continue

        hsz = header_size(anime_data, ai.addr)
        offset = ai.addr
        for _ in range(ai.act_cnt):
            header, offset = read_anime_header(anime_data, offset, hsz)
            frames, offset = read_frames(anime_data, offset, header.frame_cnt)
            if header.direct != direction or header.frame_cnt <= 0:
                continue

            out_name = f"{ai.id:06d}_act{header.action:02d}_dir{direction}.gif"
            out_path = set_out / out_name
            if skip_existing and out_path.exists():
                skipped += 1
                continue

            images: list[Image.Image] = []
            ok = True
            for frame in frames:
                info = graphic_infos.get(frame.graphic_id)
                if info is None:
                    ok = False
                    break
                try:
                    images.append(render_graphic(graphic_data, info, palette))
                except Exception:
                    ok = False
                    break
            if not ok or not images:
                continue

            save_gif(images, header.duration, out_path)
            exported += 1
            if exported % 100 == 0:
                print(f"{anime_set.name}: exported {exported} (anime index {idx}/{len(anime_infos)})", flush=True)

    return exported, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Cross Gate anime GIFs for one direction")
    parser.add_argument("--client", type=Path, default=Path(r"D:\cgtw"))
    parser.add_argument("--out", type=Path, default=Path(r"D:\cgtw\export_gif_dir6"))
    parser.add_argument("--dir", dest="direction", type=int, default=6)
    parser.add_argument("--palette", type=Path, default=Path(r"D:\cgtw\bin\pal\palet_00.cgp"))
    parser.add_argument("--set", dest="only_set", default="")
    parser.add_argument("--limit", type=int, default=0, help="max GIFs per set (0 = no limit)")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    sets = discover_sets(args.client)
    if args.only_set:
        sets = [s for s in sets if s.name == args.only_set or s.name.strip("[]") == args.only_set]
    if not sets:
        print("No anime sets found.", file=sys.stderr)
        return 1

    total = 0
    skipped = 0
    for anime_set in sets:
        print(f"Processing {anime_set.name} ...", flush=True)
        limit = args.limit if args.limit > 0 else None
        n, s = export_set(
            anime_set,
            out_dir,
            args.direction,
            args.palette,
            limit,
            args.skip_existing,
        )
        print(f"{anime_set.name}: exported {n}, skipped existing {s}", flush=True)
        total += n
        skipped += s

    print(f"Done. Total exported: {total}, skipped existing: {skipped}")
    print(f"Output: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
