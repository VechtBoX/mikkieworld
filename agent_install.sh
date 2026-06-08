#!/bin/bash
# MIKKIE WORLD Agent — Installatie script
# Gebruik: bash ~/mikkieworld/agent_install.sh

set -e

echo ""
echo "MIKKIE WORLD Agent Installatie"
echo "================================"

PLIST_SRC="$HOME/mikkieworld/com.mikkieworld.agent.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.mikkieworld.agent.plist"

# Laad env vars uit .zshrc
source "$HOME/.zshrc" 2>/dev/null || true

# Check of API keys beschikbaar zijn
if [ -z "$GUMROAD_API_TOKEN" ]; then
    echo "FOUT: GUMROAD_API_TOKEN niet gevonden in .zshrc"
    echo "Voeg toe: export GUMROAD_API_TOKEN=<jouw_token>"
    exit 1
fi

echo "API keys gevonden. Plist aanmaken..."

# Vervang placeholders in plist met echte waarden
sed \
    -e "s|PLACEHOLDER_GUMROAD|${GUMROAD_API_TOKEN}|g" \
    -e "s|PLACEHOLDER_MAILCHIMP|${MAILCHIMP_API_KEY:-}|g" \
    -e "s|PLACEHOLDER_TWITTER_KEY|${TWITTER_API_KEY:-}|g" \
    -e "s|PLACEHOLDER_TWITTER_SECRET|${TWITTER_API_SECRET:-}|g" \
    -e "s|PLACEHOLDER_TWITTER_TOKEN|${TWITTER_ACCESS_TOKEN:-}|g" \
    -e "s|PLACEHOLDER_TWITTER_TOKEN_SECRET|${TWITTER_ACCESS_TOKEN_SECRET:-}|g" \
    -e "s|PLACEHOLDER_XAI|${XAI_API_KEY:-}|g" \
    "$PLIST_SRC" > "$PLIST_DST"

echo "Plist geinstalleerd: $PLIST_DST"

# Voeg mikkie-agent alias toe aan .zshrc als die er nog niet in staat
if ! grep -q "alias mikkie-agent=" "$HOME/.zshrc" 2>/dev/null; then
    echo "alias mikkie-agent='python3 ~/mikkieworld/mikkie_agent.py'" >> "$HOME/.zshrc"
    echo "Alias mikkie-agent toegevoegd aan .zshrc"
fi

# Stop eventuele bestaande agent
launchctl unload "$PLIST_DST" 2>/dev/null || true
pkill -f mikkie_agent.py 2>/dev/null || true
sleep 1

# Start de agent
launchctl load "$PLIST_DST"

echo ""
echo "Agent gestart!"
echo ""
echo "BELANGRIJK: herlaad je terminal met:"
echo "  source ~/.zshrc"
echo ""
echo "Daarna werken deze commando's:"
echo "  mikkie-agent status   -> Status bekijken"
echo "  mikkie-agent log      -> Live log bekijken"
echo "  mikkie-agent stop     -> Agent stoppen"
echo "  mikkie-agent setup    -> Gumroad nu bijwerken"
echo "  mikkie-agent content  -> Nieuwe content genereren"
echo ""
echo "Log bestand: ~/mikkieworld/agent.log"
echo "Tail log:    tail -f ~/mikkieworld/agent.log"
