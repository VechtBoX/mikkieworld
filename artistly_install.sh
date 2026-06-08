#!/bin/bash
# MIKKIE WORLD — Artistly Agent Installatie Script (macOS fix)
# Voer uit: bash ~/mikkieworld/artistly_install.sh

set -e

echo ""
echo "🎨 MIKKIE WORLD Artistly Agent Installatie"
echo "==========================================="
echo ""

# ─── Stap 1: Playwright installeren (macOS-compatibel) ───────────────────────
echo "📦 Playwright installeren (macOS methode)..."

# Probeer pipx (meest veilig op macOS)
if command -v pipx &> /dev/null; then
    echo "   pipx gevonden — installeren via pipx..."
    pipx install playwright 2>/dev/null || true
    python3 -m playwright install chromium 2>/dev/null || \
    python3 -c "from playwright.sync_api import sync_playwright; print('Playwright OK')" 2>/dev/null || true
# Probeer pip3 met --user flag
elif pip3 install playwright --user -q 2>/dev/null; then
    echo "   pip3 --user gelukt"
    python3 -m playwright install chromium
# Probeer pip3 met --break-system-packages (macOS Homebrew fix)
elif pip3 install playwright --break-system-packages -q 2>/dev/null; then
    echo "   pip3 --break-system-packages gelukt"
    python3 -m playwright install chromium
# Probeer via brew
elif command -v brew &> /dev/null; then
    echo "   Installeren via brew + venv..."
    python3 -m venv "$HOME/.mikkie-venv" --system-site-packages 2>/dev/null || python3 -m venv "$HOME/.mikkie-venv"
    source "$HOME/.mikkie-venv/bin/activate"
    pip install playwright -q
    playwright install chromium
    deactivate
    # Update plist en agent om venv python te gebruiken
    PYTHON_PATH="$HOME/.mikkie-venv/bin/python3"
    echo "   Venv aangemaakt: $HOME/.mikkie-venv"
else
    echo "⚠️  Playwright kon niet automatisch worden geïnstalleerd."
    echo "   Voer handmatig uit:"
    echo "   python3 -m venv ~/.mikkie-venv && source ~/.mikkie-venv/bin/activate && pip install playwright && playwright install chromium"
fi

echo "✅ Playwright stap klaar"

# ─── Stap 2: Python pad bepalen ───────────────────────────────────────────────
if [ -f "$HOME/.mikkie-venv/bin/python3" ]; then
    PYTHON="$HOME/.mikkie-venv/bin/python3"
else
    PYTHON="python3"
fi

echo "   Python: $PYTHON"

# ─── Stap 3: Alias toevoegen ──────────────────────────────────────────────────
echo ""
echo "🔗 Alias instellen..."

# Schrijf naar ~/.mikkie_alias.zsh zodat source volgorde niet uitmaakt
ALIAS_FILE="$HOME/.mikkie_alias.zsh"

# Verwijder oude mikkie-artistly regels uit zowel .zshrc als alias bestand
sed -i '' '/mikkie-artistly/d' ~/.zshrc 2>/dev/null || true
sed -i '' '/mikkie-artistly/d' "$ALIAS_FILE" 2>/dev/null || true

# Voeg toe aan alias bestand (wordt geladen via .zshrc)
echo "" >> "$ALIAS_FILE"
echo "# MIKKIE WORLD Artistly Agent" >> "$ALIAS_FILE"
echo "alias mikkie-artistly='$PYTHON $HOME/mikkieworld/mikkie_artistly_agent.py'" >> "$ALIAS_FILE"

# Zorg dat alias bestand geladen wordt in .zshrc (als dat nog niet het geval is)
if ! grep -q 'mikkie_alias.zsh' ~/.zshrc 2>/dev/null; then
    echo "source \$HOME/.mikkie_alias.zsh" >> ~/.zshrc
fi

echo "✅ Alias 'mikkie-artistly' toegevoegd aan ~/.mikkie_alias.zsh"

# ─── Stap 4: Wachtwoord instellen ─────────────────────────────────────────────
echo ""
echo "🔐 Artistly wachtwoord instellen..."
echo "   (Dit is het wachtwoord van app.artistly.ai)"
read -s -p "   Wachtwoord: " ARTISTLY_PASS
echo ""

if [ -n "$ARTISTLY_PASS" ]; then
    # Verwijder oude versie
    sed -i '' '/ARTISTLY_PASSWORD/d' ~/.zshrc 2>/dev/null || true
    # Voeg nieuwe toe
    echo "export ARTISTLY_PASSWORD='$ARTISTLY_PASS'" >> ~/.zshrc
    echo "✅ Wachtwoord opgeslagen in ~/.zshrc"
fi

# ─── Stap 5: Output map aanmaken ──────────────────────────────────────────────
mkdir -p "$HOME/mikkieworld/artistly_output"
echo "✅ Output map: ~/mikkieworld/artistly_output"

# ─── Stap 6: Klaar ────────────────────────────────────────────────────────────
echo ""
echo "✅ Installatie klaar!"
echo ""
echo "⚠️  BELANGRIJK: Voer nu uit:"
echo "   source ~/.zshrc"
echo ""
echo "Daarna testen:"
echo "   mikkie-artistly test"
echo ""
echo "Alle commando's:"
echo "   mikkie-artistly status     # Status"
echo "   mikkie-artistly test       # 1 test afbeelding"
echo "   mikkie-artistly covers     # 7 Gumroad covers"
echo "   mikkie-artistly coloring   # 7 kleurplaten"
echo "   mikkie-artistly social     # 7 social posts"
echo "   mikkie-artistly stickers   # 7 stickers"
echo "   mikkie-artistly all        # Alles (35 afbeeldingen)"
echo "   mikkie-artistly log        # Log bekijken"
echo ""
