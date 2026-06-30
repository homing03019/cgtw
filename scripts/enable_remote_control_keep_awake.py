import sqlite3
import shutil
from datetime import datetime

DB = r"C:\Users\User\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"
KEY = "glassRemoteControlKeepAwakeWhilePluggedIn"
VALUE = "true"

backup = DB + f".bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(DB, backup)
print("Backup:", backup)

conn = sqlite3.connect(DB, timeout=10)
cur = conn.cursor()
cur.execute("SELECT value FROM ItemTable WHERE key = ?", (KEY,))
row = cur.fetchone()
if row:
    print(f"Existing {KEY} = {row[0]}")
    cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?", (VALUE, KEY))
else:
    print(f"Inserting {KEY} = {VALUE}")
    cur.execute("INSERT INTO ItemTable (key, value) VALUES (?, ?)", (KEY, VALUE))
conn.commit()
cur.execute("SELECT value FROM ItemTable WHERE key = ?", (KEY,))
print("Now:", cur.fetchone()[0])
conn.close()
print("Done. Reload Cursor window (Ctrl+Shift+P -> Developer: Reload Window) for setting to apply.")
