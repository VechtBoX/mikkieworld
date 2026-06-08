#!/usr/bin/env python3
"""
🛡️ MIKKIE WORLD — GUARDIAN Watchdog v2.0
==========================================
Bewaakt alle MIKKIE WORLD daemons en herstart ze automatisch bij crashes.
Stuurt Telegram alert bij elke crash en herstart.
Bewaakt nu 15+ agents inclusief Pinterest, Suno, TikTok, Niche en Gumroad Bundle.

Gebruik:
  python3 mikkie_guardian.py start   → Start GUARDIAN daemon
  python3 mikkie_guardian.py stop    → Stop GUARDIAN daemon
  python3 mikkie_guardian.py status  → Toon status van alle bewuste processen
  python3 mikkie_guardian.py health  → Uitgebreide health check alle agents
  python3 mikkie_guardian.py list    → Toon alle geregistreerde agents
"""

import os
import sys
import json
import time
import signal
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# ─── Paden ────────────────────────────────────────────────────────────────────
BASE_DIR  = Path.home() / "mikkieworld"
LOG_DIR   = Path.home() / "MIKKIE_WORLD" / "LOGS"
PID_FILE  = BASE_DIR / "pids" / "guardian.pid"
LOG_FILE  = LOG_DIR / "guardian.log"

for d in [LOG_DIR, BASE_DIR / "pids"]:
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
log = logging.getLogger("GUARDIAN")

# ─── Kleuren ──────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"

def c(text, color): return f"{color}{text}{RESET}"

# ─── Telegram ─────────────────────────────────────────────────────────────────
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

# ─── Bewuste daemons ──────────────────────────────────────────────────────────
# (naam, pid_bestand, start_commando, max_crashes_per_uur)
DAEMONS = [
    (
        "BRAIN",
        BASE_DIR / "pids" / "brain.pid",
        ["python3", str(BASE_DIR / "mikkie_brain.py"), "loop"],
        3
    ),
    (
        "MAIN",
        BASE_DIR / "pids" / "main.pid",
        ["python3", str(BASE_DIR / "mikkie_agent.py"), "daemon"],
        3
    ),
    (
        "ARTISTLY",
        BASE_DIR / "pids" / "artistly.pid",
        ["python3", str(BASE_DIR / "mikkie_artistly_agent.py"), "daemon"],
        2
    ),
    (
        "TELEGRAM_COMMANDER",
        BASE_DIR / "pids" / "telegram_commander.pid",
        ["python3", str(BASE_DIR / "mikkie_telegram_commander.py")],
        3
    ),
    (
        "INSTAGRAM",
        BASE_DIR / "pids" / "instagram.pid",
        ["python3", str(BASE_DIR / "mikkie_instagram.py"), "daemon"],
        2
    ),
]

# ─── Alle agent bestanden (voor health check) ─────────────────────────────────
ALL_AGENTS = [
    {"name": "BRAIN",              "file": "mikkie_brain.py",             "daemon": True},
    {"name": "MAIN",               "file": "mikkie_agent.py",             "daemon": True},
    {"name": "ARTISTLY",           "file": "mikkie_artistly_agent.py",    "daemon": True},
    {"name": "TELEGRAM_COMMANDER", "file": "mikkie_telegram_commander.py","daemon": True},
    {"name": "INSTAGRAM",          "file": "mikkie_instagram.py",         "daemon": True},
    {"name": "GUARDIAN",           "file": "mikkie_guardian.py",          "daemon": True},
    {"name": "HEART",              "file": "mikkie_heart.py",             "daemon": False},
    {"name": "ANALYTICS",          "file": "mikkie_analytics.py",         "daemon": False},
    {"name": "BACKUP",             "file": "mikkie_backup.py",            "daemon": False},
    {"name": "REPURPOSE",          "file": "mikkie_repurpose.py",         "daemon": False},
    {"name": "POST_DRAFT",         "file": "mikkie_post_draft.py",        "daemon": False},
    {"name": "ASSET_PROMPT",       "file": "mikkie_asset_prompt.py",      "daemon": False},
    {"name": "ENGAGEMENT_LOGGER",  "file": "mikkie_engagement_logger.py", "daemon": False},
    {"name": "PINTEREST",          "file": "mikkie_pinterest.py",         "daemon": False},
    {"name": "SUNO",               "file": "mikkie_suno.py",              "daemon": False},
    {"name": "TIKTOK",             "file": "mikkie_tiktok.py",            "daemon": False},
    {"name": "NICHE",              "file": "mikkie_niche.py",             "daemon": False},
    {"name": "GUMROAD_BUNDLE",     "file": "mikkie_gumroad_bundle.py",    "daemon": False},
    {"name": "TWEET",              "file": "mikkie_tweet.py",             "daemon": False},
    {"name": "GUMROAD",            "file": "mikkie_gumroad.py",           "daemon": False},
    {"name": "DASHBOARD",          "file": "mikkie_dashboard.py",         "daemon": False},
    {"name": "CLI",                "file": "mikkie_cli.py",               "daemon": False},
]

# ─── Crash tracking ───────────────────────────────────────────────────────────
crash_counts = {}  # {naam: [(timestamp), ...]}

def is_running(pid_file: Path) -> bool:
    """Check of een daemon nog draait via zijn PID bestand."""
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, ValueError, OSError):
        return False

def start_daemon(naam: str, commando: list, pid_file: Path) -> Optional[int]:
    """Start een daemon als achtergrond proces."""
    try:
        proc = subprocess.Popen(
            commando,
            stdout=open(LOG_DIR / f"{naam.lower()}_stdout.log", "a"),
            stderr=open(LOG_DIR / f"{naam.lower()}_stderr.log", "a"),
            cwd=str(BASE_DIR),
            start_new_session=True
        )
        pid_file.write_text(str(proc.pid))
        log.info(f"▶️  {naam} gestart (PID {proc.pid})")
        return proc.pid
    except Exception as e:
        log.error(f"❌ {naam} start mislukt: {e}")
        return None

def too_many_crashes(naam: str, max_per_uur: int) -> bool:
    """Check of een daemon te vaak gecrasht is in het afgelopen uur."""
    now = time.time()
    crashes = crash_counts.get(naam, [])
    # Houd alleen crashes van het afgelopen uur bij
    crashes = [t for t in crashes if now - t < 3600]
    crash_counts[naam] = crashes
    return len(crashes) >= max_per_uur

def record_crash(naam: str):
    crash_counts.setdefault(naam, []).append(time.time())

# ─── Guardian loop ────────────────────────────────────────────────────────────
def guardian_loop():
    """Hoofdloop — controleert elke 30 seconden alle daemons."""
    log.info("🛡️  GUARDIAN gestart — bewaakt alle MIKKIE WORLD daemons")
    telegram("🛡️ MIKKIE GUARDIAN\nActief — bewaakt alle daemons")

    def shutdown(sig, frame):
        log.info("🛑 GUARDIAN gestopt")
        telegram("🛑 MIKKIE GUARDIAN gestopt")
        if PID_FILE.exists():
            PID_FILE.unlink()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        for naam, pid_file, commando, max_crashes in DAEMONS:
            if not is_running(pid_file):
                # Daemon is gecrasht of gestopt
                if too_many_crashes(naam, max_crashes):
                    log.error(f"🚨 {naam} — te veel crashes, niet herstarten")
                    telegram(
                        f"🚨 GUARDIAN ALARM\n"
                        f"<b>{naam}</b> gecrasht {max_crashes}x in 1 uur\n"
                        f"Handmatige actie vereist!\n"
                        f"Controleer: ~/MIKKIE_WORLD/LOGS/{naam.lower()}_stderr.log"
                    )
                    continue

                record_crash(naam)
                crash_nr = len(crash_counts.get(naam, []))
                log.warning(f"⚠️  {naam} gecrasht (#{crash_nr}) — herstarten...")
                telegram(
                    f"⚠️ GUARDIAN\n"
                    f"<b>{naam}</b> gecrasht (#{crash_nr})\n"
                    f"Herstarten..."
                )

                new_pid = start_daemon(naam, commando, pid_file)
                if new_pid:
                    telegram(f"✅ GUARDIAN\n<b>{naam}</b> herstart (PID {new_pid})")
                else:
                    telegram(f"❌ GUARDIAN\n<b>{naam}</b> herstart MISLUKT")

        time.sleep(30)  # Check elke 30 seconden

# ─── Start / Stop ─────────────────────────────────────────────────────────────
def start():
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        try:
            os.kill(pid, 0)
            print(c(f"⚠️  GUARDIAN draait al (PID {pid})", YELLOW))
            return
        except ProcessLookupError:
            PID_FILE.unlink()

    pid = os.fork()
    if pid > 0:
        PID_FILE.write_text(str(pid))
        print(c(f"🛡️  GUARDIAN gestart (PID {pid})", GREEN))
        print(c(f"   Log: {LOG_FILE}", CYAN))
        return

    os.setsid()
    guardian_loop()

def stop():
    if not PID_FILE.exists():
        print(c("⚠️  GUARDIAN draait niet", YELLOW))
        return
    pid = int(PID_FILE.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        print(c(f"🛑 GUARDIAN gestopt (PID {pid})", RED))
    except ProcessLookupError:
        PID_FILE.unlink()
        print(c("⚠️  GUARDIAN was al gestopt", YELLOW))

def status():
    now = datetime.now()
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  🛡️  MIKKIE GUARDIAN — {now.strftime('%H:%M:%S')}")
    print(f"{'═'*60}{RESET}")

    # Guardian zelf
    g_status = c("○ GESTOPT", RED)
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            g_status = c(f"● ACTIEF (PID {pid})", GREEN)
        except (ProcessLookupError, ValueError):
            PID_FILE.unlink()
    print(f"  GUARDIAN    {g_status}")
    print()

    # Bewuste daemons
    for naam, pid_file, _, max_crashes in DAEMONS:
        running = is_running(pid_file)
        crashes = len(crash_counts.get(naam, []))
        if running:
            pid = int(pid_file.read_text().strip())
            s = c(f"● ACTIEF (PID {pid})", GREEN)
        else:
            s = c("○ GESTOPT", RED)
        crash_info = f"  crashes: {crashes}/{max_crashes}" if crashes > 0 else ""
        print(f"  {naam:<12} {s}{crash_info}")

    print(f"\n  Log bestanden:")
    for naam, _, _, _ in DAEMONS:
        log_f = LOG_DIR / f"{naam.lower()}_stderr.log"
        if log_f.exists():
            size = log_f.stat().st_size
            print(f"    {log_f.name:<30} {size:>8} bytes")

    print(f"\n{'═'*60}\n")

# Fix missing Optional import
from typing import Optional

def health():
    """Uitgebreide health check van alle 21 agents."""
    now = datetime.now()
    print(f"\n{BOLD}{'═'*70}{RESET}")
    print(f"  🛡️  MIKKIE GUARDIAN — HEALTH CHECK — {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  {len(ALL_AGENTS)} agents geregistreerd")
    print(f"{'═'*70}{RESET}\n")
    
    ok_count = 0
    missing_count = 0
    
    for agent in ALL_AGENTS:
        agent_file = BASE_DIR / agent["file"]
        exists = agent_file.exists()
        size = agent_file.stat().st_size if exists else 0
        daemon_label = "[DAEMON]" if agent["daemon"] else "[CLI]   "
        
        if exists:
            status_str = c(f"✅ OK ({size:,} bytes)", GREEN)
            ok_count += 1
        else:
            status_str = c("❌ ONTBREEKT", RED)
            missing_count += 1
        
        print(f"  {daemon_label} {agent['name']:<20} {status_str}")
    
    print(f"\n  {c(f'✅ {ok_count} agents aanwezig', GREEN)}")
    if missing_count > 0:
        print(f"  {c(f'❌ {missing_count} agents ontbreken', RED)}")
    print(f"{'═'*70}\n")
    
    # Stuur health report via Telegram
    telegram(f"🛡️ <b>GUARDIAN Health Check</b>\n✅ {ok_count}/{len(ALL_AGENTS)} agents aanwezig\n{'❌ ' + str(missing_count) + ' ontbreken!' if missing_count > 0 else '🟢 Alles in orde!'}")

def list_agents():
    """Toon alle geregistreerde agents."""
    print(f"\n{BOLD}🛡️  MIKKIE WORLD — Alle {len(ALL_AGENTS)} Agents{RESET}\n")
    
    daemons = [a for a in ALL_AGENTS if a["daemon"]]
    cli_agents = [a for a in ALL_AGENTS if not a["daemon"]]
    
    print(f"  {c('DAEMONS (altijd actief):', YELLOW)}")
    for a in daemons:
        print(f"    🔄 {a['name']:<20} {a['file']}")
    
    print(f"\n  {c('CLI AGENTS (op aanvraag):', CYAN)}")
    for a in cli_agents:
        print(f"    ⚡ {a['name']:<20} {a['file']}")
    
    print(f"\n  {c(f'Totaal: {len(ALL_AGENTS)} agents', GREEN)}\n")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "status":
        status()
    elif args[0] == "start":
        start()
    elif args[0] == "stop":
        stop()
    elif args[0] == "health":
        health()
    elif args[0] == "list":
        list_agents()
    else:
        print("Gebruik: python3 mikkie_guardian.py [start|stop|status|health|list]")
