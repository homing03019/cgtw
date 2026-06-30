# -*- coding: utf-8 -*-
"""GBK + user-visible string check (ignores comment-only garble)."""
from pathlib import Path
import re
import sys

GARBLED = ('锟斤拷', '\ufffd', 'ï¿½', '英锟')

def user_visible_garbled(text):
    hits = []
    for m in re.finditer(r"'([^'\\]|\\.)*'|\"([^\"\\]|\\.)*\"", text):
        s = m.group(0)
        for g in GARBLED:
            if g in s:
                hits.append(g + ' in ' + s[:60])
    for g in GARBLED:
        if g in text and any(k in text for k in ['NLG.Say', 'NLG.SystemMessage', 'ShowWindowTalked', 'NPC_createNormal']):
            if g + ' in' not in str(hits):
                for line in text.splitlines():
                    if g in line and ('NLG.' in line or 'NPC_createNormal' in line or 'windowStr' in line):
                        hits.append(f'{g} line: {line.strip()[:80]}')
                        break
    return hits

files = sys.argv[1:]
if not files:
    print('usage: verify_gbk.py file...')
    sys.exit(1)

ok = True
for f in files:
    p = Path(f)
    try:
        t = p.read_bytes().decode('gbk')
    except Exception as e:
        print(f'{p.name}: FAIL decode {e}')
        ok = False
        continue
    hits = user_visible_garbled(t)
    status = 'OK' if not hits else 'FAIL'
    print(f'{p.name}: {status} {hits[:3]}')
    if hits:
        ok = False
sys.exit(0 if ok else 1)
