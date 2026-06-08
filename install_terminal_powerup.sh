#!/bin/bash
# ⚡ MIKKIE WORLD — Terminal Power Setup
# Installeert de 10 essentiële terminal tools op je Mac
# Gebruik: bash ~/mikkieworld/install_terminal_powerup.sh

RESET="\033[0m"
BOLD="\033[1m"
GREEN="\033[92m"
YELLOW="\033[93m"
CYAN="\033[96m"

echo ""
echo -e "${BOLD}⚡ MIKKIE WORLD — Terminal Power Setup${RESET}"
echo -e "${BOLD}══════════════════════════════════════${RESET}"
echo ""

# Check Homebrew
if ! command -v brew &>/dev/null; then
    echo -e "${YELLOW}⚠️  Homebrew niet gevonden. Installeer eerst:${RESET}"
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

echo -e "${GREEN}✓ Homebrew gevonden${RESET}"
echo ""

# 1. Starship prompt
echo -e "${CYAN}[1/10] Starship prompt...${RESET}"
brew install starship 2>/dev/null
grep -q "starship init" ~/.zshrc || echo 'eval "$(starship init zsh)"' >> ~/.zshrc
echo -e "${GREEN}  ✅ Starship geïnstalleerd${RESET}"

# 2. zoxide
echo -e "${CYAN}[2/10] zoxide (slimme cd)...${RESET}"
brew install zoxide 2>/dev/null
grep -q "zoxide init" ~/.zshrc || echo 'eval "$(zoxide init zsh)"' >> ~/.zshrc
echo -e "${GREEN}  ✅ zoxide geïnstalleerd${RESET}"

# 3. fzf
echo -e "${CYAN}[3/10] fzf (fuzzy finder)...${RESET}"
brew install fzf 2>/dev/null
$(brew --prefix)/opt/fzf/install --key-bindings --completion --update-rc --no-bash --no-fish 2>/dev/null
echo -e "${GREEN}  ✅ fzf geïnstalleerd (Ctrl+R voor history search)${RESET}"

# 4. eza (moderne ls)
echo -e "${CYAN}[4/10] eza (moderne ls met icons)...${RESET}"
brew install eza 2>/dev/null
grep -q "alias ls='eza" ~/.zshrc || echo "alias ls='eza --icons --git'" >> ~/.zshrc
grep -q "alias ll='eza" ~/.zshrc || echo "alias ll='eza --icons --git -la'" >> ~/.zshrc
grep -q "alias tree='eza" ~/.zshrc || echo "alias tree='eza --icons --tree --level=2'" >> ~/.zshrc
echo -e "${GREEN}  ✅ eza geïnstalleerd${RESET}"

# 5. bat (moderne cat)
echo -e "${CYAN}[5/10] bat (syntax highlighting cat)...${RESET}"
brew install bat 2>/dev/null
grep -q "alias cat='bat" ~/.zshrc || echo "alias cat='bat --paging=never'" >> ~/.zshrc
echo -e "${GREEN}  ✅ bat geïnstalleerd${RESET}"

# 6. ripgrep
echo -e "${CYAN}[6/10] ripgrep (ultra-snelle code search)...${RESET}"
brew install ripgrep 2>/dev/null
grep -q "alias grep='rg'" ~/.zshrc || echo "alias grep='rg'" >> ~/.zshrc
echo -e "${GREEN}  ✅ ripgrep geïnstalleerd${RESET}"

# 7. lazygit
echo -e "${CYAN}[7/10] lazygit (terminal git UI)...${RESET}"
brew install lazygit 2>/dev/null
grep -q "alias lg='lazygit'" ~/.zshrc || echo "alias lg='lazygit'" >> ~/.zshrc
echo -e "${GREEN}  ✅ lazygit geïnstalleerd${RESET}"

# 8. gh (GitHub CLI) — alleen als nog niet aanwezig
echo -e "${CYAN}[8/10] GitHub CLI...${RESET}"
if ! command -v gh &>/dev/null; then
    brew install gh 2>/dev/null
    echo -e "${YELLOW}  ⚠️  Voer 'gh auth login' uit om in te loggen${RESET}"
else
    echo -e "${GREEN}  ✅ GitHub CLI al aanwezig${RESET}"
fi

# 9. tmux
echo -e "${CYAN}[9/10] tmux (persistente terminal sessies)...${RESET}"
brew install tmux 2>/dev/null
grep -q "alias t='tmux" ~/.zshrc || echo "alias t='tmux new -A -s mikkie'" >> ~/.zshrc
# Maak een tmux config aan
cat > ~/.tmux.conf << 'TMUXCONF'
# MIKKIE WORLD tmux config
set -g mouse on
set -g default-terminal "screen-256color"
set -g status-bg black
set -g status-fg colour214
set -g status-left " 🎮 MIKKIE "
set -g status-right " %H:%M "
bind | split-window -h
bind - split-window -v
TMUXCONF
echo -e "${GREEN}  ✅ tmux geïnstalleerd${RESET}"

# 10. atuin (slimme shell history)
echo -e "${CYAN}[10/10] atuin (slimme shell history)...${RESET}"
brew install atuin 2>/dev/null
grep -q "atuin init" ~/.zshrc || echo 'eval "$(atuin init zsh)"' >> ~/.zshrc
echo -e "${GREEN}  ✅ atuin geïnstalleerd${RESET}"

# MIKKIE aliases toevoegen
echo ""
echo -e "${CYAN}⚡ MIKKIE WORLD aliases toevoegen...${RESET}"

grep -q "# MIKKIE WORLD ALIASES" ~/.zshrc || cat >> ~/.zshrc << 'ALIASES'

# ═══════════════════════════════════════
# MIKKIE WORLD ALIASES
# ═══════════════════════════════════════
alias mikkie="python3 ~/mikkieworld/mikkie_cli.py"
alias m="python3 ~/mikkieworld/mikkie_cli.py"
alias mpost="python3 ~/mikkieworld/mikkie_post_draft.py x"
alias mstatus="python3 ~/mikkieworld/mikkie_cli.py status"
alias mdash="python3 ~/mikkieworld/mikkie_analytics.py dashboard"
alias mbackup="python3 ~/mikkieworld/mikkie_backup.py run"
alias mheart="python3 ~/mikkieworld/mikkie_heart.py check"
alias mbrain="python3 ~/mikkieworld/mikkie_brain.py"
alias mguard="python3 ~/mikkieworld/mikkie_guardian.py"
alias mworld="cd ~/MIKKIE_WORLD && ls"
alias magents="cd ~/mikkieworld && ls *.py"
alias mlogs="tail -f ~/MIKKIE_WORLD/LOGS/*.log 2>/dev/null || echo 'Geen logs gevonden'"
alias mgit="cd ~/mikkieworld && lg"
ALIASES

echo -e "${GREEN}  ✅ MIKKIE aliases toegevoegd${RESET}"

# Reload zshrc
echo ""
echo -e "${BOLD}══════════════════════════════════════${RESET}"
echo -e "${GREEN}✅ Alle 10 tools geïnstalleerd!${RESET}"
echo ""
echo -e "${YELLOW}Voer dit uit om alles te activeren:${RESET}"
echo -e "${BOLD}  source ~/.zshrc${RESET}"
echo ""
echo -e "${CYAN}Nieuwe commando's:${RESET}"
echo "  z mikkie      → spring direct naar ~/mikkieworld"
echo "  m status      → MIKKIE WORLD status"
echo "  m post        → genereer nieuwe post"
echo "  mdash         → analytics dashboard"
echo "  t             → start tmux sessie 'mikkie'"
echo "  lg            → lazygit UI"
echo "  Ctrl+R        → fuzzy search in history"
echo ""
