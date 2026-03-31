"""
1. CSOPORT Trading Bot — Főprogram
3 pozíció párhuzamos nyitása (ki/bekapcsolható a config.py-ban):
  POS1: TP3, fix SL (magic=11)
  POS2: TP5, fix vagy mozgó SL (magic=12)
  POS3: TP6, fix vagy mozgó SL (magic=13)

Mozgó SL verzió: config.py-ban MOZGO_SL_ENABLED = True

Indítás: python main.py
"""

import asyncio
import logging
import sys
from datetime import datetime
from telethon import TelegramClient, events

import config
from signal_parser import parse_signal
from mt5_trader import connect as mt5_connect, disconnect as mt5_disconnect
from mt5_trader import place_order, set_notifier as mt5_set_notifier, close_all_positions
from position_manager import register_deal, run_monitor
from notifier import notify_trade_opened, notify_trade_failed, send_notification
from sheets_logger import log_trade, log_skipped_signal

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("main_c1")

LABEL = "1.csoport"


# ── Heartbeat ─────────────────────────────────────────────────────────────────

async def run_heartbeat():
    last_sent_day = None
    while True:
        now = datetime.now()
        if (now.hour   == config.HEARTBEAT_HOUR and
            now.minute == config.HEARTBEAT_MINUTE and
            now.day    != last_sent_day):

            aktiv = []
            if config.POS1_ENABLED: aktiv.append(f"{config.POS1_LABEL}({config.POS1_LOT}lot, magic={config.POS1_MAGIC})")
            if config.POS2_ENABLED: aktiv.append(f"{config.POS2_LABEL}({config.POS2_LOT}lot, magic={config.POS2_MAGIC})")
            if config.POS3_ENABLED: aktiv.append(f"{config.POS3_LABEL}({config.POS3_LOT}lot, magic={config.POS3_MAGIC})")
            mozgo = "MOZGÓ SL" if config.MOZGO_SL_ENABLED else "FIX SL"

            await send_notification(
                f"✅ <b>1. csoport bot él</b>\n"
                f"Idő: {now.strftime('%Y-%m-%d %H:%M')}\n"
                f"Verzió: {mozgo}\n"
                f"Aktív pozíciók: {', '.join(aktiv) if aktiv else 'egyik sem'}"
            )
            last_sent_day = now.day
            logger.info("Heartbeat elküldve.")
        await asyncio.sleep(30)


# ── Jelzés feldolgozás ────────────────────────────────────────────────────────

async def process_signal(signal):
    logger.info(f"[{LABEL}] Jelzés: {signal.action} @ {signal.entry_mid}")
    mozgo = "MOZGÓ SL" if config.MOZGO_SL_ENABLED else "FIX SL"
    logger.info(f"[{LABEL}] Verzió: {mozgo}")

    poziciok = []
    if config.POS1_ENABLED:
        poziciok.append((config.POS1_LOT, config.POS1_MAGIC, config.POS1_TP_INDEX, config.POS1_LABEL))
    if config.POS2_ENABLED:
        poziciok.append((config.POS2_LOT, config.POS2_MAGIC, config.POS2_TP_INDEX, config.POS2_LABEL))
    if config.POS3_ENABLED:
        poziciok.append((config.POS3_LOT, config.POS3_MAGIC, config.POS3_TP_INDEX, config.POS3_LABEL))

    if not poziciok:
        logger.warning("Minden pozíció ki van kapcsolva a config.py-ban!")
        return

    for lot, magic, tp_index, pos_label in poziciok:
        deal, error = place_order(
            signal, config,
            lot_size=lot,
            magic=magic,
            tp_index=tp_index,
        )
        full_label = f"{LABEL} {pos_label}"
        if deal:
            register_deal(deal)
            await notify_trade_opened(deal, label=full_label)
            log_trade(deal)
        else:
            await notify_trade_failed(error, label=full_label)
            log_skipped_signal(signal, error)


# ── Főprogram ─────────────────────────────────────────────────────────────────

async def run_bot():
    logger.info("=" * 60)
    logger.info("1. CSOPORT Trading Bot indítása...")
    mozgo = "MOZGÓ SL" if config.MOZGO_SL_ENABLED else "FIX SL"
    logger.info(f"Verzió: {mozgo}")
    aktiv = []
    if config.POS1_ENABLED: aktiv.append(f"{config.POS1_LABEL}({config.POS1_LOT}lot, magic={config.POS1_MAGIC})")
    if config.POS2_ENABLED: aktiv.append(f"{config.POS2_LABEL}({config.POS2_LOT}lot, magic={config.POS2_MAGIC})")
    if config.POS3_ENABLED: aktiv.append(f"{config.POS3_LABEL}({config.POS3_LOT}lot, magic={config.POS3_MAGIC})")
    logger.info(f"Aktív pozíciók: {', '.join(aktiv)}")
    logger.info("=" * 60)

    mt5_set_notifier(send_notification)

    if not mt5_connect(config):
        logger.critical("MT5 csatlakozás sikertelen. Bot leáll.")
        return

    client = TelegramClient("csoport1_session", config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)

    @client.on(events.NewMessage(chats=config.SIGNAL_CHANNEL))
    async def on_message(event):
        text = event.message.text or ""
        logger.info(f"[{LABEL}] Új üzenet ({len(text)} karakter)")

        # ── Close parancs ellenőrzése ─────────────────────────────────────
        if "close" in text.lower():
            logger.info(f"[{LABEL}] CLOSE parancs érkezett!")
            sikeres, sikertelen = close_all_positions(config, label=LABEL)
            if sikeres > 0 or sikertelen > 0:
                await send_notification(
                    f"🔴 <b>Close parancs végrehajtva!</b>\n"
                    f"Forrás: <b>{LABEL}</b>\n"
                    f"✅ Sikeresen lezárva: {sikeres} pozíció\n"
                    f"❌ Sikertelen: {sikertelen} pozíció"
                )
            else:
                await send_notification(
                    f"ℹ️ <b>Close parancs érkezett</b>\n"
                    f"Forrás: <b>{LABEL}</b>\n"
                    f"Nincs nyitott bot pozíció."
                )
            return

        signal = parse_signal(text)
        if signal:
            asyncio.create_task(process_signal(signal))
        else:
            logger.debug("Nem felismert formátum — kihagyva.")

    await client.start(phone=config.TELEGRAM_PHONE)
    logger.info(f"[{LABEL}] Telegram figyelés aktív: {config.SIGNAL_CHANNEL}")

    await send_notification(
        f"🟢 <b>1. csoport bot elindult!</b>\n"
        f"Verzió: <b>{mozgo}</b>\n"
        f"Aktív: {', '.join(aktiv) if aktiv else 'egyik sem'}"
    )

    monitor_task   = asyncio.create_task(run_monitor())
    heartbeat_task = asyncio.create_task(run_heartbeat())

    try:
        await client.run_until_disconnected()
    finally:
        monitor_task.cancel()
        heartbeat_task.cancel()
        mt5_disconnect()
        await send_notification("🔴 <b>1. csoport bot leállt.</b>")


if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot manuálisan leállítva.")
