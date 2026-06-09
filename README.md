# 🌟 MIKKIE WORLD — Agent Ecosysteem v2.0

> **Avontuurlijk · Moedig · Magisch**
> 🇳🇱 *Blijf Altijd Kind. Met je kids.*
> 🇬🇧 *Always Be a Kid. With your kids.*
> 
> Een volledig geautomatiseerd 24/7 content systeem voor het MIKKIE WORLD kindermerk.
> Gebouwd door Hendrik voor zijn zoontje Mikkie.

---

## 🚀 Snel starten

```bash
# Alles in één commando starten:
cd ~/mikkieworld && ./start_mikkie_world.sh

# Status bekijken:
python3 mikkie_guardian.py health

# Controle via Telegram:
# Stuur /help naar @mikkieworld_agent_bot
```

---

## 🤖 Alle 21 Agents

### 🔴 DAEMONS (altijd actief)

| Agent | Bestand | Functie |
|-------|---------|---------|
| **BRAIN** | `mikkie_brain.py` | Centrale orchestrator — volledig 7-daags schema |
| **GUARDIAN** | `mikkie_guardian.py` | Watchdog — bewaakt alle daemons, auto-restart |
| **TELEGRAM COMMANDER** | `mikkie_telegram_commander.py` | Mobiele controle via @mikkieworld_agent_bot |
| **MAIN** | `mikkie_agent.py` | Gumroad sales monitor + dagelijkse tweets |
| **ARTISTLY** | `mikkie_artistly_agent.py` | 24/7 afbeeldingen genereren via Artistly |
| **INSTAGRAM** | `mikkie_instagram.py` | Auto-post naar Instagram via Graph API |

### ⚡ CLI AGENTS (op aanvraag / via BRAIN)

| Agent | Bestand | Functie |
|-------|---------|---------|
| **HEART** | `mikkie_heart.py` | Brand filter — COPPA, WWJD, merkwaarden check |
| **ANALYTICS** | `mikkie_analytics.py` | Dashboard + dagelijks Telegram rapport |
| **BACKUP** | `mikkie_backup.py` | Nacht backup naar iCloud + GitHub |
| **REPURPOSE** | `mikkie_repurpose.py` | 1 post → 7 platform varianten |
| **POST DRAFT** | `mikkie_post_draft.py` | Social content genereren per karakter |
| **ASSET PROMPT** | `mikkie_asset_prompt.py` | Artistly prompts per karakter + type |
| **ENGAGEMENT LOGGER** | `mikkie_engagement_logger.py` | Social media performance bijhouden |
| **PINTEREST** | `mikkie_pinterest.py` | Auto-pin kleurplaten naar 4 boards |
| **SUNO** | `mikkie_suno.py` | Muziek-prompts voor Reels/TikTok |
| **TIKTOK** | `mikkie_tiktok.py` | Video captions + hashtag strategie |
| **NICHE** | `mikkie_niche.py` | Gumroad kansen analyse + SEO keywords |
| **GUMROAD BUNDLE** | `mikkie_gumroad_bundle.py` | €29 bundel + auto-upload covers |
| **TWEET** | `mikkie_tweet.py` | Twitter/X CLI |
| **GUMROAD** | `mikkie_gumroad.py` | Gumroad product beheer |
| **DASHBOARD** | `mikkie_dashboard.py` | Terminal dashboard |
| **CLI** | `mikkie_cli.py` | Alles in één commando (`mikkie` alias) |

---

## 📅 Dagschema (BRAIN)

Elke dag heeft een karakter:

| Dag | Karakter | Rol |
|-----|----------|-----|
| Maandag | MIKKIE | The Hero |
| Dinsdag | BUBBLES | The Loyal Sidekick |
| Woensdag | KNOEST | The Forest Keeper |
| Donderdag | FIDO | The Dragon |
| Vrijdag | NYX | The Night Princess |
| Zaterdag | ZERA | The Guardian Angel |
| Zondag | ORA | The Wise Owl |

**Dagelijks schema:**
- `07:00` — Ochtend post genereren + tweeten
- `08:00` — Tweede ochtend post
- `09:00` — Repurpose naar 7 platforms + Instagram
- `10:00` — Analytics dagrapport via Telegram
- `12:00` — Middag post
- `14:00` — Gumroad sales check
- `17:00` — Avond post
- `18:00` — Repurpose + Instagram avond
- `19:00` — Prime time post
- `22:00` — Nacht Artistly batch
- `03:00` — Backup naar iCloud + GitHub

**Wekelijks extra:**
- **Maandag**: Covers genereren, Pinterest batch, Suno weekplanning, TikTok weekplanning, Niche analyse
- **Woensdag**: Kleurplaten, Pinterest pin, TikTok caption
- **Vrijdag**: Banners, Gumroad status, SEO keywords
- **Zaterdag**: Bundle update, Suno prompt, TikTok hashtags
- **Zondag**: Weekrapport, Product roadmap, Gumroad covers uploaden

---

## 🔑 Vereiste API Keys

Voeg toe aan `~/.zshrc`:

```bash
# Verplicht
export XAI_API_KEY=jouw_grok_key
export TELEGRAM_BOT_TOKEN=8955588854:AAG-IsnHvx6gFl8MSDCOxv_Mi8aTg6Soi04
export TELEGRAM_CHAT_ID=1242180867
export GUMROAD_API_TOKEN=9byVxzgAYPnwnhL3jPjZiVxOQrSvmQrweISCtzr00RI

# Optioneel (voor extra features)
export PINTEREST_ACCESS_TOKEN=jouw_pinterest_token
export SUNO_API_KEY=jouw_suno_key
export TWITTER_API_KEY=jouw_twitter_key
export TWITTER_API_SECRET=jouw_twitter_secret
export TWITTER_ACCESS_TOKEN=jouw_access_token
export TWITTER_ACCESS_SECRET=jouw_access_secret
export ARTISTLY_API_KEY=fd58524c-5603-44a2-a23d-a9703753084b
```

---

## 📱 Telegram Commando's

Stuur naar @mikkieworld_agent_bot:

```
/help          → Alle commando's
/status        → Status van alle agents
/tweet         → Post een tweet
/post          → Genereer een post
/sales         → Gumroad sales check
/analytics     → Analytics rapport
/backup        → Handmatige backup
/pin           → Pinterest pin
/tiktok        → TikTok caption
/suno          → Muziek prompt
/niche         → Niche analyse
/bundle        → Gumroad bundle update
```

---

## 📁 Mappenstructuur

```
~/MIKKIE_WORLD/
├── CONTENT/
│   ├── Covers/          ← Karakter covers (Artistly)
│   ├── Kleurplaten/     ← Kleurplaten (Artistly)
│   ├── Stickers/        ← Stickers (Artistly)
│   ├── Social/          ← Social media afbeeldingen
│   ├── Banners/         ← Banners (Artistly)
│   ├── Video/
│   │   ├── Music/       ← Suno muziek downloads
│   │   └── MusicPrompts/← Suno prompts + lyrics
│   └── PDF/             ← PDF producten
├── SOCIAL/
│   ├── X_Twitter/       ← Tweet drafts
│   ├── Instagram/       ← Instagram posts
│   ├── Pinterest/       ← Pinterest pin drafts
│   ├── TikTok/          ← TikTok captions + scripts
│   ├── Facebook/        ← Facebook posts
│   ├── LinkedIn/        ← LinkedIn posts
│   ├── WhatsApp/        ← WhatsApp berichten
│   └── YouTube/         ← YouTube scripts
├── GUMROAD/
│   ├── Products/        ← Product drafts
│   ├── Covers/          ← Product covers
│   └── PDFs/            ← Digitale producten
├── LOGS/
│   ├── Niche/           ← Niche analyse rapporten
│   ├── brain.log
│   ├── guardian.log
│   ├── commander.log
│   └── ...
└── BACKUP/              ← Lokale backups
```

---

## 🛒 Gumroad Producten

| Product | Prijs | Status |
|---------|-------|--------|
| MIKKIE Kleurplaten | €6,99 | ✅ Live |
| BUBBLES Kleurplaten | €6,99 | ✅ Live |
| KNOEST Kleurplaten | €6,99 | ✅ Live |
| FIDO Kleurplaten | €6,99 | ✅ Live |
| NYX Kleurplaten | €6,99 | ✅ Live |
| ZERA Kleurplaten | €6,99 | ✅ Live |
| ORA Kleurplaten | €6,99 | ✅ Live |
| 7 Buitenmissies PDF | €4,99 | ✅ Live |
| **Complete Bundle** | **€29,00** | ✅ Live |

🔗 [mikkieworld.gumroad.com](https://mikkieworld.gumroad.com)

---

## 🌐 Website

🔗 [mikkie.world](https://mikkie.world)

---

## 📊 Merkwaarden

- **Avontuurlijk** — kinderen uitdagen om buiten te spelen
- **Moedig** — angst overwinnen, nieuwe dingen proberen
- **Magisch** — de wereld zien als een avontuur
- **COPPA-safe** — veilig voor kinderen
- **WWJD-proof** — bijdragen aan een betere wereld

---

## 🔧 Troubleshooting

```bash
# Health check
python3 mikkie_guardian.py health

# Logs bekijken
tail -f ~/MIKKIE_WORLD/LOGS/brain.log
tail -f ~/MIKKIE_WORLD/LOGS/guardian.log

# Alles opnieuw starten
./start_mikkie_world.sh restart

# Handmatig testen
python3 mikkie_post_draft.py x
python3 mikkie_pinterest.py boards
python3 mikkie_tiktok.py trends
python3 mikkie_niche.py analyze
```

---

*MIKKIE WORLD v2.0 — Gebouwd met ❤️ voor Mikkie*  
*Lancering: 7 juli 2026*
