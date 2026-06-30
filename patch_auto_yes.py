import pathlib
import struct
import re

ROOT = pathlib.Path(r"D:/cgtw")
IMAGE_BASE = 0x10000000
CAVE_OFF = 0x5D64


def find_messagebox_calls(data: bytes) -> list[tuple[int, int, bytes]]:
    """Return MessageBoxA calls that use MB_YESNO (push 4) - the disclaimer dialog."""
    msgbox_iats = {
        0x10006094,
        0x100060A8,
        0x10006038,
        0x1000603C,
        0x10006010,
        0x10006014,
    }
    sites: list[tuple[int, int, bytes]] = []
    for match in re.finditer(b"\xFF\x15....", data):
        off = match.start()
        iat = struct.unpack_from("<I", data, off + 2)[0]
        if iat not in msgbox_iats:
            continue
        window = data[max(0, off - 128) : off]
        if b"\x6A\x04" not in window:
            continue
        orig = bytes(data[off : off + 6])
        sites.append((off, off + 6, orig))
    return sites


def apply_idguard_patches(data: bytearray) -> list[str]:
    sites = find_messagebox_calls(bytes(data))
    if not sites:
        raise SystemExit("no MessageBoxA calls found in idguardlibr.dll")

    cave = bytearray()
    notes: list[str] = []

    for call_off, resume_off, orig in sites:
        stub_off = CAVE_OFF + len(cave)
        stub = bytearray()
        stub += b"\xB8\x06\x00\x00\x00"  # mov eax, IDYES
        stub += b"\x83\xC4\x10"  # add esp, 16
        resume_va = IMAGE_BASE + resume_off
        stub_va = IMAGE_BASE + stub_off
        rel = resume_va - (stub_va + len(stub) + 5)
        stub += b"\xE9" + struct.pack("<i", rel)

        jmp_rel = stub_va - (IMAGE_BASE + call_off + 5)
        patch = b"\xE9" + struct.pack("<i", jmp_rel) + b"\x90"

        data[call_off : call_off + 6] = patch
        cave.extend(stub)
        notes.append(
            f"idguard call {call_off:#x} ({orig.hex()}) -> cave {stub_off:#x}, resume {resume_off:#x}"
        )

    data[CAVE_OFF : CAVE_OFF + len(cave)] = cave
    return notes


def apply_cg2d_patches(data: bytearray) -> list[str]:
    image_base = 0x400000
    notes: list[str] = []

    # Short-circuit CRT MessageBox helper used at startup.
    entry = 0x146D0C
    orig_entry = bytes(data[entry : entry + 6])
    if orig_entry[:2] not in (b"\x53\x33", b"\xB8\x06"):
        raise SystemExit(f"unexpected cg2d entry bytes at {entry:#x}: {orig_entry.hex()}")
    data[entry : entry + 6] = b"\xB8\x06\x00\x00\x00\xC3"  # mov eax, IDYES ; ret
    notes.append(f"cg2d helper {entry:#x} -> mov eax,6 ; ret")

    call_off = 0x146D87
    resume_off = 0x146D8D
    cave_off = 0x14C48A
    orig = bytes(data[call_off : call_off + 6])
    if orig[:1] == b"\xE9":
        notes.append(f"cg2d call {call_off:#x} already patched")
        return notes
    if orig != b"\xFF\x15\xEC\x62\x08\x01":
        raise SystemExit(f"unexpected cg2d call bytes at {call_off:#x}: {orig.hex()}")

    stub = bytearray()
    stub += b"\xB8\x06\x00\x00\x00"
    stub += b"\x83\xC4\x10"
    resume_va = image_base + resume_off
    stub_va = image_base + cave_off
    rel = resume_va - (stub_va + len(stub) + 5)
    stub += b"\xE9" + struct.pack("<i", rel)

    jmp_rel = stub_va - (image_base + call_off + 5)
    patch = b"\xE9" + struct.pack("<i", jmp_rel) + b"\x90"
    data[cave_off : cave_off + len(stub)] = stub
    data[call_off : call_off + 6] = patch
    notes.append(f"cg2d call {call_off:#x} -> cave {cave_off:#x}")
    return notes


def main() -> None:
    id_bak = ROOT / "idguardlibr.dll.bak_patch"
    cg_src = ROOT / "cg2d.exe.bak_patch"
    if not id_bak.exists():
        id_bak.write_bytes((ROOT / "idguardlibr.dll").read_bytes())

    id_data = bytearray(id_bak.read_bytes())
    cg_data = bytearray(cg_src.read_bytes())

    notes = apply_idguard_patches(id_data) + apply_cg2d_patches(cg_data)

    (ROOT / "idguardlibr.dll").write_bytes(id_data)
    (ROOT / "cg2d.exe").write_bytes(cg_data)

    print("patched MessageBoxA sites:", len([n for n in notes if n.startswith("idguard")]))
    for note in notes:
        print(" ", note)


if __name__ == "__main__":
    main()
