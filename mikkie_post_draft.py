#!/usr/bin/env python3
"""
MIKKIE WORLD — ✍️ Post Draft Agent v1.0
════════════════════════════════════════════════════════════════
Genereert kant-en-klare social media posts voor MIKKIE WORLD.
Elke post is automatisch afgestemd op het dagelijkse karakter,
het platform en de merkwaarden. HEART-check is ingebouwd.

GEBRUIK:
  python3 mikkie_post_draft.py generate              — dagelijkse post
  python3 mikkie_post_draft.py generate --karakter FIDO
  python3 mikkie_post_draft.py generate --platform instagram
  python3 mikkie_post_draft.py week                  — 7 posts voor de week
  python3 mikkie_post_draft.py campagne "thema"      — campagne posts
  python3 mikkie_post_draft.py list                  — bekijk opgeslagen posts
════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from openai import OpenAI

# ─── Config ──────────────────────────────────────────────────────
BASE_DIR    = Path.home() / "mikkieworld"
MIKKIE_ROOT = Path.home() / "MIKKIE_WORLD"
LOG_FILE    = BASE_DIR / "post_draft.log"
DRAFTS_FILE = BASE_DIR / "post_drafts.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("POST")

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# ─── MIKKIE WORLD Karakters ──────────────────────────────────────
KARAKTERS = {
    "MIKKIE":  {"rol": "The Hero",           "bewaker": "avontuur en moed",    "emoji": "⚡"},
    "BUBBLES": {"rol": "The Loyal Sidekick", "bewaker": "vriendschap en trouw", "emoji": "💙"},
    "KNOEST":  {"rol": "The Forest Keeper",  "bewaker": "natuur en rust",       "emoji": "🌳"},
    "FIDO":    {"rol": "The Dragon",         "bewaker": "vuur en bescherming",  "emoji": "🔥"},
    "NYX":     {"rol": "The Night Princess", "bewaker": "sterren en dromen",    "emoji": "🌙"},
    "ZERA":    {"rol": "The Guardian Angel", "bewaker": "hoop en geloof",       "emoji": "✨"},
    "ORA":     {"rol": "The Wise Owl",       "bewaker": "wijsheid en kennis",   "emoji": "🦉"},
}

# Dagelijks karakter schema (maandag=0 t/m zondag=6)
DAG_KARAKTER = {
    0: "MIKKIE",   # Maandag
    1: "BUBBLES",  # Dinsdag
    2: "KNOEST",   # Woensdag
    3: "FIDO",     # Donderdag
    4: "NYX",      # Vrijdag
    5: "ZERA",     # Zaterdag
    6: "ORA",      # Zondag
}

# Platform-specifieke richtlijnen
PLATFORM_SPECS = {
    "x": {
        "naam": "X/Twitter",
        "max_tekens": 280,
        "hashtags": 3,
        "toon": "kort, krachtig, één sterke zin + call-to-action",
        "emoji": "2-3 emoji's",
    },
    "instagram": {
        "naam": "Instagram",
        "max_tekens": 2200,
        "hashtags": 10,
        "toon": "verhalend, warm, vader-kind perspectief, 3-4 zinnen",
        "emoji": "3-5 emoji's verspreid door de tekst",
    },
    "pinterest": {
        "naam": "Pinterest",
        "max_tekens": 500,
        "hashtags": 5,
        "toon": "beschrijvend, inspirerend, actiegericht voor ouders",
        "emoji": "1-2 emoji's",
    },
    "facebook": {
        "naam": "Facebook",
        "max_tekens": 500,
        "hashtags": 3,
        "toon": "persoonlijk, vader-kind verhaal, uitnodigend",
        "emoji": "2-3 emoji's",
    },
}

# ─── Post generatie ──────────────────────────────────────────────
def generate_post(
    karakter: str = None,
    platform: str = "x",
    thema: str = None,
    dag_nummer: int = None
) -> dict:
    """Genereer een HEART-approved social media post."""
    
    # Bepaal karakter op basis van dag als niet opgegeven
    if karakter is None:
        dag = dag_nummer if dag_nummer is not None else datetime.now().weekday()
        karakter = DAG_KARAKTER[dag % 7]
    
    karakter = karakter.upper()
    if karakter not in KARAKTERS:
        karakter = "MIKKIE"
    
    kar_info = KARAKTERS[karakter]
    platform_info = PLATFORM_SPECS.get(platform.lower(), PLATFORM_SPECS["x"])
    
    # Thema op basis van dag als niet opgegeven
    if thema is None:
        themas = [
            "een geheime plek in het bos ontdekken",
            "een missie voltooien met vrienden",
            "iets nieuws durven proberen",
            "de natuur verkennen",
            "vader en kind avontuur",
            "dapper zijn als het moeilijk is",
            "verwondering vinden in kleine dingen",
        ]
        dag = datetime.now().weekday()
        thema = themas[dag % len(themas)]
    
    system_prompt = f"""Je bent de copywriter van MIKKIE WORLD — een magisch kindermerk.
Je schrijft social media posts die kinderen (4-10 jaar) en hun ouders inspireren om buiten te spelen.

MERKWAARDEN: Avontuurlijk · Moedig · Magisch | Blijf Altijd Kind. Met je kids.
TAAL: Nederlands
KARAKTER VAN VANDAAG: {karakter} — {kar_info['rol']} — bewaker van {kar_info['bewaker']}

PLATFORM: {platform_info['naam']}
MAX TEKENS: {platform_info['max_tekens']}
HASHTAGS: {platform_info['hashtags']} hashtags
TOON: {platform_info['toon']}
EMOJI: {platform_info['emoji']}

VERPLICHTE HASHTAGS (altijd aanwezig):
#MikkieWorld #BuitenSpelen

STIJL REGELS:
- Schrijf vanuit vader-kind perspectief
- Eindig altijd met een call-to-action om naar buiten te gaan
- Geen angst, geen negatieve vergelijkingen, geen commerciële druk
- Warm, aanmoedigend, authentiek
- Gebruik {kar_info['emoji']} emoji voor {karakter}"""

    user_prompt = f"""Schrijf een {platform_info['naam']} post over het thema: "{thema}"
Gebruik karakter {karakter} als inspiratiebron.
Maximaal {platform_info['max_tekens']} tekens.
Geef ALLEEN de post tekst terug, geen uitleg."""

    try:
        response = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=400,
            temperature=0.8
        )
        
        post_text = response.choices[0].message.content.strip()
        
        return {
            "text": post_text,
            "karakter": karakter,
            "platform": platform,
            "thema": thema,
            "tekens": len(post_text),
            "timestamp": datetime.now().isoformat(),
            "approved": None  # wordt ingevuld door HEART check
        }
        
    except Exception as e:
        log.error(f"Post generatie fout: {e}")
        return {"error": str(e), "text": ""}

def heart_check_post(post_text: str) -> dict:
    """Roep HEART agent aan voor content check."""
    heart_script = BASE_DIR / "mikkie_heart.py"
    if not heart_script.exists():
        return {"approved": True, "samenvatting": "HEART niet beschikbaar — niet gecheckt"}
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(heart_script), "pipe"],
            input=post_text,
            capture_output=True,
            text=True,
            timeout=30
        )
        approved = result.returncode == 0
        output = result.stdout.strip()
        return {
            "approved": approved,
            "samenvatting": output
        }
    except Exception as e:
        return {"approved": True, "samenvatting": f"HEART check fout: {e}"}

def save_draft(draft: dict):
    """Sla draft op in JSON bestand."""
    drafts = []
    if DRAFTS_FILE.exists():
        try:
            drafts = json.loads(DRAFTS_FILE.read_text(encoding="utf-8"))
        except:
            drafts = []
    
    drafts.append(draft)
    DRAFTS_FILE.write_text(
        json.dumps(drafts[-200:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def save_to_social_folder(draft: dict):
    """Sla goedgekeurde post op in de juiste SOCIAL map."""
    platform = draft.get("platform", "x").lower()
    platform_map = {
        "x": "X_Twitter",
        "instagram": "Instagram",
        "pinterest": "Pinterest",
        "facebook": "Facebook",
    }
    folder_name = platform_map.get(platform, "X_Twitter")
    output_dir = MIKKIE_ROOT / "SOCIAL" / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    karakter = draft.get("karakter", "MIKKIE")
    filename = f"{karakter}_{platform}_{timestamp}.txt"
    
    content = f"""MIKKIE WORLD — {platform.upper()} POST
Karakter: {karakter}
Thema: {draft.get('thema', '')}
Datum: {datetime.now().strftime('%d %b %Y %H:%M')}
Tekens: {draft.get('tekens', 0)}
HEART: {'✅ Goedgekeurd' if draft.get('approved') else '❌ Geblokkeerd'}
{'─'*50}

{draft.get('text', '')}
"""
    
    filepath = output_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath

# ─── CLI Commands ─────────────────────────────────────────────────
def cmd_generate(karakter=None, platform="x", thema=None):
    """Genereer één post met HEART check."""
    log.info(f"Post genereren — karakter: {karakter or 'auto'}, platform: {platform}")
    
    draft = generate_post(karakter=karakter, platform=platform, thema=thema)
    
    if "error" in draft:
        print(f"❌ Fout: {draft['error']}")
        return
    
    print(f"\n{'═'*60}")
    print(f"  ✍️  POST DRAFT — {draft['karakter']} voor {draft['platform'].upper()}")
    print(f"{'─'*60}")
    print(f"\n{draft['text']}\n")
    print(f"  Tekens: {draft['tekens']} | Thema: {draft['thema']}")
    
    # HEART check
    print(f"\n  ❤️  HEART check...")
    heart = heart_check_post(draft["text"])
    draft["approved"] = heart.get("approved", False)
    draft["heart_samenvatting"] = heart.get("samenvatting", "")
    
    if draft["approved"]:
        print(f"  ✅ Goedgekeurd: {heart.get('samenvatting', '')}")
        filepath = save_to_social_folder(draft)
        print(f"  💾 Opgeslagen: {filepath.relative_to(Path.home())}")
    else:
        print(f"  ❌ Geblokkeerd: {heart.get('samenvatting', '')}")
    
    print(f"{'═'*60}\n")
    
    save_draft(draft)
    
    # Output voor pipe gebruik
    if "--output" in sys.argv:
        print(draft["text"])
    
    return draft

def cmd_week():
    """Genereer 7 posts voor de hele week."""
    print(f"\n📅 Week planning — 7 posts genereren\n")
    
    for dag_nr in range(7):
        dag_namen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
        karakter = DAG_KARAKTER[dag_nr]
        kar_info = KARAKTERS[karakter]
        
        print(f"  {dag_namen[dag_nr]} — {karakter} {kar_info['emoji']}")
        
        draft = generate_post(karakter=karakter, platform="x", dag_nummer=dag_nr)
        if draft and "text" in draft:
            heart = heart_check_post(draft["text"])
            draft["approved"] = heart.get("approved", False)
            status = "✅" if draft["approved"] else "❌"
            print(f"  {status} {draft['text'][:80]}...")
            save_draft(draft)
            if draft["approved"]:
                save_to_social_folder(draft)
        
        time.sleep(1)
    
    print(f"\n✅ Week planning klaar! Bekijk posts in ~/MIKKIE_WORLD/SOCIAL/X_Twitter/\n")

def cmd_campagne(thema: str):
    """Genereer campagne posts voor alle platforms."""
    print(f"\n🚀 Campagne: '{thema}'\n")
    
    for platform in ["x", "instagram", "pinterest"]:
        print(f"  Genereren voor {platform}...")
        draft = generate_post(platform=platform, thema=thema)
        if draft and "text" in draft:
            heart = heart_check_post(draft["text"])
            draft["approved"] = heart.get("approved", False)
            status = "✅" if draft["approved"] else "❌"
            print(f"  {status} {platform}: {draft['text'][:60]}...")
            save_draft(draft)
            if draft["approved"]:
                save_to_social_folder(draft)
        time.sleep(1)
    
    print(f"\n✅ Campagne posts klaar!\n")

def cmd_list():
    """Toon opgeslagen drafts."""
    if not DRAFTS_FILE.exists():
        print("Nog geen drafts opgeslagen.")
        return
    
    drafts = json.loads(DRAFTS_FILE.read_text(encoding="utf-8"))
    print(f"\n  📝 Laatste {min(10, len(drafts))} drafts:\n")
    
    for draft in drafts[-10:]:
        status = "✅" if draft.get("approved") else "❌"
        ts = draft.get("timestamp", "")[:16]
        karakter = draft.get("karakter", "?")
        platform = draft.get("platform", "?")
        tekst = draft.get("text", "")[:60]
        print(f"  {status} {ts} [{karakter}/{platform}] {tekst}...")
    print()

# ─── Main ─────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return
    
    command = args[0]
    
    if command == "generate":
        karakter = None
        platform = "x"
        thema = None
        
        i = 1
        while i < len(args):
            if args[i] == "--karakter" and i+1 < len(args):
                karakter = args[i+1].upper()
                i += 2
            elif args[i] == "--platform" and i+1 < len(args):
                platform = args[i+1].lower()
                i += 2
            elif args[i] == "--thema" and i+1 < len(args):
                thema = args[i+1]
                i += 2
            else:
                i += 1
        
        cmd_generate(karakter=karakter, platform=platform, thema=thema)
    
    elif command == "week":
        cmd_week()
    
    elif command == "campagne":
        thema = " ".join(args[1:]) if len(args) > 1 else "MIKKIE avontuur"
        cmd_campagne(thema)
    
    elif command == "list":
        cmd_list()
    
    else:
        print(f"Onbekend commando: {command}")
        print("Gebruik: generate | week | campagne | list")

if __name__ == "__main__":
    main()
