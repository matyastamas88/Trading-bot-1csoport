import re
import logging

logger = logging.getLogger(__name__)

class TradeSignal:
    def __init__(self, action, entry_low, entry_high, tp_levels, sl, raw_text):
        self.action     = action
        self.entry_low  = entry_low
        self.entry_high = entry_high
        self.tp_levels  = tp_levels
        self.sl         = sl
        self.raw_text   = raw_text

    @property
    def entry_mid(self):
        return round((self.entry_low + self.entry_high) / 2, 2)

    @property
    def tp1(self):
        return self.tp_levels[0] if self.tp_levels else None

    def __str__(self):
        tps = " | ".join([f"TP{i+1}: {v}" for i, v in enumerate(self.tp_levels)])
        return (f"📊 {self.action} XAUUSD\n"
                f"Entry: {self.entry_low}-{self.entry_high}\n"
                f"{tps}\nSL: {self.sl}")

def parse_signal(text: str) -> TradeSignal | None:
    if not text:
        return None
    text_upper = text.upper()

    if "BUY" in text_upper:
        action = "BUY"
    elif "SELL" in text_upper:
        action = "SELL"
    else:
        return None

    entry_low = entry_high = None

    # Kezeli: "Entry Price\n4840/4835" vagy "Entry: 4840/4835" vagy "Entry: 4840-4835"
    range_match = re.search(
        r'entry[\w\s]{0,15}?\n?\s*(\d{3,5}(?:\.\d+)?)\s*[\/\-]\s*(\d{3,5}(?:\.\d+)?)',
        text, re.IGNORECASE
    )

    if range_match:
        a, b = float(range_match.group(1)), float(range_match.group(2))
        entry_low, entry_high = min(a, b), max(a, b)
    else:
        single_match = re.search(r'entry[\w\s]{0,15}?\n?\s*(\d{3,5}(?:\.\d+)?)', text, re.IGNORECASE)
        if single_match:
            entry_low = entry_high = float(single_match.group(1))

    if entry_low is None:
        return None

    tp_levels = []
    tp_matches = re.findall(r'TP\d*[:\s]+(\d{3,5}(?:\.\d+)?)', text, re.IGNORECASE)
    for v in tp_matches:
        tp_levels.append(float(v))

    if not tp_levels:
        return None

    sl = None
    sl_match = re.search(r'(?:stop\s*loss|sl)\s*[\(SL\)]*\s*:?\s*(\d{3,5}(?:\.\d+)?)', text, re.IGNORECASE)
    if sl_match:
        sl = float(sl_match.group(1))

    if sl is None:
        return None

    return TradeSignal(action, entry_low, entry_high, tp_levels, sl, text)