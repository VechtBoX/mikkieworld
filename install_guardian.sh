#!/bin/bash
# 🛡️ MIKKIE WORLD GUARDIAN — Installatie script
# Installeert de GUARDIAN als macOS launchd service (start automatisch bij login)
#
# Gebruik: bash ~/mikkieworld/install_guardian.sh

set -e

PLIST_SRC="$HOME/mikkieworld/world.mikkie.guardian.plist"
PLIST_DST="$HOME/Library/LaunchAgents/world.mikkie.guardian.plist"
LOG_DIR="$HOME/MIKKIE_WORLD/LOGS"

echo ""
echo "🛡️  MIKKIE WORLD GUARDIAN Installatie"
echo "═══════════════════════════════════════"

# Maak log map aan
mkdir -p "$LOG_DIR"
echo "✓ Log map aangemaakt: $LOG_DIR"

# Kopieer plist
cp "$PLIST_SRC" "$PLIST_DST"
echo "✓ LaunchAgent plist geïnstalleerd"

# Laad de service
launchctl unload "$PLIST_DST" 2>/dev/null || true
launchctl load -w "$PLIST_DST"
echo "✓ GUARDIAN service geladen"

# Controleer of het draait
sleep 2
if launchctl list | grep -q "world.mikkie.guardian"; then
    echo ""
    echo "✅ GUARDIAN draait! Automatisch actief bij elke login."
    echo ""
    echo "   Commando's:"
    echo "   launchctl stop world.mikkie.guardian   → Tijdelijk stoppen"
    echo "   launchctl start world.mikkie.guardian  → Herstarten"
    echo "   launchctl unload ~/Library/LaunchAgents/world.mikkie.guardian.plist → Verwijderen"
    echo ""
    echo "   Log bekijken:"
    echo "   tail -f $LOG_DIR/guardian_launchd.log"
else
    echo ""
    echo "⚠️  GUARDIAN is geïnstalleerd maar start nog niet."
    echo "   Controleer: $LOG_DIR/guardian_launchd_err.log"
fi

echo "═══════════════════════════════════════"
echo ""
