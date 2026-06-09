#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# MIKKIE WORLD — launchd Installer
# Installeert BRAIN en TELEGRAM COMMANDER als macOS services
# die automatisch starten bij reboot en herstarten bij crash.
#
# Gebruik:
#   ./install_launchd.sh install    → Installeer services
#   ./install_launchd.sh uninstall  → Verwijder services
#   ./install_launchd.sh status     → Toon status
#   ./install_launchd.sh restart    → Herstart services
# ═══════════════════════════════════════════════════════════════════════

set -e

BOLD="\033[1m"
GREEN="\033[92m"
GOLD="\033[93m"
RED="\033[91m"
RESET="\033[0m"

MIKKIE_DIR="$HOME/mikkieworld"
LOG_DIR="$HOME/MIKKIE_WORLD/LOGS"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"
PYTHON=$(which python3)

mkdir -p "$LOG_DIR" "$LAUNCH_AGENTS"

# ─── Env vars ophalen ─────────────────────────────────────────────────
XAI_KEY="${XAI_API_KEY:-NIET_INGESTELD}"
TG_TOKEN="${TELEGRAM_BOT_TOKEN:-NIET_INGESTELD}"
TG_CHAT="${TELEGRAM_CHAT_ID:-NIET_INGESTELD}"
GUMROAD="${GUMROAD_API_TOKEN:-NIET_INGESTELD}"

generate_plist() {
    local label="$1"
    local script="$2"
    local arg="$3"
    local logname="$4"
    local plist_file="$LAUNCH_AGENTS/${label}.plist"

    cat > "$plist_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${label}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${MIKKIE_DIR}/${script}</string>
        $([ -n "$arg" ] && echo "<string>${arg}</string>")
    </array>

    <key>WorkingDirectory</key>
    <string>${MIKKIE_DIR}</string>

    <key>KeepAlive</key>
    <true/>

    <key>RunAtLoad</key>
    <true/>

    <key>ThrottleInterval</key>
    <integer>30</integer>

    <key>StandardOutPath</key>
    <string>${LOG_DIR}/${logname}_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/${logname}_stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>XAI_API_KEY</key>
        <string>${XAI_KEY}</string>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>${TG_TOKEN}</string>
        <key>TELEGRAM_CHAT_ID</key>
        <string>${TG_CHAT}</string>
        <key>GUMROAD_API_TOKEN</key>
        <string>${GUMROAD}</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
EOF
    echo -e "  ${GREEN}✅ Plist aangemaakt: ${plist_file}${RESET}"
}

install_services() {
    echo -e "${BOLD}🚀 MIKKIE WORLD launchd services installeren...${RESET}"
    echo ""

    # Waarschuwing als env vars ontbreken
    if [ "$TG_TOKEN" = "NIET_INGESTELD" ]; then
        echo -e "${GOLD}⚠️  TELEGRAM_BOT_TOKEN niet ingesteld — stel in via ~/.zshrc${RESET}"
    fi

    # Genereer plist bestanden
    generate_plist "world.mikkie.brain"     "mikkie_brain.py"             "loop"  "brain"
    generate_plist "world.mikkie.commander" "mikkie_telegram_commander.py" ""     "commander"
    generate_plist "world.mikkie.healer"    "mikkie_healer.py"            "start" "healer"

    echo ""
    echo -e "${GOLD}📥 Services laden in launchd...${RESET}"

    for label in world.mikkie.brain world.mikkie.commander world.mikkie.healer; do
        launchctl unload "$LAUNCH_AGENTS/${label}.plist" 2>/dev/null || true
        launchctl load   "$LAUNCH_AGENTS/${label}.plist"
        echo -e "  ${GREEN}✅ ${label} geladen${RESET}"
    done

    echo ""
    echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${GREEN}║  ✅ MIKKIE WORLD services geïnstalleerd!                ║${RESET}"
    echo -e "${BOLD}${GREEN}║                                                          ║${RESET}"
    echo -e "${BOLD}${GREEN}║  Starten automatisch bij Mac reboot                      ║${RESET}"
    echo -e "${BOLD}${GREEN}║  Herstarten automatisch bij crash (na 30 sec)            ║${RESET}"
    echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${RESET}"
}

uninstall_services() {
    echo -e "${BOLD}🛑 MIKKIE WORLD launchd services verwijderen...${RESET}"

    for label in world.mikkie.brain world.mikkie.commander world.mikkie.healer; do
        launchctl unload "$LAUNCH_AGENTS/${label}.plist" 2>/dev/null || true
        rm -f "$LAUNCH_AGENTS/${label}.plist"
        echo -e "  ${GREEN}✅ ${label} verwijderd${RESET}"
    done
}

show_status() {
    echo -e "${BOLD}📊 MIKKIE WORLD launchd status:${RESET}"
    echo ""
    launchctl list | grep "mikkie" || echo "  Geen MIKKIE services actief"
}

restart_services() {
    echo -e "${GOLD}🔄 Services herstarten...${RESET}"
    for label in world.mikkie.brain world.mikkie.commander world.mikkie.healer; do
        launchctl stop  "$label" 2>/dev/null || true
        launchctl start "$label" 2>/dev/null || true
        echo -e "  ${GREEN}✅ ${label} herstart${RESET}"
    done
}

CMD="${1:-install}"
case "$CMD" in
    install)   install_services ;;
    uninstall) uninstall_services ;;
    status)    show_status ;;
    restart)   restart_services ;;
    *)
        echo "Gebruik: ./install_launchd.sh [install|uninstall|status|restart]"
        ;;
esac
