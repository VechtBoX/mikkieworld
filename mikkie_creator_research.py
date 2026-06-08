#!/usr/bin/env python3
"""
🌍 MIKKIE WORLD — Werelds Beste Content Creator Research
Vraag Grok: wie zijn de beste content creators ter wereld
en wat kunnen we leren voor MIKKIE WORLD?
"""

import os
import json
from openai import OpenAI

api_key  = os.environ.get("XAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
base_url = "https://api.x.ai/v1" if os.environ.get("XAI_API_KEY") else None
client   = OpenAI(api_key=api_key, base_url=base_url)
model    = "grok-3" if os.environ.get("XAI_API_KEY") else "gpt-4o"

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
PURPLE = "\033[95m"

def vraag_grok(vraag: str, rol: str = "content strateeg") -> str:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"""Je bent de {rol} ter wereld.
Je analyseert content strategieën van de beste creators en merken.
Context: MIKKIE WORLD is een magisch kindermerk (7-jarige Mikkie) gericht op 
avontuur, buiten spelen, vader-kind verbinding. Lancering 7 juli 2026.
Platforms: X, Instagram, Pinterest, TikTok, YouTube, Gumroad.
Missie: Kinderen inspireren om buiten te spelen.
Geef concrete, actionable inzichten. Geen vage adviezen."""},
            {"role": "user", "content": vraag}
        ],
        max_tokens=1500,
        temperature=0.9
    )
    return resp.choices[0].message.content.strip()

print(f"\n{BOLD}{'═'*70}{RESET}")
print(f"  🌍 MIKKIE WORLD — Werelds Beste Content Creator Analyse")
print(f"{'═'*70}{RESET}\n")

# Vraag 1: Wie zijn de besten?
print(f"{BOLD}{CYAN}🔍 VRAAG 1: Wie zijn de 5 beste content creators ter wereld voor een kindermerk?{RESET}\n")
antwoord1 = vraag_grok(
    """Noem de 5 beste content creators/merken ter wereld die succesvol zijn 
    in de kinderen/familie niche. Analyseer per creator:
    1. Naam + platform
    2. Wat maakt ze #1?
    3. Hun geheime wapen (posting strategie, content formule, engagement tactiek)
    4. Wat MIKKIE WORLD direct van hen kan stelen
    
    Denk aan: Disney, Cocomelon, Ryan's World, MrBeast Kids, Bluey, etc.
    Wees specifiek en direct.""",
    "content analist voor kindermerken"
)
print(antwoord1)

print(f"\n{BOLD}{'─'*70}{RESET}\n")

# Vraag 2: Content formule
print(f"{BOLD}{YELLOW}🔍 VRAAG 2: Wat is de ultieme content formule voor MIKKIE WORLD?{RESET}\n")
antwoord2 = vraag_grok(
    """Geef de exacte content formule die MIKKIE WORLD moet volgen om 
    viraal te gaan op elke platform. Inclusief:
    
    1. De perfecte post structuur (hook → body → CTA)
    2. De beste posting tijden per platform
    3. De hashtag strategie die werkt in 2026
    4. Welk content type het meeste deelt/spaart/koopt
    5. De emotionele trigger die ouders doet kopen
    
    Geef concrete voorbeelden met MIKKIE WORLD content.""",
    "virale content strateeg"
)
print(antwoord2)

print(f"\n{BOLD}{'─'*70}{RESET}\n")

# Vraag 3: De geheime wapens
print(f"{BOLD}{PURPLE}🔍 VRAAG 3: Welke 3 geheime wapens gebruiken top creators die niemand kent?{RESET}\n")
antwoord3 = vraag_grok(
    """Onthul de 3 minst bekende maar meest effectieve strategieën die 
    de top 1% content creators gebruiken die kleine creators niet kennen.
    
    Specifiek voor:
    - Kindermerken/familie content
    - Digitale producten (kleurplaten, PDFs)
    - NFT/blockchain community building
    
    Hoe past MIKKIE WORLD dit toe? Geef concrete implementatie stappen.""",
    "insider content strateeg met 10 jaar ervaring bij Disney en YouTube"
)
print(antwoord3)

print(f"\n{BOLD}{'─'*70}{RESET}\n")

# Vraag 4: AI agent strategie
print(f"{BOLD}{GREEN}🔍 VRAAG 4: Hoe bouwen we een AI content agent die beter is dan een menselijk team?{RESET}\n")
antwoord4 = vraag_grok(
    """MIKKIE WORLD heeft een systeem van 14 AI agents die automatisch content maken.
    
    Vraag: Hoe programmeer je een AI content agent die de stijl en energie van 
    de beste menselijke content creators nabootst?
    
    Geef:
    1. De exacte prompt structuur voor maximale kwaliteit
    2. Hoe je consistente merkstem behoudt over 1000+ posts
    3. Hoe je A/B test welke content beter presteert
    4. De feedback loop: hoe leert de agent van engagement data?
    5. Wanneer AI faalt en menselijke review nodig is
    
    Wees technisch specifiek — dit gaat direct in Python code.""",
    "AI content engineering expert"
)
print(antwoord4)

print(f"\n{BOLD}{'═'*70}{RESET}")
print(f"  ✅ Analyse compleet — sla op als creator_strategy.md")
print(f"{'═'*70}\n")

# Sla op als markdown
output = f"""# 🌍 MIKKIE WORLD — Werelds Beste Content Creator Strategie
*Gegenereerd door Grok op {__import__('datetime').datetime.now().strftime('%d %B %Y %H:%M')}*

---

## 1. De 5 Beste Content Creators voor Kindermerken

{antwoord1}

---

## 2. De Ultieme Content Formule voor MIKKIE WORLD

{antwoord2}

---

## 3. De 3 Geheime Wapens van Top Creators

{antwoord3}

---

## 4. AI Agent Strategie — Beter dan een Menselijk Team

{antwoord4}

---

*Gebruik deze strategie als basis voor alle MIKKIE WORLD agents.*
"""

with open("/tmp/creator_strategy.md", "w", encoding="utf-8") as f:
    f.write(output)

print(f"  💾 Opgeslagen als /tmp/creator_strategy.md")
