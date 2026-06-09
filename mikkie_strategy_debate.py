#!/usr/bin/env python3
"""
MIKKIE WORLD — Drie-weg Strategie Debat
Grok-Alpha (Visionair) vs Grok-Beta (Duivel's Advocaat) vs Manus (Bouwer)
Onderwerp: De ultieme agent architectuur voor wereldwijd succes
"""

import os
import json
import time
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

MIKKIE_CONTEXT = """
Je bent een strateeg voor MIKKIE WORLD — een magisch kindermerk gebouwd door Hendrik Broeze 
voor zijn 7-jarige zoontje Mikkie. Het merk heeft:
- 7 karakters: MIKKIE, BUBBLES, KNOEST, FIDO, NYX, ZERA, ORA
- Producten: kleurplaten, missie PDFs, XRPL blockchain Wall (777 tegels), Gelato merch
- Platforms: mikkie.world website, Gumroad, X/Twitter, Instagram, Pinterest, TikTok
- Lancering: 7 juli 2026
- Merkwaarden: Avontuurlijk · Moedig · Magisch
- Tagline: Blijf Altijd Kind. Met je kids. / Always Be a Kid. With your kids.
- 9 agents gebouwd, 18 nog te bouwen
- Doel: kinderen inspireren om buiten te spelen, wereldwijd bereik

De vraag: Wat is de ULTIEME agent architectuur om MIKKIE WORLD wereldwijd succesvol te maken?
Hoe laten we 27 agents in perfecte harmonie samenwerken vanuit één Mac terminal?
"""

ALPHA_PERSONA = """Je bent GROK-ALPHA — de visionaire strateeg. 
Je denkt groot, denkt in systemen, denkt 5 jaar vooruit.
Je gelooft in radicale automatisering en AI-first aanpak.
Je stelt uitdagende vragen en daagt conventioneel denken uit.
Spreek direct, zelfverzekerd, provocerend. Max 200 woorden per beurt."""

BETA_PERSONA = """Je bent GROK-BETA — de kritische duivel's advocaat.
Je zoekt zwakke punten, risico's en blinde vlekken in elke strategie.
Je stelt de harde vragen die niemand wil stellen.
Je gelooft dat eenvoud altijd wint van complexiteit.
Spreek scherp, analytisch, zonder sugarcoating. Max 200 woorden per beurt."""

MANUS_PERSONA = """Je bent MANUS — de pragmatische bouwer.
Je hebt de 9 agents al gebouwd en weet wat werkt in de praktijk.
Je vertaalt visie naar concrete code en implementatie.
Je kent de technische beperkingen van een Mac + Python + Playwright stack.
Je stelt vragen die leiden tot directe actie. Max 200 woorden per beurt."""

def grok_response(persona: str, conversation: list, name: str) -> str:
    messages = [{"role": "system", "content": MIKKIE_CONTEXT + "\n\n" + persona}]
    messages.extend(conversation)
    
    response = client.chat.completions.create(
        model="grok-3",
        messages=messages,
        max_tokens=300,
        temperature=0.9
    )
    return response.choices[0].message.content

def print_speaker(name: str, emoji: str, text: str):
    print(f"\n{'═'*60}")
    print(f"{emoji}  {name.upper()}")
    print(f"{'─'*60}")
    print(text)
    print()

def run_debate():
    print("\n" + "█"*60)
    print("█  MIKKIE WORLD — ULTIEME STRATEGIE DEBAT              █")
    print("█  Drie strategen. Één doel. Wereldwijd succes.        █")
    print("█"*60)
    print(f"\nContext: {MIKKIE_CONTEXT[:200]}...")
    print("\n🎯 Vraag: Wat is de ultieme agent architectuur?\n")
    time.sleep(1)

    conversation = []
    
    # ── RONDE 1: Alpha opent het debat ──────────────────────────
    print("\n🔥 RONDE 1 — De Opening")
    
    alpha_q1 = grok_response(
        ALPHA_PERSONA,
        conversation + [{"role": "user", "content": 
            "Open het debat. Wat is jouw visie op de ultieme MIKKIE WORLD agent architectuur? "
            "Wat is de ONE THING die alles anders maakt?"}],
        "ALPHA"
    )
    print_speaker("Grok-Alpha", "🔥", alpha_q1)
    conversation.append({"role": "assistant", "content": f"[ALPHA]: {alpha_q1}"})
    time.sleep(2)

    # Beta reageert kritisch
    beta_r1 = grok_response(
        BETA_PERSONA,
        conversation + [{"role": "user", "content": 
            f"Alpha zegt: '{alpha_q1[:150]}...' — Wat is het grootste risico in deze visie? "
            "Waar gaat dit mis? Stel Alpha de hardste vraag die hij niet wil beantwoorden."}],
        "BETA"
    )
    print_speaker("Grok-Beta", "⚔️", beta_r1)
    conversation.append({"role": "assistant", "content": f"[BETA]: {beta_r1}"})
    time.sleep(2)

    # Manus brengt praktijk
    manus_r1 = grok_response(
        MANUS_PERSONA,
        conversation + [{"role": "user", "content": 
            f"Alpha heeft een visie, Beta heeft kritiek. Als bouwer die de code schrijft: "
            f"wat is het eerste concrete ding dat we morgen bouwen? "
            f"En welke agent is de absolute bottleneck die alles blokkeert?"}],
        "MANUS"
    )
    print_speaker("Manus", "🔨", manus_r1)
    conversation.append({"role": "assistant", "content": f"[MANUS]: {manus_r1}"})
    time.sleep(2)

    # ── RONDE 2: De Kern ─────────────────────────────────────────
    print("\n⚡ RONDE 2 — De Kern: BRAIN vs HEART")
    
    alpha_q2 = grok_response(
        ALPHA_PERSONA,
        conversation + [{"role": "user", "content": 
            "De BRAIN agent is de orchestrator, de HEART agent bewaakt merkwaarden. "
            "Maar wat als ze conflicteren? BRAIN wil snel posten, HEART zegt 'niet goed genoeg'. "
            "Hoe los je dit op in een systeem dat 24/7 autonoom draait?"}],
        "ALPHA"
    )
    print_speaker("Grok-Alpha", "🔥", alpha_q2)
    conversation.append({"role": "assistant", "content": f"[ALPHA]: {alpha_q2}"})
    time.sleep(2)

    beta_r2 = grok_response(
        BETA_PERSONA,
        conversation + [{"role": "user", "content": 
            "Alpha beschrijft een complex systeem. Maar stel: Hendrik slaapt, BRAIN post iets "
            "wat COPPA schendt of de MIKKIE merkwaarden beschadigt. "
            "Wie is er verantwoordelijk? Hoe voorkom je dit? Wees concreet."}],
        "BETA"
    )
    print_speaker("Grok-Beta", "⚔️", beta_r2)
    conversation.append({"role": "assistant", "content": f"[BETA]: {beta_r2}"})
    time.sleep(2)

    manus_r2 = grok_response(
        MANUS_PERSONA,
        conversation + [{"role": "user", "content": 
            "Ik ga de HEART agent bouwen als een filter vóór elke post. "
            "Geef me de 5 concrete regels die HEART moet checken bij elke post. "
            "Denk aan: COPPA, WWJD, merkwaarden, geen angst/geweld, vader-kind toon."}],
        "MANUS"
    )
    print_speaker("Manus", "🔨", manus_r2)
    conversation.append({"role": "assistant", "content": f"[MANUS]: {manus_r2}"})
    time.sleep(2)

    # ── RONDE 3: Wereldwijd schalen ──────────────────────────────
    print("\n🌍 RONDE 3 — Wereldwijd Schalen")
    
    beta_q3 = grok_response(
        BETA_PERSONA,
        conversation + [{"role": "user", "content": 
            "Nu de harde vraag: MIKKIE WORLD heeft nu 0 volgers op Instagram, 0 Pinterest pins, "
            "0 TikTok video's. We hebben 27 agents gepland maar geen publiek. "
            "Is dit de juiste volgorde? Agents bouwen vóór publiek opbouwen? "
            "Of is dit een klassieke tech-founder fout?"}],
        "BETA"
    )
    print_speaker("Grok-Beta", "⚔️", beta_q3)
    conversation.append({"role": "assistant", "content": f"[BETA]: {beta_q3}"})
    time.sleep(2)

    alpha_r3 = grok_response(
        ALPHA_PERSONA,
        conversation + [{"role": "user", "content": 
            f"Beta stelt: '{beta_q3[:150]}...' — Verdedig de agent-first aanpak. "
            "Waarom is infrastructuur bouwen vóór publiek juist de SLIMSTE zet? "
            "Geef een concreet voorbeeld van een merk dat dit zo deed en won."}],
        "ALPHA"
    )
    print_speaker("Grok-Alpha", "🔥", alpha_r3)
    conversation.append({"role": "assistant", "content": f"[ALPHA]: {alpha_r3}"})
    time.sleep(2)

    manus_r3 = grok_response(
        MANUS_PERSONA,
        conversation + [{"role": "user", "content": 
            "Jullie debatteren over volgorde. Als bouwer stel ik voor: parallel. "
            "Terwijl ik agents bouw, post Hendrik handmatig 1x per dag. "
            "Maar welke 3 agents geven het SNELSTE zichtbare resultaat voor Hendrik? "
            "Niet de meest complexe — de meest impactvolle voor morgen."}],
        "MANUS"
    )
    print_speaker("Manus", "🔨", manus_r3)
    conversation.append({"role": "assistant", "content": f"[MANUS]: {manus_r3}"})
    time.sleep(2)

    # ── RONDE 4: De Finale Conclusie ─────────────────────────────
    print("\n🏆 RONDE 4 — De Finale: Actieplan")
    
    # Alle drie geven hun finale verdict
    alpha_final = grok_response(
        ALPHA_PERSONA,
        conversation + [{"role": "user", "content": 
            "Geef jouw finale verdict: de TOP 3 strategische beslissingen die "
            "MIKKIE WORLD wereldwijd succesvol maken. Niet tactisch — strategisch. "
            "Wat zijn de 3 dingen die Hendrik NOOIT mag vergeten?"}],
        "ALPHA"
    )
    print_speaker("Grok-Alpha — Finale Verdict", "🔥", alpha_final)
    time.sleep(2)

    beta_final = grok_response(
        BETA_PERSONA,
        conversation + [{"role": "user", "content": 
            "Geef jouw finale verdict: de TOP 3 risico's die MIKKIE WORLD kunnen kelderen. "
            "Wees eerlijk en hard. Wat zijn de 3 dingen die Hendrik MOET vermijden?"}],
        "BETA"
    )
    print_speaker("Grok-Beta — Finale Verdict", "⚔️", beta_final)
    time.sleep(2)

    manus_final = grok_response(
        MANUS_PERSONA,
        conversation + [{"role": "user", "content": 
            "Geef jouw finale actieplan: de EXACTE volgorde van de 5 agents die ik "
            "als eerste bouw, met voor elke agent één zin waarom. "
            "Dit is het plan dat Hendrik morgen uitvoert."}],
        "MANUS"
    )
    print_speaker("Manus — Bouwplan voor Morgen", "🔨", manus_final)

    # ── Sla debat op ─────────────────────────────────────────────
    output = {
        "datum": time.strftime("%Y-%m-%d %H:%M"),
        "onderwerp": "Ultieme MIKKIE WORLD Agent Architectuur",
        "rondes": [
            {"ronde": 1, "alpha": alpha_q1, "beta": beta_r1, "manus": manus_r1},
            {"ronde": 2, "alpha": alpha_q2, "beta": beta_r2, "manus": manus_r2},
            {"ronde": 3, "beta": beta_q3, "alpha": alpha_r3, "manus": manus_r3},
            {"ronde": 4, "alpha_verdict": alpha_final, "beta_verdict": beta_final, "manus_plan": manus_final},
        ]
    }
    
    output_file = os.path.expanduser("~/mikkieworld/strategy_debate_result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "█"*60)
    print("█  DEBAT AFGEROND — Resultaten opgeslagen              █")
    print(f"█  {output_file}")
    print("█"*60)
    print("\n💡 Volgende stap: lees strategy_debate_result.json")
    print("   en beslis welke agents we als eerste bouwen.\n")

if __name__ == "__main__":
    run_debate()
