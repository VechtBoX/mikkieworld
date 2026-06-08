#!/usr/bin/env python3
"""
📌 MIKKIE WORLD — Pinterest Agent
Automatisch pinnen van kleurplaten, covers en social posts naar Pinterest.
Pinterest is het #1 platform voor ouders die kleurplaten zoeken.

Gebruik:
  python3 mikkie_pinterest.py pin          # Pin de laatste afbeelding
  python3 mikkie_pinterest.py batch        # Pin alle afbeeldingen in output map
  python3 mikkie_pinterest.py boards       # Toon alle boards
  python3 mikkie_pinterest.py setup        # Maak MIKKIE boards aan
"""

import os, sys, json, time, datetime, requests
from pathlib import Path
from openai import OpenAI

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
PINTEREST_TOKEN = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
GUMROAD_TOKEN   = os.environ.get("GUMROAD_API_TOKEN", "9byVxzgAYPnwnhL3jPjZiVxOQrSvmQrweISCtzr00RI")
AGENTS_DIR      = Path.home() / "mikkieworld"
WORLD_DIR       = Path.home() / "MIKKIE_WORLD"
OUTPUT_DIR      = AGENTS_DIR / "artistly_output"
PINTEREST_DIR   = WORLD_DIR / "SOCIAL" / "Pinterest"
LOG_FILE        = WORLD_DIR / "LOGS" / "pinterest.log"

# Grok voor caption generatie
api_key  = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
client   = OpenAI(api_key=api_key, base_url=base_url)
model    = "grok-3" if os.environ.get("XAI_API_KEY") else "gpt-4o-mini"

# MIKKIE Pinterest boards
BOARDS = {
    "kleurplaten": {
        "name": "MIKKIE WORLD Kleurplaten",
        "description": "Gratis kleurplaten voor kinderen! Avontuurlijke karakters om buiten te spelen 🌟 #MikkieWorld #Kleurplaten #BuitenSpelen",
        "keywords": ["kleurplaten", "coloring pages", "kids activities", "outdoor play", "adventure"]
    },
    "stickers": {
        "name": "MIKKIE WORLD Stickers",
        "description": "Magische MIKKIE stickers voor kinderen ✨ #MikkieWorld #Stickers #KidsStickers",
        "keywords": ["stickers", "kids stickers", "printable stickers", "adventure stickers"]
    },
    "covers": {
        "name": "MIKKIE WORLD Characters",
        "description": "Maak kennis met de 7 magische karakters van MIKKIE WORLD 🏰 #MikkieWorld #KidsCharacters",
        "keywords": ["kids characters", "adventure characters", "magical world", "children book"]
    },
    "inspiratie": {
        "name": "MIKKIE WORLD Buiten Avonturen",
        "description": "Inspiratie voor buiten spelen met kinderen 🌿 #BuitenSpelen #Avontuur #VaderKind",
        "keywords": ["outdoor play", "adventure kids", "father son", "nature play", "buiten spelen"]
    }
}

BOLD  = "\033[1m"
GREEN = "\033[92m"
CYAN  = "\033[96m"
GOLD  = "\033[93m"
RED   = "\033[91m"
RESET = "\033[0m"

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def tg_send(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat  = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat: return
    try:
        import urllib.request
        payload = json.dumps({"chat_id": chat, "text": text, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except: pass

# ═══════════════════════════════════════════════════════
# CAPTION GENERATOR
# ═══════════════════════════════════════════════════════
def generate_pin_caption(filename: str, content_type: str, character: str) -> dict:
    """Genereer een Pinterest-geoptimaliseerde caption via Grok."""
    
    type_context = {
        "cover":    "een karakter illustratie voor kinderen",
        "coloring": "een gratis kleurplaat voor kinderen",
        "sticker":  "een leuke sticker voor kinderen",
        "social":   "een inspirerende post over buiten spelen",
        "banner":   "een banner voor het MIKKIE WORLD merk"
    }.get(content_type, "MIKKIE WORLD content")
    
    prompt = f"""Je schrijft een Pinterest pin voor MIKKIE WORLD — een magisch kindermerk.

Afbeelding: {type_context} van karakter {character}
Merkwaarden: Avontuurlijk · Moedig · Magisch · Buiten spelen · Vader-kind

Schrijf:
1. TITLE (max 100 tekens, pakkend, SEO-vriendelijk)
2. DESCRIPTION (max 500 tekens, met call-to-action, hashtags)
3. LINK (gebruik: https://mikkieworld.gumroad.com)
4. KEYWORDS (5 Pinterest-zoektermen, komma-gescheiden)

Formaat als JSON:
{{"title": "...", "description": "...", "link": "...", "keywords": "..."}}

Taal: Nederlands met enkele Engelse hashtags voor bereik."""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        text = resp.choices[0].message.content.strip()
        # Extract JSON
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Caption fout: {e}")
    
    # Fallback
    return {
        "title": f"MIKKIE WORLD — {character} Avontuur 🌟",
        "description": f"Ontdek {character} in MIKKIE WORLD! Gratis kleurplaten en avontuurlijke content voor kinderen. Buiten spelen is magisch! ✨ #MikkieWorld #BuitenSpelen #Avontuur #Kinderen #KleurplaatGratis",
        "link": "https://mikkieworld.gumroad.com",
        "keywords": "kleurplaten gratis, kinderen activiteiten, buiten spelen, avontuur kinderen, MIKKIE WORLD"
    }

# ═══════════════════════════════════════════════════════
# PINTEREST API
# ═══════════════════════════════════════════════════════
def pinterest_api(method: str, endpoint: str, data: dict = None, files: dict = None):
    """Pinterest API v5 request."""
    if not PINTEREST_TOKEN:
        return None, "Geen PINTEREST_ACCESS_TOKEN ingesteld"
    
    url = f"https://api.pinterest.com/v5/{endpoint}"
    headers = {"Authorization": f"Bearer {PINTEREST_TOKEN}"}
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=30)
        elif method == "POST" and files:
            resp = requests.post(url, headers=headers, data=data, files=files, timeout=60)
        elif method == "POST":
            headers["Content-Type"] = "application/json"
            resp = requests.post(url, headers=headers, json=data, timeout=30)
        
        if resp.status_code in [200, 201]:
            return resp.json(), None
        else:
            return None, f"API fout {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, str(e)

def get_boards():
    """Haal alle Pinterest boards op."""
    data, err = pinterest_api("GET", "boards")
    if err:
        return None, err
    return data.get("items", []), None

def create_board(name: str, description: str):
    """Maak een nieuw Pinterest board aan."""
    data, err = pinterest_api("POST", "boards", {
        "name": name,
        "description": description,
        "privacy": "PUBLIC"
    })
    return data, err

def create_pin(board_id: str, image_path: str, title: str, description: str, link: str):
    """Maak een nieuwe Pinterest pin aan met afbeelding upload."""
    
    # Stap 1: Upload afbeelding
    with open(image_path, "rb") as f:
        media_data, err = pinterest_api("POST", "media", 
            data={"media_type": "image"},
            files={"file": (Path(image_path).name, f, "image/png")}
        )
    
    if err or not media_data:
        # Fallback: pin zonder upload (gebruik URL als die beschikbaar is)
        log(f"Upload fout: {err} — sla pin op als draft")
        return None, err
    
    media_id = media_data.get("media_id")
    
    # Stap 2: Maak pin aan
    pin_data = {
        "board_id": board_id,
        "title": title,
        "description": description,
        "link": link,
        "media_source": {
            "source_type": "media_id",
            "media_id": media_id
        }
    }
    
    result, err = pinterest_api("POST", "pins", pin_data)
    return result, err

# ═══════════════════════════════════════════════════════
# LOKALE DRAFT (als Pinterest token niet beschikbaar is)
# ═══════════════════════════════════════════════════════
def save_pin_draft(image_path: str, caption: dict, board_name: str):
    """Sla pin op als lokaal draft bestand."""
    PINTEREST_DIR.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = Path(image_path).stem
    draft_file = PINTEREST_DIR / f"{stem}_{ts}_pin.json"
    
    draft = {
        "image": str(image_path),
        "board": board_name,
        "title": caption["title"],
        "description": caption["description"],
        "link": caption["link"],
        "keywords": caption["keywords"],
        "created_at": datetime.datetime.now().isoformat(),
        "status": "draft"
    }
    
    with open(draft_file, "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)
    
    return draft_file

# ═══════════════════════════════════════════════════════
# PARSE FILENAME
# ═══════════════════════════════════════════════════════
def parse_filename(filename: str) -> tuple:
    """Extraheer karakter en type uit bestandsnaam."""
    characters = ["MIKKIE", "BUBBLES", "KNOEST", "FIDO", "NYX", "ZERA", "ORA"]
    types = ["cover", "coloring", "sticker", "social", "banner"]
    
    fn = filename.upper()
    char = next((c for c in characters if c in fn), "MIKKIE")
    ctype = next((t for t in types if t in fn.lower()), "cover")
    
    return char, ctype

def get_board_for_type(content_type: str) -> str:
    """Geef het juiste board terug voor een content type."""
    mapping = {
        "coloring": "kleurplaten",
        "sticker":  "stickers",
        "cover":    "covers",
        "social":   "inspiratie",
        "banner":   "inspiratie"
    }
    return mapping.get(content_type, "inspiratie")

# ═══════════════════════════════════════════════════════
# COMMANDO'S
# ═══════════════════════════════════════════════════════
def cmd_pin_latest():
    """Pin de meest recente afbeelding."""
    if not OUTPUT_DIR.exists():
        log("❌ artistly_output map niet gevonden")
        return
    
    images = sorted(OUTPUT_DIR.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not images:
        log("❌ Geen afbeeldingen gevonden in artistly_output/")
        return
    
    latest = images[0]
    char, ctype = parse_filename(latest.name)
    board_key = get_board_for_type(ctype)
    board_info = BOARDS[board_key]
    
    log(f"📌 Pin genereren voor: {latest.name}")
    caption = generate_pin_caption(latest.name, ctype, char)
    
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  📌 PINTEREST PIN — {char} ({ctype})")
    print(f"{'─'*60}{RESET}")
    print(f"  Board:       {board_info['name']}")
    print(f"  Title:       {caption['title']}")
    print(f"  Description: {caption['description'][:100]}...")
    print(f"  Link:        {caption['link']}")
    print(f"  Keywords:    {caption['keywords']}")
    print(f"{'═'*60}{RESET}\n")
    
    if PINTEREST_TOKEN:
        # Probeer echte API
        boards, err = get_boards()
        board_id = None
        if boards:
            for b in boards:
                if board_info["name"].lower() in b.get("name", "").lower():
                    board_id = b["id"]
                    break
        
        if board_id:
            result, err = create_pin(board_id, str(latest), caption["title"], caption["description"], caption["link"])
            if result:
                log(f"✅ Pin live op Pinterest! ID: {result.get('id')}")
                tg_send(f"📌 *Pinterest pin live!*\n{char} {ctype}\n{caption['title']}")
                return
    
    # Sla op als draft
    draft = save_pin_draft(str(latest), caption, board_info["name"])
    log(f"💾 Pin draft opgeslagen: {draft.name}")
    print(f"  {GOLD}💾 Draft opgeslagen in MIKKIE_WORLD/SOCIAL/Pinterest/{RESET}")
    print(f"  {CYAN}ℹ️  Voeg PINTEREST_ACCESS_TOKEN toe om direct te posten{RESET}\n")

def cmd_batch():
    """Pin alle afbeeldingen in de output map."""
    if not OUTPUT_DIR.exists():
        log("❌ artistly_output map niet gevonden")
        return
    
    images = sorted(OUTPUT_DIR.glob("*.png"))
    if not images:
        log("❌ Geen afbeeldingen gevonden")
        return
    
    log(f"📌 Batch pin: {len(images)} afbeeldingen")
    print(f"\n{BOLD}📌 PINTEREST BATCH — {len(images)} pins{RESET}\n")
    
    succes = 0
    for img in images:
        char, ctype = parse_filename(img.name)
        board_key = get_board_for_type(ctype)
        board_info = BOARDS[board_key]
        
        caption = generate_pin_caption(img.name, ctype, char)
        draft = save_pin_draft(str(img), caption, board_info["name"])
        log(f"  ✅ {img.name} → {board_info['name']}")
        succes += 1
        time.sleep(0.5)  # Voorkom rate limiting
    
    print(f"\n{GREEN}✅ {succes}/{len(images)} pins opgeslagen als draft{RESET}")
    print(f"{CYAN}📁 Locatie: ~/MIKKIE_WORLD/SOCIAL/Pinterest/{RESET}\n")
    tg_send(f"📌 *Pinterest batch klaar!*\n{succes} pins gegenereerd als draft\n📁 ~/MIKKIE_WORLD/SOCIAL/Pinterest/")

def cmd_boards():
    """Toon alle boards of de geconfigureerde boards."""
    print(f"\n{BOLD}📌 MIKKIE WORLD Pinterest Boards{RESET}\n")
    
    if PINTEREST_TOKEN:
        boards, err = get_boards()
        if boards:
            for b in boards:
                print(f"  • {b.get('name')} (ID: {b.get('id')})")
            return
    
    print(f"  {GOLD}Geconfigureerde boards (nog aan te maken):{RESET}\n")
    for key, board in BOARDS.items():
        print(f"  📌 {board['name']}")
        print(f"     {board['description'][:80]}...")
        print()
    
    print(f"  {CYAN}ℹ️  Voeg PINTEREST_ACCESS_TOKEN toe voor live boards{RESET}")
    print(f"  {CYAN}   Maak token aan op: https://developers.pinterest.com{RESET}\n")

def cmd_setup():
    """Maak alle MIKKIE boards aan op Pinterest."""
    if not PINTEREST_TOKEN:
        print(f"\n{RED}❌ PINTEREST_ACCESS_TOKEN niet ingesteld{RESET}")
        print(f"\n{GOLD}Stap 1: Ga naar https://developers.pinterest.com{RESET}")
        print(f"{GOLD}Stap 2: Maak een app aan{RESET}")
        print(f"{GOLD}Stap 3: Genereer een access token{RESET}")
        print(f"{GOLD}Stap 4: Voeg toe aan ~/.zshrc:{RESET}")
        print(f"  export PINTEREST_ACCESS_TOKEN=jouw_token\n")
        return
    
    print(f"\n{BOLD}📌 MIKKIE Pinterest boards aanmaken...{RESET}\n")
    for key, board in BOARDS.items():
        result, err = create_board(board["name"], board["description"])
        if result:
            log(f"✅ Board aangemaakt: {board['name']} (ID: {result.get('id')})")
        else:
            log(f"⚠️  Board fout: {err}")
    
    print(f"\n{GREEN}✅ Boards aangemaakt!{RESET}\n")

def cmd_setup_token_instructions():
    """Geef instructies voor Pinterest token setup."""
    print(f"""
{BOLD}📌 Pinterest Token Setup{RESET}

{GOLD}Stap 1 — Maak Pinterest Developer account aan:{RESET}
  https://developers.pinterest.com/apps/

{GOLD}Stap 2 — Maak een nieuwe app aan:{RESET}
  • App naam: MIKKIE WORLD
  • Redirect URI: https://mikkie.world/pinterest/callback

{GOLD}Stap 3 — Genereer access token:{RESET}
  • Ga naar je app → Generate access token
  • Scopes: boards:read, boards:write, pins:read, pins:write

{GOLD}Stap 4 — Voeg toe aan ~/.zshrc:{RESET}
  export PINTEREST_ACCESS_TOKEN=jouw_token_hier
  source ~/.zshrc

{GOLD}Stap 5 — Test:{RESET}
  python3 ~/mikkieworld/mikkie_pinterest.py boards
""")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pin"
    
    if cmd == "pin":
        cmd_pin_latest()
    elif cmd == "batch":
        cmd_batch()
    elif cmd == "boards":
        cmd_boards()
    elif cmd == "setup":
        cmd_setup()
    elif cmd == "token":
        cmd_setup_token_instructions()
    else:
        print(f"Gebruik: python3 mikkie_pinterest.py [pin|batch|boards|setup|token]")
