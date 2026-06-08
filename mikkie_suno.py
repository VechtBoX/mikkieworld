#!/usr/bin/env python3
"""
🎵 MIKKIE WORLD — Suno Muziek Agent
Automatisch MIKKIE avonturenmuziek genereren voor Reels en TikTok.
Gebruikt Suno API (als beschikbaar) of genereert geoptimaliseerde muziek-prompts.

Gebruik:
  python3 mikkie_suno.py generate          # Genereer muziek voor vandaag's karakter
  python3 mikkie_suno.py prompt            # Genereer Suno prompt (geen API nodig)
  python3 mikkie_suno.py playlist          # Toon de volledige MIKKIE playlist
  python3 mikkie_suno.py weekly            # Genereer prompts voor de hele week
"""

import os, sys, json, time, datetime, random
from pathlib import Path
from openai import OpenAI

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
SUNO_API_KEY   = os.environ.get("SUNO_API_KEY", "")
SUNO_API_URL   = "https://studio-api.suno.ai/api/external/generate/"
AGENTS_DIR     = Path.home() / "mikkieworld"
WORLD_DIR      = Path.home() / "MIKKIE_WORLD"
MUSIC_DIR      = WORLD_DIR / "CONTENT" / "Video" / "Music"
PROMPTS_DIR    = WORLD_DIR / "CONTENT" / "Video" / "MusicPrompts"
LOG_FILE       = WORLD_DIR / "LOGS" / "suno.log"

# Grok voor prompt generatie
api_key  = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
client   = OpenAI(api_key=api_key, base_url=base_url)
model    = "grok-3" if os.environ.get("XAI_API_KEY") else "gpt-4o-mini"

# MIKKIE karakters per dag van de week
CHARACTERS = {
    0: {"name": "MIKKIE",   "role": "The Hero",           "vibe": "avontuurlijk, moedig, energiek"},
    1: {"name": "BUBBLES",  "role": "The Loyal Sidekick",  "vibe": "vrolijk, speels, loyaal"},
    2: {"name": "KNOEST",   "role": "The Forest Keeper",   "vibe": "mysterieus, oud, wijs"},
    3: {"name": "FIDO",     "role": "The Dragon",          "vibe": "krachtig, vurig, beschermend"},
    4: {"name": "NYX",      "role": "The Night Princess",  "vibe": "magisch, dromerig, nacht"},
    5: {"name": "ZERA",     "role": "The Guardian Angel",  "vibe": "kalm, heilig, beschermend"},
    6: {"name": "ORA",      "role": "The Wise Owl",        "vibe": "wijs, mysterieus, nacht"}
}

# Muziekstijlen per karakter
MUSIC_STYLES = {
    "MIKKIE":   "upbeat children's adventure, orchestral, heroic, 120 BPM",
    "BUBBLES":  "playful bubbly pop, xylophone, happy, 130 BPM",
    "KNOEST":   "mystical forest ambient, deep drums, ancient, 80 BPM",
    "FIDO":     "epic dragon theme, brass, powerful, 100 BPM",
    "NYX":      "dreamy night lullaby, piano, magical, 70 BPM",
    "ZERA":     "angelic choir, harp, peaceful, 90 BPM",
    "ORA":      "wise owl jazz, flute, mysterious, 95 BPM"
}

# Tekst templates per karakter (voor Suno lyrics)
LYRICS_TEMPLATES = {
    "MIKKIE": """[Verse 1]
Mikkie rent door het bos, de wind in zijn haar
Avontuur roept hem, hij is altijd klaar
Met moed in zijn hart en een glimlach zo breed
Mikkie de held, hij gaat altijd mee

[Chorus]
Mikkie, Mikkie, avontuur!
Mikkie, Mikkie, elke dag opnieuw!
Buiten spelen, dat is zijn droom
Mikkie WORLD, de magie bloeit!""",

    "BUBBLES": """[Verse 1]
Bubbles springt en danst in de zon
Ze lacht en zingt van het begin tot het eind
Trouw als een vriend, altijd aan je zij
Bubbles de sidekick, zo blij en zo vrij

[Chorus]
Bubbles, Bubbles, vrolijk en blij!
Bubbles, Bubbles, altijd erbij!
Samen spelen, dat is de magie
Bubbles WORLD, zo vrij!""",

    "KNOEST": """[Verse 1]
Knoest de boswachter, oud en wijs
Zijn wortels diep in het aardse paradijs
Hij fluistert verhalen van lang geleden
Van bomen en dieren in vrede en vrede

[Chorus]
Knoest, Knoest, wachter van het bos!
Knoest, Knoest, zijn kracht is grendeloos!
Luister naar de natuur, ze spreekt tot jou
Knoest WORLD, eeuwig trouw!""",

    "FIDO": """[Verse 1]
Fido de draak, zijn vleugels zo groot
Hij vliegt door de wolken, hij kent geen nood
Zijn adem van vuur, zijn schubben zo sterk
Fido beschermt, dat is zijn werk

[Chorus]
Fido, Fido, draak van het licht!
Fido, Fido, hij vecht voor het recht!
Vlieg met me mee, naar het avontuur
Fido WORLD, voor altijd en nu!""",

    "NYX": """[Verse 1]
Nyx de nachtprinses, sterren in haar haar
Ze danst op de maan als de nacht valt klaar
Haar magie straalt in het donker zo diep
Ze zingt een lied als de wereld slaapt

[Chorus]
Nyx, Nyx, prinses van de nacht!
Nyx, Nyx, vol van magie en kracht!
Droom maar zacht, de sterren waken
Nyx WORLD, dromen maken!""",

    "ZERA": """[Verse 1]
Zera de engel, haar vleugels zo wit
Ze zweeft door de hemel, haar hart vol met licht
Ze beschermt de kinderen, dag en nacht
Zera de hoeder, vol liefde en kracht

[Chorus]
Zera, Zera, engel van het licht!
Zera, Zera, ze beschermt jou dicht!
Voel haar vleugels, warm en zacht
Zera WORLD, vol liefde en kracht!""",

    "ORA": """[Verse 1]
Ora de uil, zijn ogen zo groot
Hij ziet alles in het donker, hij kent geen nood
Zijn wijsheid is oud, zijn kennis zo diep
Ora de wijze, hij nooit slaapt

[Chorus]
Ora, Ora, uil van de nacht!
Ora, Ora, vol wijsheid en kracht!
Leer van de sterren, ze vertellen veel
Ora WORLD, het eeuwige spel!"""
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

def get_today_character():
    """Geef het karakter van vandaag terug (op basis van dag van de week)."""
    weekday = datetime.datetime.now().weekday()
    return CHARACTERS[weekday]

# ═══════════════════════════════════════════════════════
# GROK PROMPT GENERATOR
# ═══════════════════════════════════════════════════════
def generate_suno_prompt(character: dict, purpose: str = "reel") -> dict:
    """Genereer een geoptimaliseerde Suno muziek-prompt via Grok."""
    
    style = MUSIC_STYLES.get(character["name"], "children's adventure music")
    lyrics = LYRICS_TEMPLATES.get(character["name"], "")
    
    purpose_context = {
        "reel":    "30 seconden Instagram Reel intro muziek",
        "tiktok":  "15 seconden TikTok hook muziek",
        "full":    "2 minuten volledig kinderlied",
        "ambient": "5 minuten achtergrondmuziek voor video's"
    }.get(purpose, "30 seconden Reel muziek")
    
    prompt = f"""Je bent een muziekproducer voor MIKKIE WORLD — een magisch kindermerk.

Karakter: {character['name']} — {character['role']}
Vibe: {character['vibe']}
Stijl: {style}
Doel: {purpose_context}

Maak een Suno AI muziek-prompt die:
1. Geschikt is voor kinderen (COPPA-safe)
2. De karakter-vibe perfect weergeeft
3. Energiek genoeg is voor social media
4. Magisch en avontuurlijk klinkt

Geef terug als JSON:
{{
  "style_prompt": "...",
  "title": "...",
  "duration_hint": "...",
  "mood_tags": ["...", "..."],
  "suno_tags": "..."
}}

De style_prompt moet direct in Suno ingevoerd kunnen worden (max 200 tekens)."""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.8
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Prompt generatie fout: {e}")
    
    # Fallback
    return {
        "style_prompt": f"children's adventure music, {style}, magical, uplifting, MIKKIE WORLD",
        "title": f"MIKKIE WORLD — {character['name']} Theme",
        "duration_hint": "30 seconds",
        "mood_tags": ["adventure", "magical", "children", "uplifting"],
        "suno_tags": f"children, adventure, {character['name'].lower()}, magical, uplifting"
    }

# ═══════════════════════════════════════════════════════
# SUNO API (als beschikbaar)
# ═══════════════════════════════════════════════════════
def suno_generate(style_prompt: str, title: str, lyrics: str = "", duration: int = 30):
    """Genereer muziek via Suno API."""
    if not SUNO_API_KEY:
        return None, "Geen SUNO_API_KEY ingesteld"
    
    import requests
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": style_prompt,
        "title": title,
        "tags": "children adventure magical",
        "make_instrumental": len(lyrics) == 0,
        "wait_audio": False
    }
    
    if lyrics:
        payload["lyrics"] = lyrics
    
    try:
        resp = requests.post(SUNO_API_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json(), None
        else:
            return None, f"Suno API fout {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, str(e)

def suno_check_status(task_id: str):
    """Check de status van een Suno generatie taak."""
    if not SUNO_API_KEY:
        return None, "Geen SUNO_API_KEY"
    
    import requests
    headers = {"Authorization": f"Bearer {SUNO_API_KEY}"}
    
    try:
        resp = requests.get(f"https://studio-api.suno.ai/api/external/clips/?ids={task_id}",
            headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"Status fout: {resp.status_code}"
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════════
# LOKALE OPSLAG
# ═══════════════════════════════════════════════════════
def save_music_prompt(character: str, prompt_data: dict, lyrics: str = ""):
    """Sla muziek-prompt op als lokaal bestand."""
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_file = PROMPTS_DIR / f"{character}_{ts}_suno_prompt.json"
    
    data = {
        "character": character,
        "created_at": datetime.datetime.now().isoformat(),
        "prompt": prompt_data,
        "lyrics": lyrics,
        "status": "draft",
        "suno_url": "https://suno.com",
        "instructions": f"1. Ga naar https://suno.com\n2. Klik 'Create'\n3. Plak style_prompt: {prompt_data.get('style_prompt', '')}\n4. Voeg lyrics toe (optioneel)\n5. Genereer en download"
    }
    
    with open(prompt_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Sla ook lyrics apart op als .txt
    if lyrics:
        lyrics_file = PROMPTS_DIR / f"{character}_{ts}_lyrics.txt"
        with open(lyrics_file, "w", encoding="utf-8") as f:
            f.write(f"# {prompt_data.get('title', character + ' Theme')}\n\n")
            f.write(lyrics)
    
    return prompt_file

# ═══════════════════════════════════════════════════════
# COMMANDO'S
# ═══════════════════════════════════════════════════════
def cmd_generate():
    """Genereer muziek voor het karakter van vandaag."""
    char = get_today_character()
    log(f"🎵 Muziek genereren voor: {char['name']} ({char['role']})")
    
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  🎵 SUNO MUZIEK — {char['name']}")
    print(f"  {char['role']} | {char['vibe']}")
    print(f"{'═'*60}{RESET}\n")
    
    # Genereer prompts voor Reel en TikTok
    for purpose in ["reel", "tiktok"]:
        print(f"  {GOLD}Genereer {purpose.upper()} prompt...{RESET}")
        prompt_data = generate_suno_prompt(char, purpose)
        lyrics = LYRICS_TEMPLATES.get(char["name"], "")
        
        print(f"\n  {BOLD}📝 {purpose.upper()} Prompt:{RESET}")
        print(f"  Style: {prompt_data.get('style_prompt', '')}")
        print(f"  Title: {prompt_data.get('title', '')}")
        print(f"  Mood:  {', '.join(prompt_data.get('mood_tags', []))}")
        
        if SUNO_API_KEY:
            # Probeer echte API
            result, err = suno_generate(
                prompt_data["style_prompt"],
                prompt_data["title"],
                lyrics if purpose == "full" else ""
            )
            if result:
                log(f"✅ Suno generatie gestart: {result}")
                tg_send(f"🎵 *Suno muziek gestart!*\n{char['name']} {purpose}\n{prompt_data['title']}")
            else:
                log(f"⚠️  Suno API fout: {err}")
        
        # Altijd opslaan als draft
        draft = save_music_prompt(char["name"], prompt_data, lyrics)
        log(f"💾 Prompt opgeslagen: {draft.name}")
    
    print(f"\n{GREEN}✅ Muziek-prompts gegenereerd!{RESET}")
    print(f"{CYAN}📁 Locatie: ~/MIKKIE_WORLD/CONTENT/Video/MusicPrompts/{RESET}")
    
    if not SUNO_API_KEY:
        print(f"\n{GOLD}ℹ️  Voeg SUNO_API_KEY toe voor automatisch genereren{RESET}")
        print(f"{GOLD}   Of gebruik de prompts handmatig op https://suno.com{RESET}\n")

def cmd_prompt():
    """Genereer alleen een Suno prompt (geen API nodig)."""
    char = get_today_character()
    prompt_data = generate_suno_prompt(char, "reel")
    lyrics = LYRICS_TEMPLATES.get(char["name"], "")
    
    print(f"\n{BOLD}🎵 SUNO PROMPT — {char['name']}{RESET}\n")
    print(f"  {GOLD}Style Prompt (kopieer dit naar Suno):{RESET}")
    print(f"  {prompt_data.get('style_prompt', '')}\n")
    print(f"  {GOLD}Title:{RESET} {prompt_data.get('title', '')}")
    print(f"  {GOLD}Tags:{RESET} {prompt_data.get('suno_tags', '')}")
    
    if lyrics:
        print(f"\n  {GOLD}Lyrics:{RESET}")
        for line in lyrics.split("\n")[:10]:
            print(f"  {line}")
        print(f"  ...")
    
    print(f"\n  {CYAN}🔗 Ga naar: https://suno.com{RESET}")
    print(f"  {CYAN}   Klik 'Create' en plak de style prompt{RESET}\n")
    
    draft = save_music_prompt(char["name"], prompt_data, lyrics)
    log(f"💾 Prompt opgeslagen: {draft.name}")

def cmd_playlist():
    """Toon de volledige MIKKIE playlist."""
    print(f"\n{BOLD}🎵 MIKKIE WORLD Playlist — 7 Karakters{RESET}\n")
    
    for day, char in CHARACTERS.items():
        days = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
        style = MUSIC_STYLES.get(char["name"], "")
        print(f"  {GOLD}{days[day]}:{RESET} {char['name']} — {char['role']}")
        print(f"           Stijl: {style}")
        print()

def cmd_weekly():
    """Genereer Suno prompts voor de hele week."""
    print(f"\n{BOLD}🎵 MIKKIE WORLD — Weekplanning Muziek{RESET}\n")
    
    days = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
    all_prompts = []
    
    for day_num, char in CHARACTERS.items():
        print(f"  {GOLD}{days[day_num]}: {char['name']}...{RESET}")
        prompt_data = generate_suno_prompt(char, "reel")
        lyrics = LYRICS_TEMPLATES.get(char["name"], "")
        draft = save_music_prompt(char["name"], prompt_data, lyrics)
        all_prompts.append({
            "day": days[day_num],
            "character": char["name"],
            "title": prompt_data.get("title", ""),
            "style": prompt_data.get("style_prompt", "")
        })
        log(f"  ✅ {char['name']} prompt opgeslagen")
        time.sleep(0.5)
    
    # Sla weekoverzicht op
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    week_file = PROMPTS_DIR / f"week_{datetime.datetime.now().strftime('%Y%m%d')}_playlist.json"
    with open(week_file, "w", encoding="utf-8") as f:
        json.dump(all_prompts, f, ensure_ascii=False, indent=2)
    
    print(f"\n{GREEN}✅ 7 muziek-prompts gegenereerd!{RESET}")
    print(f"{CYAN}📁 Locatie: ~/MIKKIE_WORLD/CONTENT/Video/MusicPrompts/{RESET}\n")
    tg_send(f"🎵 *Weekplanning muziek klaar!*\n7 Suno prompts gegenereerd\n📁 ~/MIKKIE_WORLD/CONTENT/Video/MusicPrompts/")

def cmd_setup_suno():
    """Geef instructies voor Suno API setup."""
    print(f"""
{BOLD}🎵 Suno API Setup{RESET}

{GOLD}Optie 1 — Suno API (automatisch):{RESET}
  1. Ga naar https://suno.com/account
  2. Klik op 'API' of 'Developer'
  3. Genereer een API key
  4. Voeg toe aan ~/.zshrc:
     export SUNO_API_KEY=jouw_key_hier
  5. Test: python3 ~/mikkieworld/mikkie_suno.py generate

{GOLD}Optie 2 — Handmatig (gratis):{RESET}
  1. python3 ~/mikkieworld/mikkie_suno.py prompt
  2. Kopieer de style prompt
  3. Ga naar https://suno.com
  4. Plak en genereer
  5. Download MP3

{GOLD}Aanbevolen workflow:{RESET}
  • Dagelijks: python3 mikkie_suno.py generate
  • Wekelijks: python3 mikkie_suno.py weekly
  • Prompts staan in: ~/MIKKIE_WORLD/CONTENT/Video/MusicPrompts/
""")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "generate"
    
    if cmd == "generate":
        cmd_generate()
    elif cmd == "prompt":
        cmd_prompt()
    elif cmd == "playlist":
        cmd_playlist()
    elif cmd == "weekly":
        cmd_weekly()
    elif cmd == "setup":
        cmd_setup_suno()
    else:
        print(f"Gebruik: python3 mikkie_suno.py [generate|prompt|playlist|weekly|setup]")
