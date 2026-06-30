from pathlib import Path
import re

t = Path(r"D:/cgtw/luaUI/modules/map.lua").read_text(encoding="gbk")
Path(r"D:/cgtw/verify_result.txt").write_text("", encoding="utf-8")

def w(msg):
    p = Path(r"D:/cgtw/verify_result.txt")
    p.write_text(p.read_text(encoding="utf-8") + msg + "\n", encoding="utf-8")

for line in t.splitlines():
    if line.startswith("local combox"):
        w("combox: " + line)
    if line.startswith("local 文本"):
        w("textbg: " + line)

w("_queueNavigation: " + str("_queueNavigation" in t))
w("OnKeyPress(13: " + str("OnKeyPress(13" in t))
w("return MapModule: " + str("return MapModule" in t))
w("syntax bad })): " + str("}))" in t))
w("syntax bad ,,: " + str(",\n\t\t\t," in t))

# check inputY block
m = re.search(r"self\.inputY = win:AddTextInput\(\{.*?\n\t\t\t\}\)", t, re.DOTALL)
if m:
    w("inputY block ends OK")
else:
    w("inputY block BROKEN")

w("done")
