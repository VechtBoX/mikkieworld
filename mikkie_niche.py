#!/usr/bin/env python3
"""
🔍 MIKKIE WORLD — NICHE Agent
Artistly Niche Finder integratie + Gumroad kansen analyse.
Vindt winstgevende niches voor nieuwe kleurplaten en digitale producten.

Gebruik:
  python3 mikkie_niche.py analyze          # Analyseer huidige niches
  python3 mikkie_niche.py opportunities    # Vind nieuwe Gumroad kansen
  python3 mikkie_niche.py keywords         # Genereer SEO keywords
  python3 mikkie_niche.py roadmap          # Product roadmap genereren
  python3 mikkie_niche.py competition      # Concurrentieanalyse
"""

import os, sys, json, time, datetime
from pathlib import Path
from openai import OpenAI

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
ARTISTLY_KEY = os.environ.get("ARTISTLY_API_KEY", "fd58524c-5603-44a2-a23d-a9703753084b")
GUMROAD_TOKEN = os.environ.get("GUMROAD_API_TOKEN", "9byVxzgAYPnwnhL3jPjZiVxOQrSvmQrweISCtzr00RI")
AGENTS_DIR   = Path.home() / "mikkieworld"
WORLD_DIR    = Path.home() / "MIKKIE_WORLD"
NICHE_DIR    = WORLD_DIR / "LOGS" / "Niche"
LOG_FILE     = WORLD_DIR / "LOGS" / "niche.log"

api_key  = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
client   = OpenAI(api_key=api_key, base_url=base_url)
model    = "grok-3" if os.environ.get("XAI_API_KEY") else "gpt-4o-mini"

# Huidige MIKKIE producten
CURRENT_PRODUCTS = [
    {"name": "MIKKIE Kleurplaten", "type": "coloring", "character": "MIKKIE", "price": 6.99},
    {"name": "BUBBLES Kleurplaten", "type": "coloring", "character": "BUBBLES", "price": 6.99},
    {"name": "KNOEST Kleurplaten", "type": "coloring", "character": "KNOEST", "price": 6.99},
    {"name": "FIDO Kleurplaten", "type": "coloring", "character": "FIDO", "price": 6.99},
    {"name": "NYX Kleurplaten", "type": "coloring", "character": "NYX", "price": 6.99},
    {"name": "ZERA Kleurplaten", "type": "coloring", "character": "ZERA", "price": 6.99},
    {"name": "ORA Kleurplaten", "type": "coloring", "character": "ORA", "price": 6.99},
    {"name": "7 Buitenmissies PDF", "type": "activity", "character": "ALL", "price": 4.99},
    {"name": "Complete Bundle", "type": "bundle", "character": "ALL", "price": 29.00}
]

# Potentiële nieuwe niches
NICHE_CATEGORIES = [
    "seizoensgebonden kleurplaten (lente, zomer, herfst, winter)",
    "thema kleurplaten (dieren, natuur, ruimte, zee)",
    "activiteiten boekjes (dot-to-dot, mazes, word searches)",
    "sticker sheets (printable stickers per karakter)",
    "poster sets (A4 decoratie posters voor kinderkamer)",
    "flashcards (educatief: letters, cijfers, dieren)",
    "birthday party printables (uitnodigingen, banners, tags)",
    "reward charts (beloningskaarten voor kinderen)",
    "bedtime story scripts (vader leest voor)",
    "outdoor adventure kits (printable activiteiten voor buiten)"
]

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

def save_niche_report(filename: str, data: dict):
    """Sla niche rapport op."""
    NICHE_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = NICHE_DIR / f"{filename}_{ts}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return report_file

# ═══════════════════════════════════════════════════════
# GROK ANALYSE
# ═══════════════════════════════════════════════════════
def analyze_niche_opportunities() -> dict:
    """Analyseer niche kansen via Grok."""
    
    products_str = "\n".join([f"- {p['name']} (€{p['price']})" for p in CURRENT_PRODUCTS])
    niches_str = "\n".join([f"- {n}" for n in NICHE_CATEGORIES])
    
    prompt = f"""Je bent een digitale product expert gespecialiseerd in kinderencontent op Gumroad.

MIKKIE WORLD is een magisch kindermerk (7 karakters: MIKKIE, BUBBLES, KNOEST, FIDO, NYX, ZERA, ORA).
Doelgroep: Ouders met kinderen 4-10 jaar, focus op buiten spelen en vader-kind avonturen.
Platform: Gumroad (digitale downloads)
Huidige producten:
{products_str}

Potentiële nieuwe niches:
{niches_str}

Analyseer welke 5 nieuwe producten het meeste potentieel hebben voor MIKKIE WORLD.
Overweeg: zoekvolume, concurrentie, prijs, productietijd, fit met merk.

Geef terug als JSON:
{{
  "top_5_opportunities": [
    {{
      "product_name": "...",
      "niche": "...",
      "estimated_price": 0.00,
      "difficulty": "laag/medium/hoog",
      "revenue_potential": "laag/medium/hoog",
      "time_to_create": "...",
      "why": "...",
      "first_step": "..."
    }}
  ],
  "quick_wins": ["...", "...", "..."],
  "avoid": ["...", "..."],
  "monthly_revenue_estimate": "..."
}}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Analyse fout: {e}")
    
    return {
        "top_5_opportunities": [
            {"product_name": "MIKKIE Seizoen Kleurplaten — Zomer", "niche": "seizoensgebonden", "estimated_price": 7.99, "difficulty": "laag", "revenue_potential": "hoog", "time_to_create": "2-3 uur", "why": "Zomer = hoog zoekvolume voor buiten activiteiten", "first_step": "Maak 10 zomer kleurplaten via Artistly"},
            {"product_name": "MIKKIE Reward Chart", "niche": "opvoeding tools", "estimated_price": 4.99, "difficulty": "laag", "revenue_potential": "medium", "time_to_create": "1-2 uur", "why": "Ouders zoeken altijd beloningskaarten", "first_step": "Ontwerp printable beloningskaart met MIKKIE"},
            {"product_name": "MIKKIE Birthday Party Kit", "niche": "verjaardagsfeestje", "estimated_price": 12.99, "difficulty": "medium", "revenue_potential": "hoog", "time_to_create": "4-5 uur", "why": "Hoge intentie aankoop, ouders betalen graag voor feestje", "first_step": "Maak uitnodiging + banner + tags set"},
            {"product_name": "MIKKIE Outdoor Adventure Kit", "niche": "buiten activiteiten", "estimated_price": 9.99, "difficulty": "medium", "revenue_potential": "hoog", "time_to_create": "3-4 uur", "why": "Perfect fit met MIKKIE merkwaarden", "first_step": "Maak printable bingo, scavenger hunt, activiteiten kaarten"},
            {"product_name": "MIKKIE Sticker Sheet Bundle", "niche": "stickers", "estimated_price": 5.99, "difficulty": "laag", "revenue_potential": "medium", "time_to_create": "2 uur", "why": "Kinderen houden van stickers, ouders kopen ze graag", "first_step": "Maak sticker sheets per karakter via Artistly"}
        ],
        "quick_wins": ["Seizoen kleurplaten", "Reward charts", "Sticker sheets"],
        "avoid": ["Educatieve flashcards (te veel concurrentie)", "Kleurboeken (te duur om te produceren)"],
        "monthly_revenue_estimate": "€200-500 bij 5 nieuwe producten"
    }

def generate_seo_keywords(product_type: str = "kleurplaten") -> dict:
    """Genereer SEO keywords voor Gumroad producten."""
    
    prompt = f"""Je bent een SEO expert voor Gumroad en Etsy kinderencontent.

Product type: {product_type}
Merk: MIKKIE WORLD (magisch kindermerk, buiten spelen, avontuur)
Doelgroep: Ouders met kinderen 4-10 jaar (NL + internationale markt)

Genereer een complete keyword strategie:
1. HOOFD keywords (5): hoog zoekvolume, direct relevant
2. LONG-TAIL keywords (10): specifiek, lage concurrentie
3. GUMROAD tags (10): exact voor Gumroad product tags
4. ETSY tags (13): exact voor Etsy listing tags

Geef terug als JSON:
{{
  "main_keywords": ["...", "...", "...", "...", "..."],
  "long_tail": ["...", "...", "...", "...", "...", "...", "...", "...", "...", "..."],
  "gumroad_tags": ["...", "...", "...", "...", "...", "...", "...", "...", "...", "..."],
  "etsy_tags": ["...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "...", "..."],
  "title_formula": "...",
  "description_tip": "..."
}}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.6
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Keywords fout: {e}")
    
    return {
        "main_keywords": ["kleurplaten kinderen", "coloring pages kids", "printable coloring", "adventure coloring", "kids printables"],
        "long_tail": ["gratis kleurplaten kinderen downloaden", "avontuur kleurplaten 4-8 jaar", "MIKKIE WORLD kleurplaten", "buiten spelen activiteiten kinderen", "vader kind activiteiten printable"],
        "gumroad_tags": ["kinderen", "kleurplaten", "avontuur", "printable", "buiten spelen", "MIKKIE", "digitaal", "download", "kids", "coloring"],
        "etsy_tags": ["coloring pages kids", "printable coloring", "adventure coloring", "kids activities", "outdoor play", "father son", "magical coloring", "instant download", "children printable", "fantasy coloring", "MIKKIE WORLD", "dutch kids", "kleurplaten"],
        "title_formula": "[Karakter] Kleurplaten — [Type] | Printable PDF | MIKKIE WORLD",
        "description_tip": "Begin met het probleem dat je oplost: 'Zoek je leuke activiteiten voor je kind?'"
    }

def generate_product_roadmap() -> dict:
    """Genereer een 90-daagse product roadmap."""
    
    prompt = """Je bent een product strateg voor MIKKIE WORLD — een magisch kindermerk op Gumroad.

Huidige situatie: 9 producten live, €0-50/maand omzet
Doel: €500/maand binnen 90 dagen

Maak een concrete 90-daagse product roadmap:
- Week 1-2: Quick wins (makkelijk te maken, snel te verkopen)
- Week 3-4: Medium producten (meer waarde, hogere prijs)
- Maand 2: Bundle strategie
- Maand 3: Premium producten

Geef terug als JSON:
{
  "week_1_2": [{"product": "...", "price": 0.00, "hours": 0, "action": "..."}],
  "week_3_4": [{"product": "...", "price": 0.00, "hours": 0, "action": "..."}],
  "month_2": [{"product": "...", "price": 0.00, "hours": 0, "action": "..."}],
  "month_3": [{"product": "...", "price": 0.00, "hours": 0, "action": "..."}],
  "revenue_projection": {"week_2": "...", "week_4": "...", "month_2": "...", "month_3": "..."},
  "key_actions": ["...", "...", "..."]
}"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.7
        )
        text = resp.choices[0].message.content.strip()
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        log(f"Roadmap fout: {e}")
    
    return {
        "week_1_2": [
            {"product": "Seizoen kleurplaten (zomer)", "price": 7.99, "hours": 3, "action": "Maak 10 zomer kleurplaten via Artistly"},
            {"product": "Reward chart bundle", "price": 4.99, "hours": 2, "action": "Ontwerp 5 beloningskaarten"}
        ],
        "week_3_4": [
            {"product": "Sticker sheet bundle (alle 7 karakters)", "price": 9.99, "hours": 4, "action": "Maak sticker sheets via Artistly"},
            {"product": "Birthday party kit MIKKIE", "price": 12.99, "hours": 5, "action": "Ontwerp uitnodiging + banner + tags"}
        ],
        "month_2": [
            {"product": "Outdoor adventure kit", "price": 14.99, "hours": 6, "action": "Maak bingo, scavenger hunt, activiteiten kaarten"},
            {"product": "Premium bundle (alles)", "price": 49.99, "hours": 2, "action": "Bundel alle producten"}
        ],
        "month_3": [
            {"product": "Seizoen kleurplaten (herfst)", "price": 7.99, "hours": 3, "action": "Maak 10 herfst kleurplaten"},
            {"product": "Advent calendar printable", "price": 9.99, "hours": 4, "action": "Maak 24-daagse advent kalender"}
        ],
        "revenue_projection": {"week_2": "€20-50", "week_4": "€50-100", "month_2": "€150-250", "month_3": "€300-500"},
        "key_actions": ["Upload covers naar alle producten", "Voeg SEO keywords toe aan titels", "Maak Pinterest boards aan voor kleurplaten"]
    }

def analyze_competition() -> dict:
    """Analyseer de concurrentie op Gumroad voor kinderencontent."""
    
    prompt = """Je bent een marktanalist voor digitale kinderencontent op Gumroad en Etsy.

Analyseer de concurrentie voor MIKKIE WORLD (kleurplaten, stickers, activiteiten voor kinderen).

Geef inzicht in:
1. Wie zijn de top concurrenten?
2. Wat doen zij goed?
3. Waar liggen de gaten (kansen voor MIKKIE WORLD)?
4. Wat is de gemiddelde prijs?
5. Hoe onderscheidt MIKKIE WORLD zich?

Geef terug als JSON:
{
  "market_size": "...",
  "top_competitors": [{"name": "...", "strength": "...", "weakness": "..."}],
  "price_range": {"low": 0.00, "average": 0.00, "high": 0.00},
  "market_gaps": ["...", "...", "..."],
  "mikkie_advantages": ["...", "...", "..."],
  "positioning": "...",
  "action_items": ["...", "...", "..."]
}"""

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
        log(f"Concurrentie fout: {e}")
    
    return {
        "market_size": "Grote markt: miljoenen ouders zoeken wekelijks naar printable kinderactiviteiten",
        "top_competitors": [
            {"name": "Etsy kleurplaten shops", "strength": "Groot bereik, veel reviews", "weakness": "Generiek, geen verhaal/merk"},
            {"name": "Teachers Pay Teachers", "strength": "Educatief publiek", "weakness": "Niet gericht op avontuur/buiten"},
            {"name": "Creative Fabrica", "strength": "Grote collectie", "weakness": "Geen persoonlijk verhaal"}
        ],
        "price_range": {"low": 1.99, "average": 5.99, "high": 14.99},
        "market_gaps": ["Avontuur + buiten spelen combinatie", "Vader-kind focus", "Coherent merkverhaal met karakters"],
        "mikkie_advantages": ["Sterk merkverhaal (Hendrik + Mikkie)", "7 unieke karakters", "Avontuur + buiten spelen focus", "COPPA-safe en WWJD-proof"],
        "positioning": "Premium kinderenmerk met verhaal — niet zomaar kleurplaten maar een avontuur",
        "action_items": ["Voeg verhaal toe aan elke productpagina", "Maak karakters herkenbaar via consistent design", "Gebruik 'vader-kind' als USP in alle marketing"]
    }

# ═══════════════════════════════════════════════════════
# COMMANDO'S
# ═══════════════════════════════════════════════════════
def cmd_analyze():
    """Analyseer huidige niche positie."""
    print(f"\n{BOLD}🔍 NICHE ANALYSE — MIKKIE WORLD{RESET}\n")
    
    print(f"  {GOLD}Kansen analyseren via Grok...{RESET}")
    opportunities = analyze_niche_opportunities()
    
    print(f"\n  {BOLD}Top 5 Kansen:{RESET}\n")
    for i, opp in enumerate(opportunities.get("top_5_opportunities", []), 1):
        print(f"  {GOLD}{i}. {opp.get('product_name', '')}{RESET}")
        print(f"     Prijs: €{opp.get('estimated_price', 0):.2f} | Moeilijkheid: {opp.get('difficulty', '')} | Potentieel: {opp.get('revenue_potential', '')}")
        print(f"     Waarom: {opp.get('why', '')}")
        print(f"     Eerste stap: {opp.get('first_step', '')}")
        print()
    
    print(f"  {GREEN}Quick wins:{RESET} {', '.join(opportunities.get('quick_wins', []))}")
    print(f"  {RED}Vermijd:{RESET} {', '.join(opportunities.get('avoid', []))}")
    print(f"  {GOLD}Maandelijkse omzet schatting:{RESET} {opportunities.get('monthly_revenue_estimate', '')}\n")
    
    report = save_niche_report("niche_analyse", opportunities)
    log(f"💾 Rapport opgeslagen: {report.name}")
    tg_send(f"🔍 *Niche analyse klaar!*\nTop kans: {opportunities.get('top_5_opportunities', [{}])[0].get('product_name', '')}\nSchatting: {opportunities.get('monthly_revenue_estimate', '')}")

def cmd_opportunities():
    """Vind nieuwe Gumroad kansen."""
    print(f"\n{BOLD}💡 GUMROAD KANSEN — MIKKIE WORLD{RESET}\n")
    
    print(f"  {GOLD}Analyseren...{RESET}\n")
    opportunities = analyze_niche_opportunities()
    roadmap = generate_product_roadmap()
    
    print(f"  {BOLD}90-Daagse Roadmap:{RESET}\n")
    
    sections = [
        ("Week 1-2 (Quick Wins)", "week_1_2"),
        ("Week 3-4 (Medium)", "week_3_4"),
        ("Maand 2 (Bundels)", "month_2"),
        ("Maand 3 (Premium)", "month_3")
    ]
    
    for title, key in sections:
        items = roadmap.get(key, [])
        if items:
            print(f"  {GOLD}{title}:{RESET}")
            for item in items:
                print(f"    • {item.get('product', '')} — €{item.get('price', 0):.2f} ({item.get('hours', 0)}u)")
                print(f"      → {item.get('action', '')}")
            print()
    
    proj = roadmap.get("revenue_projection", {})
    print(f"  {GREEN}Omzet projectie:{RESET}")
    for period, amount in proj.items():
        print(f"    {period}: {amount}")
    print()
    
    report = save_niche_report("opportunities", {"opportunities": opportunities, "roadmap": roadmap})
    log(f"💾 Rapport opgeslagen: {report.name}")

def cmd_keywords():
    """Genereer SEO keywords."""
    print(f"\n{BOLD}🔑 SEO KEYWORDS — MIKKIE WORLD{RESET}\n")
    
    for product_type in ["kleurplaten", "stickers", "activiteiten"]:
        print(f"  {GOLD}{product_type.upper()}:{RESET}")
        keywords = generate_seo_keywords(product_type)
        
        print(f"  Hoofd: {', '.join(keywords.get('main_keywords', []))}")
        print(f"  Long-tail: {', '.join(keywords.get('long_tail', [])[:5])}...")
        print(f"  Gumroad tags: {', '.join(keywords.get('gumroad_tags', []))}")
        print(f"  Titel formule: {keywords.get('title_formula', '')}")
        print()
        
        save_niche_report(f"keywords_{product_type}", keywords)
        time.sleep(0.5)

def cmd_roadmap():
    """Genereer product roadmap."""
    print(f"\n{BOLD}🗺️  PRODUCT ROADMAP — 90 Dagen{RESET}\n")
    
    roadmap = generate_product_roadmap()
    
    total_products = sum(len(roadmap.get(k, [])) for k in ["week_1_2", "week_3_4", "month_2", "month_3"])
    print(f"  {CYAN}Totaal nieuwe producten: {total_products}{RESET}\n")
    
    for period, key in [("Week 1-2", "week_1_2"), ("Week 3-4", "week_3_4"), ("Maand 2", "month_2"), ("Maand 3", "month_3")]:
        items = roadmap.get(key, [])
        total_revenue = sum(item.get("price", 0) for item in items)
        print(f"  {GOLD}{period}:{RESET} {len(items)} producten")
        for item in items:
            print(f"    ✅ {item.get('product', '')} — €{item.get('price', 0):.2f}")
        print()
    
    proj = roadmap.get("revenue_projection", {})
    print(f"  {GREEN}Omzet projectie:{RESET}")
    for period, amount in proj.items():
        print(f"    {period.replace('_', ' ')}: {amount}")
    
    print(f"\n  {GOLD}Key actions:{RESET}")
    for action in roadmap.get("key_actions", []):
        print(f"    → {action}")
    print()
    
    report = save_niche_report("roadmap_90d", roadmap)
    log(f"💾 Roadmap opgeslagen: {report.name}")
    tg_send(f"🗺️ *Product roadmap gegenereerd!*\n{total_products} nieuwe producten gepland\nDoel: €500/maand in 90 dagen")

def cmd_competition():
    """Analyseer de concurrentie."""
    print(f"\n{BOLD}🥊 CONCURRENTIEANALYSE — MIKKIE WORLD{RESET}\n")
    
    analysis = analyze_competition()
    
    print(f"  {GOLD}Markt:{RESET} {analysis.get('market_size', '')}\n")
    
    print(f"  {GOLD}Top concurrenten:{RESET}")
    for comp in analysis.get("top_competitors", []):
        print(f"    • {comp.get('name', '')}")
        print(f"      ✅ {comp.get('strength', '')}")
        print(f"      ❌ {comp.get('weakness', '')}")
    print()
    
    price = analysis.get("price_range", {})
    print(f"  {GOLD}Prijsrange:{RESET} €{price.get('low', 0):.2f} — €{price.get('average', 0):.2f} (gem) — €{price.get('high', 0):.2f}")
    
    print(f"\n  {GREEN}MIKKIE WORLD voordelen:{RESET}")
    for adv in analysis.get("mikkie_advantages", []):
        print(f"    ✅ {adv}")
    
    print(f"\n  {GOLD}Positionering:{RESET}")
    print(f"  {analysis.get('positioning', '')}")
    
    print(f"\n  {CYAN}Actie items:{RESET}")
    for action in analysis.get("action_items", []):
        print(f"    → {action}")
    print()
    
    report = save_niche_report("competition", analysis)
    log(f"💾 Concurrentieanalyse opgeslagen: {report.name}")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "analyze"
    
    if cmd == "analyze":
        cmd_analyze()
    elif cmd == "opportunities":
        cmd_opportunities()
    elif cmd == "keywords":
        cmd_keywords()
    elif cmd == "roadmap":
        cmd_roadmap()
    elif cmd == "competition":
        cmd_competition()
    else:
        print(f"Gebruik: python3 mikkie_niche.py [analyze|opportunities|keywords|roadmap|competition]")
