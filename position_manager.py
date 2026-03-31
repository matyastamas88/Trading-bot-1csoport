"""
Pozíció figyelő — v2
- Mozgó SL trigger: POS1 (TP3) pozíció lezárulása alapján, nem ár figyeléssel
- JSON mentés adatvesztés ellen
"""

import asyncio
import logging
import json
import os
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import config
from mt5_trader import modify_position, is_position_open, cancel_pending_order, is_pending_open
from notifier import send_notification

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 5

_active_deals:  dict[int, dict] = {}
_pending_deals: dict[int, dict] = {}

POSITIONS_FILE = getattr(config, 'POSITIONS_FILE', 'positions.json')

# Csoportosítás jelzés alapján: signal_id → [ticket1, ticket2, ticket3]
# Így tudjuk melyik pozíciók tartoznak össze
_signal_groups: dict[str, list[int]] = {}


# ── JSON mentés / betöltés ────────────────────────────────────────────────────

def _save_positions():
    data = {
        "active":        {str(k): v for k, v in _active_deals.items()},
        "pending":       {str(k): v for k, v in _pending_deals.items()},
        "signal_groups": _signal_groups,
    }
    try:
        with open(POSITIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Pozíció mentés sikertelen: {e}")


def _load_positions():
    global _signal_groups
    if not os.path.exists(POSITIONS_FILE):
        return
    try:
        with open(POSITIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.get("active", {}).items():
            ticket = int(k)
            if is_position_open(ticket):
                _active_deals[ticket] = v
                logger.info(f"♻️ Pozíció visszatöltve: #{ticket} | Magic: {v.get('magic')}")
        for k, v in data.get("pending", {}).items():
            ticket = int(k)
            if is_pending_open(ticket):
                _pending_deals[ticket] = v
                logger.info(f"♻️ Pending visszatöltve: #{ticket}")
        _signal_groups = data.get("signal_groups", {})
        if _active_deals or _pending_deals:
            logger.info(f"Visszatöltve: {len(_active_deals)} aktív, {len(_pending_deals)} pending")
    except Exception as e:
        logger.error(f"Pozíció betöltés sikertelen: {e}")


# ── Mozgó SL lépési táblázat ──────────────────────────────────────────────────

def build_mozgo_sl_table(start_tp_index: int, last_tp_index: int) -> dict:
    """
    Dinamikus mozgó SL táblázat.
    start_tp elérésekor → SL = Entry
    start_tp+1 elérésekor → SL = TP(start_tp-1) ha van, különben Entry marad
    stb.
    """
    table = {}
    for i in range(start_tp_index, last_tp_index):
        if i == start_tp_index:
            sl_source = "entry"
        else:
            sl_source = max(0, i - 2)
        table[i] = {"sl_source": sl_source, "next_tp_index": i + 1}
    return table


def _get_new_sl(deal: dict, sl_source) -> float:
    if sl_source == "entry":
        return deal["entry_price"]
    idx = int(sl_source)
    if idx < len(deal["tp_levels"]):
        return deal["tp_levels"][idx]
    return deal["entry_price"]


# ── Magic → label ─────────────────────────────────────────────────────────────

def _magic_label(magic: int) -> str:
    csoport = "1.csoport"
    if hasattr(config, 'LOG_FILE'):
        if 'csoport3' in config.LOG_FILE:
            csoport = "3.csoport"
        elif 'csoport2' in config.LOG_FILE:
            csoport = "2.csoport"
    for attr, label_attr in [('POS1_MAGIC','POS1_LABEL'),('POS2_MAGIC','POS2_LABEL'),('POS3_MAGIC','POS3_LABEL')]:
        if getattr(config, attr, None) == magic:
            return f"{csoport} {getattr(config, label_attr, attr)}"
    return f"magic={magic}"


# ── Regisztráció ──────────────────────────────────────────────────────────────

def register_deal(deal: dict):
    """
    Regisztrálja a pozíciót figyelésre.
    A signal_id alapján csoportosítja az összetartozó pozíciókat.
    """
    ticket = deal["ticket"]
    signal_id = deal.get("signal_id", "")

    if deal.get("is_pending"):
        _pending_deals[ticket] = deal
        logger.info(f"⏳ Pending figyelés: #{ticket} | {_magic_label(deal['magic'])}")
    else:
        _active_deals[ticket] = deal
        logger.info(f"Pozíció figyelés: #{ticket} | {_magic_label(deal['magic'])}")

    # Csoportba regisztrálás
    if signal_id:
        if signal_id not in _signal_groups:
            _signal_groups[signal_id] = []
        if ticket not in _signal_groups[signal_id]:
            _signal_groups[signal_id].append(ticket)

    _save_positions()


# ── TP3 elérés detektálása deal history alapján ───────────────────────────────

def _was_closed_at_tp(ticket: int) -> bool:
    """
    Ellenőrzi hogy a pozíció TP szinten zárult-e (nem SL-en vagy manuálisan).
    MT5 history alapján: ha a zárási ár közel van a TP szinthez.
    """
    if not mt5.history_deals_get(position=ticket):
        return False
    deals = mt5.history_deals_get(position=ticket)
    if not deals:
        return False
    # Az utolsó deal a zárás
    close_deal = sorted(deals, key=lambda d: d.time)[-1]
    # entry típus = 1 (OUT), reason = 1 (TP)
    return close_deal.reason == mt5.DEAL_REASON_TP


def _get_sister_deals(ticket: int) -> list[dict]:
    """
    Visszaadja az összetartozó pozíciókat (ugyanabból a jelzésből nyitottak).
    """
    for signal_id, tickets in _signal_groups.items():
        if ticket in tickets:
            return [_active_deals[t] for t in tickets if t in _active_deals and t != ticket]
    return []


# ── Pending ellenőrzés ────────────────────────────────────────────────────────

async def _check_pending(ticket: int, deal: dict):
    label = _magic_label(deal["magic"])

    if not is_pending_open(ticket):
        if is_position_open(ticket):
            logger.info(f"✅ Pending teljesült: #{ticket} ({label})")
            deal["is_pending"] = False
            _active_deals[ticket] = deal
            await send_notification(
                f"✅ <b>Limit megbízás teljesült!</b>\n"
                f"Forrás: <b>{label}</b>\n"
                f"Ticket: #{ticket} | Magic: {deal.get('magic', '?')}\n"
                f"Ár: <b>{deal['price']}</b>\n"
                f"SL: {deal['sl']} | TP: {deal['tp']}"
            )
        else:
            await send_notification(
                f"ℹ️ <b>Pending megszűnt</b>\n"
                f"Forrás: <b>{label}</b>\n"
                f"Ticket: #{ticket}"
            )
        del _pending_deals[ticket]
        _save_positions()
        return

    if config.PENDING_TIMEOUT_MINUTES <= 0:
        return

    created_at = datetime.fromisoformat(deal["time"])
    if datetime.now() - created_at >= timedelta(minutes=config.PENDING_TIMEOUT_MINUTES):
        cancelled = cancel_pending_order(ticket)
        del _pending_deals[ticket]
        _save_positions()
        if cancelled:
            await send_notification(
                f"⏰ <b>Pending törölve — időtúllépés</b>\n"
                f"Forrás: <b>{label}</b>\n"
                f"Ticket: #{ticket} | {config.PENDING_TIMEOUT_MINUTES} perc eltelt."
            )


# ── Aktív pozíció ellenőrzés ──────────────────────────────────────────────────

async def _check_deal(ticket: int, deal: dict):
    label = _magic_label(deal["magic"])
    magic = deal["magic"]
    pos1_magic = getattr(config, 'POS1_MAGIC', None)

    # ── Pozíció lezárult? ────────────────────────────────────────────────────
    if not is_position_open(ticket):
        logger.info(f"Pozíció zárul: #{ticket} ({label})")

        # Ha ez a POS1 (TP3-as) pozíció és TP-n zárt → mozgassuk a testvér pozíciók SL-jét
        if config.MOZGO_SL_ENABLED and magic == pos1_magic:
            if _was_closed_at_tp(ticket):
                logger.info(f"📍 POS1 (TP3) TP-n zárt → testvér pozíciók SL mozgatása")
                sister_deals = _get_sister_deals(ticket)
                for sister in sister_deals:
                    await _apply_mozgo_sl_step(sister, triggered_by_pos1=True)
            else:
                logger.info(f"POS1 nem TP-n zárt (SL vagy manuális) — mozgó SL nem aktiválódik")

        await send_notification(
            f"🏁 <b>Pozíció lezárult</b>\n"
            f"Forrás: <b>{label}</b>\n"
            f"Ticket: #{ticket} | Utolsó cél: TP{deal['tp_index']+1}"
        )
        del _active_deals[ticket]
        _save_positions()
        return

    # Fix SL verzió — nincs teendő
    if not config.MOZGO_SL_ENABLED:
        return

    # POS1 (TP3) esetén nem kell ár figyelés — azt a zárás triggeri
    if magic == pos1_magic:
        return

    # POS2/POS3: csak ha már mozgó SL aktív (tp_index > start_tp_index)
    start_tp = deal.get("start_tp_index", deal["tp_index"])
    if deal["tp_index"] <= start_tp and deal.get("mozgo_sl_active", False) is False:
        return  # Még nem aktiválódott a mozgó SL

    # Ha már mozgó SL aktív, figyeljük a következő TP szinteket ár alapján
    current_tp_index = deal["tp_index"]
    last_tp = len(deal["tp_levels"]) - 1
    step_table = build_mozgo_sl_table(start_tp, last_tp)

    if current_tp_index not in step_table:
        return

    tick = mt5.symbol_info_tick(config.SYMBOL)
    if tick is None:
        return

    current_price = tick.bid if deal["action"] == "SELL" else tick.ask
    current_tp    = deal["tp_levels"][current_tp_index]

    tp_reached = (
        (deal["action"] == "SELL" and current_price <= current_tp) or
        (deal["action"] == "BUY"  and current_price >= current_tp)
    )

    if tp_reached:
        await _apply_mozgo_sl_step(deal, triggered_by_pos1=False)


async def _apply_mozgo_sl_step(deal: dict, triggered_by_pos1: bool = False):
    """
    Elvégzi az SL mozgatást a következő szintre.
    triggered_by_pos1=True: POS1 zárása triggelte (TP3 elérve)
    triggered_by_pos1=False: ár alapú trigger (TP4, TP5 stb.)
    """
    ticket = deal["ticket"]
    label  = _magic_label(deal["magic"])

    if not is_position_open(ticket):
        return

    start_tp = deal.get("start_tp_index", deal["tp_index"])
    last_tp  = len(deal["tp_levels"]) - 1
    step_table = build_mozgo_sl_table(start_tp, last_tp)

    if triggered_by_pos1:
        # POS1 zárása = TP3 elérve = első lépés: SL → Entry
        current_tp_index = start_tp
        deal["mozgo_sl_active"] = True
    else:
        current_tp_index = deal["tp_index"]

    if current_tp_index not in step_table:
        return

    step        = step_table[current_tp_index]
    new_sl      = _get_new_sl(deal, step["sl_source"])
    next_tp_idx = step["next_tp_index"]

    if next_tp_idx < len(deal["tp_levels"]):
        new_tp     = deal["tp_levels"][next_tp_idx]
        next_label = f"TP{next_tp_idx+1}"
    else:
        new_tp     = deal["tp"]
        next_label = "utolsó TP"

    sl_source = step["sl_source"]
    sl_label  = "Entry" if sl_source == "entry" else f"TP{int(sl_source)+1}"
    tp_name   = f"TP{current_tp_index+1}"

    ok = modify_position(ticket, new_sl, new_tp, config.SYMBOL)
    if ok:
        deal["sl"]              = new_sl
        deal["tp"]              = new_tp
        deal["tp_index"]        = next_tp_idx
        deal["mozgo_sl_active"] = True
        _active_deals[ticket]   = deal
        _save_positions()
        await send_notification(
            f"📍 <b>{tp_name} elérve!</b>\n"
            f"Forrás: <b>{label}</b>\n"
            f"Ticket: #{ticket}\n"
            f"SL átmozgatva: <b>{new_sl}</b> ({sl_label})\n"
            f"Következő cél: <b>{new_tp}</b> ({next_label})"
        )
    else:
        logger.error(f"SL/TP módosítás sikertelen #{ticket}")


# ── Fő loop ───────────────────────────────────────────────────────────────────

async def run_monitor():
    mozgo = "MOZGÓ SL" if config.MOZGO_SL_ENABLED else "FIX SL"
    logger.info(f"Pozíció figyelő indult | Verzió: {mozgo} | Pending timeout: {config.PENDING_TIMEOUT_MINUTES} perc")
    _load_positions()

    while True:
        for ticket, deal in list(_pending_deals.items()):
            try:
                await _check_pending(ticket, deal)
            except Exception as e:
                logger.error(f"Pending hiba #{ticket}: {e}")

        for ticket, deal in list(_active_deals.items()):
            try:
                await _check_deal(ticket, deal)
            except Exception as e:
                logger.error(f"Pozíció hiba #{ticket}: {e}")

        await asyncio.sleep(CHECK_INTERVAL)
