#!/usr/bin/env python3
"""
🧠 MIKKIE WORLD — BRAIN Orchestrator v1.0
==========================================
Centrale orchestrator die alle agents automatisch op schema aanstuurt.
Draait als daemon op de achtergrond en coördineert het volledige dagschema.

Gebruik:
  python3 mikkie_brain.py start    → Start BRAIN daemon op achtergrond
  python3 mikkie_brain.py stop     → Stop BRAIN daemon
  python3 mikkie_brain.py status   → Toon huidig schema en volgende taak
  python3 mikkie_brain.py run now  → Voer dagelijkse routine nu direct uit
  python3 mikkie_brain.py schedule → Toon volledig weekschema
"""

import os
import sys
import json
import time
import signal
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ─── Paden ────────────────────────────────────────────────────────────────────
BASE_DIR   = Path.home() / "mikkieworld"
BRAIN_DIR  = Path.home() / "MIKKIE_WORLD"
LOG_DIR    = BRAIN_DIR / "LOGS"
PID_FILE   = BASE_DIR / "pids" / "brain.pid"
LOG_FILE   = LOG_DIR / "brain.log"
STATE_FILE = BRAIN_DIR / "brain_state.json"

# Zorg dat mappen bestaan
for d in [LOG_DIR, BASE_DIR / "pids", BRAIN_DIR / "SOCIAL" / "X_Twitter",
          BRAIN_DIR / "CONTENT" / "covers", BRAIN_DIR / "GUMROAD"]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("BRAIN")

# ─── Kleuren ──────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
PURPLE = "\033[95m"

def c(text, color): return f"{color}{text}{RESET}"

# ─── Telegram helper ──────────────────────────────────────────────────────────
def telegram(msg: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat  = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    try:
        import urllib.request
        data = json.dumps({"chat_id": chat, "text": msg, "parse_mode": "HTML"}).encode()
        req  = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

# ─── Karakter schema (dag van de week) ────────────────────────────────────────
KARAKTER_SCHEMA = {
    0: "MIKKIE",    # Maandag
    1: "BUBBLES",   # Dinsdag
    2: "KNOEST",    # Woensdag
    3: "FIDO",      # Donderdag
    4: "NYX",       # Vrijdag
    5: "ZERA",      # Zaterdag
    6: "ORA",       # Zondag
}

# ─── Volledig dagschema ────────────────────────────────────────────────────────
# Elke taak: (uur, minuut, naam, commando, beschrijving)
DAGSCHEMA = [
    # Ochtend — content genereren
    (7,  0,  "morning_post_1",    ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],
             "Post #1 genereren voor X"),
    (7,  5,  "morning_tweet",     ["python3", str(BASE_DIR/"mikkie_tweet.py"), "auto"],
             "Post #1 live op X"),
    (8,  0,  "morning_post_2",    ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],
             "Post #2 genereren voor X"),
    (8,  5,  "morning_tweet_2",   ["python3", str(BASE_DIR/"mikkie_tweet.py"), "auto"],
             "Post #2 live op X"),

    # Middag — content + Artistly
    (12, 0,  "middag_post",       ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],
             "Middag post genereren"),
    (12, 5,  "middag_tweet",      ["python3", str(BASE_DIR/"mikkie_tweet.py"), "auto"],
             "Middag post live op X"),
    (13, 0,  "artistly_covers",   ["python3", str(BASE_DIR/"mikkie_artistly_agent.py"), "covers"],
             "Artistly covers genereren (wekelijks maandag)"),

    # Middag — Gumroad check
    (14, 0,  "gumroad_check",     ["python3", str(BASE_DIR/"mikkie_agent.py"), "check"],
             "Gumroad sales check"),

    # Avond — content
    (17, 0,  "avond_post",        ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],
             "Avond post genereren"),
    (17, 5,  "avond_tweet",       ["python3", str(BASE_DIR/"mikkie_tweet.py"), "auto"],
             "Avond post live op X"),
    (19, 0,  "prime_post",        ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],
             "Prime time post genereren"),
    (19, 5,  "prime_tweet",       ["python3", str(BASE_DIR/"mikkie_tweet.py"), "auto"],
             "Prime time post live op X"),

    # Nacht — Artistly batch
    (22, 0,  "nacht_artistly",    ["python3", str(BASE_DIR/"mikkie_artistly_agent.py"), "social"],
             "Nacht Artistly social posts genereren"),
    (22, 30, "nacht_stickers",    ["python3", str(BASE_DIR/"mikkie_artistly_agent.py"), "stickers"],
             "Nacht Artistly stickers genereren"),

    # Dagrapport
    (23, 55, "dagrapport",        ["python3", str(BASE_DIR/"mikkie_engagement_logger.py"), "report"],
             "Dagelijks rapport via Telegram"),
]

# Wekelijkse taken (dag: [(uur, min, naam, commando, beschrijving)])
WEEKSCHEMA = {
    0: [  # Maandag
        (13, 0, "maandag_covers",    ["python3", str(BASE_DIR/"mikkie_artistly_agent.py"), "covers"],
               "Maandag: covers genereren voor alle 7 karakters"),
    ],
    1: [  # Dinsdag
        (13, 0, "dinsdag_coloring",  ["python3", str(BASE_DIR/"mikkie_artistly_agent.py"), "coloring"],
               "Dinsdag: kleurplaten genereren"),
    ],
    3: [  # Donderdag
        (13, 0, "donderdag_banners", ["python3", str(BASE_DIR/"mikkie_artistly_agent.py"), "banners"],
               "Donderdag: banners genereren"),
    ],
    6: [  # Zondag
        (10, 0, "zondag_rapport",    ["python3", str(BASE_DIR/"mikkie_engagement_logger.py"), "weekly"],
               "Zondag: weekrapport via Telegram"),
    ],
}

# ─── State management ─────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"last_run": {}, "stats": {"posts": 0, "images": 0, "sales": 0}}

def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))

def task_ran_today(task_name: str, state: dict) -> bool:
    today = datetime.now().strftime("%Y-%m-%d")
    return state.get("last_run", {}).get(task_name) == today

def mark_task_done(task_name: str, state: dict):
    state.setdefault("last_run", {})[task_name] = datetime.now().strftime("%Y-%m-%d")
    save_state(state)

# ─── Taak uitvoeren ───────────────────────────────────────────────────────────
def run_task(naam: str, commando: list, beschrijving: str, state: dict) -> bool:
    """Voer een taak uit en log het resultaat."""
    if task_ran_today(naam, state):
        log.info(f"⏭️  {naam} — al uitgevoerd vandaag, overgeslagen")
        return True

    log.info(f"▶️  {naam} — {beschrijving}")
    try:
        result = subprocess.run(
            commando,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minuten timeout
            cwd=str(BASE_DIR)
        )
        if result.returncode == 0:
            log.info(f"✅ {naam} — geslaagd")
            mark_task_done(naam, state)
            return True
        else:
            log.error(f"❌ {naam} — mislukt (code {result.returncode})")
            log.error(f"   stderr: {result.stderr[:200]}")
            telegram(f"⚠️ MIKKIE BRAIN\n<b>{naam}</b> mislukt\n{result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        log.error(f"⏰ {naam} — timeout na 5 minuten")
        telegram(f"⏰ MIKKIE BRAIN\n<b>{naam}</b> timeout")
        return False
    except FileNotFoundError:
        log.warning(f"⚠️  {naam} — script niet gevonden, overgeslagen")
        return True  # Niet als fout beschouwen
    except Exception as e:
        log.error(f"💥 {naam} — onverwachte fout: {e}")
        telegram(f"💥 MIKKIE BRAIN\n<b>{naam}</b> crash: {e}")
        return False

# ─── Dagelijkse routine ───────────────────────────────────────────────────────
def run_daily_routine(force: bool = False):
    """Voer alle taken uit die nu gepland zijn."""
    state = load_state()
    now   = datetime.now()
    dag   = now.weekday()  # 0=maandag, 6=zondag

    log.info(f"🧠 BRAIN check — {now.strftime('%A %d %B %H:%M')}")

    # Dagelijkse taken
    for uur, minuut, naam, commando, beschrijving in DAGSCHEMA:
        gepland = now.replace(hour=uur, minute=minuut, second=0, microsecond=0)
        # Voer uit als het tijd is (binnen 5 minuten window) of als force=True
        if force or (now >= gepland and now < gepland + timedelta(minutes=5)):
            run_task(naam, commando, beschrijving, state)

    # Wekelijkse taken voor vandaag
    for uur, minuut, naam, commando, beschrijving in WEEKSCHEMA.get(dag, []):
        gepland = now.replace(hour=uur, minute=minuut, second=0, microsecond=0)
        if force or (now >= gepland and now < gepland + timedelta(minutes=5)):
            run_task(naam, commando, beschrijving, state)

def run_all_now():
    """Voer de volledige dagelijkse routine nu direct uit (negeer tijden)."""
    state = load_state()
    now   = datetime.now()
    dag   = now.weekday()
    karakter = KARAKTER_SCHEMA[dag]

    log.info(f"🚀 BRAIN — Volledige dagelijkse routine starten")
    log.info(f"   Karakter van vandaag: {karakter}")
    telegram(f"🧠 MIKKIE BRAIN gestart\nKarakter: <b>{karakter}</b>\n{now.strftime('%A %d %B %H:%M')}")

    taken = [
        ("dagpost_1",   ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],      "Post #1 genereren"),
        ("dagpost_2",   ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],      "Post #2 genereren"),
        ("dagpost_3",   ["python3", str(BASE_DIR/"mikkie_post_draft.py"), "x"],      "Post #3 genereren"),
        ("gumroad",     ["python3", str(BASE_DIR/"mikkie_agent.py"),      "check"],  "Gumroad check"),
        ("rapport",     ["python3", str(BASE_DIR/"mikkie_engagement_logger.py"), "report"], "Dagrapport"),
    ]

    geslaagd = 0
    for naam, commando, beschrijving in taken:
        # Reset today-check voor force run
        state.setdefault("last_run", {})[naam] = ""
        save_state(state)
        if run_task(naam, commando, beschrijving, state):
            geslaagd += 1

    log.info(f"✅ Routine klaar: {geslaagd}/{len(taken)} taken geslaagd")
    telegram(f"✅ MIKKIE BRAIN klaar\n{geslaagd}/{len(taken)} taken geslaagd")

# ─── Daemon loop ──────────────────────────────────────────────────────────────
def daemon_loop():
    """Hoofdloop — controleert elke minuut of er taken uitgevoerd moeten worden."""
    log.info("🧠 MIKKIE BRAIN daemon gestart")
    telegram("🧠 MIKKIE BRAIN\nDaemon gestart — 24/7 actief")

    # Graceful shutdown
    def shutdown(sig, frame):
        log.info("🛑 BRAIN daemon gestopt")
        telegram("🛑 MIKKIE BRAIN gestopt")
        if PID_FILE.exists():
            PID_FILE.unlink()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        try:
            run_daily_routine()
        except Exception as e:
            log.error(f"💥 BRAIN loop fout: {e}")
            telegram(f"💥 MIKKIE BRAIN loop fout: {e}")
        time.sleep(60)  # Check elke minuut

# ─── Start / Stop ─────────────────────────────────────────────────────────────
def start_daemon():
    """Start de BRAIN als achtergrond daemon."""
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, 0)
            print(c(f"⚠️  BRAIN draait al (PID {pid})", YELLOW))
            return
        except ProcessLookupError:
            PID_FILE.unlink()

    # Fork naar achtergrond
    pid = os.fork()
    if pid > 0:
        # Parent process
        PID_FILE.write_text(str(pid))
        print(c(f"🧠 BRAIN gestart (PID {pid})", GREEN))
        print(c(f"   Log: {LOG_FILE}", CYAN))
        print(c(f"   Stop: python3 mikkie_brain.py stop", CYAN))
        return

    # Child process — wordt de daemon
    os.setsid()
    daemon_loop()

def stop_daemon():
    """Stop de BRAIN daemon."""
    if not PID_FILE.exists():
        print(c("⚠️  BRAIN draait niet", YELLOW))
        return

    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        print(c(f"🛑 BRAIN gestopt (PID {pid})", RED))
    except ProcessLookupError:
        PID_FILE.unlink()
        print(c("⚠️  BRAIN was al gestopt", YELLOW))

def show_status():
    """Toon de huidige status en het volgende geplande taak."""
    now = datetime.now()
    dag = now.weekday()
    karakter = KARAKTER_SCHEMA[dag]
    state = load_state()

    # Check of daemon draait
    daemon_status = c("○ GESTOPT", RED)
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, 0)
            daemon_status = c(f"● ACTIEF (PID {pid})", GREEN)
        except ProcessLookupError:
            PID_FILE.unlink()

    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  🧠 MIKKIE WORLD BRAIN — {now.strftime('%A %d %B %H:%M')}")
    print(f"{'═'*60}{RESET}")
    print(f"  Status:     {daemon_status}")
    print(f"  Karakter:   {c(karakter, PURPLE)}")
    print(f"  Posts:      {state.get('stats', {}).get('posts', 0)} gegenereerd")
    print(f"  Afbeeldingen: {state.get('stats', {}).get('images', 0)} gegenereerd")

    # Volgende taak
    print(f"\n  {BOLD}📅 Volgende geplande taken:{RESET}")
    for uur, minuut, naam, _, beschrijving in DAGSCHEMA:
        gepland = now.replace(hour=uur, minute=minuut, second=0, microsecond=0)
        if gepland > now:
            delta = gepland - now
            uren  = int(delta.total_seconds() // 3600)
            mins  = int((delta.total_seconds() % 3600) // 60)
            al_gedaan = task_ran_today(naam, state)
            status = c("✓ gedaan", GREEN) if al_gedaan else c(f"over {uren}u {mins}m", CYAN)
            print(f"  {gepland.strftime('%H:%M')}  {beschrijving:<45} {status}")
            if not al_gedaan:
                break  # Toon alleen de eerstvolgende

    print(f"\n  {BOLD}📋 Commando's:{RESET}")
    print(f"  python3 mikkie_brain.py start     → Start 24/7 daemon")
    print(f"  python3 mikkie_brain.py stop      → Stop daemon")
    print(f"  python3 mikkie_brain.py run now   → Alles nu uitvoeren")
    print(f"  python3 mikkie_brain.py schedule  → Volledig weekschema")
    print(f"{'═'*60}\n")

def show_schedule():
    """Toon het volledige weekschema."""
    dagen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  🧠 MIKKIE WORLD BRAIN — Weekschema")
    print(f"{'═'*60}{RESET}")

    for dag_nr, dag_naam in enumerate(dagen):
        karakter = KARAKTER_SCHEMA[dag_nr]
        print(f"\n  {BOLD}{dag_naam} — {c(karakter, PURPLE)}{RESET}")
        for uur, minuut, naam, _, beschrijving in DAGSCHEMA[:6]:  # Toon eerste 6 dagelijkse taken
            print(f"    {uur:02d}:{minuut:02d}  {beschrijving}")
        for uur, minuut, naam, _, beschrijving in WEEKSCHEMA.get(dag_nr, []):
            print(f"    {uur:02d}:{minuut:02d}  {c(beschrijving, YELLOW)} (wekelijks)")

    print(f"\n{'═'*60}\n")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "status":
        show_status()
    elif args[0] == "start":
        start_daemon()
    elif args[0] == "stop":
        stop_daemon()
    elif args[0] == "run" and len(args) > 1 and args[1] == "now":
        run_all_now()
    elif args[0] == "schedule":
        show_schedule()
    elif args[0] == "loop":
        # Direct in foreground draaien (voor launchd)
        daemon_loop()
    else:
        print(f"Gebruik: python3 mikkie_brain.py [start|stop|status|run now|schedule]")
