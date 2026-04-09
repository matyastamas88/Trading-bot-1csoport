"""
Trading Bot — Beállítási varázsló
Egyszer futtatd ezt a programot a beállítások megadásához.
Indítás: python setup.py
"""

import json
import os

SETTINGS_FILE = "user_settings.json"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 55)
    print("   Trading Bot — Személyes beállítások")
    print("=" * 55)
    print()

def kerd_int(szoveg, min_val, max_val):
    while True:
        try:
            val = int(input(szoveg))
            if min_val <= val <= max_val:
                return val
            print(f"  ⚠️  Csak {min_val}-{max_val} közötti számot adj meg!")
        except ValueError:
            print("  ⚠️  Számot adj meg!")

def kerd_float(szoveg, min_val, max_val):
    while True:
        try:
            val = float(input(szoveg).replace(',', '.'))
            if min_val <= val <= max_val:
                return val
            print(f"  ⚠️  {min_val}-{max_val} közötti értéket adj meg!")
        except ValueError:
            print("  ⚠️  Számot adj meg! (pl. 1.5)")

def kerd_igen_nem(szoveg):
    while True:
        val = input(szoveg).strip().lower()
        if val in ['i', 'igen', 'y', 'yes']:
            return True
        if val in ['n', 'nem', 'no']:
            return False
        print("  ⚠️  Írj 'i'-t (igen) vagy 'n'-t (nem)!")

def main():
    clear()
    print_header()
    print("Ez a varázsló segít beállítani a Trading Bot személyes")
    print("beállításait. A .env fájlban lévő adatokat NEM érinti.")
    print()
    input("Nyomj Enter-t a folytatáshoz...")

    settings = {}

    # ── 1. POZÍCIÓK ──────────────────────────────────────────────────────────
    clear()
    print_header()
    print("1. lépés: Pozíciók kiválasztása")
    print("-" * 55)
    print()
    print("  POS1 (magic=11): TP3 célra — gyorsan zár, fix SL")
    print("  POS2 (magic=12): TP5 célra — közepes cél")
    print("  POS3 (magic=13): TP6 célra — maximális profit")
    print()
    print("  Melyik kombinációt szeretnéd futtatni?")
    print()
    print("  1 = Csak POS1 (TP3)")
    print("  2 = Csak POS3 (TP6)")
    print("  3 = POS1 + POS2 (TP3 + TP5)")
    print("  4 = POS1 + POS3 (TP3 + TP6)")
    print("  5 = POS2 + POS3 (TP5 + TP6)")
    print("  6 = Mind a három (TP3 + TP5 + TP6)")
    print()

    valasztas = kerd_int("  Választás (1-6): ", 1, 6)

    kombik = {
        1: (True,  False, False),
        2: (False, False, True),
        3: (True,  True,  False),
        4: (True,  False, True),
        5: (False, True,  True),
        6: (True,  True,  True),
    }
    pos1_en, pos2_en, pos3_en = kombik[valasztas]
    settings["POS1_ENABLED"] = pos1_en
    settings["POS2_ENABLED"] = pos2_en
    settings["POS3_ENABLED"] = pos3_en

    # ── 2. LOT MÉRETEZÉS ─────────────────────────────────────────────────────
    clear()
    print_header()
    print("2. lépés: Lot méretezés")
    print("-" * 55)
    print()
    print("  Automata: a bot kiszámolja a lot méretet a számlaegyenleg")
    print("            és a megadott kockázat % alapján.")
    print()
    print("  Manuális: te adod meg a fix lot méretet minden pozícióhoz.")
    print()

    auto_lot = kerd_igen_nem("  Automata lot méretezést szeretnél? (i/n): ")
    settings["AUTO_LOT"] = auto_lot

    if auto_lot:
        # ── 2a. KOCKÁZAT % ───────────────────────────────────────────────────
        clear()
        print_header()
        print("2a. lépés: Kockázat mértéke")
        print("-" * 55)
        print()
        print("  Mennyi legyen a maximális kockázat kereskedésenként?")
        print("  Ez a számlaegyenleg %-ában értendő.")
        print()
        print("  Példa 1000 USD egyenlegnél:")
        print("    0.5% → max 5 USD veszteség / kereskedés")
        print("    1.0% → max 10 USD veszteség / kereskedés")
        print("    2.0% → max 20 USD veszteség / kereskedés")
        print()
        print("  Ajánlott: 0.5% - 2% (kezdőknek 0.5%-1%)")
        print()

        if pos1_en:
            kock1 = kerd_float("  POS1 (TP3) kockázat % (pl. 1.0): ", 0.1, 10.0)
            settings["POS1_RISK_PCT"] = kock1
        if pos2_en:
            kock2 = kerd_float("  POS2 (TP5) kockázat % (pl. 0.5): ", 0.1, 10.0)
            settings["POS2_RISK_PCT"] = kock2
        if pos3_en:
            kock3 = kerd_float("  POS3 (TP6) kockázat % (pl. 0.5): ", 0.1, 10.0)
            settings["POS3_RISK_PCT"] = kock3

        settings["POS1_LOT"] = None
        settings["POS2_LOT"] = None
        settings["POS3_LOT"] = None

    else:
        # ── 2b. MANUÁLIS LOT ─────────────────────────────────────────────────
        clear()
        print_header()
        print("2b. lépés: Manuális lot méretek")
        print("-" * 55)
        print()
        print("  Add meg a fix lot méretet minden aktív pozícióhoz.")
        print("  (0.01 = mini lot, ajánlott kezdőknek)")
        print()

        if pos1_en:
            lot1 = kerd_float("  POS1 (TP3) lot méret (pl. 0.01): ", 0.01, 100.0)
            settings["POS1_LOT"] = lot1
        else:
            settings["POS1_LOT"] = 0.01

        if pos2_en:
            lot2 = kerd_float("  POS2 (TP5) lot méret (pl. 0.01): ", 0.01, 100.0)
            settings["POS2_LOT"] = lot2
        else:
            settings["POS2_LOT"] = 0.01

        if pos3_en:
            lot3 = kerd_float("  POS3 (TP6) lot méret (pl. 0.01): ", 0.01, 100.0)
            settings["POS3_LOT"] = lot3
        else:
            settings["POS3_LOT"] = 0.01

        settings["POS1_RISK_PCT"] = None
        settings["POS2_RISK_PCT"] = None
        settings["POS3_RISK_PCT"] = None

    # ── 3. MAX NAPI VESZTESÉG ─────────────────────────────────────────────────
    clear()
    print_header()
    print("3. lépés: Napi veszteség limit")
    print("-" * 55)
    print()
    print("  Ha a nap folyamán a bot ennyit veszít, automatikusan")
    print("  leáll és másnap reggel újraindul.")
    print()
    print("  Példa 1000 USD egyenlegnél:")
    print("    3% → 30 USD napi veszteség után leáll")
    print("    5% → 50 USD napi veszteség után leáll")
    print()

    napi_limit = kerd_igen_nem("  Szeretnél napi veszteség limitet? (i/n): ")
    if napi_limit:
        napi_pct = kerd_float("  Max napi veszteség % (pl. 5.0): ", 0.1, 50.0)
        settings["DAILY_LOSS_LIMIT_PCT"] = napi_pct
    else:
        settings["DAILY_LOSS_LIMIT_PCT"] = 0.0


    # ── 4. MOZGÓ SL ───────────────────────────────────────────────────────────
    clear()
    print_header()
    print("4. lépés: Mozgó Stop Loss")
    print("-" * 55)
    print()
    print("  Fix SL:   az SL végig az eredeti szinten marad.")
    print()
    print("  Mozgó SL: ha az ár eléri a TP3 szintet, az SL")
    print("            átmozdul az entry szintre (0 kockázat)")
    print("            Ha eléri TP4-et → SL = TP1 szintre")
    print("            Ha eléri TP5-öt → SL = TP2 szintre")
    print()
    print("  Ajánlott: mozgó SL esetén kisebb lehet a profit")
    print("            de jobban véd a visszafordulás ellen.")
    print()

    mozgo_sl = kerd_igen_nem("  Mozgó SL-t szeretnél? (i/n): ")
    settings["MOZGO_SL_ENABLED"] = mozgo_sl


    # ── 5. MAX NAPI KERESKEDÉS ────────────────────────────────────────────────
    clear()
    print_header()
    print("5. lépés: Napi maximum kereskedések száma")
    print("-" * 55)
    print()
    print("  Hány kereskedést indíthat a bot naponta?")
    print("  (Ez egy jelzésre nyitott pozíció-csoportot jelent)")
    print()
    print("  0 = korlátlan")
    print("  1 = maximum 1 jelzés naponta (ajánlott kezdőknek)")
    print("  2 = maximum 2 jelzés naponta")
    print()
    print("  Ha elérte a napi limitet, értesítést küld és")
    print("  másnap este 20:00 után automatikusan visszaáll.")
    print()

    max_napi = kerd_int("  Max napi kereskedés (0=korlátlan): ", 0, 10)
    settings["MAX_NAPI_KERESKEDES"] = max_napi

    # ── ÖSSZEFOGLALÁS ─────────────────────────────────────────────────────────
    clear()
    print_header()
    print("Összefoglalás — kérlek ellenőrizd!")
    print("-" * 55)
    print()

    aktiv = []
    if settings["POS1_ENABLED"]: aktiv.append("POS1/TP3")
    if settings["POS2_ENABLED"]: aktiv.append("POS2/TP5")
    if settings["POS3_ENABLED"]: aktiv.append("POS3/TP6")
    print(f"  Aktív pozíciók:   {', '.join(aktiv)}")

    if settings["AUTO_LOT"]:
        lot_info = []
        if settings["POS1_ENABLED"]: lot_info.append(f"POS1: {settings.get('POS1_RISK_PCT')}%")
        if settings["POS2_ENABLED"]: lot_info.append(f"POS2: {settings.get('POS2_RISK_PCT')}%")
        if settings["POS3_ENABLED"]: lot_info.append(f"POS3: {settings.get('POS3_RISK_PCT')}%")
        print(f"  Lot méretezés:    Automata ({', '.join(lot_info)})")
    else:
        lot_info = []
        if settings["POS1_ENABLED"]: lot_info.append(f"POS1: {settings.get('POS1_LOT')} lot")
        if settings["POS2_ENABLED"]: lot_info.append(f"POS2: {settings.get('POS2_LOT')} lot")
        if settings["POS3_ENABLED"]: lot_info.append(f"POS3: {settings.get('POS3_LOT')} lot")
        print(f"  Lot méretezés:    Manuális ({', '.join(lot_info)})")

    if settings["DAILY_LOSS_LIMIT_PCT"] > 0:
        print(f"  Napi limit:       {settings['DAILY_LOSS_LIMIT_PCT']}%")
    else:
        print(f"  Napi limit:       kikapcsolva")

    print(f"  Mozgó SL:         {'igen' if settings.get('MOZGO_SL_ENABLED') else 'nem'}")
    max_k = settings.get('MAX_NAPI_KERESKEDES', 0)
    print(f"  Max napi keresk.: {'korlátlan' if max_k == 0 else str(max_k)}")
    print()

    # Időablak alapértékek (nem kérdezzük, de kell a config-nak)
    settings["TRADE_HOURS_ENABLED"] = False
    settings["TRADE_HOUR_START"]    = 0
    settings["TRADE_HOUR_END"]      = 24

    mentes = kerd_igen_nem("  Elmented a beállításokat? (i/n): ")
    if mentes:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        print()
        print("  ✅ Beállítások elmentve!")
        print(f"  Fájl: {os.path.abspath(SETTINGS_FILE)}")
        print()
        print("  Most már elindíthatod a botot a main1.bat-tal.")
    else:
        print()
        print("  ❌ Mentés megszakítva — semmi nem változott.")

    print()
    input("  Nyomj Enter-t a kilépéshez...")

if __name__ == "__main__":
    main()
