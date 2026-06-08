#!/usr/bin/env python3
"""
🛒 MIKKIE WORLD — Gumroad Bundel Agent
Beheert de €29 MIKKIE WORLD Complete Bundle en uploadt covers automatisch.

Gebruik:
  python3 mikkie_gumroad_bundle.py status          # Toon alle producten
  python3 mikkie_gumroad_bundle.py bundle          # Maak/update Complete Bundle
  python3 mikkie_gumroad_bundle.py upload-covers   # Upload covers naar producten
  python3 mikkie_gumroad_bundle.py descriptions    # Update alle product beschrijvingen
  python3 mikkie_gumroad_bundle.py prices          # Toon/update prijzen
"""

import os, sys, json, time, datetime, requests
from pathlib import Path
from openai import OpenAI

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
GUMROAD_TOKEN  = os.environ.get("GUMROAD_API_TOKEN", "9byVxzgAYPnwnhL3jPjZiVxOQrSvmQrweISCtzr00RI")
GUMROAD_BASE   = "https://api.gumroad.com/v2"
AGENTS_DIR     = Path.home() / "mikkieworld"
WORLD_DIR      = Path.home() / "MIKKIE_WORLD"
COVERS_DIR     = WORLD_DIR / "GUMROAD" / "Covers"
PRODUCTS_DIR   = WORLD_DIR / "GUMROAD" / "Products"
LOG_FILE       = WORLD_DIR / "LOGS" / "gumroad_bundle.log"

# Grok voor beschrijvingen
api_key  = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
client   = OpenAI(api_key=api_key, base_url=base_url)
model    = "grok-3" if os.environ.get("XAI_API_KEY") else "gpt-4o-mini"

# MIKKIE karakters en hun producten
CHARACTERS = [
    {"name": "MIKKIE",   "role": "The Hero",           "price": 699,  "emoji": "⚔️"},
    {"name": "BUBBLES",  "role": "The Loyal Sidekick",  "price": 699,  "emoji": "🫧"},
    {"name": "KNOEST",   "role": "The Forest Keeper",   "price": 699,  "emoji": "🌳"},
    {"name": "FIDO",     "role": "The Dragon",          "price": 699,  "emoji": "🐉"},
    {"name": "NYX",      "role": "The Night Princess",  "price": 699,  "emoji": "🌙"},
    {"name": "ZERA",     "role": "The Guardian Angel",  "price": 699,  "emoji": "👼"},
    {"name": "ORA",      "role": "The Wise Owl",        "price": 699,  "emoji": "🦉"}
]

BUNDLE_CONFIG = {
    "name": "MIKKIE WORLD Complete Bundle — Alle 7 Karakters",
    "price": 2900,  # €29,00 in centen
    "description_short": "Alle 7 MIKKIE WORLD karakters in één bundel! Kleurplaten, stickers en covers voor MIKKIE, BUBBLES, KNOEST, FIDO, NYX, ZERA en ORA.",
    "tags": ["kinderen", "kleurplaten", "avontuur", "bundel", "MIKKIE WORLD"]
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
# GUMROAD API
# ═══════════════════════════════════════════════════════
def gumroad_get(endpoint: str, params: dict = None):
    """GET request naar Gumroad API."""
    url = f"{GUMROAD_BASE}/{endpoint}"
    headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
    try:
        resp = requests.get(url, headers=headers, params=params or {}, timeout=30)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"GET fout {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, str(e)

def gumroad_post(endpoint: str, data: dict = None, files: dict = None):
    """POST request naar Gumroad API."""
    url = f"{GUMROAD_BASE}/{endpoint}"
    headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
    try:
        if files:
            resp = requests.post(url, headers=headers, data=data or {}, files=files, timeout=60)
        else:
            resp = requests.post(url, headers=headers, data=data or {}, timeout=30)
        if resp.status_code in [200, 201]:
            return resp.json(), None
        return None, f"POST fout {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, str(e)

def gumroad_put(endpoint: str, data: dict = None):
    """PUT request naar Gumroad API."""
    url = f"{GUMROAD_BASE}/{endpoint}"
    headers = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}
    try:
        resp = requests.put(url, headers=headers, data=data or {}, timeout=30)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"PUT fout {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, str(e)

def get_all_products():
    """Haal alle Gumroad producten op."""
    data, err = gumroad_get("products")
    if err:
        return None, err
    return data.get("products", []), None

# ═══════════════════════════════════════════════════════
# BESCHRIJVING GENERATOR
# ═══════════════════════════════════════════════════════
def generate_product_description(character: dict, product_type: str = "kleurplaten") -> str:
    """Genereer een Gumroad product beschrijving via Grok."""
    
    prompt = f"""Je schrijft een Gumroad product beschrijving voor MIKKIE WORLD.

Product: {character['name']} — {character['role']} {character['emoji']}
Type: {product_type}
Merkwaarden: Avontuurlijk · Moedig · Magisch · Buiten spelen · Vader-kind

Schrijf een aantrekkelijke beschrijving die:
1. Ouders aanspreekt (kopers zijn ouders, niet kinderen)
2. De waarde duidelijk maakt (buiten spelen, creativiteit, avontuur)
3. COPPA-safe is (geen persoonlijke data van kinderen)
4. Een duidelijke call-to-action heeft
5. Max 300 woorden, in het Nederlands

Gebruik HTML opmaak (h2, p, ul, strong) voor Gumroad.
Voeg aan het einde toe: "🌐 Meer info: https://mikkie.world"
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log(f"Beschrijving fout: {e}")
        return f"""<h2>{character['name']} {character['emoji']} — {character['role']}</h2>
<p>Ontdek <strong>{character['name']}</strong> uit MIKKIE WORLD! Dit pakket bevat prachtige kleurplaten en stickers voor kinderen die houden van avontuur en buiten spelen.</p>
<ul>
<li>✅ Hoge kwaliteit printbare bestanden (PDF + PNG)</li>
<li>✅ Geschikt voor kinderen van 4-10 jaar</li>
<li>✅ Perfect voor een regenachtige dag of als cadeau</li>
<li>✅ Instant download na aankoop</li>
</ul>
<p><strong>MIKKIE WORLD</strong> — Avontuurlijk · Moedig · Magisch</p>
<p>🌐 Meer info: https://mikkie.world</p>"""

def generate_bundle_description() -> str:
    """Genereer de Complete Bundle beschrijving."""
    
    prompt = """Je schrijft een Gumroad product beschrijving voor de MIKKIE WORLD Complete Bundle.

Bundel: Alle 7 MIKKIE WORLD karakters
Prijs: €29 (normaal €49 — 40% korting)
Karakters: MIKKIE (held), BUBBLES (sidekick), KNOEST (boswachter), FIDO (draak), NYX (nachtprinses), ZERA (engel), ORA (uil)
Inhoud: Kleurplaten, stickers en covers per karakter

Schrijf een aantrekkelijke bundel beschrijving die:
1. De waarde van de bundel benadrukt (bespaar €20!)
2. Elk karakter kort introduceert
3. Perfect is voor ouders die alles willen
4. Een urgentie-element heeft (beperkte aanbieding)
5. Max 400 woorden, in het Nederlands

Gebruik HTML opmaak voor Gumroad.
Voeg toe: "🌐 Meer info: https://mikkie.world"
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        log(f"Bundle beschrijving fout: {e}")
        return """<h2>🌟 MIKKIE WORLD Complete Bundle — Alle 7 Karakters!</h2>
<p><strong>Bespaar €20!</strong> Normaal €49, nu slechts <strong>€29</strong> voor de complete collectie!</p>
<h3>Wat zit er in de bundel?</h3>
<ul>
<li>⚔️ <strong>MIKKIE</strong> — The Hero (kleurplaten + stickers)</li>
<li>🫧 <strong>BUBBLES</strong> — The Loyal Sidekick</li>
<li>🌳 <strong>KNOEST</strong> — The Forest Keeper</li>
<li>🐉 <strong>FIDO</strong> — The Dragon</li>
<li>🌙 <strong>NYX</strong> — The Night Princess</li>
<li>👼 <strong>ZERA</strong> — The Guardian Angel</li>
<li>🦉 <strong>ORA</strong> — The Wise Owl</li>
</ul>
<p>✅ 70+ printbare bestanden (PDF + PNG)<br>
✅ Hoge kwaliteit voor thuis printen<br>
✅ Instant download na aankoop<br>
✅ Perfect voor kinderen van 4-10 jaar</p>
<p><strong>MIKKIE WORLD</strong> — Avontuurlijk · Moedig · Magisch</p>
<p>🌐 Meer info: https://mikkie.world</p>"""

# ═══════════════════════════════════════════════════════
# COVER UPLOAD
# ═══════════════════════════════════════════════════════
def find_cover_for_character(character_name: str) -> Path | None:
    """Zoek de cover afbeelding voor een karakter."""
    # Zoek in artistly_output
    artistly_dir = AGENTS_DIR / "artistly_output"
    if artistly_dir.exists():
        for img in sorted(artistly_dir.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True):
            if character_name.upper() in img.name.upper() and "cover" in img.name.lower():
                return img
        # Fallback: eerste afbeelding met karakternaam
        for img in sorted(artistly_dir.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True):
            if character_name.upper() in img.name.upper():
                return img
    
    # Zoek in GUMROAD/Covers
    if COVERS_DIR.exists():
        for img in COVERS_DIR.glob(f"*{character_name}*"):
            return img
    
    return None

def upload_cover_to_product(product_id: str, image_path: Path):
    """Upload een cover afbeelding naar een Gumroad product."""
    with open(image_path, "rb") as f:
        result, err = gumroad_post(
            f"products/{product_id}/edit",
            data={"name": ""},  # Behoud bestaande naam
            files={"preview": (image_path.name, f, "image/png")}
        )
    return result, err

# ═══════════════════════════════════════════════════════
# COMMANDO'S
# ═══════════════════════════════════════════════════════
def cmd_status():
    """Toon alle Gumroad producten."""
    print(f"\n{BOLD}🛒 GUMROAD PRODUCTEN — MIKKIE WORLD{RESET}\n")
    
    products, err = get_all_products()
    if err:
        print(f"  {RED}❌ API fout: {err}{RESET}")
        print(f"  {GOLD}Token: {GUMROAD_TOKEN[:20]}...{RESET}\n")
        return
    
    if not products:
        print(f"  {GOLD}Geen producten gevonden{RESET}\n")
        return
    
    total_sales = 0
    for p in products:
        price = p.get("price", 0) / 100
        sales = p.get("sales_count", 0)
        revenue = price * sales
        total_sales += revenue
        
        print(f"  {GOLD}• {p.get('name', 'Onbekend')}{RESET}")
        print(f"    ID: {p.get('id')} | Prijs: €{price:.2f} | Verkopen: {sales} | Omzet: €{revenue:.2f}")
        print()
    
    print(f"  {GREEN}Totale omzet: €{total_sales:.2f}{RESET}\n")
    tg_send(f"🛒 *Gumroad status*\n{len(products)} producten\nTotale omzet: €{total_sales:.2f}")

def cmd_bundle():
    """Maak of update de Complete Bundle."""
    print(f"\n{BOLD}🌟 MIKKIE WORLD Complete Bundle aanmaken...{RESET}\n")
    
    # Genereer beschrijving
    print(f"  {GOLD}Beschrijving genereren...{RESET}")
    description = generate_bundle_description()
    
    # Check of bundle al bestaat
    products, err = get_all_products()
    bundle_id = None
    
    if products:
        for p in products:
            if "Complete Bundle" in p.get("name", "") or "bundel" in p.get("name", "").lower():
                bundle_id = p.get("id")
                log(f"Bundle gevonden: {bundle_id}")
                break
    
    bundle_data = {
        "name": BUNDLE_CONFIG["name"],
        "price": BUNDLE_CONFIG["price"],
        "description": description,
        "tags": ",".join(BUNDLE_CONFIG["tags"]),
        "published": True,
        "url": "https://mikkieworld.gumroad.com"
    }
    
    if bundle_id:
        # Update bestaande bundle
        result, err = gumroad_put(f"products/{bundle_id}", bundle_data)
        action = "bijgewerkt"
    else:
        # Maak nieuwe bundle aan
        result, err = gumroad_post("products", bundle_data)
        action = "aangemaakt"
    
    if err:
        log(f"⚠️  Bundle API fout: {err}")
        # Sla op als draft
        PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
        draft_file = PRODUCTS_DIR / "bundle_draft.json"
        with open(draft_file, "w", encoding="utf-8") as f:
            json.dump({
                "config": BUNDLE_CONFIG,
                "description": description,
                "created_at": datetime.datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        log(f"💾 Bundle draft opgeslagen: {draft_file}")
        print(f"\n  {GOLD}💾 Bundle draft opgeslagen (API niet beschikbaar){RESET}")
        print(f"  {CYAN}   Locatie: ~/MIKKIE_WORLD/GUMROAD/Products/bundle_draft.json{RESET}\n")
    else:
        log(f"✅ Bundle {action}: {result.get('product', {}).get('id', 'onbekend')}")
        print(f"\n  {GREEN}✅ Bundle {action}!{RESET}")
        print(f"  {CYAN}   Prijs: €{BUNDLE_CONFIG['price']/100:.2f}{RESET}")
        print(f"  {CYAN}   URL: https://mikkieworld.gumroad.com{RESET}\n")
        tg_send(f"🌟 *Gumroad bundle {action}!*\n{BUNDLE_CONFIG['name']}\nPrijs: €{BUNDLE_CONFIG['price']/100:.2f}")

def cmd_upload_covers():
    """Upload covers naar alle Gumroad producten."""
    print(f"\n{BOLD}🖼️  Cover upload — MIKKIE WORLD{RESET}\n")
    
    products, err = get_all_products()
    if err:
        print(f"  {RED}❌ API fout: {err}{RESET}\n")
        return
    
    if not products:
        print(f"  {GOLD}Geen producten gevonden{RESET}\n")
        return
    
    uploaded = 0
    for p in products:
        product_name = p.get("name", "")
        product_id = p.get("id")
        
        # Zoek bijpassend karakter
        char_name = None
        for char in CHARACTERS:
            if char["name"] in product_name.upper():
                char_name = char["name"]
                break
        
        if not char_name:
            continue
        
        cover = find_cover_for_character(char_name)
        if not cover:
            log(f"  ⚠️  Geen cover gevonden voor {char_name}")
            continue
        
        log(f"  📤 Upload cover voor {char_name}: {cover.name}")
        result, err = upload_cover_to_product(product_id, cover)
        
        if err:
            log(f"  ❌ Upload fout voor {char_name}: {err}")
        else:
            log(f"  ✅ Cover geüpload voor {char_name}")
            uploaded += 1
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n  {GREEN}✅ {uploaded} covers geüpload{RESET}\n")
    if uploaded > 0:
        tg_send(f"🖼️ *{uploaded} Gumroad covers geüpload!*")

def cmd_update_descriptions():
    """Update alle product beschrijvingen via Grok."""
    print(f"\n{BOLD}📝 Beschrijvingen updaten — MIKKIE WORLD{RESET}\n")
    
    products, err = get_all_products()
    if err:
        print(f"  {RED}❌ API fout: {err}{RESET}\n")
        return
    
    updated = 0
    for p in products:
        product_name = p.get("name", "")
        product_id = p.get("id")
        
        # Zoek bijpassend karakter
        char = None
        for c in CHARACTERS:
            if c["name"] in product_name.upper():
                char = c
                break
        
        if not char:
            continue
        
        print(f"  {GOLD}Beschrijving genereren voor {char['name']}...{RESET}")
        description = generate_product_description(char)
        
        result, err = gumroad_put(f"products/{product_id}", {"description": description})
        if err:
            log(f"  ❌ Update fout voor {char['name']}: {err}")
        else:
            log(f"  ✅ Beschrijving bijgewerkt voor {char['name']}")
            updated += 1
        
        time.sleep(1)
    
    print(f"\n  {GREEN}✅ {updated} beschrijvingen bijgewerkt{RESET}\n")
    if updated > 0:
        tg_send(f"📝 *{updated} Gumroad beschrijvingen bijgewerkt!*")

def cmd_prices():
    """Toon en update productprijzen."""
    print(f"\n{BOLD}💰 GUMROAD PRIJZEN — MIKKIE WORLD{RESET}\n")
    
    products, err = get_all_products()
    if err:
        print(f"  {RED}❌ API fout: {err}{RESET}\n")
        return
    
    print(f"  {'Product':<45} {'Prijs':>8} {'Verkopen':>10} {'Omzet':>10}")
    print(f"  {'─'*45} {'─'*8} {'─'*10} {'─'*10}")
    
    total = 0
    for p in products:
        name = p.get("name", "Onbekend")[:44]
        price = p.get("price", 0) / 100
        sales = p.get("sales_count", 0)
        revenue = price * sales
        total += revenue
        print(f"  {name:<45} €{price:>6.2f} {sales:>10} €{revenue:>8.2f}")
    
    print(f"\n  {GREEN}Totaal: €{total:.2f}{RESET}\n")

def cmd_create_character_products():
    """Maak producten aan voor alle 7 karakters (als ze nog niet bestaan)."""
    print(f"\n{BOLD}🎨 Karakter producten aanmaken...{RESET}\n")
    
    products, err = get_all_products()
    existing_names = [p.get("name", "").upper() for p in (products or [])]
    
    created = 0
    for char in CHARACTERS:
        product_name = f"MIKKIE WORLD — {char['name']} {char['emoji']} Kleurplaten & Stickers"
        
        if any(char["name"] in name for name in existing_names):
            log(f"  ⏭️  {char['name']} bestaat al")
            continue
        
        print(f"  {GOLD}Aanmaken: {char['name']}...{RESET}")
        description = generate_product_description(char)
        
        result, err = gumroad_post("products", {
            "name": product_name,
            "price": char["price"],
            "description": description,
            "tags": f"kinderen,kleurplaten,avontuur,{char['name'].lower()},MIKKIE WORLD",
            "published": True
        })
        
        if err:
            log(f"  ❌ Aanmaken fout voor {char['name']}: {err}")
        else:
            log(f"  ✅ Product aangemaakt: {char['name']}")
            created += 1
        
        time.sleep(1)
    
    print(f"\n  {GREEN}✅ {created} producten aangemaakt{RESET}\n")
    if created > 0:
        tg_send(f"🎨 *{created} Gumroad producten aangemaakt!*")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "status":
        cmd_status()
    elif cmd == "bundle":
        cmd_bundle()
    elif cmd == "upload-covers":
        cmd_upload_covers()
    elif cmd == "descriptions":
        cmd_update_descriptions()
    elif cmd == "prices":
        cmd_prices()
    elif cmd == "create":
        cmd_create_character_products()
    else:
        print(f"Gebruik: python3 mikkie_gumroad_bundle.py [status|bundle|upload-covers|descriptions|prices|create]")
