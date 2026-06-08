#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# MIKKIE WORLD — Mappenstructuur Setup Script
# Versie: 1.0 | Avontuurlijk · Moedig · Magisch
# ═══════════════════════════════════════════════════════════════════
# Gebruik: bash ~/mikkieworld/setup_mikkie_folders.sh
# ═══════════════════════════════════════════════════════════════════

set -e

MIKKIE_ROOT="$HOME/MIKKIE_WORLD"
AGENTS_DIR="$HOME/mikkieworld"

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║     MIKKIE WORLD — Mappenstructuur Setup      ║"
echo "║     Avontuurlijk · Moedig · Magisch           ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# ─── 1. MAPPEN AANMAKEN ───────────────────────────────────────────
echo "📁 Mappen aanmaken..."

# Social media output — per platform
mkdir -p "$MIKKIE_ROOT/SOCIAL/X_Twitter"
mkdir -p "$MIKKIE_ROOT/SOCIAL/Instagram"
mkdir -p "$MIKKIE_ROOT/SOCIAL/Facebook"
mkdir -p "$MIKKIE_ROOT/SOCIAL/Pinterest"
mkdir -p "$MIKKIE_ROOT/SOCIAL/TikTok"

# Content per type
mkdir -p "$MIKKIE_ROOT/CONTENT/covers"
mkdir -p "$MIKKIE_ROOT/CONTENT/coloring"
mkdir -p "$MIKKIE_ROOT/CONTENT/stickers"
mkdir -p "$MIKKIE_ROOT/CONTENT/banners"
mkdir -p "$MIKKIE_ROOT/CONTENT/illustrations"
mkdir -p "$MIKKIE_ROOT/CONTENT/video"

# Gumroad producten — per karakter
mkdir -p "$MIKKIE_ROOT/GUMROAD/MIKKIE"
mkdir -p "$MIKKIE_ROOT/GUMROAD/BUBBLES"
mkdir -p "$MIKKIE_ROOT/GUMROAD/KNOEST"
mkdir -p "$MIKKIE_ROOT/GUMROAD/FIDO"
mkdir -p "$MIKKIE_ROOT/GUMROAD/NYX"
mkdir -p "$MIKKIE_ROOT/GUMROAD/ZERA"
mkdir -p "$MIKKIE_ROOT/GUMROAD/ORA"
mkdir -p "$MIKKIE_ROOT/GUMROAD/FOUNDERS_PACK"

# Website & branding
mkdir -p "$MIKKIE_ROOT/BRANDING/logo"
mkdir -p "$MIKKIE_ROOT/BRANDING/fonts"
mkdir -p "$MIKKIE_ROOT/BRANDING/kleuren"

# Logs & archief
mkdir -p "$MIKKIE_ROOT/LOGS"
mkdir -p "$MIKKIE_ROOT/ARCHIEF/$(date +%Y-%m)"

echo "   ✅ Alle mappen aangemaakt onder $MIKKIE_ROOT"

# ─── 2. BESTAANDE BESTANDEN VERPLAATSEN ──────────────────────────
echo ""
echo "📦 Bestaande bestanden verplaatsen..."

# Verplaats artistly output naar CONTENT submappen
if [ -d "$AGENTS_DIR/artistly_output" ]; then
    # Covers
    find "$AGENTS_DIR/artistly_output" -name "*_cover_*.png" -exec mv {} "$MIKKIE_ROOT/CONTENT/covers/" \; 2>/dev/null && \
        echo "   ✅ Covers verplaatst naar CONTENT/covers/" || true

    # Kleurplaten
    find "$AGENTS_DIR/artistly_output" -name "*_coloring_*.png" -exec mv {} "$MIKKIE_ROOT/CONTENT/coloring/" \; 2>/dev/null && \
        echo "   ✅ Kleurplaten verplaatst naar CONTENT/coloring/" || true

    # Stickers
    find "$AGENTS_DIR/artistly_output" -name "*_sticker_*.png" -exec mv {} "$MIKKIE_ROOT/CONTENT/stickers/" \; 2>/dev/null && \
        echo "   ✅ Stickers verplaatst naar CONTENT/stickers/" || true

    # Social posts
    find "$AGENTS_DIR/artistly_output" -name "*_social_*.png" -exec mv {} "$MIKKIE_ROOT/SOCIAL/X_Twitter/" \; 2>/dev/null && \
        echo "   ✅ Social posts verplaatst naar SOCIAL/X_Twitter/" || true

    # Banners
    find "$AGENTS_DIR/artistly_output" -name "*_banner_*.png" -exec mv {} "$MIKKIE_ROOT/CONTENT/banners/" \; 2>/dev/null && \
        echo "   ✅ Banners verplaatst naar CONTENT/banners/" || true

    # Overige bestanden
    find "$AGENTS_DIR/artistly_output" -name "*.png" -exec mv {} "$MIKKIE_ROOT/CONTENT/illustrations/" \; 2>/dev/null || true
fi

# Verplaats logs naar LOGS map
for logfile in "$AGENTS_DIR"/*.log; do
    [ -f "$logfile" ] && cp "$logfile" "$MIKKIE_ROOT/LOGS/" 2>/dev/null || true
done
echo "   ✅ Logs gekopieerd naar LOGS/"

# ─── 3. README BESTANDEN AANMAKEN ────────────────────────────────
echo ""
echo "📝 README bestanden aanmaken..."

cat > "$MIKKIE_ROOT/SOCIAL/X_Twitter/README.txt" << 'EOF'
X / TWITTER — MIKKIE WORLD
══════════════════════════
Formaat:  1080 x 1080 px (vierkant) of 1920x1080 (landscape)
Bestand:  PNG of JPG
Naamgeving: KARAKTER_type_DATUM_TIJD.png
Agent:    mikkie_artistly_agent.py → social
Post:     mikkie_agent.py → dagelijks om 09:00

Tip: Kopieer caption uit artistly_agent.log
EOF

cat > "$MIKKIE_ROOT/SOCIAL/Instagram/README.txt" << 'EOF'
INSTAGRAM — MIKKIE WORLD
════════════════════════
Post formaat:   1080 x 1080 px
Reels formaat:  1080 x 1920 px
Story formaat:  1080 x 1920 px

Nog te bouwen: Instagram auto-post via Graph API
EOF

cat > "$MIKKIE_ROOT/SOCIAL/Pinterest/README.txt" << 'EOF'
PINTEREST — MIKKIE WORLD
════════════════════════
Ideaal formaat: 1000 x 1500 px (2:3 ratio)
Boards: Kleurplaten, Buitenspelen, Karakters, Missies

Nog te bouwen: Pinterest auto-pin via API
EOF

cat > "$MIKKIE_ROOT/CONTENT/covers/README.txt" << 'EOF'
GUMROAD COVERS — MIKKIE WORLD
══════════════════════════════
Formaat:  2000 x 2000 px (vierkant)
Gebruik:  Gumroad product thumbnail
Agent:    mikkie_artistly_agent.py → covers
Upload:   mikkie_agent.py → upload_covers_to_gumroad()

Na elke maandag run worden covers automatisch geüpload.
EOF

cat > "$MIKKIE_ROOT/README.txt" << 'EOF'
MIKKIE WORLD — Centrale Mappenstructuur
════════════════════════════════════════
Avontuurlijk · Moedig · Magisch

SOCIAL/          ← Content per social media platform
  X_Twitter/     ← Posts voor X (agent post automatisch om 09:00)
  Instagram/     ← Posts + Reels
  Facebook/      ← Posts + Banners
  Pinterest/     ← Pins (kleurplaten, missies)
  TikTok/        ← Video thumbnails

CONTENT/         ← Alle gegenereerde content
  covers/        ← Gumroad product covers (auto-upload maandag)
  coloring/      ← Kleurplaten (woensdag run)
  stickers/      ← Sticker sheets
  banners/       ← Website banners
  illustrations/ ← Losse illustraties
  video/         ← Video content (binnenkort)

GUMROAD/         ← Per karakter: cover + PDF + assets
BRANDING/        ← Logo, fonts, kleurenpalet
LOGS/            ← Agent logs (agent.log, artistly_agent.log)
ARCHIEF/         ← Oude runs per maand

Agents draaien in: ~/mikkieworld/
Website code in:   ~/mikkie-world/
EOF

echo "   ✅ README bestanden aangemaakt"

# ─── 4. FINDER ZIJBALK INSTELLEN ─────────────────────────────────
echo ""
echo "🔖 Finder zijbalk instellen..."

# Gebruik sfltool (macOS 10.12+) om mappen toe te voegen aan Finder zijbalk
# sfltool add-item voegt toe aan Favorieten sectie

add_to_sidebar() {
    local folder_path="$1"
    if [ -d "$folder_path" ]; then
        # sfltool is de officiële Apple tool voor sidebar management
        sfltool add-item "file://$folder_path" 2>/dev/null || \
        # Fallback: gebruik AppleScript
        osascript -e "tell application \"Finder\" to make new alias file at (path to desktop) to POSIX file \"$folder_path\"" 2>/dev/null || true
    fi
}

# Voeg de belangrijkste mappen toe aan Finder zijbalk
add_to_sidebar "$MIKKIE_ROOT"
add_to_sidebar "$MIKKIE_ROOT/SOCIAL/X_Twitter"
add_to_sidebar "$MIKKIE_ROOT/CONTENT/covers"
add_to_sidebar "$MIKKIE_ROOT/CONTENT/coloring"
add_to_sidebar "$MIKKIE_ROOT/GUMROAD"
add_to_sidebar "$AGENTS_DIR"

# Herstart Finder om zijbalk te vernieuwen
killall Finder 2>/dev/null || true
sleep 1

echo "   ✅ Finder zijbalk bijgewerkt"
echo "   💡 Als mappen niet zichtbaar zijn: sleep ze handmatig naar 'Favorieten' in Finder"

# ─── 5. AGENT CONFIG BIJWERKEN ───────────────────────────────────
echo ""
echo "⚙️  Agent output paden bijwerken in ~/.zshrc..."

# Voeg MIKKIE_WORLD_ROOT toe als env var zodat agent hem kan gebruiken
if ! grep -q "MIKKIE_WORLD_ROOT" ~/.zshrc 2>/dev/null; then
    echo "" >> ~/.zshrc
    echo "# MIKKIE WORLD — Centrale mappenstructuur" >> ~/.zshrc
    echo "export MIKKIE_WORLD_ROOT=\"$MIKKIE_ROOT\"" >> ~/.zshrc
    echo "   ✅ MIKKIE_WORLD_ROOT toegevoegd aan ~/.zshrc"
else
    echo "   ℹ️  MIKKIE_WORLD_ROOT al aanwezig in ~/.zshrc"
fi

# ─── 6. SAMENVATTING ─────────────────────────────────────────────
echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║            ✅ SETUP VOLTOOID!                 ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""
echo "📁 Structuur aangemaakt in: $MIKKIE_ROOT"
echo ""
echo "Finder zijbalk bevat nu:"
echo "  ★ MIKKIE_WORLD       ← alles"
echo "  ★ X_Twitter          ← social posts"
echo "  ★ covers             ← Gumroad covers"
echo "  ★ coloring           ← kleurplaten"
echo "  ★ GUMROAD            ← producten"
echo "  ★ mikkieworld        ← agents"
echo ""
echo "Volgende stap:"
echo "  source ~/.zshrc"
echo "  cd ~/mikkieworld && git pull"
echo "  python3 mikkie_artistly_agent.py covers"
echo ""
echo "Afbeeldingen gaan nu automatisch naar de juiste map! 🚀"
