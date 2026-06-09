#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# 🌟 MIKKIE WORLD — Start Script v2.0
# Eén commando om het complete MIKKIE WORLD agent ecosysteem te starten
# 
# Gebruik:
#   ./start_mikkie_world.sh          → Start alles
#   ./start_mikkie_world.sh stop     → Stop alles
#   ./start_mikkie_world.sh status   → Toon status
#   ./start_mikkie_world.sh health   → Health check alle agents
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# Kleuren
BOLD="\033[1m"
GREEN="\033[92m"
GOLD="\033[93m"
CYAN="\033[96m"
RED="\033[91m"
RESET="\033[0m"

MIKKIE_DIR="$HOME/mikkieworld"
WORLD_DIR="$HOME/MIKKIE_WORLD"
LOG_DIR="$WORLD_DIR/LOGS"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║  🌟 MIKKIE WORLD — Agent Ecosysteem v2.0                ║${RESET}"
echo -e "${BOLD}║  Avontuurlijk · Moedig · Magisch                        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${RESET}"
echo ""

# ─── Functies ─────────────────────────────────────────────────────────────────

install_packages() {
    echo -e "${GOLD}📦 Python packages controleren...${RESET}"
    
    local packages=("requests" "tweepy" "openai" "pillow" "selenium" "schedule" "python-telegram-bot" "python-dotenv")
    local missing_pkgs=()
    
    for pkg in "${packages[@]}"; do
        # Controleer import naam (python-telegram-bot importeert als 'telegram')
        import_name="$pkg"
        if [ "$pkg" = "python-telegram-bot" ]; then import_name="telegram"; fi
        if [ "$pkg" = "pillow" ]; then import_name="PIL"; fi
        if [ "$pkg" = "python-dotenv" ]; then import_name="dotenv"; fi
        
        if ! python3 -c "import $import_name" 2>/dev/null; then
            missing_pkgs+=("$pkg")
        fi
    done
    
    if [ ${#missing_pkgs[@]} -gt 0 ]; then
        echo -e "  ${GOLD}⚠️  Ontbrekende packages: ${missing_pkgs[*]}${RESET}"
        echo -e "  ${CYAN}📥 Installeren...${RESET}"
        pip3 install --quiet "${missing_pkgs[@]}" && \
            echo -e "  ${GREEN}✅ Packages geïnstalleerd${RESET}" || \
            echo -e "  ${RED}❌ Installatie mislukt — probeer handmatig: pip3 install ${missing_pkgs[*]}${RESET}"
    else
        echo -e "  ${GREEN}✅ Alle packages aanwezig${RESET}"
    fi
}

check_env() {
    echo -e "${GOLD}🔍 Omgeving controleren...${RESET}"
    
    # Verplichte env vars
    local missing=0
    for var in XAI_API_KEY TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID GUMROAD_API_TOKEN; do
        if [ -z "${!var}" ]; then
            echo -e "  ${RED}❌ $var niet ingesteld${RESET}"
            missing=$((missing + 1))
        else
            echo -e "  ${GREEN}✅ $var aanwezig${RESET}"
        fi
    done
    
    # Optionele vars
    for var in PINTEREST_ACCESS_TOKEN SUNO_API_KEY TWITTER_API_KEY ARTISTLY_API_KEY; do
        if [ -z "${!var}" ]; then
            echo -e "  ${GOLD}⚠️  $var niet ingesteld (optioneel)${RESET}"
        else
            echo -e "  ${GREEN}✅ $var aanwezig${RESET}"
        fi
    done
    
    if [ $missing -gt 0 ]; then
        echo ""
        echo -e "${RED}❌ $missing verplichte env vars ontbreken!${RESET}"
        echo -e "${GOLD}Voeg ze toe aan ~/.zshrc en run: source ~/.zshrc${RESET}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Omgeving OK${RESET}"
}

create_folders() {
    echo -e "${GOLD}📁 Mappen aanmaken...${RESET}"
    
    local dirs=(
        "$WORLD_DIR/CONTENT/Covers"
        "$WORLD_DIR/CONTENT/Kleurplaten"
        "$WORLD_DIR/CONTENT/Stickers"
        "$WORLD_DIR/CONTENT/Social"
        "$WORLD_DIR/CONTENT/Banners"
        "$WORLD_DIR/CONTENT/Video/Music"
        "$WORLD_DIR/CONTENT/Video/MusicPrompts"
        "$WORLD_DIR/CONTENT/PDF"
        "$WORLD_DIR/SOCIAL/X_Twitter"
        "$WORLD_DIR/SOCIAL/Instagram"
        "$WORLD_DIR/SOCIAL/Pinterest"
        "$WORLD_DIR/SOCIAL/TikTok"
        "$WORLD_DIR/SOCIAL/Facebook"
        "$WORLD_DIR/SOCIAL/LinkedIn"
        "$WORLD_DIR/SOCIAL/WhatsApp"
        "$WORLD_DIR/SOCIAL/YouTube"
        "$WORLD_DIR/GUMROAD/Products"
        "$WORLD_DIR/GUMROAD/Covers"
        "$WORLD_DIR/GUMROAD/PDFs"
        "$WORLD_DIR/LOGS/Niche"
        "$WORLD_DIR/BACKUP"
        "$MIKKIE_DIR/pids"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
    done
    
    echo -e "${GREEN}✅ Alle mappen aangemaakt${RESET}"
}

start_daemons() {
    echo -e "${GOLD}🚀 Daemons starten...${RESET}"
    mkdir -p "$LOG_DIR"
    
    # BRAIN — centrale orchestrator
    if ! pgrep -f "mikkie_brain.py loop" > /dev/null 2>&1; then
        nohup python3 "$MIKKIE_DIR/mikkie_brain.py" loop \
            > "$LOG_DIR/brain.log" 2>&1 &
        echo $! > "$MIKKIE_DIR/pids/brain.pid"
        echo -e "  ${GREEN}✅ BRAIN gestart (PID $!)${RESET}"
    else
        echo -e "  ${CYAN}ℹ️  BRAIN draait al${RESET}"
    fi
    
    # TELEGRAM COMMANDER — mobiele controle
    if ! pgrep -f "mikkie_telegram_commander.py" > /dev/null 2>&1; then
        nohup python3 "$MIKKIE_DIR/mikkie_telegram_commander.py" \
            > "$LOG_DIR/commander.log" 2>&1 &
        echo $! > "$MIKKIE_DIR/pids/telegram_commander.pid"
        echo -e "  ${GREEN}✅ TELEGRAM COMMANDER gestart (PID $!)${RESET}"
    else
        echo -e "  ${CYAN}ℹ️  TELEGRAM COMMANDER draait al${RESET}"
    fi
    
    # GUARDIAN — watchdog (start als laatste)
    sleep 2
    if ! pgrep -f "mikkie_guardian.py start" > /dev/null 2>&1; then
        python3 "$MIKKIE_DIR/mikkie_guardian.py" start
        echo -e "  ${GREEN}✅ GUARDIAN gestart${RESET}"
    else
        echo -e "  ${CYAN}ℹ️  GUARDIAN draait al${RESET}"
    fi
}

stop_daemons() {
    echo -e "${GOLD}🛑 Daemons stoppen...${RESET}"
    
    # Stop GUARDIAN eerst
    python3 "$MIKKIE_DIR/mikkie_guardian.py" stop 2>/dev/null || true
    
    # Stop andere daemons via PID bestanden
    for pid_file in "$MIKKIE_DIR/pids"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file" 2>/dev/null)
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null
                echo -e "  ${GREEN}✅ Gestopt: $(basename $pid_file .pid) (PID $pid)${RESET}"
            fi
            rm -f "$pid_file"
        fi
    done
    
    echo -e "${GREEN}✅ Alle daemons gestopt${RESET}"
}

show_status() {
    echo -e "${BOLD}📊 MIKKIE WORLD Status${RESET}"
    echo ""
    python3 "$MIKKIE_DIR/mikkie_guardian.py" status
}

show_health() {
    python3 "$MIKKIE_DIR/mikkie_guardian.py" health
}

run_morning_tasks() {
    echo -e "${GOLD}🌅 Ochtendtaken uitvoeren...${RESET}"
    
    # Genereer content voor vandaag
    python3 "$MIKKIE_DIR/mikkie_post_draft.py" x 2>/dev/null || true
    python3 "$MIKKIE_DIR/mikkie_suno.py" prompt 2>/dev/null || true
    python3 "$MIKKIE_DIR/mikkie_tiktok.py" caption 2>/dev/null || true
    python3 "$MIKKIE_DIR/mikkie_pinterest.py" pin 2>/dev/null || true
    
    echo -e "${GREEN}✅ Ochtendtaken klaar${RESET}"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

CMD="${1:-start}"

case "$CMD" in
    start)
        install_packages
        check_env || exit 1
        create_folders
        start_daemons
        echo ""
        echo -e "${BOLD}${GREEN}╔══════════════════════════════════════════════════════════╗${RESET}"
        echo -e "${BOLD}${GREEN}║  ✅ MIKKIE WORLD is actief!                             ║${RESET}"
        echo -e "${BOLD}${GREEN}║                                                          ║${RESET}"
        echo -e "${BOLD}${GREEN}║  🧠 BRAIN orchestreert alle agents                      ║${RESET}"
        echo -e "${BOLD}${GREEN}║  🛡️  GUARDIAN bewaakt 21 agents                         ║${RESET}"
        echo -e "${BOLD}${GREEN}║  📱 Telegram bot: @mikkieworld_agent_bot                ║${RESET}"
        echo -e "${BOLD}${GREEN}║                                                          ║${RESET}"
        echo -e "${BOLD}${GREEN}║  Gebruik: mikkie status    → Status bekijken            ║${RESET}"
        echo -e "${BOLD}${GREEN}║  Gebruik: mikkie health    → Health check               ║${RESET}"
        echo -e "${BOLD}${GREEN}╚══════════════════════════════════════════════════════════╝${RESET}"
        echo ""
        ;;
    stop)
        stop_daemons
        ;;
    status)
        show_status
        ;;
    health)
        show_health
        ;;
    morning)
        run_morning_tasks
        ;;
    restart)
        stop_daemons
        sleep 2
        install_packages
        check_env || exit 1
        start_daemons
        ;;
    *)
        echo -e "Gebruik: ./start_mikkie_world.sh [start|stop|status|health|morning|restart]"
        ;;
esac
