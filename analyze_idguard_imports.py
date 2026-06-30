import pathlib
import struct

path = pathlib.Path(r"D:/cgtw/idguardlibr.dll")
data = path.read_bytes()

e = struct.unpack_from("<I", data, 0x3C)[0]
opt = e + 24
magic = struct.unpack_from("<H", data, opt)[0]
opt_size = 96 if magic == 0x10B else 112
image_base = struct.unpack_from("<I", data, opt + 28)[0]
import_rva = struct.unpack_from("<I", data, opt + 104)[0]
nsec = struct.unpack_from("<H", data, e + 6)[0]
sec_off = opt + opt_size

sections = []
for i in range(nsec):
    o = sec_off + i * 40
    name = data[o : o + 8].split(b"\0", 1)[0]
    vrva, vsize, roff, rsize = struct.unpack_from("<IIII", data, o + 12)
    sections.append((name, vrva, roff, rsize))


def rva_to_off(rva):
    for _, vrva, roff, rsize in sections:
        if vrva <= rva < vrva + max(rsize, 1):
            return roff + (rva - vrva)
    return None


def read_cstr(off):
    end = data.find(b"\0", off)
    return data[off:end]


imp_off = rva_to_off(import_rva)
print("import_off", hex(imp_off))
while True:
    ilt_rva, ts, fc, name_rva, iat_rva = struct.unpack_from("<IIIII", data, imp_off)
    if ilt_rva == 0 and name_rva == 0:
        break
    name_off = rva_to_off(name_rva)
    dll = read_cstr(name_off).decode("ascii", "ignore")
    print(f"\nDLL: {dll} IAT_RVA={iat_rva:#x}")
    ilt_off = rva_to_off(ilt_rva)
    iat_off = rva_to_off(iat_rva)
    idx = 0
    while True:
        entry = struct.unpack_from("<I", data, ilt_off + idx * 4)[0]
        if entry == 0:
            break
        if entry & 0x80000000:
            print(f"  [{idx}] ordinal {entry & 0xFFFF}")
        else:
            hint_off = rva_to_off(entry)
            hint = struct.unpack_from("<H", data, hint_off)[0]
            fn = read_cstr(hint_off + 2).decode("ascii", "ignore")
            iat_slot_va = image_base + iat_rva + idx * 4
            print(f"  [{idx}] {fn} IAT={iat_slot_va:#x}")
        idx += 1
    imp_off += 20

print("\n=== callsite 0x57fd context ===")
for off in [0x5768, 0x57bf, 0x57fd]:
    chunk = data[off - 16 : off + 6]
    print(hex(off), chunk.hex())
