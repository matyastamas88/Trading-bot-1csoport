"""
Config updater - az uj_bot_telepito.bat hivja meg
Hasznalat: python config_updater.py <magic1> <magic2> <magic3> <log> <spread> <pos>
"""
import re, sys

magic1     = sys.argv[1]
magic2     = sys.argv[2]
magic3     = sys.argv[3]
log_nev    = sys.argv[4]
spread_nev = sys.argv[5]
pos_nev    = sys.argv[6]

with open('config.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(r'POS1_MAGIC\s*=\s*\d+',            f'POS1_MAGIC    = {magic1}', c)
c = re.sub(r'POS2_MAGIC\s*=\s*\d+',            f'POS2_MAGIC    = {magic2}', c)
c = re.sub(r'POS3_MAGIC\s*=\s*\d+',            f'POS3_MAGIC    = {magic3}', c)
c = re.sub(r'LOG_FILE\s*=\s*"[^"]+"',          f'LOG_FILE        = "{log_nev}"', c)
c = re.sub(r'SPREAD_LOG_FILE\s*=\s*"[^"]+"',   f'SPREAD_LOG_FILE = "{spread_nev}"', c)
c = re.sub(r'POSITIONS_FILE\s*=\s*"[^"]+"',    f'POSITIONS_FILE  = "{pos_nev}"', c)

with open('config.py', 'w', encoding='utf-8') as f:
    f.write(c)

print(f"config.py frissitve: magic={magic1},{magic2},{magic3} | log={log_nev}")
