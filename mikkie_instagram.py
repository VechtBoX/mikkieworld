#!/usr/bin/env python3
"""
📸 MIKKIE WORLD — INSTAGRAM Agent v1.0
=======================================
Post automatisch naar Instagram via de Meta Graph API.
Ondersteunt foto posts en Reels captions.

Vereiste env vars:
  INSTAGRAM_ACCESS_TOKEN  — Meta Graph API token (lang-levend)
  INSTAGRAM_ACCOUNT_ID    — Instagram Business Account ID

Gebruik:
  python3 mikkie_instagram.py post "caption" /pad/naar/afbeelding.jpg
  python3 mikkie_instagram.py latest          → Post de laatste gegenereerde afbeelding
  python3 mikkie_instagram.py setup           → Toon setup instructies
  python3 mikkie_instagram.py status          → Check API verbinding
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
BASE_DIR      = Path.home() / "mikkieworld"
SOCIAL_DIR    = Path.home() / "MIKKIE_WORLD" / "SOCIAL"
INSTAGRAM_DIR = SOCIAL_DIR / "Instagram"
LOG_DIR       = Path.home() / "MIKKIE_WORLD" / "LOGS"
OUTPUT_DIR    = Path.home() / "mikkieworld" / "artistly_output"

for d in [INSTAGRAM_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("INSTAGRAM")

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

# ─── Meta Graph API ───────────────────────────────────────────────────────────
GRAPH_URL = "https://graph.facebook.com/v21.0"

def get_credentials():
    token      = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
    account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")
    return token, account_id

def upload_image_to_instagram(image_url: str, caption: str) -> dict:
    """
    Post een afbeelding naar Instagram via de Graph API.
    image_url moet een publiek toegankelijke URL zijn.
    """
    token, account_id = get_credentials()
    if not token or not account_id:
        return {"error": "INSTAGRAM_ACCESS_TOKEN of INSTAGRAM_ACCOUNT_ID niet ingesteld"}

    # Stap 1: Maak media container
    log.info("Stap 1/2: Media container aanmaken...")
    container_resp = requests.post(
        f"{GRAPH_URL}/{account_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": token
        },
        timeout=30
    )
    container = container_resp.json()

    if "error" in container:
        return {"error": f"Container fout: {container['error'].get('message', container['error'])}"}

    container_id = container.get("id")
    log.info(f"Container ID: {container_id}")

    # Wacht even voor verwerking
    time.sleep(3)

    # Stap 2: Publiceer de container
    log.info("Stap 2/2: Publiceren...")
    publish_resp = requests.post(
        f"{GRAPH_URL}/{account_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": token
        },
        timeout=30
    )
    result = publish_resp.json()

    if "error" in result:
        return {"error": f"Publiceer fout: {result['error'].get('message', result['error'])}"}

    return {"success": True, "post_id": result.get("id"), "container_id": container_id}

def upload_local_image(local_path: Path, caption: str) -> dict:
    """
    Upload een lokale afbeelding via imgbb (gratis) en post naar Instagram.
    Alternatief: gebruik Cloudinary of een eigen server.
    """
    # Probeer imgbb gratis upload
    imgbb_key = os.environ.get("IMGBB_API_KEY")
    if imgbb_key:
        try:
            import base64
            with open(local_path, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()

            resp = requests.post(
                "https://api.imgbb.com/1/upload",
                data={"key": imgbb_key, "image": img_data, "expiration": 600},
                timeout=30
            )
            result = resp.json()
            if result.get("success"):
                image_url = result["data"]["url"]
                log.info(f"Afbeelding geüpload naar imgbb: {image_url}")
                return upload_image_to_instagram(image_url, caption)
        except Exception as e:
            log.error(f"imgbb upload mislukt: {e}")

    # Fallback: sla op als draft voor handmatige post
    return save_as_draft(local_path, caption)

def save_as_draft(image_path: Path, caption: str) -> dict:
    """Sla op als draft voor handmatige post via Later/Buffer of direct."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    draft_dir = INSTAGRAM_DIR / "drafts"
    draft_dir.mkdir(exist_ok=True)

    # Kopieer afbeelding
    import shutil
    dest_img = draft_dir / f"post_{timestamp}{image_path.suffix}"
    shutil.copy2(image_path, dest_img)

    # Sla caption op
    caption_file = draft_dir / f"post_{timestamp}_caption.txt"
    caption_file.write_text(caption, encoding="utf-8")

    telegram(
        f"📸 INSTAGRAM DRAFT\n"
        f"Klaar voor handmatige post:\n"
        f"📁 {dest_img.name}\n"
        f"📝 {caption[:100]}..."
    )

    return {"draft": True, "image": str(dest_img), "caption_file": str(caption_file)}

# ─── Post de laatste afbeelding ───────────────────────────────────────────────
def post_latest():
    """Post de meest recente Artistly afbeelding naar Instagram."""
    # Zoek in artistly_output
    search_dirs = [OUTPUT_DIR, SOCIAL_DIR / "X_Twitter"]
    afbeeldingen = []
    for d in search_dirs:
        if d.exists():
            afbeeldingen.extend(d.glob("*.png"))
            afbeeldingen.extend(d.glob("*.jpg"))
            afbeeldingen.extend(d.glob("*.jpeg"))

    if not afbeeldingen:
        print(c("⚠️  Geen afbeeldingen gevonden", YELLOW))
        return

    # Meest recente
    afbeelding = sorted(afbeeldingen, key=lambda f: f.stat().st_mtime, reverse=True)[0]
    karakter = afbeelding.stem.split("_")[0] if "_" in afbeelding.stem else "MIKKIE"

    # Lees bijpassende caption als die bestaat
    caption_file = afbeelding.with_suffix(".txt")
    if caption_file.exists():
        caption = caption_file.read_text(encoding="utf-8").strip()
    else:
        # Genereer caption
        caption = generate_instagram_caption(karakter)

    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  📸 INSTAGRAM POST")
    print(f"  Afbeelding: {afbeelding.name}")
    print(f"  Caption: {caption[:80]}...")
    print(f"{'─'*60}{RESET}")

    result = upload_local_image(afbeelding, caption)

    if result.get("success"):
        print(c(f"  ✅ Gepost! Post ID: {result['post_id']}", GREEN))
        telegram(f"📸 INSTAGRAM\n✅ Post live!\n{caption[:100]}...")
    elif result.get("draft"):
        print(c(f"  📋 Opgeslagen als draft", YELLOW))
        print(f"  Afbeelding: {result['image']}")
    else:
        print(c(f"  ❌ Fout: {result.get('error')}", RED))

    print(f"{'═'*60}\n")

def generate_instagram_caption(karakter: str) -> str:
    """Genereer een Instagram caption via Grok."""
    try:
        from openai import OpenAI
        api_key  = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
        client   = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

        dag = datetime.now().weekday()
        karakters = {0:"MIKKIE",1:"BUBBLES",2:"KNOEST",3:"FIDO",4:"NYX",5:"ZERA",6:"ORA"}
        karakter = karakters.get(dag, "MIKKIE")

        response = client.chat.completions.create(
            model="grok-3-mini" if os.environ.get("XAI_API_KEY") else "gpt-4o-mini",
            messages=[{"role": "user", "content": f"""Schrijf een Instagram caption voor MIKKIE WORLD.
Karakter: {karakter}
Stijl: Warm, vader-kind, avontuurlijk, magisch
Formaat: 3-4 zinnen + 8-10 hashtags onderaan
Taal: Nederlands
Missie: Kinderen inspireren om buiten te spelen
Schrijf ALLEEN de caption, geen uitleg."""}],
            max_tokens=400,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"✨ {karakter} en zijn avontuur wacht op jou! Ga naar buiten en ontdek de magie. 🌟\n\n#MikkieWorld #BuitenSpelen #Avontuur #Kinderen #Magie"

# ─── Status check ─────────────────────────────────────────────────────────────
def check_status():
    token, account_id = get_credentials()
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  📸 INSTAGRAM Agent Status")
    print(f"{'─'*60}{RESET}")

    if token:
        print(f"  Access Token:  {c('✓ ingesteld', GREEN)} ({token[:20]}...)")
    else:
        print(f"  Access Token:  {c('✗ niet ingesteld', RED)}")
        print(f"  → export INSTAGRAM_ACCESS_TOKEN=<token>")

    if account_id:
        print(f"  Account ID:    {c('✓ ingesteld', GREEN)} ({account_id})")
    else:
        print(f"  Account ID:    {c('✗ niet ingesteld', RED)}")
        print(f"  → export INSTAGRAM_ACCOUNT_ID=<id>")

    if token and account_id:
        # Test API verbinding
        try:
            resp = requests.get(
                f"{GRAPH_URL}/{account_id}",
                params={"fields": "name,username", "access_token": token},
                timeout=10
            )
            data = resp.json()
            if "username" in data:
                username = data["username"]
                print(f"  Account:       {c('@' + username, GREEN)}")
                print(f"  Status:        {c('● VERBONDEN', GREEN)}")
            else:
                print(f"  Status:        {c('✗ API fout', RED)}")
                fout = data.get('error', {}).get('message', 'Onbekend')
                print(f"  Fout: {fout}")
        except Exception as e:
            print(f"  Status:        {c(f'✗ Verbinding mislukt: {e}', RED)}")
    else:
        print(f"\n  {c('Setup vereist — voer uit:', YELLOW)}")
        print(f"  python3 mikkie_instagram.py setup")

    # Drafts
    draft_dir = INSTAGRAM_DIR / "drafts"
    if draft_dir.exists():
        drafts = list(draft_dir.glob("*_caption.txt"))
        if drafts:
            print(f"\n  📋 Drafts klaar: {c(str(len(drafts)), YELLOW)} posts wachten")

    print(f"{'═'*60}\n")

def show_setup():
    print(f"""
{BOLD}{'═'*60}{RESET}
  📸 INSTAGRAM Setup — Stap voor stap
{'═'*60}{RESET}

  Stap 1: Facebook Developer Account
  ───────────────────────────────────
  1. Ga naar: https://developers.facebook.com
  2. Maak een app aan (type: Business)
  3. Voeg Instagram Graph API toe

  Stap 2: Instagram Business Account koppelen
  ────────────────────────────────────────────
  1. Zorg dat @mikkieworld777 een Business Account is
  2. Koppel aan een Facebook pagina
  3. Voeg de pagina toe aan je Facebook app

  Stap 3: Access Token ophalen
  ────────────────────────────
  1. Ga naar: https://developers.facebook.com/tools/explorer
  2. Selecteer je app
  3. Klik "Generate Access Token"
  4. Voeg permissies toe: instagram_basic, instagram_content_publish
  5. Kopieer het token

  Stap 4: Account ID ophalen
  ──────────────────────────
  curl "https://graph.facebook.com/v21.0/me/accounts?access_token=<TOKEN>"
  → Kopieer de Instagram Account ID

  Stap 5: Toevoegen aan ~/.zshrc
  ───────────────────────────────
  echo 'export INSTAGRAM_ACCESS_TOKEN=<token>' >> ~/.zshrc
  echo 'export INSTAGRAM_ACCOUNT_ID=<id>' >> ~/.zshrc
  source ~/.zshrc

  Stap 6: Testen
  ──────────────
  python3 mikkie_instagram.py status
  python3 mikkie_instagram.py latest

{'═'*60}
  💡 Tip: Gebruik imgbb.com voor gratis afbeelding hosting
  echo 'export IMGBB_API_KEY=<key>' >> ~/.zshrc
{'═'*60}
""")

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "status":
        check_status()
    elif args[0] == "setup":
        show_setup()
    elif args[0] == "latest":
        post_latest()
    elif args[0] == "post" and len(args) >= 2:
        caption = args[1]
        image   = Path(args[2]) if len(args) > 2 else None
        if image and image.exists():
            result = upload_local_image(image, caption)
            print(json.dumps(result, indent=2))
        else:
            print(c("❌ Geef een geldig afbeeldingspad op", RED))
    else:
        print("Gebruik: python3 mikkie_instagram.py [status|setup|latest|post 'caption' pad]")
