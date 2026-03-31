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

# --- SYMBOL ---
SYMBOL     = "XAUUSD-VIP"
SLIPPAGE   = 10
MAX_SPREAD = 400

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
