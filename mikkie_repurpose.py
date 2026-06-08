#!/usr/bin/env python3
"""
🔄 MIKKIE WORLD — REPURPOSE Agent v1.0
=======================================
Neemt één stuk content en maakt er automatisch 7 varianten van
voor 7 verschillende platforms. Elke variant passt bij de stijl
en het formaat van het platform.

Gebruik:
  python3 mikkie_repurpose.py post "tekst van de post"
  python3 mikkie_repurpose.py file ~/MIKKIE_WORLD/SOCIAL/X_Twitter/MIKKIE_x_20260609.txt
  python3 mikkie_repurpose.py latest     → Repurpose de laatste X post
  python3 mikkie_repurpose.py all        → Repurpose alle posts van vandaag
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR    = Path.home() / "mikkieworld"
SOCIAL_DIR  = Path.home() / "MIKKIE_WORLD" / "SOCIAL"
LOG_DIR     = Path.home() / "MIKKIE_WORLD" / "LOGS"

for d in [LOG_DIR,
          SOCIAL_DIR / "X_Twitter",
          SOCIAL_DIR / "Instagram",
          SOCIAL_DIR / "Pinterest",
          SOCIAL_DIR / "TikTok",
          SOCIAL_DIR / "Facebook",
          SOCIAL_DIR / "LinkedIn",
          SOCIAL_DIR / "YouTube"]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("REPURPOSE")

# ─── Kleuren ──────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
PURPLE = "\033[95m"

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

# ─── Platform definities ──────────────────────────────────────────────────────
PLATFORMS = {
    "x": {
        "naam": "X/Twitter",
        "map": SOCIAL_DIR / "X_Twitter",
        "max_tekens": 280,
        "stijl": "Kort, krachtig, 2-3 hashtags. Direct en energiek. Emoji toegestaan.",
        "formaat": "Tweet (max 280 tekens)"
    },
    "instagram": {
        "naam": "Instagram",
        "map": SOCIAL_DIR / "Instagram",
        "max_tekens": 2200,
        "stijl": "Visueel verhaal, emotioneel, 5-10 hashtags aan het einde. Gebruik line breaks. Persoonlijk.",
        "formaat": "Instagram caption (max 2200 tekens, hashtags onderaan)"
    },
    "pinterest": {
        "naam": "Pinterest",
        "map": SOCIAL_DIR / "Pinterest",
        "max_tekens": 500,
        "stijl": "Beschrijvend, SEO-vriendelijk, focus op 'buiten spelen', 'avontuur', 'kinderen'. Geen hashtags.",
        "formaat": "Pinterest pin beschrijving (max 500 tekens)"
    },
    "tiktok": {
        "naam": "TikTok",
        "map": SOCIAL_DIR / "TikTok",
        "max_tekens": 150,
        "stijl": "Trendy, energiek, 3-5 hashtags inclusief trending. Gebruik TikTok-taal.",
        "formaat": "TikTok caption (max 150 tekens)"
    },
    "facebook": {
        "naam": "Facebook",
        "map": SOCIAL_DIR / "Facebook",
        "max_tekens": 500,
        "stijl": "Warm en persoonlijk, vader-kind perspectief, vraag om reactie aan het einde. 1-2 hashtags.",
        "formaat": "Facebook post (max 500 tekens)"
    },
    "linkedin": {
        "naam": "LinkedIn",
        "map": SOCIAL_DIR / "LinkedIn",
        "max_tekens": 700,
        "stijl": "Professioneel maar warm. Ondernemer + vader verhaal. Merkopbouw. 3 hashtags.",
        "formaat": "LinkedIn post (max 700 tekens)"
    },
    "youtube": {
        "naam": "YouTube Shorts",
        "map": SOCIAL_DIR / "YouTube",
        "max_tekens": 500,
        "stijl": "Script voor 30-60 seconden video. Hook in eerste 3 seconden. Call to action aan het einde.",
        "formaat": "YouTube Shorts script (30-60 sec)"
    },
}

# ─── Grok client ──────────────────────────────────────────────────────────────
def get_client() -> OpenAI:
    api_key = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)

# ─── Repurpose één post ───────────────────────────────────────────────────────
def repurpose_post(originele_tekst: str, karakter: str = "MIKKIE") -> dict:
    """Maak 7 platform-varianten van één post."""
    client = get_client()
    resultaten = {}

    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  🔄 REPURPOSE — {karakter}")
    print(f"  Origineel: {originele_tekst[:80]}...")
    print(f"{'─'*60}{RESET}")

    for platform_id, platform in PLATFORMS.items():
        log.info(f"Genereren voor {platform['naam']}...")

        prompt = f"""Je bent de MIKKIE WORLD content specialist.

ORIGINELE POST:
{originele_tekst}

KARAKTER: {karakter}
PLATFORM: {platform['naam']}
FORMAAT: {platform['formaat']}
STIJL: {platform['stijl']}

MERKWAARDEN: Avontuurlijk · Moedig · Magisch
MISSIE: Kinderen inspireren om buiten te spelen
TOON: Warm, vader-kind energie, Nederlands

Schrijf een {platform['formaat']} gebaseerd op de originele post.
Pas de stijl en het formaat aan voor {platform['naam']}.
Houd de kern van de boodschap maar maak het platform-native.
Schrijf ALLEEN de post tekst, geen uitleg."""

        try:
            response = client.chat.completions.create(
                model="grok-3-mini" if os.environ.get("XAI_API_KEY") else "gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.8
            )
            tekst = response.choices[0].message.content.strip()
            resultaten[platform_id] = tekst

            # Opslaan
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            bestand = platform["map"] / f"{karakter}_{platform_id}_{timestamp}.txt"
            bestand.write_text(tekst, encoding="utf-8")

            print(f"\n  {c(platform['naam'], CYAN)} ({len(tekst)} tekens):")
            print(f"  {tekst[:120]}{'...' if len(tekst) > 120 else ''}")
            print(f"  {c(f'💾 {bestand.name}', PURPLE)}")

        except Exception as e:
            log.error(f"❌ {platform['naam']} mislukt: {e}")
            resultaten[platform_id] = None

    geslaagd = sum(1 for v in resultaten.values() if v)
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  ✅ {geslaagd}/7 platforms gegenereerd")
    print(f"{'═'*60}\n")

    telegram(
        f"🔄 REPURPOSE klaar\n"
        f"<b>{karakter}</b> — {geslaagd}/7 platforms\n"
        f"Bestanden in ~/MIKKIE_WORLD/SOCIAL/"
    )

    return resultaten

# ─── Repurpose laatste post ───────────────────────────────────────────────────
def repurpose_latest():
    """Repurpose de meest recente X post."""
    x_dir = SOCIAL_DIR / "X_Twitter"
    bestanden = sorted(x_dir.glob("*.txt"), key=lambda f: f.stat().st_mtime, reverse=True)

    if not bestanden:
        print(c("⚠️  Geen X posts gevonden in SOCIAL/X_Twitter/", YELLOW))
        return

    bestand = bestanden[0]
    tekst = bestand.read_text(encoding="utf-8").strip()

    # Extraheer karakter uit bestandsnaam
    karakter = bestand.stem.split("_")[0] if "_" in bestand.stem else "MIKKIE"

    print(f"  📄 Repurpose: {bestand.name}")
    repurpose_post(tekst, karakter)

# ─── Repurpose alle posts van vandaag ─────────────────────────────────────────
def repurpose_all_today():
    """Repurpose alle X posts van vandaag."""
    x_dir = SOCIAL_DIR / "X_Twitter"
    vandaag = datetime.now().strftime("%Y%m%d")
    bestanden = [f for f in x_dir.glob(f"*{vandaag}*.txt")]

    if not bestanden:
        print(c(f"⚠️  Geen posts van vandaag ({vandaag}) gevonden", YELLOW))
        return

    print(f"  📄 {len(bestanden)} posts van vandaag repurposen...")
    for bestand in bestanden:
        tekst = bestand.read_text(encoding="utf-8").strip()
        karakter = bestand.stem.split("_")[0] if "_" in bestand.stem else "MIKKIE"
        repurpose_post(tekst, karakter)

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print("Gebruik: python3 mikkie_repurpose.py [post 'tekst' | file pad | latest | all]")
        sys.exit(0)

    if args[0] == "post" and len(args) > 1:
        repurpose_post(" ".join(args[1:]))
    elif args[0] == "file" and len(args) > 1:
        pad = Path(args[1])
        if pad.exists():
            tekst = pad.read_text(encoding="utf-8").strip()
            karakter = pad.stem.split("_")[0] if "_" in pad.stem else "MIKKIE"
            repurpose_post(tekst, karakter)
        else:
            print(c(f"❌ Bestand niet gevonden: {pad}", "\033[91m"))
    elif args[0] == "latest":
        repurpose_latest()
    elif args[0] == "all":
        repurpose_all_today()
    else:
        print("Gebruik: python3 mikkie_repurpose.py [post 'tekst' | file pad | latest | all]")
