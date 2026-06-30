import pathlib
import struct
import re

path = pathlib.Path(r"D:/cgtw/idguardlibr.dll")
data = path.read_bytes()

e = struct.unpack_from("<I", data, 0x3C)[0]
opt = e + 24
magic = struct.unpack_from("<H", data, opt)[0]
opt_size = 96 if magic == 0x10B else 112
image_base = struct.unpack_from("<I", data, opt + 28)[0]
nsec = struct.unpack_from("<H", data, e + 6)[0]
sec_off = opt + opt_size

sections = []
for i in range(nsec):
    o = sec_off + i * 40
    name = data[o : o + 8].split(b"\0", 1)[0]
    vrva, vsize, roff, rsize = struct.unpack_from("<IIII", data, o + 12)
    sections.append((name, vrva, vsize, roff, rsize))


def rva_to_off(rva):
    for _, vrva, _, roff, rsize in sections:
        if vrva <= rva < vrva + max(rsize, 1):
            return roff + (rva - vrva)
    return None


def off_to_va(off):
    for _, vrva, _, roff, rsize in sections:
        if roff <= off < roff + rsize:
            return image_base + vrva + (off - roff)
    return None


print("image_base", hex(image_base))
for s in sections:
    print(s)

mb = data.find(b"MessageBoxA\x00")
print("MessageBoxA str", hex(mb))

for m in re.finditer(b"\xff15....", data):
    off = m.start()
    iat_va = struct.unpack_from("<I", data, off + 2)[0]
    iat_rva = iat_va - image_base
    slot = rva_to_off(iat_rva)
    pre = data[max(0, off - 24) : off]
    pushes = []
    for i in range(len(pre) - 4):
        if pre[i] == 0x68:
            pushes.append(struct.unpack_from("<I", pre, i + 1)[0])
    print(
        f"call {off:#x} iat_va={iat_va:#x} slot={slot:#x if slot else 0} "
        f"pushes={[hex(x) for x in pushes[-3:]]}"
    )

for m in re.finditer(b"\x6a\x04", data):
    off = m.start()
    ctx = data[off : off + 12]
    if off > 0x1000:
        print(f"push4 {off:#x} ctx={ctx.hex()}")
