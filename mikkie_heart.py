#!/usr/bin/env python3
"""
MIKKIE WORLD — ❤️ HEART Agent v1.0
════════════════════════════════════════════════════════════════
De merkbewaker. Checkt ELKE post, caption, beschrijving en
afbeeldingsprompt vóór publicatie op 5 harde regels:

  1. COPPA-veilig       — geen persoonlijke data van kinderen
  2. WWJD-filter        — opbouwend, geen rot woord
  3. Merkwaarden        — Avontuurlijk · Moedig · Magisch
  4. Vader-kind toon    — warm, aanmoedigend, nooit belerend
  5. Buiten-spelen call — inspireert tot actie buiten het scherm

Gebruik:
  python3 mikkie_heart.py check "jouw tekst hier"
  python3 mikkie_heart.py check-file post.txt
  python3 mikkie_heart.py check-prompt "afbeeldingsprompt"
  python3 mikkie_heart.py batch posts_folder/
  echo "tekst" | python3 mikkie_heart.py pipe

Integratie (vanuit andere agents):
  from mikkie_heart import heart_check
  result = heart_check(text)
  if result["approved"]: post_it()
════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from openai import OpenAI

# ─── Config ──────────────────────────────────────────────────────
BASE_DIR  = Path.home() / "mikkieworld"
LOG_FILE  = BASE_DIR / "heart_agent.log"
HEART_LOG = BASE_DIR / "heart_decisions.json"  # audit trail

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ─── Logging ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("HEART")

# ─── Grok client ─────────────────────────────────────────────────
client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# ─── De 5 HEART Regels ───────────────────────────────────────────
HEART_SYSTEM_PROMPT = """Je bent de HEART agent van MIKKIE WORLD — de merkbewaker.
Je taak: beoordeel content op 5 harde regels en geef een JSON-oordeel.

MIKKIE WORLD context:
- Kindermerk voor kinderen van 4-10 jaar
- Kernmissie: kinderen inspireren om buiten te spelen
- Merkwaarden: Avontuurlijk · Moedig · Magisch
- Tagline (NL): Blijf Altijd Kind. Met je kids.
- Tagline (EN): Always Be a Kid. With your kids.
- Oprichter: Hendrik Broeze, voor zijn zoontje Mikkie (7 jaar)
- Karakters: MIKKIE, BUBBLES, KNOEST, FIDO, NYX, ZERA, ORA

DE 5 HEART REGELS:

REGEL 1 — COPPA-VEILIG
✅ Geen verzoek om persoonlijke data van kinderen
✅ Geen targeting op leeftijd/locatie van kinderen
✅ Geen content die kinderen in gevaar brengt
❌ BLOKKEER: "stuur ons je naam en adres", "hoe oud ben jij?", gevaarlijke activiteiten

REGEL 2 — WWJD-FILTER (Wat Zou Jezus Doen)
✅ Opbouwend, bemoedigend, positief
✅ Genade-gevend voor de luisteraar
✅ Geen rot woord, geen schelden, geen negativiteit
❌ BLOKKEER: scheldwoorden, spot, angst, manipulatie, negatieve vergelijkingen

REGEL 3 — MERKWAARDEN
✅ Avontuurlijk: uitdagt tot ontdekking en actie
✅ Moedig: moedigt aan om dingen te proberen
✅ Magisch: verwondering, fantasie, bijzonder gevoel
❌ BLOKKEER: saai, belerend, commercieel zonder ziel, generieke content

REGEL 4 — VADER-KIND TOON
✅ Warm, aanmoedigend, gelijkwaardig
✅ Vader die naast het kind staat, niet boven
✅ Humor, authenticiteit, innerlijke autoriteit
❌ BLOKKEER: belerend, neerbuigend, overdreven enthousiast (nep), angstig

REGEL 5 — BUITEN-SPELEN CALL
✅ Inspireert tot actie buiten het scherm
✅ Natuur, avontuur, beweging, verbeelding
✅ Of: digitale content die leidt naar buiten-activiteit
❌ BLOKKEER: content die kinderen puur aan het scherm kluistert zonder buiten-element

JOUW OUTPUT — altijd exact dit JSON formaat:
{
  "approved": true/false,
  "score": 0-100,
  "regel_1_coppa": {"pass": true/false, "opmerking": "..."},
  "regel_2_wwjd": {"pass": true/false, "opmerking": "..."},
  "regel_3_merkwaarden": {"pass": true/false, "opmerking": "..."},
  "regel_4_toon": {"pass": true/false, "opmerking": "..."},
  "regel_5_buiten": {"pass": true/false, "opmerking": "..."},
  "verbeterd_voorstel": "verbeterde versie van de tekst (alleen als approved=false)",
  "samenvatting": "één zin waarom approved of geblokkeerd"
}

BELANGRIJK: approved=true alleen als ALLE 5 regels pass=true zijn.
Geef altijd een verbeterd_voorstel als approved=false."""

# ─── Kern functie ────────────────────────────────────────────────
def heart_check(text: str, content_type: str = "post") -> dict:
    """
    Checkt tekst op alle 5 HEART regels via Grok.
    Returns: dict met approved, score, per-regel oordeel, verbeterd voorstel
    """
    if not text or not text.strip():
        return {
            "approved": False,
            "score": 0,
            "samenvatting": "Lege tekst — niets te beoordelen",
            "error": "empty_input"
        }

    prompt = f"""Beoordeel deze {content_type} voor MIKKIE WORLD:

---
{text.strip()}
---

Geef je oordeel in het gevraagde JSON formaat."""

    try:
        response = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": HEART_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.1  # laag = consistent en betrouwbaar
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Extraheer JSON uit de response
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        
        result = json.loads(raw)
        result["input_text"] = text[:200]
        result["content_type"] = content_type
        result["timestamp"] = datetime.now().isoformat()
        
        return result
        
    except json.JSONDecodeError as e:
        log.warning(f"JSON parse fout: {e} — raw: {raw[:100]}")
        return {
            "approved": False,
            "score": 0,
            "samenvatting": f"Parse fout: {e}",
            "raw_response": raw[:200],
            "error": "json_parse_error"
        }
    except Exception as e:
        log.error(f"HEART check fout: {e}")
        return {
            "approved": False,
            "score": 0,
            "samenvatting": f"Technische fout: {e}",
            "error": str(e)
        }

def save_decision(result: dict, text: str):
    """Sla HEART beslissing op in audit trail."""
    decisions = []
    if HEART_LOG.exists():
        try:
            decisions = json.loads(HEART_LOG.read_text(encoding="utf-8"))
        except:
            decisions = []
    
    decisions.append({
        "timestamp": datetime.now().isoformat(),
        "approved": result.get("approved", False),
        "score": result.get("score", 0),
        "samenvatting": result.get("samenvatting", ""),
        "text_preview": text[:100]
    })
    
    # Bewaar laatste 500 beslissingen
    HEART_LOG.write_text(
        json.dumps(decisions[-500:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def send_telegram(msg: str):
    """Stuur Telegram alert."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        import urllib.request
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

def print_result(result: dict, verbose: bool = True):
    """Print HEART resultaat mooi in terminal."""
    approved = result.get("approved", False)
    score    = result.get("score", 0)
    
    print("\n" + "═"*60)
    if approved:
        print(f"  ❤️  HEART — ✅ GOEDGEKEURD  (score: {score}/100)")
    else:
        print(f"  ❤️  HEART — ❌ GEBLOKKEERD  (score: {score}/100)")
    print("═"*60)
    
    if verbose:
        regels = [
            ("COPPA-veilig",    result.get("regel_1_coppa", {})),
            ("WWJD-filter",     result.get("regel_2_wwjd", {})),
            ("Merkwaarden",     result.get("regel_3_merkwaarden", {})),
            ("Vader-kind toon", result.get("regel_4_toon", {})),
            ("Buiten-spelen",   result.get("regel_5_buiten", {})),
        ]
        for naam, regel in regels:
            if isinstance(regel, dict):
                icon = "✅" if regel.get("pass") else "❌"
                opmerking = regel.get("opmerking", "")
                print(f"  {icon} {naam:<20} {opmerking}")
    
    print(f"\n  💬 {result.get('samenvatting', '')}")
    
    if not approved and result.get("verbeterd_voorstel"):
        print(f"\n  ✏️  Verbeterd voorstel:")
        print(f"  {result['verbeterd_voorstel']}")
    
    print("═"*60 + "\n")

# ─── CLI Interface ────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ("--help", "-h", "help"):
        print(__doc__)
        return
    
    command = args[0]
    
    # ── check "tekst" ──────────────────────────────────────────
    if command == "check":
        if len(args) < 2:
            print("Gebruik: python3 mikkie_heart.py check \"jouw tekst\"")
            return
        text = " ".join(args[1:])
        log.info(f"Checking: {text[:60]}...")
        result = heart_check(text, "post")
        print_result(result)
        save_decision(result, text)
        
        if not result.get("approved"):
            send_telegram(f"❤️ HEART geblokkeerd:\n{result.get('samenvatting')}\n\nTekst: {text[:100]}")
    
    # ── check-file post.txt ────────────────────────────────────
    elif command == "check-file":
        if len(args) < 2:
            print("Gebruik: python3 mikkie_heart.py check-file bestand.txt")
            return
        filepath = Path(args[1])
        if not filepath.exists():
            print(f"❌ Bestand niet gevonden: {filepath}")
            return
        text = filepath.read_text(encoding="utf-8")
        log.info(f"Checking bestand: {filepath.name}")
        result = heart_check(text, "post")
        print_result(result)
        save_decision(result, text)
    
    # ── check-prompt "afbeeldingsprompt" ──────────────────────
    elif command == "check-prompt":
        if len(args) < 2:
            print("Gebruik: python3 mikkie_heart.py check-prompt \"prompt tekst\"")
            return
        text = " ".join(args[1:])
        log.info(f"Checking prompt: {text[:60]}...")
        result = heart_check(text, "afbeeldingsprompt")
        print_result(result)
        save_decision(result, text)
    
    # ── batch posts_folder/ ────────────────────────────────────
    elif command == "batch":
        if len(args) < 2:
            print("Gebruik: python3 mikkie_heart.py batch map/")
            return
        folder = Path(args[1])
        if not folder.is_dir():
            print(f"❌ Map niet gevonden: {folder}")
            return
        
        files = list(folder.glob("*.txt")) + list(folder.glob("*.md"))
        log.info(f"Batch check: {len(files)} bestanden in {folder}")
        
        approved_count = 0
        blocked_count  = 0
        
        for f in files:
            text = f.read_text(encoding="utf-8")
            result = heart_check(text, "post")
            save_decision(result, text)
            
            status = "✅" if result.get("approved") else "❌"
            score  = result.get("score", 0)
            print(f"  {status} {f.name:<40} score: {score}/100")
            
            if result.get("approved"):
                approved_count += 1
            else:
                blocked_count += 1
            
            time.sleep(0.5)  # rate limiting
        
        print(f"\n  Resultaat: {approved_count} goedgekeurd, {blocked_count} geblokkeerd")
        send_telegram(
            f"❤️ HEART batch klaar\n"
            f"✅ {approved_count} goedgekeurd\n"
            f"❌ {blocked_count} geblokkeerd"
        )
    
    # ── pipe (stdin) ───────────────────────────────────────────
    elif command == "pipe":
        text = sys.stdin.read().strip()
        if not text:
            print("❌ Geen input ontvangen via stdin")
            return
        result = heart_check(text, "post")
        # Minimale output voor pipe gebruik
        if result.get("approved"):
            print("APPROVED")
            sys.exit(0)
        else:
            print(f"BLOCKED: {result.get('samenvatting', '')}")
            sys.exit(1)
    
    # ── stats ──────────────────────────────────────────────────
    elif command == "stats":
        if not HEART_LOG.exists():
            print("Nog geen beslissingen opgeslagen.")
            return
        decisions = json.loads(HEART_LOG.read_text(encoding="utf-8"))
        total    = len(decisions)
        approved = sum(1 for d in decisions if d.get("approved"))
        blocked  = total - approved
        avg_score = sum(d.get("score", 0) for d in decisions) / total if total else 0
        
        print(f"\n  ❤️  HEART Statistieken")
        print(f"  {'─'*40}")
        print(f"  Totaal gecheckt:  {total}")
        print(f"  ✅ Goedgekeurd:   {approved} ({approved/total*100:.0f}%)" if total else "")
        print(f"  ❌ Geblokkeerd:   {blocked} ({blocked/total*100:.0f}%)" if total else "")
        print(f"  Gemiddelde score: {avg_score:.0f}/100")
        print(f"  Laatste check:    {decisions[-1]['timestamp'][:16] if decisions else 'n.v.t.'}\n")
    
    else:
        print(f"Onbekend commando: {command}")
        print("Gebruik: check | check-file | check-prompt | batch | pipe | stats")

if __name__ == "__main__":
    main()
