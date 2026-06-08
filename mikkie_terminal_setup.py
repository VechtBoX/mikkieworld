#!/usr/bin/env python3
"""
⚡ MIKKIE WORLD — Terminal Power Setup
Vraag Grok: de 10 meest essentiële terminal toevoegingen
voor een Mac power user die een AI content merk runt in 2026.
"""

import os
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

def vraag(prompt):
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": """Je bent een Mac terminal expert en productiviteitsgoeroe.
De gebruiker is Hendrik — een ondernemer die een AI-gedreven kindermerk (MIKKIE WORLD) runt.
Hij heeft: Python agents, GitHub repos, Gumroad producten, X/Twitter automation, Telegram bots.
Zijn Mac heeft: zsh, Homebrew, Python 3.11, git.
Geef alleen concrete, direct uitvoerbare terminal commando's. Geen vage adviezen."""},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.7
    )
    return resp.choices[0].message.content.strip()

print(f"\n{BOLD}{'═'*70}{RESET}")
print(f"  ⚡ MIKKIE WORLD — 10 Essentiële Terminal Toevoegingen")
print(f"{'═'*70}{RESET}\n")

antwoord = vraag("""
Geef de 10 meest essentiële dingen die Hendrik moet toevoegen aan zijn Mac terminal
om maximaal productief te zijn als AI content creator en ondernemer in 2026.

Voor elke toevoeging:
1. Naam + wat het is
2. Waarom het essentieel is voor zijn workflow
3. Het exacte installatie/setup commando
4. Een concrete use case voor MIKKIE WORLD

Categorieën om te overwegen:
- Shell configuratie (.zshrc aliases, functies, prompt)
- Tools (fzf, ripgrep, bat, eza, zoxide, starship, tmux, etc.)
- Git workflow verbeteringen
- Python/AI workflow tools
- Monitoring & logging
- Keyboard shortcuts & productiviteit

Geef de commando's die direct in de terminal werken op macOS met Homebrew.
Sorteer op impact — meest waardevolle eerst.
""")

print(antwoord)

print(f"\n{BOLD}{'═'*70}{RESET}")

# Sla op
with open("/tmp/terminal_setup.md", "w", encoding="utf-8") as f:
    f.write(f"# ⚡ MIKKIE WORLD — Terminal Power Setup\n\n{antwoord}\n")

print(f"  💾 Opgeslagen als /tmp/terminal_setup.md")
print(f"{'═'*70}\n")
