from pathlib import Path
import re

raw = Path(r"D:/cgtw/luaUI/modules/map.lua").read_bytes()
text = raw.decode("gbk")

print("file size", len(raw))
print("_startNavigation", "_startNavigation" in text)
print("WinMgr.AutoCopilot", "WinMgr.AutoCopilot" in text)

for m in re.finditer(r"cliSendMsg\('([^']*)'", text):
    print("cliSendMsg:", m.group(1))

# compare with original zip
src = next(Path(r"C:/Users/User/Downloads").glob("UIMAP*/map.lua"))
orig = src.read_text(encoding="gbk")
print("\noriginal has AutoCopilot in run btn:", "self:AutoCopilot" in orig)

# check if map module loads - look for syntax errors
# extract _startNavigation function
i = text.find("function MapModule:_startNavigation")
j = text.find("function MapModule:updateMapPoints")
fn = text[i:j]
print("\n_startNavigation length", len(fn))
print(fn[:500])
