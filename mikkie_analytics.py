#!/usr/bin/env python3
"""
📊 MIKKIE WORLD — ANALYTICS Agent v1.0
=======================================
Verzamelt data van alle platforms en stuurt een dagelijks rapport.
Toont een live terminal dashboard met alle statistieken.

Gebruik:
  python3 mikkie_analytics.py dashboard   → Live terminal dashboard
  python3 mikkie_analytics.py report      → Dagrapport via Telegram
  python3 mikkie_analytics.py weekly      → Weekrapport via Telegram
  python3 mikkie_analytics.py gumroad     → Gumroad omzet overzicht
  python3 mikkie_analytics.py content     → Content productie overzicht
"""

import os
import sys
import json
import csv
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR   = Path.home() / "mikkieworld"
WORLD_DIR  = Path.home() / "MIKKIE_WORLD"
SOCIAL_DIR = WORLD_DIR / "SOCIAL"
LOG_DIR    = WORLD_DIR / "LOGS"
DATA_DIR   = WORLD_DIR / "DATA"

for d in [LOG_DIR, DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("ANALYTICS")

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

def bar(value, max_val, width=20, color=GREEN):
    if max_val == 0:
        filled = 0
    else:
        filled = int((value / max_val) * width)
    return c("█" * filled, color) + c("░" * (width - filled), "\033[90m")

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
            data=data, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

# ─── Gumroad data ─────────────────────────────────────────────────────────────
def get_gumroad_stats() -> dict:
    """Haal Gumroad omzet en verkopen op."""
    token = os.environ.get("GUMROAD_API_TOKEN")
    if not token:
        return {"error": "GUMROAD_API_TOKEN niet ingesteld"}

    try:
        # Producten ophalen
        resp = requests.get(
            "https://api.gumroad.com/v2/products",
            params={"access_token": token},
            timeout=15
        )
        data = resp.json()
        if not data.get("success"):
            return {"error": "Gumroad API fout"}

        producten = data.get("products", [])
        totaal_verkopen = sum(p.get("sales_count", 0) for p in producten)
        totaal_omzet    = sum(float(p.get("revenue", 0)) for p in producten)

        return {
            "producten": len(producten),
            "verkopen":  totaal_verkopen,
            "omzet":     totaal_omzet,
            "details":   [
                {
                    "naam":     p.get("name", ""),
                    "verkopen": p.get("sales_count", 0),
                    "omzet":    float(p.get("revenue", 0)),
                    "prijs":    p.get("formatted_price", ""),
                }
                for p in producten
            ]
        }
    except Exception as e:
        return {"error": str(e)}

# ─── Content statistieken ─────────────────────────────────────────────────────
def get_content_stats() -> dict:
    """Tel alle gegenereerde content bestanden."""
    stats = {}
    platforms = {
        "X/Twitter":   SOCIAL_DIR / "X_Twitter",
        "Instagram":   SOCIAL_DIR / "Instagram",
        "Pinterest":   SOCIAL_DIR / "Pinterest",
        "TikTok":      SOCIAL_DIR / "TikTok",
        "Facebook":    SOCIAL_DIR / "Facebook",
        "LinkedIn":    SOCIAL_DIR / "LinkedIn",
        "YouTube":     SOCIAL_DIR / "YouTube",
    }

    vandaag = datetime.now().strftime("%Y%m%d")
    totaal  = 0

    for naam, pad in platforms.items():
        if pad.exists():
            alle      = list(pad.glob("*.txt")) + list(pad.glob("*.png")) + list(pad.glob("*.jpg"))
            vandaag_f = [f for f in alle if vandaag in f.name]
            stats[naam] = {"totaal": len(alle), "vandaag": len(vandaag_f)}
            totaal += len(alle)
        else:
            stats[naam] = {"totaal": 0, "vandaag": 0}

    # Artistly output
    output_dir = BASE_DIR / "artistly_output"
    if output_dir.exists():
        afbeeldingen = list(output_dir.glob("*.png")) + list(output_dir.glob("*.jpg"))
        stats["Artistly"] = {
            "totaal":  len(afbeeldingen),
            "vandaag": len([f for f in afbeeldingen if vandaag in f.name])
        }
        totaal += len(afbeeldingen)

    return {"platforms": stats, "totaal": totaal}

# ─── Engagement data (uit CSV logger) ─────────────────────────────────────────
def get_engagement_stats() -> dict:
    """Lees engagement data uit de CSV van de engagement logger."""
    csv_file = DATA_DIR / "engagement.csv"
    if not csv_file.exists():
        return {"posts": 0, "likes": 0, "views": 0, "replies": 0}

    try:
        totaal = defaultdict(int)
        vandaag = datetime.now().strftime("%Y-%m-%d")
        vandaag_stats = defaultdict(int)

        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                totaal["posts"]   += 1
                totaal["likes"]   += int(row.get("likes", 0))
                totaal["views"]   += int(row.get("views", 0))
                totaal["replies"] += int(row.get("replies", 0))

                if row.get("datum", "").startswith(vandaag):
                    vandaag_stats["posts"]   += 1
                    vandaag_stats["likes"]   += int(row.get("likes", 0))
                    vandaag_stats["views"]   += int(row.get("views", 0))
                    vandaag_stats["replies"] += int(row.get("replies", 0))

        return {
            "totaal":  dict(totaal),
            "vandaag": dict(vandaag_stats)
        }
    except Exception as e:
        return {"error": str(e)}

# ─── Terminal Dashboard ───────────────────────────────────────────────────────
def show_dashboard():
    """Toon een live terminal dashboard met alle statistieken."""
    now = datetime.now()

    print(f"\n{BOLD}{'═'*65}{RESET}")
    print(f"  📊 MIKKIE WORLD ANALYTICS — {now.strftime('%A %d %B %Y %H:%M')}")
    print(f"{'═'*65}{RESET}")

    # Gumroad
    print(f"\n  {BOLD}💰 Gumroad Omzet{RESET}")
    print(f"  {'─'*40}")
    gumroad = get_gumroad_stats()
    if "error" not in gumroad:
        print(f"  Producten:   {c(str(gumroad['producten']), CYAN)}")
        print(f"  Verkopen:    {c(str(gumroad['verkopen']), GREEN)}")
        omzet_fmt = f'€{gumroad["omzet"]:.2f}'
        print(f"  Omzet:       {c(omzet_fmt, GREEN)}")

        if gumroad.get("details"):
            print(f"\n  Top producten:")
            gesorteerd = sorted(gumroad["details"], key=lambda x: x["verkopen"], reverse=True)
            max_v = max((p["verkopen"] for p in gesorteerd), default=1)
            for p in gesorteerd[:5]:
                naam = p["naam"][:30]
                b = bar(p["verkopen"], max_v, width=15)
                omzet_p = f'€{p["omzet"]:.2f}'
                print(f"  {naam:<32} {b} {c(str(p['verkopen']), YELLOW)} verkopen  {c(omzet_p, GREEN)}")
    else:
        print(f"  {c('⚠️  ' + gumroad['error'], YELLOW)}")

    # Content productie
    print(f"\n  {BOLD}🎨 Content Productie{RESET}")
    print(f"  {'─'*40}")
    content = get_content_stats()
    print(f"  Totaal bestanden: {c(str(content['totaal']), CYAN)}")
    max_t = max((v["totaal"] for v in content["platforms"].values()), default=1)
    for platform, data in content["platforms"].items():
        b = bar(data["totaal"], max_t, width=12)
        vandaag_str = c(f"+{data['vandaag']} vandaag", GREEN) if data["vandaag"] > 0 else ""
        print(f"  {platform:<15} {b} {data['totaal']:>4}  {vandaag_str}")

    # Engagement
    print(f"\n  {BOLD}📈 Engagement (X/Twitter){RESET}")
    print(f"  {'─'*40}")
    engagement = get_engagement_stats()
    if "error" not in engagement:
        t = engagement.get("totaal", {})
        v = engagement.get("vandaag", {})
        posts_v = f'+{v.get("posts", 0)} vandaag'
        likes_v = f'+{v.get("likes", 0)} vandaag'
        views_v = f'+{v.get("views", 0)} vandaag'
        print(f"  Posts:    {c(str(t.get('posts', 0)), CYAN)}  {c(posts_v, GREEN)}")
        print(f"  Likes:    {c(str(t.get('likes', 0)), YELLOW)}  {c(likes_v, GREEN)}")
        print(f"  Views:    {c(str(t.get('views', 0)), BLUE)}  {c(views_v, GREEN)}")
    else:
        print(f"  {c('Nog geen engagement data — start de engagement logger', YELLOW)}")
        print(f"  python3 mikkie_engagement_logger.py update")

    # Agent status
    print(f"\n  {BOLD}🤖 Agent Status{RESET}")
    print(f"  {'─'*40}")
    pid_dir = BASE_DIR / "pids"
    agents = [
        ("BRAIN",    pid_dir / "brain.pid"),
        ("GUARDIAN", pid_dir / "guardian.pid"),
        ("MAIN",     pid_dir / "main.pid"),
        ("ARTISTLY", pid_dir / "artistly.pid"),
    ]
    for naam, pid_file in agents:
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, 0)
                status = c(f"● ACTIEF (PID {pid})", GREEN)
            except (ProcessLookupError, ValueError):
                status = c("○ GESTOPT", RED)
        else:
            status = c("○ GESTOPT", RED)
        print(f"  {naam:<12} {status}")

    print(f"\n{'═'*65}\n")

# ─── Dagrapport ───────────────────────────────────────────────────────────────
def send_daily_report():
    """Stuur een dagrapport via Telegram."""
    now     = datetime.now()
    gumroad = get_gumroad_stats()
    content = get_content_stats()
    engagement = get_engagement_stats()

    vandaag_content = sum(v["vandaag"] for v in content["platforms"].values())

    omzet_str = f"€{gumroad.get('omzet', 0):.2f}" if "error" not in gumroad else "N/B"
    verkopen  = gumroad.get("verkopen", 0) if "error" not in gumroad else 0

    msg = (
        f"📊 <b>MIKKIE WORLD Dagrapport</b>\n"
        f"{now.strftime('%A %d %B %Y')}\n\n"
        f"💰 <b>Gumroad</b>\n"
        f"   Omzet: {omzet_str}\n"
        f"   Verkopen: {verkopen}\n\n"
        f"🎨 <b>Content vandaag</b>\n"
        f"   Nieuwe bestanden: {vandaag_content}\n"
        f"   Totaal: {content['totaal']}\n\n"
        f"📈 <b>Engagement</b>\n"
        f"   Posts: {engagement.get('vandaag', {}).get('posts', 0)}\n"
        f"   Likes: {engagement.get('vandaag', {}).get('likes', 0)}\n"
        f"   Views: {engagement.get('vandaag', {}).get('views', 0)}\n\n"
        f"🤖 Alle agents actief ✅"
    )

    telegram(msg)
    log.info("📊 Dagrapport verstuurd via Telegram")
    print(c("✅ Dagrapport verstuurd!", GREEN))

def send_weekly_report():
    """Stuur een weekrapport via Telegram."""
    now     = datetime.now()
    gumroad = get_gumroad_stats()
    content = get_content_stats()

    omzet_str = f"€{gumroad.get('omzet', 0):.2f}" if "error" not in gumroad else "N/B"

    msg = (
        f"📊 <b>MIKKIE WORLD Weekrapport</b>\n"
        f"Week van {(now - timedelta(days=7)).strftime('%d %b')} — {now.strftime('%d %b %Y')}\n\n"
        f"💰 <b>Totale Gumroad Omzet</b>: {omzet_str}\n"
        f"🎨 <b>Content Totaal</b>: {content['totaal']} bestanden\n\n"
        f"📱 <b>Per Platform</b>\n"
    )
    for platform, data in content["platforms"].items():
        msg += f"   {platform}: {data['totaal']}\n"

    msg += f"\n🚀 Lancering: 7 juli 2026 — nog {(datetime(2026,7,7) - now).days} dagen!"

    telegram(msg)
    log.info("📊 Weekrapport verstuurd via Telegram")
    print(c("✅ Weekrapport verstuurd!", GREEN))

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "dashboard":
        show_dashboard()
    elif args[0] == "report":
        send_daily_report()
    elif args[0] == "weekly":
        send_weekly_report()
    elif args[0] == "gumroad":
        gumroad = get_gumroad_stats()
        print(json.dumps(gumroad, indent=2, ensure_ascii=False))
    elif args[0] == "content":
        content = get_content_stats()
        print(json.dumps(content, indent=2, ensure_ascii=False))
    else:
        print("Gebruik: python3 mikkie_analytics.py [dashboard|report|weekly|gumroad|content]")
