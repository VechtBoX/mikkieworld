# MIKKIE WORLD — Professionele Daemon Management Strategie
## Hoe voorkom je `os.fork()` crashes voorgoed?

**Datum:** 9 juni 2026  
**Aanleiding:** BRAIN + ARTISTLY crash-loop door `OSError: [Errno 9] Bad file descriptor`  
**Root cause:** `os.fork()` is onveilig op macOS met Python 3.12+ (en Python 3.14)

---

## Wat ging er mis (technisch)

```
os.fork()  →  child process erft kapotte file descriptors
           →  Python 3.14 initialiseert streams strenger
           →  "Fatal Python error: init_sys_streams: can't initialize sys standard streams"
           →  GUARDIAN ziet crash → herstart → crash → herstart → loop
```

`os.fork()` is een Unix-primitive die **nooit bedoeld was voor macOS** in combinatie met moderne Python. Het werkt wel op Linux servers, maar op macOS (en zeker Python 3.12+) is het gevaarlijk.

---

## De 4 Professionele Opties — Vergelijking

| Optie | Wat is het | Moeilijkheid | Best voor |
|---|---|---|---|
| **1. subprocess.Popen** | Python stdlib, geen fork | ⭐ Makkelijk | Huidige fix (nu) |
| **2. supervisord** | Industriestandaard process manager | ⭐⭐ Gemiddeld | Professionele setup |
| **3. launchd** | macOS native, ingebouwd in OS | ⭐⭐⭐ Complex | Permanente macOS service |
| **4. PM2** | Node.js process manager, werkt ook voor Python | ⭐⭐ Gemiddeld | Als je al Node hebt |

---

## Optie 1 — subprocess.Popen (HUIDIGE FIX — al doorgevoerd)

**Wat:** Vervang `os.fork()` door `subprocess.Popen(..., start_new_session=True)`

```python
# ❌ FOUT — os.fork() op macOS Python 3.14
pid = os.fork()
if pid > 0:
    return  # parent
os.setsid()
daemon_loop()  # child crasht hier

# ✅ GOED — subprocess.Popen, macOS-safe
proc = subprocess.Popen(
    ["python3", "mikkie_brain.py", "loop"],
    stdout=open(LOG_FILE, "a"),
    stderr=open(STDERR_FILE, "a"),
    start_new_session=True,   # ← dit vervangt os.setsid()
    cwd=str(BASE_DIR)
)
pid_file.write_text(str(proc.pid))
```

**Voordelen:**
- Geen externe tools nodig
- Werkt op macOS én Linux
- Al ingebouwd in Python stdlib
- `start_new_session=True` doet hetzelfde als `os.setsid()` maar veilig

**Nadelen:**
- Geen web dashboard
- Geen automatische restart bij reboot (tenzij je launchd toevoegt)

**Conclusie:** Dit is de fix die ik nu doorvoer. Voldoende voor MIKKIE WORLD.

---

## Optie 2 — Supervisord (AANBEVOLEN voor productie)

**Wat:** De industriestandaard process manager voor Python daemons. Gebruikt door Netflix, Spotify, duizenden startups.

**Installatie op macOS:**
```bash
# macOS: gebruik brew (NIET pip3 — dat blokkeert macOS via PEP 668)
brew install supervisor
```

**Configuratie** (`~/mikkieworld/supervisord.conf`):
```ini
[supervisord]
logfile=%(ENV_HOME)s/MIKKIE_WORLD/LOGS/supervisord.log
pidfile=%(ENV_HOME)s/mikkieworld/pids/supervisord.pid
nodaemon=false

[program:brain]
command=python3 %(ENV_HOME)s/mikkieworld/mikkie_brain.py loop
directory=%(ENV_HOME)s/mikkieworld
autostart=true
autorestart=true
startretries=3
stderr_logfile=%(ENV_HOME)s/MIKKIE_WORLD/LOGS/brain_stderr.log
stdout_logfile=%(ENV_HOME)s/MIKKIE_WORLD/LOGS/brain_stdout.log
environment=XAI_API_KEY="%(ENV_XAI_API_KEY)s",TELEGRAM_BOT_TOKEN="%(ENV_TELEGRAM_BOT_TOKEN)s",TELEGRAM_CHAT_ID="%(ENV_TELEGRAM_CHAT_ID)s"

[program:telegram_commander]
command=python3 %(ENV_HOME)s/mikkieworld/mikkie_telegram_commander.py
directory=%(ENV_HOME)s/mikkieworld
autostart=true
autorestart=true
startretries=5
stderr_logfile=%(ENV_HOME)s/MIKKIE_WORLD/LOGS/commander_stderr.log
stdout_logfile=%(ENV_HOME)s/MIKKIE_WORLD/LOGS/commander_stdout.log

[inet_http_server]
port=127.0.0.1:9001

[supervisorctl]
serverurl=http://127.0.0.1:9001
```

**Gebruik:**
```bash
supervisord -c ~/mikkieworld/supervisord.conf                        # Start
supervisorctl -c ~/mikkieworld/supervisord.conf status               # Status alle agents
supervisorctl -c ~/mikkieworld/supervisord.conf restart brain        # Herstart BRAIN
supervisorctl -c ~/mikkieworld/supervisord.conf tail -f brain        # Live logs
supervisorctl -c ~/mikkieworld/supervisord.conf stop all             # Stop alles
```

**Voordelen:**
- Geen `os.fork()` — supervisord doet alles
- Automatische restart bij crash (configureerbaar: max 3x, dan alarm)
- Web dashboard op http://localhost:9001
- Env vars veilig doorgeven
- Industriestandaard — gebruikt door grote bedrijven

**Nadelen:**
- Start niet automatisch bij reboot (combineer met launchd)
- Extra tool om te leren

---

## Optie 3 — launchd (macOS NATIVE — meest robuust)

**Wat:** Ingebouwd in macOS. Elke app die je op je Mac installeert gebruikt dit. Herstart automatisch bij reboot, bij crash, op schema.

**Plist bestand** (`~/Library/LaunchAgents/world.mikkie.brain.plist`):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>world.mikkie.brain</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/hendrikbroeze/mikkieworld/mikkie_brain.py</string>
        <string>loop</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>/Users/hendrikbroeze/mikkieworld</string>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/hendrikbroeze/MIKKIE_WORLD/LOGS/brain_stdout.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/hendrikbroeze/MIKKIE_WORLD/LOGS/brain_stderr.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>XAI_API_KEY</key>
        <string>JOUW_KEY_HIER</string>
        <key>TELEGRAM_BOT_TOKEN</key>
        <string>JOUW_TOKEN_HIER</string>
        <key>TELEGRAM_CHAT_ID</key>
        <string>JOUW_CHAT_ID_HIER</string>
    </dict>
</dict>
</plist>
```

**Installeren:**
```bash
launchctl load ~/Library/LaunchAgents/world.mikkie.brain.plist
launchctl start world.mikkie.brain
launchctl list | grep mikkie    # Status
launchctl stop world.mikkie.brain
launchctl unload ~/Library/LaunchAgents/world.mikkie.brain.plist
```

**Voordelen:**
- Start automatisch bij Mac reboot
- macOS native — geen extra software
- Meest stabiel op macOS
- `KeepAlive: true` = automatische restart bij crash

**Nadelen:**
- XML plist = niet prettig om te schrijven
- Env vars hardcoded in plist (beveiligingsrisico)
- Moeilijker te debuggen

---

## Optie 4 — PM2 (als je Node.js al hebt)

**Wat:** Process manager uit de Node.js wereld, maar werkt uitstekend voor Python.

```bash
npm install -g pm2

# Start BRAIN
pm2 start mikkie_brain.py --interpreter python3 --name brain -- loop

# Start TELEGRAM COMMANDER  
pm2 start mikkie_telegram_commander.py --interpreter python3 --name commander

# Status
pm2 status
pm2 logs brain
pm2 restart brain

# Automatisch starten bij reboot
pm2 startup
pm2 save
```

**Voordelen:**
- Mooie web dashboard (`pm2 plus`)
- Eenvoudigste syntax
- Werkt op macOS, Linux, Windows
- Automatische restart bij reboot via `pm2 startup`

**Nadelen:**
- Vereist Node.js
- Niet de Python-standaard

---

## Mijn Aanbeveling voor MIKKIE WORLD

### Nu (vandaag) — Fase 1
**Gebruik `subprocess.Popen`** — al doorgevoerd in GUARDIAN en BRAIN.  
Dit lost de crash-loop direct op. Geen extra tools nodig.

### Over 2-4 weken — Fase 2 (optioneel maar sterk aanbevolen)
**Voeg supervisord toe** als MIKKIE WORLD groeit naar 10+ daemons.

```bash
# Installeer via brew (macOS-safe)
brew install supervisor

# Config staat al klaar in ~/mikkieworld/supervisord.conf
# Start
supervisord -c ~/mikkieworld/supervisord.conf
```

### Na lancering (7 juli 2026) — Fase 3
**Voeg launchd toe** zodat BRAIN en TELEGRAM COMMANDER automatisch starten bij Mac reboot.  
Ik kan de plist bestanden genereren als je dat wilt.

---

## Samenvatting — Gouden Regels

> **Regel 1:** Gebruik NOOIT `os.fork()` op macOS met Python 3.10+  
> **Regel 2:** Gebruik altijd `subprocess.Popen(..., start_new_session=True)` voor background processen  
> **Regel 3:** Schrijf altijd stdout én stderr naar aparte logbestanden  
> **Regel 4:** Gebruik een process manager (supervisord of launchd) voor productie  
> **Regel 5:** Bouw crash-limieten in (max 3x per uur) zodat je geen oneindige loops krijgt

---

*MIKKIE WORLD — Avontuurlijk · Moedig · Magisch*  
*Blijf Altijd Kind. Met je kids.*
