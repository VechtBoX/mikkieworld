#!/usr/bin/env python3
"""
MIKKIE WORLD — Site Agent
=========================
Lokale agent die de live mikkie.world website monitort en data synchroniseert.
Geen Manus sessie nodig voor dagelijkse monitoring en rapportage.

Commando's:
  python3 mikkie_site_agent.py status       — Volledige site status (health + Wall + signups)
  python3 mikkie_site_agent.py health       — Snelle health check (database, SMTP, Stripe, XRPL)
  python3 mikkie_site_agent.py wall         — Wall statistieken (claims, rarity, XRP)
  python3 mikkie_site_agent.py signups      — Pre-launch signups overzicht
  python3 mikkie_site_agent.py countdown    — Countdown tot lancering 7 juli 2026
  python3 mikkie_site_agent.py watch        — Live monitor (elke 5 min refresh)
  python3 mikkie_site_agent.py report       — Dagrapport genereren + opslaan

Tagline: Blijf Altijd Kind. Met je kids. | Always Be a Kid. With your kids.
"""

import sys
import json
import time
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuratie ───────────────────────────────────────────────────────────
BASE_URL    = "https://mikkie.world"
LAUNCH_DATE = datetime(2026, 7, 7, 7, 7, 0, tzinfo=timezone.utc)
BASE_DIR    = Path(__file__).parent
LOGS_DIR    = Path.home() / "MIKKIE_WORLD" / "LOGS"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ANSI kleuren
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
GOLD   = "\033[33m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
CYAN   = "\033[96m"

# ─── HTTP helpers ────────────────────────────────────────────────────────────
def get_json(path: str, timeout: int = 10) -> dict:
    """GET request naar de live website API."""
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "User-Agent": "MikkieWorldSiteAgent/1.0 (mikkie.world)",
            })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"Verbindingsfout: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}

def trpc_get(procedure: str, timeout: int = 10) -> dict:
    """tRPC GET query."""
    return get_json(f"/api/trpc/{procedure}", timeout)

# ─── Health Check ────────────────────────────────────────────────────────────
def cmd_health(verbose: bool = True) -> dict:
    """Controleer alle services op de live website."""
    if verbose:
        print(f"\n{BOLD}🏥 MIKKIE WORLD — Health Check{RESET}")
        print(f"   {CYAN}{BASE_URL}{RESET}")
        print(f"   {datetime.now().strftime('%d %b %Y %H:%M:%S')}\n")

    data = get_json("/api/health")

    if "error" in data:
        if verbose:
            print(f"   {RED}❌ Site onbereikbaar: {data['error']}{RESET}")
        return {"status": "down", "error": data["error"]}

    status   = data.get("status", "unknown")
    services = data.get("services", {})
    version  = data.get("version", "?")

    if verbose:
        icon = f"{GREEN}✅" if status == "healthy" else f"{RED}❌"
        print(f"   {icon} Status: {BOLD}{status.upper()}{RESET}  (v{version})")
        print()

        service_icons = {
            "database": "🗄️ ",
            "smtp":     "📧",
            "stripe":   "💳",
            "xrpl":     "🔗",
            "gelato":   "🛒",
        }

        for svc, info in services.items():
            svc_status  = info.get("status", "unknown")
            latency     = info.get("latencyMs", "?")
            icon_svc    = service_icons.get(svc, "🔧")
            color       = GREEN if svc_status == "ok" else RED
            latency_col = GREEN if isinstance(latency, int) and latency < 500 else YELLOW
            print(f"   {icon_svc} {svc:<12} {color}{svc_status:<8}{RESET}  {latency_col}{latency}ms{RESET}")

    return {"status": status, "services": services, "version": version}

# ─── Wall Statistieken ───────────────────────────────────────────────────────
def cmd_wall(verbose: bool = True) -> dict:
    """Haal Wall statistieken op van de live website."""
    if verbose:
        print(f"\n{BOLD}🧱 MIKKIE Wall — Statistieken{RESET}")
        print(f"   Lancering: 7 juli 2026 | 777 tegels\n")

    data = trpc_get("wall.getStats")

    if "error" in data:
        if verbose:
            print(f"   {RED}❌ Fout: {data['error']}{RESET}")
        return {}

    result = data.get("result", {}).get("data", {}).get("json", {})

    claimed   = result.get("claimed", 0)
    total     = result.get("total", 777)
    available = result.get("available", 777)
    total_xrp = result.get("totalXrp", 0)
    rarity    = result.get("rarityBreakdown", {})

    pct = (claimed / total * 100) if total > 0 else 0
    bar_len = 30
    filled  = int(bar_len * pct / 100)
    bar     = f"{GREEN}{'█' * filled}{RESET}{'░' * (bar_len - filled)}"

    if verbose:
        print(f"   {bar}  {BOLD}{pct:.1f}%{RESET} verkocht")
        print()
        print(f"   🟢 Verkocht:    {BOLD}{claimed}{RESET} / {total} tegels")
        print(f"   ⬜ Beschikbaar: {BOLD}{available}{RESET} tegels")
        print(f"   💰 XRP omzet:   {BOLD}{total_xrp:,.0f} XRP{RESET}")
        print()

        rarity_labels = {
            "special":  ("1/1 Special",  "🌟"),
            "legendary":("Legendary",    "⚡"),
            "epic":     ("Epic",         "🔥"),
            "rare":     ("Rare",         "💎"),
            "uncommon": ("Uncommon",     "🔵"),
            "common":   ("Common",       "⚪"),
        }

        if rarity:
            print(f"   {BOLD}Rarity verdeling:{RESET}")
            for key, (label, icon) in rarity_labels.items():
                count = rarity.get(key, 0)
                if count > 0:
                    print(f"   {icon} {label:<14} {GOLD}{count}{RESET} tegels")

    return {
        "claimed": claimed,
        "total": total,
        "available": available,
        "totalXrp": total_xrp,
        "pct": round(pct, 1),
    }

# ─── Countdown ───────────────────────────────────────────────────────────────
def cmd_countdown(verbose: bool = True) -> dict:
    """Countdown tot lancering 7 juli 2026."""
    now   = datetime.now(timezone.utc)
    delta = LAUNCH_DATE - now

    if delta.total_seconds() < 0:
        if verbose:
            print(f"\n   {GREEN}{BOLD}🚀 MIKKIE WORLD IS GELANCEERD!{RESET}")
        return {"launched": True}

    days    = delta.days
    hours   = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60

    if verbose:
        print(f"\n{BOLD}⏳ Countdown tot lancering{RESET}")
        print(f"   7 juli 2026 — 07:07 uur\n")
        print(f"   {GOLD}{BOLD}{days}{RESET} dagen  "
              f"{GOLD}{BOLD}{hours:02d}{RESET} uur  "
              f"{GOLD}{BOLD}{minutes:02d}{RESET} min  "
              f"{GOLD}{BOLD}{seconds:02d}{RESET} sec")
        print()

        urgency = ""
        if days < 7:
            urgency = f"   {RED}{BOLD}⚠️  Minder dan een week! Final sprint!{RESET}"
        elif days < 14:
            urgency = f"   {YELLOW}⚡ Twee weken te gaan — alles live testen!{RESET}"
        elif days < 30:
            urgency = f"   {CYAN}📅 Bijna een maand — focus op Wall en marketing{RESET}"
        if urgency:
            print(urgency)

    return {"days": days, "hours": hours, "minutes": minutes, "launched": False}

# ─── Volledige Status ────────────────────────────────────────────────────────
def cmd_status():
    """Volledige site status — health + Wall + countdown."""
    print(f"\n{'═' * 55}")
    print(f"  {GOLD}{BOLD}MIKKIE WORLD — Site Dashboard{RESET}")
    print(f"  Blijf Altijd Kind. Met je kids.")
    print(f"{'═' * 55}")

    health_data   = cmd_health(verbose=True)
    print(f"\n{'─' * 55}")
    wall_data     = cmd_wall(verbose=True)
    print(f"\n{'─' * 55}")
    countdown_data = cmd_countdown(verbose=True)
    print(f"{'═' * 55}\n")

    # Samenvatting
    site_ok  = health_data.get("status") == "healthy"
    claimed  = wall_data.get("claimed", 0)
    days     = countdown_data.get("days", "?")

    print(f"  {BOLD}Samenvatting:{RESET}")
    print(f"  {'✅' if site_ok else '❌'} Site: {'online' if site_ok else 'OFFLINE'}")
    print(f"  🧱 Wall: {claimed}/777 tegels verkocht")
    print(f"  ⏳ Lancering: nog {days} dagen")
    print()

# ─── Watch Mode ──────────────────────────────────────────────────────────────
def cmd_watch():
    """Live monitor — refresh elke 5 minuten."""
    print(f"\n{BOLD}👁️  Watch mode gestart — refresh elke 5 minuten{RESET}")
    print(f"   Druk Ctrl+C om te stoppen\n")

    try:
        while True:
            os.system("clear")
            cmd_status()
            print(f"   {CYAN}Volgende refresh over 5 minuten...{RESET}")
            time.sleep(300)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Watch mode gestopt.{RESET}\n")

# ─── Dagrapport ──────────────────────────────────────────────────────────────
def cmd_report():
    """Genereer een dagrapport en sla het op."""
    now      = datetime.now()
    filename = LOGS_DIR / f"site_rapport_{now.strftime('%Y%m%d_%H%M')}.txt"

    health_data    = cmd_health(verbose=False)
    wall_data      = cmd_wall(verbose=False)
    countdown_data = cmd_countdown(verbose=False)

    lines = [
        "MIKKIE WORLD — Site Dagrapport",
        f"Datum: {now.strftime('%d %b %Y %H:%M')}",
        "=" * 50,
        "",
        "HEALTH",
        f"  Status:     {health_data.get('status', 'unknown').upper()}",
        f"  Versie:     {health_data.get('version', '?')}",
        "",
    ]

    services = health_data.get("services", {})
    for svc, info in services.items():
        lines.append(f"  {svc:<12} {info.get('status','?'):<8}  {info.get('latencyMs','?')}ms")

    lines += [
        "",
        "WALL",
        f"  Verkocht:   {wall_data.get('claimed', 0)} / {wall_data.get('total', 777)} tegels",
        f"  Beschikbaar:{wall_data.get('available', 777)} tegels",
        f"  XRP omzet:  {wall_data.get('totalXrp', 0):,.0f} XRP",
        f"  Voortgang:  {wall_data.get('pct', 0):.1f}%",
        "",
        "LANCERING",
        f"  Datum:      7 juli 2026 07:07",
        f"  Nog:        {countdown_data.get('days', '?')} dagen",
        "",
        "─" * 50,
        "Blijf Altijd Kind. Met je kids.",
        "mikkie.world",
    ]

    report_text = "\n".join(lines)
    filename.write_text(report_text, encoding="utf-8")

    print(f"\n{GREEN}✅ Dagrapport opgeslagen:{RESET}")
    print(f"   {filename}")
    print()
    print(report_text)

# ─── Help ────────────────────────────────────────────────────────────────────
def cmd_help():
    print(f"""
{GOLD}{BOLD}MIKKIE WORLD — Site Agent{RESET}
{CYAN}Blijf Altijd Kind. Met je kids.{RESET}

Gebruik:
  python3 mikkie_site_agent.py <commando>

Commando's:
  status      Volledige site status (health + Wall + countdown)
  health      Snelle health check (database, SMTP, Stripe, XRPL)
  wall        Wall statistieken (claims, rarity, XRP omzet)
  countdown   Countdown tot lancering 7 juli 2026
  watch       Live monitor (elke 5 min refresh)
  report      Dagrapport genereren + opslaan in LOGS/

Alias (na git pull):
  mikkie-site status
  mikkie-site wall
  mikkie-site watch
""")

# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        cmd_status()
    elif cmd == "health":
        cmd_health()
    elif cmd == "wall":
        cmd_wall()
    elif cmd == "countdown":
        cmd_countdown()
    elif cmd == "watch":
        cmd_watch()
    elif cmd == "report":
        cmd_report()
    elif cmd in ("help", "--help", "-h"):
        cmd_help()
    else:
        print(f"{RED}Onbekend commando: {cmd}{RESET}")
        cmd_help()
