#!/bin/bash
# MIKKIE WORLD — Artistly Agent Installatie Script
# Voer uit: bash ~/mikkieworld/artistly_install.sh

set -e

echo ""
echo "🎨 MIKKIE WORLD Artistly Agent Installatie"
echo "==========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 niet gevonden. Installeer via: brew install python3"
    exit 1
fi

# Install Playwright
echo "📦 Playwright installeren..."
pip3 install playwright -q
python3 -m playwright install chromium
echo "✅ Playwright geïnstalleerd"

# Add alias to .zshrc
ALIAS_LINE='alias mikkie-artistly="python3 ~/mikkieworld/mikkie_artistly_agent.py"'
if ! grep -q "mikkie-artistly" ~/.zshrc 2>/dev/null; then
    echo "" >> ~/.zshrc
    echo "# MIKKIE WORLD Artistly Agent" >> ~/.zshrc
    echo "$ALIAS_LINE" >> ~/.zshrc
    echo "✅ Alias 'mikkie-artistly' toegevoegd aan ~/.zshrc"
else
    echo "✅ Alias al aanwezig"
fi

# Ask for Artistly password
echo ""
echo "🔐 Artistly wachtwoord instellen..."
echo "   (Dit is het wachtwoord van app.artistly.ai)"
read -s -p "   Wachtwoord: " ARTISTLY_PASS
echo ""

if [ -n "$ARTISTLY_PASS" ]; then
    # Add to .zshrc
    if grep -q "ARTISTLY_PASSWORD" ~/.zshrc 2>/dev/null; then
        sed -i '' "s/export ARTISTLY_PASSWORD=.*/export ARTISTLY_PASSWORD='$ARTISTLY_PASS'/" ~/.zshrc
    else
        echo "export ARTISTLY_PASSWORD='$ARTISTLY_PASS'" >> ~/.zshrc
    fi
    echo "✅ Wachtwoord opgeslagen in ~/.zshrc"

    # Update plist
    PLIST_SRC="$HOME/mikkieworld/com.mikkieworld.artistly.plist"
    if [ -f "$PLIST_SRC" ]; then
        sed -i '' "s/VERVANG_DIT_MET_JOUW_WACHTWOORD/$ARTISTLY_PASS/" "$PLIST_SRC"
        echo "✅ Plist bijgewerkt met wachtwoord"
    fi
fi

# Install launchd service
PLIST_DEST="$HOME/Library/LaunchAgents/com.mikkieworld.artistly.plist"
PLIST_SRC="$HOME/mikkieworld/com.mikkieworld.artistly.plist"

if [ -f "$PLIST_SRC" ]; then
    cp "$PLIST_SRC" "$PLIST_DEST"
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    launchctl load "$PLIST_DEST"
    echo "✅ Artistly agent geïnstalleerd als achtergrondproces"
else
    echo "⚠️  Plist niet gevonden: $PLIST_SRC"
fi

# Create output directory
mkdir -p "$HOME/mikkieworld/artistly_output"
echo "✅ Output map aangemaakt: ~/mikkieworld/artistly_output"

# Source .zshrc
source ~/.zshrc 2>/dev/null || true

echo ""
echo "🚀 Installatie klaar!"
echo ""
echo "Gebruik:"
echo "  mikkie-artistly status     # Status bekijken"
echo "  mikkie-artistly test       # 1 test afbeelding genereren"
echo "  mikkie-artistly covers     # Alle 7 Gumroad covers genereren"
echo "  mikkie-artistly coloring   # Alle 7 kleurplaten genereren"
echo "  mikkie-artistly social     # Alle 7 social media posts genereren"
echo "  mikkie-artistly stickers   # Alle 7 stickers genereren"
echo "  mikkie-artistly all        # Alles (35 afbeeldingen)"
echo "  mikkie-artistly log        # Log bekijken"
echo ""
echo "Vergeet niet: source ~/.zshrc"
echo ""
