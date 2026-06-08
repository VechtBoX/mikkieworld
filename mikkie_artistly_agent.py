#!/usr/bin/env python3
"""
MIKKIE WORLD — Artistly AI Content Agent
24/7 content creation via browser automation
Genereert automatisch: Gumroad covers, kleurplaten, social media posts, stickers
"""

import os
import sys
import json
import time
import asyncio
import logging
import argparse
import datetime
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
ARTISTLY_EMAIL = os.environ.get("ARTISTLY_EMAIL", "hendrik.broeze@gmail.com")
ARTISTLY_PASSWORD = os.environ.get("ARTISTLY_PASSWORD", "")
OUTPUT_DIR = Path(os.environ.get("ARTISTLY_OUTPUT", os.path.expanduser("~/mikkieworld/artistly_output")))
LOG_FILE = Path(os.path.expanduser("~/mikkieworld/artistly_agent.log"))
STATE_FILE = Path(os.path.expanduser("~/mikkieworld/artistly_state.json"))

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("artistly-agent")

# ─── MIKKIE Content Prompts ───────────────────────────────────────────────────
CHARACTERS = {
    "MIKKIE": {
        "desc": "brave 7-year-old adventurous boy, brown hair, crystal blue eyes, wearing a green adventurer jacket",
        "color": "#3A8FA8",
        "emoji": "⚔️"
    },
    "BUBBLES": {
        "desc": "cheerful magical bubble fairy with rainbow wings, playful and joyful",
        "color": "#FF69B4",
        "emoji": "🫧"
    },
    "KNOEST": {
        "desc": "wise ancient forest tree spirit, gnarled wood face, glowing green eyes, gentle giant",
        "color": "#5B9957",
        "emoji": "🌳"
    },
    "FIDO": {
        "desc": "friendly small dragon with golden scales, big curious eyes, tiny wings",
        "color": "#D4A017",
        "emoji": "🐉"
    },
    "NYX": {
        "desc": "mysterious night princess with dark flowing hair, silver star crown, moonlight glow",
        "color": "#4B0082",
        "emoji": "🌙"
    },
    "ZERA": {
        "desc": "radiant guardian angel with golden wings, warm smile, protective aura",
        "color": "#FFD700",
        "emoji": "👼"
    },
    "ORA": {
        "desc": "wise old owl with round spectacles, purple wizard robe, ancient book",
        "color": "#8B4513",
        "emoji": "🦉"
    }
}

CONTENT_TYPES = {
    "gumroad_cover": {
        "prompt_template": "{character_desc}, magical storybook illustration, vibrant colors, children's book art style, white background, product cover art, professional quality, 1:1 square format",
        "category": "Poster Maker",
        "aspect": "1:1 (1024 X 1024) px",
        "folder": "Mikkie",
        "description": "Gumroad product cover"
    },
    "coloring_page": {
        "prompt_template": "{character_desc}, black and white coloring page for children, thick clean outlines, simple shapes, no shading, white background, printable coloring book style",
        "category": "Create From Prompt",
        "aspect": "2:3 (832 X 1216) px",
        "folder": "Mikkie",
        "description": "Kleurplaat voor Quest Bundle"
    },
    "social_post": {
        "prompt_template": "{character_desc}, magical adventure scene, vibrant storybook illustration, Instagram post style, inspirational children's content, outdoor nature setting",
        "category": "Social Media Posts",
        "aspect": "1:1 (1024 X 1024) px",
        "folder": "Mikkie",
        "description": "Social media post"
    },
    "sticker": {
        "prompt_template": "{character_desc}, cute sticker design, white outline, transparent background, chibi style, kawaii children's character, clean vector look",
        "category": "Sticker",
        "aspect": "1:1 (1024 X 1024) px",
        "folder": "Mikkie",
        "description": "Sticker voor Gelato"
    },
    "hero_banner": {
        "prompt_template": "{character_desc}, epic magical landscape background, cinematic wide shot, children's fantasy world, crystal blue and gold color palette, MIKKIE WORLD branding style",
        "category": "Create From Prompt",
        "aspect": "16:9 (1344 X 768) px",
        "folder": "Mikkie",
        "description": "Hero banner voor website"
    }
}

# ─── State Management ─────────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "generated": [],
        "last_run": None,
        "total_images": 0,
        "session_count": 0
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

# ─── Playwright Agent ─────────────────────────────────────────────────────────
async def login(page):
    """Login to Artistly"""
    log.info("Inloggen bij Artistly...")
    await page.goto("https://app.artistly.ai/login", wait_until="networkidle")
    await asyncio.sleep(2)

    # Check if already logged in
    if "personal-designs" in page.url or "dashboard" in page.url or "choose-designer" in page.url:
        log.info("Al ingelogd!")
        return True

    # Fill login form
    try:
        await page.fill('input[type="email"]', ARTISTLY_EMAIL)
        await page.fill('input[type="password"]', ARTISTLY_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/dashboard**", timeout=15000)
        log.info("Succesvol ingelogd!")
        return True
    except Exception as e:
        log.error(f"Login mislukt: {e}")
        return False

async def generate_image(page, character_name, content_type, state):
    """Generate one image for a character and content type"""
    char = CHARACTERS[character_name]
    ctype = CONTENT_TYPES[content_type]

    prompt = ctype["prompt_template"].format(character_desc=char["desc"])
    description = f"{character_name} — {ctype['description']}"

    log.info(f"Genereren: {description}")

    try:
        # Navigate to image designer
        await page.goto("https://app.artistly.ai/ai/image-designer-v6", wait_until="networkidle")
        await asyncio.sleep(2)

        # Select category if not "Create From Prompt"
        category = ctype["category"]
        if category != "Create From Prompt":
            # Click the category button
            cat_buttons = await page.query_selector_all("div.cursor-pointer, div[class*='cursor']")
            for btn in cat_buttons:
                text = await btn.inner_text()
                if category.lower() in text.lower():
                    await btn.click()
                    await asyncio.sleep(1)
                    break

        # Enter prompt
        textarea = await page.query_selector("textarea[placeholder='Enter prompt here']")
        if not textarea:
            log.error("Prompt textarea niet gevonden")
            return None

        await textarea.fill(prompt)
        await asyncio.sleep(0.5)

        # Select aspect ratio
        aspect_select = await page.query_selector("select")
        if aspect_select:
            await aspect_select.select_option(label=ctype["aspect"])
            await asyncio.sleep(0.5)

        # Select folder "Mikkie"
        folder_selects = await page.query_selector_all("select")
        for sel in folder_selects:
            options = await sel.query_selector_all("option")
            for opt in options:
                val = await opt.inner_text()
                if "Mikkie" in val:
                    await sel.select_option(label="Mikkie")
                    break

        # Click Generate
        gen_btn = await page.query_selector("#generate_image_flux, button:has-text('Generate Image')")
        if not gen_btn:
            log.error("Generate knop niet gevonden")
            return None

        await gen_btn.click()
        log.info(f"Generatie gestart voor {description}...")

        # Wait for redirect to personal-designs
        try:
            await page.wait_for_url("**/personal-designs**", timeout=30000)
            log.info(f"Generatie succesvol gestart: {description}")
        except:
            log.warning("Geen redirect naar personal-designs — mogelijk al daar")

        # Update state
        state["generated"].append({
            "character": character_name,
            "type": content_type,
            "prompt": prompt[:100],
            "timestamp": datetime.datetime.now().isoformat()
        })
        state["total_images"] += 1
        save_state(state)

        # Wait between generations to avoid rate limiting
        await asyncio.sleep(10)

        return True

    except Exception as e:
        log.error(f"Fout bij genereren {description}: {e}")
        return None

async def download_latest_images(page, output_dir, limit=10):
    """Download the latest generated images from personal-designs"""
    output_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Laatste {limit} afbeeldingen downloaden...")
    await page.goto("https://app.artistly.ai/personal-designs", wait_until="networkidle")
    await asyncio.sleep(3)

    # Find all download buttons
    download_btns = await page.query_selector_all("button:has-text('Download Image')")
    log.info(f"{len(download_btns)} afbeeldingen gevonden")

    downloaded = 0
    for i, btn in enumerate(download_btns[:limit]):
        try:
            # Get the image URL from nearby img element
            parent = await btn.evaluate_handle("el => el.closest('.group, .relative, div')")
            img = await parent.query_selector("img")
            if img:
                src = await img.get_attribute("src")
                if src and "cdn.artistly.ai" in src:
                    # Download the image
                    import urllib.request
                    filename = f"artistly_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{i:02d}.png"
                    filepath = output_dir / filename
                    urllib.request.urlretrieve(src, filepath)
                    log.info(f"Gedownload: {filename}")
                    downloaded += 1
        except Exception as e:
            log.warning(f"Download {i} mislukt: {e}")

    log.info(f"{downloaded} afbeeldingen gedownload naar {output_dir}")
    return downloaded

async def run_content_batch(characters=None, content_types=None):
    """Run a batch of content generation"""
    from playwright.async_api import async_playwright

    if not ARTISTLY_PASSWORD:
        log.error("ARTISTLY_PASSWORD niet ingesteld! Gebruik: export ARTISTLY_PASSWORD='jouw_wachtwoord'")
        return

    if characters is None:
        characters = list(CHARACTERS.keys())
    if content_types is None:
        content_types = ["gumroad_cover"]

    state = load_state()
    state["session_count"] += 1
    state["last_run"] = datetime.datetime.now().isoformat()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()

        try:
            # Login
            logged_in = await login(page)
            if not logged_in:
                log.error("Kan niet inloggen — agent stopt")
                return

            # Generate content for each character and type
            total = len(characters) * len(content_types)
            done = 0

            for char_name in characters:
                for ctype in content_types:
                    done += 1
                    log.info(f"[{done}/{total}] {char_name} × {ctype}")
                    result = await generate_image(page, char_name, ctype, state)
                    if result:
                        log.info(f"✅ {char_name} {ctype} succesvol")
                    else:
                        log.warning(f"⚠️ {char_name} {ctype} mislukt")

            # Download generated images
            await asyncio.sleep(15)  # Wait for processing
            await download_latest_images(page, OUTPUT_DIR, limit=total)

        finally:
            await browser.close()

    save_state(state)
    log.info(f"Batch klaar! {state['total_images']} totale afbeeldingen gegenereerd")

async def run_daemon():
    """24/7 daemon mode"""
    log.info("🚀 MIKKIE WORLD Artistly Agent gestart in daemon modus")
    log.info(f"Output map: {OUTPUT_DIR}")

    # Schedule:
    # - Maandag 07:00: Gumroad covers voor alle 7 karakters
    # - Woensdag 07:00: Kleurplaten voor alle 7 karakters
    # - Vrijdag 07:00: Social media posts voor alle 7 karakters
    # - Zondag 07:00: Stickers voor alle 7 karakters

    SCHEDULE = {
        0: ("gumroad_cover", "Maandag: Gumroad covers"),     # Monday
        2: ("coloring_page", "Woensdag: Kleurplaten"),        # Wednesday
        4: ("social_post", "Vrijdag: Social posts"),          # Friday
        6: ("sticker", "Zondag: Stickers"),                   # Sunday
    }

    while True:
        now = datetime.datetime.now()
        weekday = now.weekday()
        hour = now.hour

        if hour == 7 and weekday in SCHEDULE:
            ctype, desc = SCHEDULE[weekday]
            log.info(f"📅 Geplande taak: {desc}")
            await run_content_batch(
                characters=list(CHARACTERS.keys()),
                content_types=[ctype]
            )
            # Sleep 23 hours to avoid double-running
            await asyncio.sleep(23 * 3600)
        else:
            # Check every 30 minutes
            log.info(f"⏰ Wachten... volgende check over 30 min (nu: {now.strftime('%H:%M')})")
            await asyncio.sleep(1800)

# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="MIKKIE WORLD Artistly AI Content Agent")
    parser.add_argument("command", nargs="?", default="status",
                        choices=["start", "daemon", "covers", "coloring", "social", "stickers", "banners",
                                 "all", "status", "log", "download", "test"],
                        help="Commando om uit te voeren")
    parser.add_argument("--characters", "-c", nargs="+", choices=list(CHARACTERS.keys()),
                        help="Specifieke karakters (standaard: alle 7)")
    parser.add_argument("--output", "-o", help="Output map voor afbeeldingen")

    args = parser.parse_args()

    if args.output:
        global OUTPUT_DIR
        OUTPUT_DIR = Path(args.output)

    if args.command == "status":
        state = load_state()
        print("\n🎨 MIKKIE WORLD Artistly Agent Status")
        print("=" * 40)
        print(f"Totale afbeeldingen: {state.get('total_images', 0)}")
        print(f"Sessies uitgevoerd: {state.get('session_count', 0)}")
        print(f"Laatste run: {state.get('last_run', 'Nog niet gestart')}")
        print(f"Output map: {OUTPUT_DIR}")
        if OUTPUT_DIR.exists():
            files = list(OUTPUT_DIR.glob("*.png")) + list(OUTPUT_DIR.glob("*.jpg"))
            print(f"Bestanden in output: {len(files)}")
        print(f"\nLaatste 5 generaties:")
        for item in state.get("generated", [])[-5:]:
            print(f"  {item.get('timestamp', '')[:16]} — {item.get('character')} {item.get('type')}")
        print()

    elif args.command == "log":
        if LOG_FILE.exists():
            with open(LOG_FILE) as f:
                lines = f.readlines()
            print("".join(lines[-50:]))
        else:
            print("Geen log gevonden")

    elif args.command == "test":
        print("🧪 Test: 1 afbeelding genereren (MIKKIE gumroad cover)...")
        if not ARTISTLY_PASSWORD:
            print("❌ ARTISTLY_PASSWORD niet ingesteld!")
            print("   Gebruik: export ARTISTLY_PASSWORD='jouw_wachtwoord'")
            return
        asyncio.run(run_content_batch(
            characters=["MIKKIE"],
            content_types=["gumroad_cover"]
        ))

    elif args.command == "covers":
        print("🖼️  Gumroad covers genereren voor alle 7 karakters...")
        chars = args.characters or list(CHARACTERS.keys())
        asyncio.run(run_content_batch(characters=chars, content_types=["gumroad_cover"]))

    elif args.command == "coloring":
        print("🎨 Kleurplaten genereren voor alle 7 karakters...")
        chars = args.characters or list(CHARACTERS.keys())
        asyncio.run(run_content_batch(characters=chars, content_types=["coloring_page"]))

    elif args.command == "social":
        print("📱 Social media posts genereren...")
        chars = args.characters or list(CHARACTERS.keys())
        asyncio.run(run_content_batch(characters=chars, content_types=["social_post"]))

    elif args.command == "stickers":
        print("🏷️  Stickers genereren voor alle 7 karakters...")
        chars = args.characters or list(CHARACTERS.keys())
        asyncio.run(run_content_batch(characters=chars, content_types=["sticker"]))

    elif args.command == "banners":
        print("🌟 Hero banners genereren...")
        chars = args.characters or list(CHARACTERS.keys())
        asyncio.run(run_content_batch(characters=chars, content_types=["hero_banner"]))

    elif args.command == "all":
        print("🚀 Alle content types genereren voor alle 7 karakters (35 afbeeldingen)...")
        chars = args.characters or list(CHARACTERS.keys())
        asyncio.run(run_content_batch(
            characters=chars,
            content_types=["gumroad_cover", "coloring_page", "social_post", "sticker", "hero_banner"]
        ))

    elif args.command in ("start", "daemon"):
        print("🔄 Artistly Agent gestart in 24/7 daemon modus...")
        print("   Druk Ctrl+C om te stoppen")
        asyncio.run(run_daemon())

if __name__ == "__main__":
    main()
