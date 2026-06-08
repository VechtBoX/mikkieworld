#!/usr/bin/env python3
"""
MIKKIE WORLD — 🎨 Asset Prompt Agent v1.0
════════════════════════════════════════════════════════════════
Genereert geoptimaliseerde Artistly prompts voor alle content types.
Werkt samen met mikkie_artistly_agent.py voor automatische generatie.

GEBRUIK:
  python3 mikkie_asset_prompt.py cover MIKKIE
  python3 mikkie_asset_prompt.py coloring KNOEST
  python3 mikkie_asset_prompt.py sticker FIDO
  python3 mikkie_asset_prompt.py social NYX --thema "nacht avontuur"
  python3 mikkie_asset_prompt.py all          — prompts voor alle 7 karakters
  python3 mikkie_asset_prompt.py week         — weekplan met prompts
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

BASE_DIR    = Path.home() / "mikkieworld"
MIKKIE_ROOT = Path.home() / "MIKKIE_WORLD"
LOG_FILE    = BASE_DIR / "asset_prompt.log"
PROMPTS_FILE = BASE_DIR / "generated_prompts.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("ASSET")

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# ─── Karakter visuele beschrijvingen ─────────────────────────────
KARAKTER_VISUALS = {
    "MIKKIE": {
        "beschrijving": "brave 7-year-old boy with curly brown hair, bright blue eyes, wearing an adventurer's outfit with a small backpack",
        "kleuren": "blue and gold",
        "sfeer": "adventurous, brave, curious",
        "emoji": "⚡"
    },
    "BUBBLES": {
        "beschrijving": "cheerful small blue bubble fairy with sparkly wings and a big smile, loyal companion",
        "kleuren": "crystal blue and silver",
        "sfeer": "loyal, playful, bubbly",
        "emoji": "💙"
    },
    "KNOEST": {
        "beschrijving": "wise old tree spirit with a kind face made of bark, mossy beard, gentle giant",
        "kleuren": "forest green and brown",
        "sfeer": "peaceful, wise, protective",
        "emoji": "🌳"
    },
    "FIDO": {
        "beschrijving": "friendly small dragon with golden scales, big innocent eyes, tiny wings, playful",
        "kleuren": "gold and orange",
        "sfeer": "fierce but friendly, protective, warm",
        "emoji": "🔥"
    },
    "NYX": {
        "beschrijving": "mysterious night princess with dark flowing hair, star crown, silver dress, moonlit glow",
        "kleuren": "deep purple and silver",
        "sfeer": "mysterious, dreamy, magical",
        "emoji": "🌙"
    },
    "ZERA": {
        "beschrijving": "radiant guardian angel with white wings, golden halo, gentle smile, soft light",
        "kleuren": "white and gold",
        "sfeer": "hopeful, peaceful, divine",
        "emoji": "✨"
    },
    "ORA": {
        "beschrijving": "wise old owl with round glasses, a book under wing, warm brown feathers, knowing eyes",
        "kleuren": "warm brown and amber",
        "sfeer": "wise, calm, knowledgeable",
        "emoji": "🦉"
    }
}

# ─── Content type templates ───────────────────────────────────────
CONTENT_TEMPLATES = {
    "cover": {
        "stijl": "storybook illustration, children's book cover art, vibrant colors, magical atmosphere, professional digital art",
        "formaat": "square 1:1, centered composition",
        "kwaliteit": "high detail, warm lighting, enchanting, suitable for children ages 4-10",
        "achtergrond": "magical forest with crystal blue sky, golden sunlight filtering through trees"
    },
    "coloring": {
        "stijl": "black and white coloring page, clean bold outlines, no shading, simple details suitable for children",
        "formaat": "portrait A4, clear white background",
        "kwaliteit": "thick clean lines, simple shapes, fun and engaging for children ages 4-8",
        "achtergrond": "simple outdoor scene with trees and nature elements"
    },
    "sticker": {
        "stijl": "cute sticker design, cartoon style, bold outline, transparent background ready",
        "formaat": "square, centered character, white border",
        "kwaliteit": "vibrant colors, fun expression, child-friendly, merchandise quality",
        "achtergrond": "transparent or white circle background"
    },
    "social": {
        "stijl": "social media post illustration, inspirational quote card, storybook aesthetic",
        "formaat": "square 1080x1080, text-safe margins",
        "kwaliteit": "eye-catching, shareable, emotional resonance",
        "achtergrond": "gradient of crystal blue and gold, magical particles"
    },
    "banner": {
        "stijl": "website banner, panoramic illustration, magical world",
        "formaat": "landscape 16:9 or 3:1",
        "kwaliteit": "cinematic, epic scale, inviting",
        "achtergrond": "sweeping magical landscape with all MIKKIE WORLD elements"
    }
}

def generate_prompt(karakter: str, content_type: str, thema: str = None) -> str:
    """Genereer een geoptimaliseerde Artistly prompt via Grok."""
    
    karakter = karakter.upper()
    if karakter not in KARAKTER_VISUALS:
        karakter = "MIKKIE"
    
    kar = KARAKTER_VISUALS[karakter]
    template = CONTENT_TEMPLATES.get(content_type, CONTENT_TEMPLATES["cover"])
    
    thema_text = f" The scene shows: {thema}." if thema else ""
    
    system_prompt = """Je bent een expert Artistly/Midjourney prompt engineer voor kinderboek illustraties.
Schrijf een korte, krachtige Engelse prompt (max 150 woorden) die:
1. Het karakter visueel perfect beschrijft
2. De sfeer en stijl van MIKKIE WORLD vastlegt
3. Technisch geoptimaliseerd is voor AI beeldgeneratie
4. Geschikt is voor kinderen van 4-10 jaar (veilig, vrolijk, avontuurlijk)
Geef ALLEEN de prompt tekst, geen uitleg."""

    user_prompt = f"""Maak een {content_type} prompt voor karakter {karakter}:

Karakter: {kar['beschrijving']}
Kleuren: {kar['kleuren']}
Sfeer: {kar['sfeer']}
Stijl: {template['stijl']}
Formaat: {template['formaat']}
Kwaliteit: {template['kwaliteit']}
Achtergrond: {template['achtergrond']}{thema_text}

Schrijf de volledige Artistly prompt in het Engels."""

    try:
        response = client.chat.completions.create(
            model="grok-3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"Prompt generatie fout: {e}")
        # Fallback prompt
        return f"{kar['beschrijving']}, {template['stijl']}, {kar['sfeer']}, children's book illustration, {kar['kleuren']} color palette, magical atmosphere, MIKKIE WORLD style"

def save_prompt(karakter: str, content_type: str, prompt: str, thema: str = None):
    """Sla gegenereerde prompt op."""
    prompts = []
    if PROMPTS_FILE.exists():
        try:
            prompts = json.loads(PROMPTS_FILE.read_text(encoding="utf-8"))
        except:
            prompts = []
    
    prompts.append({
        "timestamp": datetime.now().isoformat(),
        "karakter": karakter,
        "content_type": content_type,
        "thema": thema,
        "prompt": prompt
    })
    
    PROMPTS_FILE.write_text(
        json.dumps(prompts[-500:], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return
    
    command = args[0]
    
    # ── cover/coloring/sticker/social/banner KARAKTER ─────────
    if command in CONTENT_TEMPLATES:
        karakter = args[1].upper() if len(args) > 1 else "MIKKIE"
        thema = None
        
        # Zoek --thema flag
        if "--thema" in args:
            idx = args.index("--thema")
            if idx + 1 < len(args):
                thema = args[idx + 1]
        
        log.info(f"Prompt genereren: {karakter} — {command}")
        prompt = generate_prompt(karakter, command, thema)
        
        kar_info = KARAKTER_VISUALS.get(karakter, {})
        emoji = kar_info.get("emoji", "🎨")
        
        print(f"\n{'═'*60}")
        print(f"  {emoji} {karakter} — {command.upper()} PROMPT")
        print(f"{'─'*60}")
        print(f"\n{prompt}\n")
        print(f"{'═'*60}\n")
        
        save_prompt(karakter, command, prompt, thema)
        
        # Schrijf ook naar een bestand voor gebruik door artistly agent
        output_dir = MIKKIE_ROOT / "CONTENT" / command + "s" if command != "social" else MIKKIE_ROOT / "SOCIAL" / "X_Twitter"
        output_dir = BASE_DIR / "prompts"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{karakter}_{command}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        (output_dir / filename).write_text(prompt, encoding="utf-8")
        log.info(f"Prompt opgeslagen: prompts/{filename}")
    
    # ── all — alle karakters voor één content type ─────────────
    elif command == "all":
        content_type = args[1] if len(args) > 1 else "cover"
        print(f"\n🎨 Prompts genereren voor alle 7 karakters — {content_type}\n")
        
        for karakter in KARAKTER_VISUALS.keys():
            kar_info = KARAKTER_VISUALS[karakter]
            prompt = generate_prompt(karakter, content_type)
            save_prompt(karakter, content_type, prompt)
            print(f"  {kar_info['emoji']} {karakter}: {prompt[:80]}...")
            time.sleep(0.5)
        
        print(f"\n✅ Alle prompts opgeslagen in ~/mikkieworld/prompts/\n")
    
    # ── week — weekplan ────────────────────────────────────────
    elif command == "week":
        dag_namen = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
        dag_karakter = ["MIKKIE", "BUBBLES", "KNOEST", "FIDO", "NYX", "ZERA", "ORA"]
        
        print(f"\n📅 Week Prompt Plan\n")
        for i, (dag, karakter) in enumerate(zip(dag_namen, dag_karakter)):
            kar_info = KARAKTER_VISUALS[karakter]
            prompt = generate_prompt(karakter, "cover")
            save_prompt(karakter, "cover", prompt)
            print(f"  {dag} — {karakter} {kar_info['emoji']}")
            print(f"  {prompt[:100]}...\n")
            time.sleep(0.5)
        
        print(f"✅ Week plan klaar!\n")
    
    else:
        print(f"Onbekend commando: {command}")
        print(f"Beschikbaar: {', '.join(list(CONTENT_TEMPLATES.keys()) + ['all', 'week'])}")

if __name__ == "__main__":
    main()
