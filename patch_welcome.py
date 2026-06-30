import pathlib
import struct

path = pathlib.Path(r"D:/cgtw/cg2d.exe.bak_patch")
data = bytearray(path.read_bytes())

IMAGE_BASE = 0x400000
TEXT_RVA = 0x1000
TEXT_OFF = 0x1000
PATCH_OFF = 0x146D7A
PATCH_LEN = 19
RESUME_OFF = 0x146D8D
MB_IAT = 0x010862EC
CAVE_OFF = 0x14C48A

cave_va = IMAGE_BASE + (CAVE_OFF - TEXT_OFF + TEXT_RVA)
text = "歡迎來到魔力寶貝,好好享受冒險之旅".encode("gbk")
caption = "提示".encode("gbk")

stub_size = 32
text_off = CAVE_OFF + stub_size
cap_off = text_off + len(text) + 1
cap_va = IMAGE_BASE + (cap_off - TEXT_OFF + TEXT_RVA)
text_va = IMAGE_BASE + (text_off - TEXT_OFF + TEXT_RVA)
resume_va = IMAGE_BASE + RESUME_OFF

code = bytearray()
code += b"\x6a\x04"
code += b"\x68" + struct.pack("<I", cap_va)
code += b"\x68" + struct.pack("<I", text_va)
code += b"\x6a\x00"
code += b"\xff\x15" + struct.pack("<I", MB_IAT)
code += b"\xe9" + struct.pack("<i", resume_va - (cave_va + len(code) + 5))

orig = bytes(data[PATCH_OFF : PATCH_OFF + PATCH_LEN])
if not orig.startswith(b"\xff\x74\x24\x18"):
    raise SystemExit(f"unexpected bytes at patch site: {orig.hex()}")

jmp_rel = cave_va - (IMAGE_BASE + PATCH_OFF + 5)
patch = b"\xe9" + struct.pack("<i", jmp_rel) + b"\x90" * (PATCH_LEN - 5)

data[CAVE_OFF : CAVE_OFF + len(code)] = code
data[text_off : text_off + len(text) + 1] = text + b"\x00"
data[cap_off : cap_off + len(caption) + 1] = caption + b"\x00"
data[PATCH_OFF : PATCH_OFF + PATCH_LEN] = patch

out = pathlib.Path(r"D:/cgtw/cg2d.exe.welcome_patch")
out.write_bytes(data)
print(f"saved {out}")
print(f"code={code.hex()}")
print(f"patch={patch.hex()}")
print(f"text_va={text_va:#x} cap_va={cap_va:#x} resume={resume_va:#x}")
