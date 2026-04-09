# ============================================================
#  1. CSOPORT Trading Bot - Konfiguráció
#  Érzékeny adatok a .env fájlban vannak!
#  pip install python-dotenv  (egyszer kell)
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# --- ÜZEMMÓD ---
AUTO_MODE        = True
APPROVAL_TIMEOUT = 120

# --- TELEGRAM API (.env-ből) ---
TELEGRAM_API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_PHONE    = os.getenv("TELEGRAM_PHONE", "")
SIGNAL_CHANNEL    = int(os.getenv("SIGNAL_CHANNEL", "0"))

# --- ÉRTESÍTÉSI BOT (.env-ből) ---
NOTIFY_BOT_TOKEN = os.getenv("NOTIFY_BOT_TOKEN", "")
NOTIFY_CHAT_ID   = int(os.getenv("NOTIFY_CHAT_ID", "0"))

# --- MT5 BEÁLLÍTÁSOK (.env-ből) ---
MT5_LOGIN    = int(os.getenv("MT5_LOGIN", "0"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER   = os.getenv("MT5_SERVER", "VTMarkets-Demo")

# --- MT5 TERMINAL ELÉRÉSI ÚT (.env-ből vagy itt) ---
MT5_TERMINAL_PATH = os.getenv(
    "MT5_TERMINAL_PATH",
    r"C:\Program Files\VT Markets (Pty) MT5 Terminal\terminal64.exe"
)

# --- SYMBOL (.env-ből) ---
SYMBOL     = os.getenv("SYMBOL", "XAUUSD-VIP")  # VT Markets: XAUUSD-VIP | BlackBull: XAUUSD
SLIPPAGE   = 10
MAX_SPREAD = 400

# --- BOT NEVE (.env-ből) ---
# Ezt add meg a .env fájlban: BOT_NEV=SuperXAUUSD
# Ez a név jelenik meg minden Telegram értesítésben
BOT_NEV = os.getenv("BOT_NEV", "1.csoport")

# --- SESSION FÁJL NEVE (.env-ből) ---
# Minden botnak egyedi session fájl kell!
SESSION_NEV = os.getenv("SESSION_NEV", "csoport1_session")

# ============================================================
#  POZÍCIÓ BEÁLLÍTÁSOK
# ============================================================

POS1_ENABLED  = True
POS1_LOT      = 0.03
POS1_TP_INDEX = 2
POS1_MAGIC    = 11
POS1_LABEL    = "TP3-fix"

POS2_ENABLED  = True
POS2_LOT      = 0.02
POS2_TP_INDEX = 4
POS2_MAGIC    = 12
POS2_LABEL    = "TP5-fix"

POS3_ENABLED  = True
POS3_LOT      = 0.01
POS3_TP_INDEX = 5
POS3_MAGIC    = 13
POS3_LABEL    = "TP6-fix"

MOZGO_SL_ENABLED = False

PENDING_TIMEOUT_MINUTES = 30
HEARTBEAT_HOUR   = 20
HEARTBEAT_MINUTE = 0

LOG_FILE        = "csoport1_bot.log"
SPREAD_LOG_FILE = "csoport1_spread_log.csv"
POSITIONS_FILE  = "csoport1_positions.json"

# --- PARANCS CSATORNA ---
COMMAND_CHANNEL = -5120457999  # Bot Parancsok&Infok csoport

# ============================================================
#  FELHASZNÁLÓI BEÁLLÍTÁSOK (setup.py által generált)
#  Ha létezik user_settings.json, felülírja a fenti értékeket
# ============================================================

import json as _json

_settings_file = os.path.join(os.path.dirname(__file__), "user_settings.json")
if os.path.exists(_settings_file):
    try:
        with open(_settings_file, "r", encoding="utf-8") as _f:
            _s = _json.load(_f)

        # Pozíciók
        if "POS1_ENABLED"  in _s: POS1_ENABLED  = _s["POS1_ENABLED"]
        if "POS2_ENABLED"  in _s: POS2_ENABLED  = _s["POS2_ENABLED"]
        if "POS3_ENABLED"  in _s: POS3_ENABLED  = _s["POS3_ENABLED"]

        # Lot méretek (csak ha manuális)
        if _s.get("POS1_LOT") is not None: POS1_LOT = _s["POS1_LOT"]
        if _s.get("POS2_LOT") is not None: POS2_LOT = _s["POS2_LOT"]
        if _s.get("POS3_LOT") is not None: POS3_LOT = _s["POS3_LOT"]

        # Automata lot
        AUTO_LOT       = _s.get("AUTO_LOT", False)
        POS1_RISK_PCT  = _s.get("POS1_RISK_PCT", 1.0)
        POS2_RISK_PCT  = _s.get("POS2_RISK_PCT", 1.0)
        POS3_RISK_PCT  = _s.get("POS3_RISK_PCT", 1.0)

        # Mozgó SL
        if "MOZGO_SL_ENABLED" in _s: MOZGO_SL_ENABLED = _s["MOZGO_SL_ENABLED"]

        # Napi max kereskedés
        MAX_NAPI_KERESKEDES = _s.get("MAX_NAPI_KERESKEDES", 0)

        # Napi limit
        DAILY_LOSS_LIMIT_PCT = _s.get("DAILY_LOSS_LIMIT_PCT", 0.0)

        # Időablak
        TRADE_HOURS_ENABLED = _s.get("TRADE_HOURS_ENABLED", False)
        TRADE_HOUR_START    = _s.get("TRADE_HOUR_START", 0)
        TRADE_HOUR_END      = _s.get("TRADE_HOUR_END", 24)

    except Exception as _e:
        print(f"⚠️ user_settings.json betöltési hiba: {_e} — alapértelmezett értékek használva")
        AUTO_LOT             = False
        DAILY_LOSS_LIMIT_PCT = 0.0
        TRADE_HOURS_ENABLED  = False
        TRADE_HOUR_START     = 0
        TRADE_HOUR_END       = 24
        POS1_RISK_PCT        = 1.0
        POS2_RISK_PCT        = 1.0
        POS3_RISK_PCT        = 1.0
        MAX_NAPI_KERESKEDES  = 0
else:
    # Ha nincs user_settings.json, alapértelmezett értékek
    AUTO_LOT             = False
    DAILY_LOSS_LIMIT_PCT = 0.0
    TRADE_HOURS_ENABLED  = False
    TRADE_HOUR_START     = 0
    TRADE_HOUR_END       = 24
    POS1_RISK_PCT        = 1.0
    POS2_RISK_PCT        = 1.0
    POS3_RISK_PCT        = 1.0
    MAX_NAPI_KERESKEDES  = 0
