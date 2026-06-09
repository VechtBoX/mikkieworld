#!/usr/bin/env python3
"""
🎵 MIKKIE WORLD — TikTok Agent
Automatisch TikTok video captions, hooks en hashtag strategieën genereren.
TikTok is het #1 platform voor virale kinderencontent.

Gebruik:
  python3 mikkie_tiktok.py caption         # Genereer caption voor vandaag
  python3 mikkie_tiktok.py hook            # Genereer 5 video hooks
  python3 mikkie_tiktok.py hashtags        # Genereer trending hashtag set
  python3 mikkie_tiktok.py script          # Genereer volledig video script
  python3 mikkie_tiktok.py weekly          # Genereer weekplanning
  python3 mikkie_tiktok.py trends          # Toon TikTok trends voor kinderencontent
"""

import os, sys, json, time, datetime
from pathlib import Path
from openai import OpenAI

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
AGENTS_DIR   = Path.home() / "mikkieworld"
WORLD_DIR    = Path.home() / "MIKKIE_WORLD"
TIKTOK_DIR   = WORLD_DIR / "SOCIAL" / "TikTok"
LOG_FILE     = WORLD_DIR / "LOGS" / "tiktok.log"

api_key  = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
client   = OpenAI(api_key=api_key, base_url=base_url)
model    = "grok-3" if os.environ.get("XAI_API_KEY") else "gpt-4o-mini"

# Karakters per dag
CHARACTERS = {
    0: {"name": "MIKKIE",   "role": "The Hero",           "vibe": "avontuurlijk, moedig, energiek",    "color": "#3A8FA8"},
    1: {"name": "BUBBLES",  "role": "The Loyal Sidekick",  "vibe": "vrolijk, speels, loyaal",            "color": "#D4A017"},
    2: {"name": "KNOEST",   "role": "The Forest Keeper",   "vibe": "mysterieus, oud, wijs",              "color": "#5B9957"},
    3: {"name": "FIDO",     "role": "The Dragon",          "vibe": "krachtig, vurig, beschermend",       "color": "#E84040"},
    4: {"name": "NYX",      "role": "The Night Princess",  "vibe": "magisch, dromerig, nacht",           "color": "#6B4FA8"},
    5: {"name": "ZERA",     "role": "The Guardian Angel",  "vibe": "kalm, heilig, beschermend",          "color": "#F8F4EB"},
    6: {"name": "ORA",      "role": "The Wise Owl",        "vibe": "wijs, mysterieus, nacht",            "color": "#D4A017"}
}

# TikTok trending hashtags voor kinderencontent (2025-2026)
BASE_HASHTAGS = {
    "nl": ["#kinderen", "#buitenspelen", "#avontuur", "#kleurplaten", "#kindervideo",
           "#vaderenkind", "#magisch", "#sprookje", "#creatief", "#speeltijd"],
    "en": ["#kidsoftiktok", "#coloringpage", "#kidsvideo", "#adventure", "#magical",
           "#childrensbook", "#outdoorplay", "#fatherson", "#kidscontent", "#fantasy"],
    "trending": ["#fyp", "#foryou", "#viral", "#trending", "#tiktokforkids",
                 "#kidstok", "#parenttok", "#familytok", "#storytime", "#animation"]
}

# Video formats voor TikTok
VIDEO_FORMATS = {
    "kleurplaat_reveal": {
        "duration": "15-30s",
        "hook": "Raad eens wie dit is! 🤔",
        "format": "Reveal van kleurplaat → karakter animatie",
        "cta": "Gratis downloaden via link in bio!"
    },
    "buiten_challenge": {
        "duration": "30-60s",
        "hook": "Kan jij dit avontuur ook doen? 🌿",
        "format": "Outdoor activiteit challenge met MIKKIE karakter",
        "cta": "Tag een vriend die dit ook kan!"
    },
    "verhaal_snippet": {
        "duration": "60s",
        "hook": "Dit verhaal zal je verrassen... 📖",
        "format": "Kort verhaal fragment met voice-over",
        "cta": "Volg voor meer MIKKIE verhalen!"
    },
    "karakter_intro": {
        "duration": "15s",
        "hook": "Ontmoet [KARAKTER]! 🌟",
        "format": "Snelle karakter introductie met muziek",
        "cta": "Welk karakter is jouw favoriet? Comment!"
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

def get_today_character():
    weekday = datetime.datetime.now().weekday()
    return CHARACTERS[weekday]

def save_tiktok_draft(filename: str, content: dict):
    """Sla TikTok draft op als JSON bestand."""
    TIKTOK_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    draft_file = TIKTOK_DIR / f"{filename}_{ts}.json"
    with open(draft_file, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    return draft_file

# ═══════════════════════════════════════════════════════
# GROK GENERATORS
# ═══════════════════════════════════════════════════════
def generate_tiktok_caption(character: dict, video_format: str = "kleurplaat_reveal") -> dict:
    """Genereer een TikTok caption via Grok."""
    
    fmt = VIDEO_FORMATS.get(video_format, VIDEO_FORMATS["kleurplaat_reveal"])
    
    prompt = f"""Je schrijft TikTok content voor MIKKIE WORLD — een magisch kindermerk.

Karakter: {character['name']} — {character['role']}
Vibe: {character['vibe']}
Video format: {video_format} ({fmt['duration']})
Hook concept: {fmt['hook']}

Schrijf TikTok content die:
1. Begint met een STERKE hook (eerste 3 seconden = alles)
2. Ouders en kinderen aanspreekt (doelgroep: ouders 25-40)
3. COPPA-safe is (geen persoonlijke data)
4. Viral potentieel heeft (emotie, verrassing, of challenge)
5. Eindigt met een duidelijke call-to-action

Geef terug als JSON:
{{
  "hook": "...",
  "caption": "...",
  "cta": "...",
  "hashtags": "...",
  "video_idea": "...",
  "trending_sound_suggestion": "..."
}}

Caption max 150 tekens. Hashtags: mix Nederlands + Engels + trending."""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.8
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Caption fout: {e}")
    
    # Fallback
    all_tags = (BASE_HASHTAGS["nl"][:5] + BASE_HASHTAGS["en"][:5] + BASE_HASHTAGS["trending"][:5])
    return {
        "hook": f"Ontmoet {character['name']} — de {character['role']}! 🌟",
        "caption": f"MIKKIE WORLD — {character['name']} gaat op avontuur! Avontuurlijk · Moedig · Magisch | Blijf Altijd Kind. Met je kids. ✨",
        "cta": "Gratis kleurplaten via link in bio! 👇",
        "hashtags": " ".join(all_tags),
        "video_idea": f"Toon {character['name']} in een avontuurlijke scene, gebruik MIKKIE WORLD muziek",
        "trending_sound_suggestion": "Gebruik trending kinderenmuziek of MIKKIE WORLD theme"
    }

def generate_video_hooks(character: dict, count: int = 5) -> list:
    """Genereer meerdere video hooks voor A/B testing."""
    
    prompt = f"""Je schrijft TikTok video hooks voor MIKKIE WORLD.

Karakter: {character['name']} — {character['role']}
Vibe: {character['vibe']}

Genereer {count} STERKE opening hooks (eerste 3 seconden van een video).
Elke hook moet:
- Max 10 woorden zijn
- Nieuwsgierigheid wekken OF emotie triggeren
- Geschikt zijn voor ouders met kinderen
- Uniek zijn (geen herhaling)

Geef terug als JSON array:
["hook 1", "hook 2", "hook 3", "hook 4", "hook 5"]"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.9
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Hooks fout: {e}")
    
    return [
        f"Raad eens wie {character['name']} is! 🤔",
        f"Dit verhaal zal je verrassen... 📖",
        f"Jouw kind MOET dit zien! 👀",
        f"Het magische avontuur begint hier ✨",
        f"Waarom buiten spelen zo belangrijk is 🌿"
    ]

def generate_video_script(character: dict, format_type: str = "karakter_intro") -> dict:
    """Genereer een volledig TikTok video script."""
    
    fmt = VIDEO_FORMATS.get(format_type, VIDEO_FORMATS["karakter_intro"])
    
    prompt = f"""Je schrijft een TikTok video script voor MIKKIE WORLD.

Karakter: {character['name']} — {character['role']}
Vibe: {character['vibe']}
Format: {format_type} ({fmt['duration']})

Schrijf een volledig video script met:
1. HOOK (0-3s): Openingszin die stopt met scrollen
2. INTRO (3-10s): Snel karakter introduceren
3. BODY (10-45s): Hoofdinhoud (verhaal/activiteit/reveal)
4. CTA (45-60s): Call-to-action

Geef terug als JSON:
{{
  "hook_text": "...",
  "hook_visual": "...",
  "intro_text": "...",
  "body_text": "...",
  "body_visual": "...",
  "cta_text": "...",
  "music_note": "...",
  "total_duration": "..."
}}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Script fout: {e}")
    
    return {
        "hook_text": f"Ontmoet {character['name']}!",
        "hook_visual": f"Close-up van {character['name']} karakter illustratie",
        "intro_text": f"{character['name']} is {character['role']} in MIKKIE WORLD",
        "body_text": f"Vertel het verhaal van {character['name']} en zijn avonturen",
        "body_visual": "Animatie of illustratie van het karakter in actie",
        "cta_text": "Volg @mikkieworld voor meer avonturen! Gratis kleurplaten via link in bio!",
        "music_note": "Gebruik MIKKIE WORLD theme muziek",
        "total_duration": fmt["duration"]
    }

def generate_hashtag_strategy(character: dict) -> dict:
    """Genereer een complete hashtag strategie."""
    
    prompt = f"""Je bent een TikTok hashtag expert voor kinderencontent.

Karakter: {character['name']} — {character['role']}
Merk: MIKKIE WORLD (magisch kindermerk, buiten spelen, vader-kind)

Genereer een complete hashtag strategie:
1. NICHE hashtags (5): specifiek voor dit karakter/content type
2. COMMUNITY hashtags (5): voor de ouder/kind community
3. TRENDING hashtags (5): momenteel trending op TikTok
4. BRAND hashtags (3): altijd gebruiken

Geef terug als JSON:
{{
  "niche": ["...", "...", "...", "...", "..."],
  "community": ["...", "...", "...", "...", "..."],
  "trending": ["...", "...", "...", "...", "..."],
  "brand": ["#MikkieWorld", "...", "..."],
  "full_set": "...",
  "tip": "..."
}}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Hashtag fout: {e}")
    
    all_tags = BASE_HASHTAGS["nl"] + BASE_HASHTAGS["en"] + BASE_HASHTAGS["trending"]
    return {
        "niche": BASE_HASHTAGS["nl"][:5],
        "community": BASE_HASHTAGS["en"][:5],
        "trending": BASE_HASHTAGS["trending"][:5],
        "brand": ["#MikkieWorld", "#BuitenSpelen", "#Avontuur"],
        "full_set": " ".join(all_tags[:20]),
        "tip": "Gebruik max 5-8 hashtags per video voor beste bereik"
    }

# ═══════════════════════════════════════════════════════
# COMMANDO'S
# ═══════════════════════════════════════════════════════
def cmd_caption():
    """Genereer TikTok caption voor vandaag's karakter."""
    char = get_today_character()
    log(f"🎵 TikTok caption genereren voor: {char['name']}")
    
    caption = generate_tiktok_caption(char)
    
    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"  🎵 TIKTOK CAPTION — {char['name']}")
    print(f"{'─'*60}{RESET}")
    print(f"\n  {GOLD}🪝 HOOK:{RESET}")
    print(f"  {caption.get('hook', '')}")
    print(f"\n  {GOLD}📝 CAPTION:{RESET}")
    print(f"  {caption.get('caption', '')}")
    print(f"\n  {GOLD}📢 CTA:{RESET}")
    print(f"  {caption.get('cta', '')}")
    print(f"\n  {GOLD}#️⃣  HASHTAGS:{RESET}")
    print(f"  {caption.get('hashtags', '')}")
    print(f"\n  {GOLD}🎬 VIDEO IDEE:{RESET}")
    print(f"  {caption.get('video_idea', '')}")
    print(f"\n  {GOLD}🎵 GELUID:{RESET}")
    print(f"  {caption.get('trending_sound_suggestion', '')}")
    print(f"{'═'*60}{RESET}\n")
    
    draft = save_tiktok_draft(f"{char['name']}_caption", caption)
    log(f"💾 Draft opgeslagen: {draft.name}")
    print(f"  {CYAN}📁 Draft: ~/MIKKIE_WORLD/SOCIAL/TikTok/{RESET}\n")

def cmd_hooks():
    """Genereer 5 video hooks voor A/B testing."""
    char = get_today_character()
    hooks = generate_video_hooks(char, 5)
    
    print(f"\n{BOLD}🪝 TIKTOK HOOKS — {char['name']} (A/B Test){RESET}\n")
    for i, hook in enumerate(hooks, 1):
        print(f"  {GOLD}{i}.{RESET} {hook}")
    print()
    
    draft = save_tiktok_draft(f"{char['name']}_hooks", {"hooks": hooks, "character": char["name"]})
    log(f"💾 Hooks opgeslagen: {draft.name}")

def cmd_hashtags():
    """Genereer hashtag strategie voor vandaag."""
    char = get_today_character()
    strategy = generate_hashtag_strategy(char)
    
    print(f"\n{BOLD}#️⃣  HASHTAG STRATEGIE — {char['name']}{RESET}\n")
    print(f"  {GOLD}Niche:{RESET} {' '.join(strategy.get('niche', []))}")
    print(f"  {GOLD}Community:{RESET} {' '.join(strategy.get('community', []))}")
    print(f"  {GOLD}Trending:{RESET} {' '.join(strategy.get('trending', []))}")
    print(f"  {GOLD}Brand:{RESET} {' '.join(strategy.get('brand', []))}")
    print(f"\n  {GREEN}Volledige set:{RESET}")
    print(f"  {strategy.get('full_set', '')}")
    print(f"\n  {CYAN}💡 Tip: {strategy.get('tip', '')}{RESET}\n")
    
    draft = save_tiktok_draft(f"{char['name']}_hashtags", strategy)
    log(f"💾 Hashtags opgeslagen: {draft.name}")

def cmd_script():
    """Genereer volledig video script."""
    char = get_today_character()
    
    # Kies random format
    import random
    fmt = random.choice(list(VIDEO_FORMATS.keys()))
    script = generate_video_script(char, fmt)
    
    print(f"\n{BOLD}🎬 VIDEO SCRIPT — {char['name']} ({fmt}){RESET}\n")
    print(f"  {GOLD}⏱️  Duur:{RESET} {script.get('total_duration', '30-60s')}")
    print(f"\n  {GOLD}🪝 HOOK (0-3s):{RESET}")
    print(f"  Tekst: {script.get('hook_text', '')}")
    print(f"  Beeld: {script.get('hook_visual', '')}")
    print(f"\n  {GOLD}📖 INTRO (3-10s):{RESET}")
    print(f"  {script.get('intro_text', '')}")
    print(f"\n  {GOLD}🎭 BODY (10-50s):{RESET}")
    print(f"  Tekst: {script.get('body_text', '')}")
    print(f"  Beeld: {script.get('body_visual', '')}")
    print(f"\n  {GOLD}📢 CTA (50-60s):{RESET}")
    print(f"  {script.get('cta_text', '')}")
    print(f"\n  {GOLD}🎵 MUZIEK:{RESET}")
    print(f"  {script.get('music_note', '')}")
    print()
    
    draft = save_tiktok_draft(f"{char['name']}_script_{fmt}", script)
    log(f"💾 Script opgeslagen: {draft.name}")

def cmd_weekly():
    """Genereer TikTok weekplanning."""
    print(f"\n{BOLD}📅 TIKTOK WEEKPLANNING — MIKKIE WORLD{RESET}\n")
    
    days = ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"]
    formats = list(VIDEO_FORMATS.keys())
    weekly_plan = []
    
    for day_num, char in CHARACTERS.items():
        fmt = formats[day_num % len(formats)]
        print(f"  {GOLD}{days[day_num]}: {char['name']}...{RESET}")
        
        caption = generate_tiktok_caption(char, fmt)
        hooks = generate_video_hooks(char, 3)
        
        day_plan = {
            "day": days[day_num],
            "character": char["name"],
            "format": fmt,
            "caption": caption,
            "hooks": hooks,
            "posting_time": "19:00" if day_num < 5 else "11:00"
        }
        weekly_plan.append(day_plan)
        
        draft = save_tiktok_draft(f"{days[day_num]}_{char['name']}", day_plan)
        log(f"  ✅ {days[day_num]} plan opgeslagen")
        time.sleep(0.5)
    
    # Sla weekoverzicht op
    TIKTOK_DIR.mkdir(parents=True, exist_ok=True)
    week_file = TIKTOK_DIR / f"week_{datetime.datetime.now().strftime('%Y%m%d')}_planning.json"
    with open(week_file, "w", encoding="utf-8") as f:
        json.dump(weekly_plan, f, ensure_ascii=False, indent=2)
    
    print(f"\n{GREEN}✅ 7-daagse TikTok planning gegenereerd!{RESET}")
    print(f"{CYAN}📁 Locatie: ~/MIKKIE_WORLD/SOCIAL/TikTok/{RESET}\n")
    tg_send(f"🎵 *TikTok weekplanning klaar!*\n7 video captions + hooks gegenereerd\n📁 ~/MIKKIE_WORLD/SOCIAL/TikTok/")

def cmd_trends():
    """Toon TikTok trends voor kinderencontent."""
    print(f"""
{BOLD}📈 TIKTOK TRENDS — Kinderencontent 2026{RESET}

{GOLD}Top video formats:{RESET}
  1. Kleurplaat reveal (15-30s) — hoog engagement
  2. Buiten activiteit challenge (30-60s) — viral potentieel
  3. Karakter verhaal snippet (60s) — storytelling
  4. Vader-kind duo content — emotioneel, deelbaar
  5. "Raad eens wie" mysteries — interactie

{GOLD}Beste posttijden:{RESET}
  • Doordeweeks: 19:00-21:00 (kinderen naar bed, ouders scrollen)
  • Weekend: 10:00-12:00 (ochtend activiteiten)
  • Vrijdag: 20:00 (weekend stemming)

{GOLD}Trending hashtags (juni 2026):{RESET}
  {' '.join(BASE_HASHTAGS['trending'])}

{GOLD}Content die werkt:{RESET}
  ✅ Emotionele vader-kind momenten
  ✅ "Gratis download" in caption
  ✅ Kleurplaat reveals met muziek
  ✅ Buiten avonturen challenges
  ✅ Karakter introductie series

{GOLD}Vermijd:{RESET}
  ❌ Te lange video's (>60s voor kinderencontent)
  ❌ Teveel tekst in beeld
  ❌ Saaie talking head video's
  ❌ Geen muziek gebruiken
""")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "caption"
    
    if cmd == "caption":
        cmd_caption()
    elif cmd == "hook":
        cmd_hooks()
    elif cmd == "hashtags":
        cmd_hashtags()
    elif cmd == "script":
        cmd_script()
    elif cmd == "weekly":
        cmd_weekly()
    elif cmd == "trends":
        cmd_trends()
    else:
        print(f"Gebruik: python3 mikkie_tiktok.py [caption|hook|hashtags|script|weekly|trends]")
