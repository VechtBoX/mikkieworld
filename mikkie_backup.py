#!/usr/bin/env python3
"""
💾 MIKKIE WORLD — BACKUP Agent v1.0
=====================================
Dagelijkse automatische backup van alle MIKKIE WORLD bestanden
naar iCloud Drive en GitHub. Nooit meer data verlies.

Backup strategie:
  - iCloud: ~/MIKKIE_WORLD/ → iCloud Drive/MIKKIE_WORLD/ (automatisch gesynchroniseerd)
  - GitHub: ~/mikkieworld/*.py → private repo (code backup)
  - Lokaal: ~/MIKKIE_WORLD/BACKUP/ → dagelijkse zip snapshot

Gebruik:
  python3 mikkie_backup.py run       → Voer volledige backup uit
  python3 mikkie_backup.py icloud    → Alleen iCloud sync
  python3 mikkie_backup.py github    → Alleen GitHub push
  python3 mikkie_backup.py zip       → Maak lokale zip snapshot
  python3 mikkie_backup.py status    → Toon backup status
  python3 mikkie_backup.py restore   → Toon herstel instructies
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path.home() / "mikkieworld"
WORLD_DIR   = Path.home() / "MIKKIE_WORLD"
BACKUP_DIR  = WORLD_DIR / "BACKUP"
LOG_DIR     = WORLD_DIR / "LOGS"
ICLOUD_DIR  = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "MIKKIE_WORLD"

for d in [BACKUP_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("BACKUP")

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
            data=data, headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

# ─── iCloud backup ────────────────────────────────────────────────────────────
def backup_icloud() -> dict:
    """
    Sync MIKKIE_WORLD naar iCloud Drive.
    iCloud Drive is automatisch gesynchroniseerd door macOS.
    We kopiëren de bestanden naar de iCloud map.
    """
    if not ICLOUD_DIR.parent.exists():
        return {"success": False, "error": "iCloud Drive niet gevonden. Is iCloud ingeschakeld?"}

    try:
        ICLOUD_DIR.mkdir(parents=True, exist_ok=True)

        # Gebruik rsync voor efficiënte sync (alleen gewijzigde bestanden)
        result = subprocess.run(
            [
                "rsync", "-av", "--delete",
                "--exclude=*.pyc",
                "--exclude=__pycache__",
                "--exclude=*.log",  # Logs niet naar iCloud
                str(WORLD_DIR) + "/",
                str(ICLOUD_DIR) + "/"
            ],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode == 0:
            # Tel gesynchroniseerde bestanden
            bestanden = list(ICLOUD_DIR.rglob("*"))
            bestanden = [f for f in bestanden if f.is_file()]
            log.info(f"✅ iCloud sync: {len(bestanden)} bestanden")
            return {"success": True, "bestanden": len(bestanden)}
        else:
            return {"success": False, "error": result.stderr[:200]}

    except FileNotFoundError:
        # rsync niet beschikbaar, gebruik cp
        try:
            shutil.copytree(
                str(WORLD_DIR), str(ICLOUD_DIR),
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("*.pyc", "__pycache__", "*.log")
            )
            return {"success": True, "methode": "cp"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── GitHub backup ────────────────────────────────────────────────────────────
def backup_github() -> dict:
    """Push alle agent code naar GitHub."""
    try:
        # Check of git repo bestaat
        git_dir = BASE_DIR / ".git"
        if not git_dir.exists():
            return {"success": False, "error": "Geen git repo gevonden in ~/mikkieworld"}

        # Git add + commit + push
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(BASE_DIR), capture_output=True, timeout=30
        )

        # Check of er iets te committen is
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=10
        )

        if not status.stdout.strip():
            log.info("GitHub: Geen wijzigingen om te committen")
            return {"success": True, "wijzigingen": 0}

        commit = subprocess.run(
            ["git", "commit", "-m", f"backup: automatische backup {timestamp}"],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=30
        )

        push = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=60
        )

        if push.returncode == 0:
            # Tel gewijzigde bestanden
            wijzigingen = len(status.stdout.strip().split("\n"))
            log.info(f"✅ GitHub push: {wijzigingen} bestanden")
            return {"success": True, "wijzigingen": wijzigingen}
        else:
            return {"success": False, "error": push.stderr[:200]}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Lokale zip snapshot ──────────────────────────────────────────────────────
def backup_zip() -> dict:
    """Maak een dagelijkse zip snapshot van alle MIKKIE WORLD bestanden."""
    try:
        datum     = datetime.now().strftime("%Y%m%d")
        zip_naam  = BACKUP_DIR / f"mikkie_world_backup_{datum}.zip"

        if zip_naam.exists():
            log.info(f"Zip backup van vandaag bestaat al: {zip_naam.name}")
            return {"success": True, "bestand": str(zip_naam), "nieuw": False}

        # Maak zip van WORLD_DIR (exclusief logs en grote bestanden)
        shutil.make_archive(
            str(BACKUP_DIR / f"mikkie_world_backup_{datum}"),
            "zip",
            str(Path.home()),
            "MIKKIE_WORLD"
        )

        grootte = zip_naam.stat().st_size / (1024 * 1024)  # MB
        log.info(f"✅ Zip backup: {zip_naam.name} ({grootte:.1f} MB)")

        # Verwijder backups ouder dan 7 dagen
        for oud_zip in BACKUP_DIR.glob("mikkie_world_backup_*.zip"):
            datum_str = oud_zip.stem.split("_")[-1]
            try:
                oud_datum = datetime.strptime(datum_str, "%Y%m%d")
                if (datetime.now() - oud_datum).days > 7:
                    oud_zip.unlink()
                    log.info(f"Oude backup verwijderd: {oud_zip.name}")
            except ValueError:
                pass

        return {"success": True, "bestand": str(zip_naam), "grootte_mb": round(grootte, 1)}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ─── Volledige backup ─────────────────────────────────────────────────────────
def run_full_backup():
    """Voer alle drie backup methodes uit."""
    now = datetime.now()
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  💾 MIKKIE WORLD BACKUP — {now.strftime('%d %B %Y %H:%M')}")
    print(f"{'─'*60}{RESET}")

    resultaten = {}

    # 1. GitHub
    print(f"\n  📦 GitHub backup...")
    github = backup_github()
    resultaten["github"] = github
    if github["success"]:
        w = github.get("wijzigingen", 0)
        print(c(f"  ✅ GitHub: {w} bestanden gepusht", GREEN))
    else:
        print(c(f"  ❌ GitHub: {github.get('error', 'Onbekend')}", RED))

    # 2. iCloud
    print(f"\n  ☁️  iCloud sync...")
    icloud = backup_icloud()
    resultaten["icloud"] = icloud
    if icloud["success"]:
        b = icloud.get("bestanden", "?")
        print(c(f"  ✅ iCloud: {b} bestanden gesynchroniseerd", GREEN))
    else:
        print(c(f"  ⚠️  iCloud: {icloud.get('error', 'Niet beschikbaar')}", YELLOW))

    # 3. Lokale zip
    print(f"\n  🗜️  Lokale zip snapshot...")
    zip_r = backup_zip()
    resultaten["zip"] = zip_r
    if zip_r["success"]:
        if zip_r.get("nieuw") is False:
            print(c(f"  ✅ Zip: Al aangemaakt vandaag", GREEN))
        else:
            print(c(f"  ✅ Zip: {zip_r.get('grootte_mb', '?')} MB opgeslagen", GREEN))
    else:
        print(c(f"  ❌ Zip: {zip_r.get('error', 'Onbekend')}", RED))

    # Samenvatting
    geslaagd = sum(1 for r in resultaten.values() if r.get("success"))
    print(f"\n{'─'*60}")
    print(f"  Backup: {geslaagd}/3 methodes geslaagd")
    print(f"{'═'*60}\n")

    # Telegram rapport
    telegram(
        f"💾 MIKKIE BACKUP\n"
        f"{now.strftime('%d %B %H:%M')}\n\n"
        f"{'✅' if resultaten['github']['success'] else '❌'} GitHub: "
        f"{resultaten['github'].get('wijzigingen', 0)} bestanden\n"
        f"{'✅' if resultaten['icloud']['success'] else '⚠️'} iCloud: "
        f"{resultaten['icloud'].get('bestanden', 'N/B')} bestanden\n"
        f"{'✅' if resultaten['zip']['success'] else '❌'} Zip: "
        f"{resultaten['zip'].get('grootte_mb', 'N/B')} MB\n\n"
        f"Backup: {geslaagd}/3 ✅"
    )

# ─── Status ───────────────────────────────────────────────────────────────────
def show_status():
    """Toon backup status en laatste backup tijden."""
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  💾 BACKUP Status")
    print(f"{'─'*60}{RESET}")

    # Lokale backups
    print(f"\n  Lokale zip backups:")
    zips = sorted(BACKUP_DIR.glob("*.zip"), reverse=True)
    if zips:
        for z in zips[:5]:
            grootte = z.stat().st_size / (1024 * 1024)
            datum   = datetime.fromtimestamp(z.stat().st_mtime)
            print(f"  {z.name:<45} {grootte:>6.1f} MB  {datum.strftime('%d %b %H:%M')}")
    else:
        print(f"  {c('Nog geen backups', YELLOW)}")

    # iCloud status
    print(f"\n  iCloud Drive:")
    if ICLOUD_DIR.exists():
        bestanden = list(ICLOUD_DIR.rglob("*"))
        bestanden = [f for f in bestanden if f.is_file()]
        print(c(f"  ✅ {len(bestanden)} bestanden gesynchroniseerd", GREEN))
    else:
        print(c(f"  ⚠️  iCloud map niet gevonden", YELLOW))
        print(f"  Verwacht: {ICLOUD_DIR}")

    # GitHub status
    print(f"\n  GitHub:")
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            cwd=str(BASE_DIR), capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                print(f"  {c(line, CYAN)}")
        else:
            print(c("  ⚠️  Git log niet beschikbaar", YELLOW))
    except Exception:
        print(c("  ⚠️  Git niet beschikbaar", YELLOW))

    print(f"\n{'═'*60}\n")

def show_restore():
    """Toon herstel instructies."""
    print(f"""
{BOLD}{'═'*60}{RESET}
  💾 BACKUP Herstel Instructies
{'═'*60}{RESET}

  Methode 1: GitHub (aanbevolen voor code)
  ─────────────────────────────────────────
  cd ~
  git clone https://github.com/VechtBoX/mikkieworld.git
  cd mikkieworld && pip3 install openai xai-sdk requests

  Methode 2: iCloud (voor content bestanden)
  ──────────────────────────────────────────
  cp -r ~/Library/Mobile\\ Documents/com~apple~CloudDocs/MIKKIE_WORLD ~/MIKKIE_WORLD

  Methode 3: Lokale zip (volledige snapshot)
  ──────────────────────────────────────────
  cd ~/MIKKIE_WORLD/BACKUP
  ls -la  # Kies de gewenste datum
  unzip mikkie_world_backup_YYYYMMDD.zip -d ~/

  Na herstel:
  ──────────
  source ~/.zshrc
  python3 ~/mikkieworld/mikkie_guardian.py start
  python3 ~/mikkieworld/mikkie_brain.py start

{'═'*60}
""")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "run":
        run_full_backup()
    elif args[0] == "icloud":
        result = backup_icloud()
        print(json.dumps(result, indent=2))
    elif args[0] == "github":
        result = backup_github()
        print(json.dumps(result, indent=2))
    elif args[0] == "zip":
        result = backup_zip()
        print(json.dumps(result, indent=2))
    elif args[0] == "status":
        show_status()
    elif args[0] == "restore":
        show_restore()
    else:
        print("Gebruik: python3 mikkie_backup.py [run|icloud|github|zip|status|restore]")
