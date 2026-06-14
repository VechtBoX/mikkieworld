#!/usr/bin/env python3
"""
MIKKIE WORLD — 🎮 CLI Orchestrator v1.0
════════════════════════════════════════════════════════════════
De centrale terminal voor het hele MIKKIE WORLD agent ecosysteem.
Één commando om ze allemaal te besturen.

GEBRUIK:
  python3 mikkie_cli.py status          — overzicht van alle agents
  python3 mikkie_cli.py run all         — start alle daemons
  python3 mikkie_cli.py run <agent>     — start specifieke agent
  python3 mikkie_cli.py stop all        — stop alle daemons
  python3 mikkie_cli.py post            — genereer + check + post
  python3 mikkie_cli.py daily           — dagelijkse run (post + covers)
  python3 mikkie_cli.py check "tekst"   — HEART check op tekst
  python3 mikkie_cli.py stats           — statistieken alle agents
  python3 mikkie_cli.py logs            — live logs bekijken
  python3 mikkie_cli.py setup           — eerste keer setup

SNELKOPPELINGEN (voeg toe aan ~/.zshrc):
  alias mikkie="python3 ~/mikkieworld/mikkie_cli.py"
  alias mpost="python3 ~/mikkieworld/mikkie_cli.py post"
  alias mstatus="python3 ~/mikkieworld/mikkie_cli.py status"
════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────────
BASE_DIR    = Path.home() / "mikkieworld"
MIKKIE_ROOT = Path.home() / "MIKKIE_WORLD"
PID_DIR     = BASE_DIR / "pids"
LOG_DIR     = BASE_DIR  # logs in mikkieworld/
STATE_FILE  = BASE_DIR / "agent_state.json"

PID_DIR.mkdir(parents=True, exist_ok=True)

# ─── Agent Registry ──────────────────────────────────────────────
AGENTS = {
    # Naam              Script                    Beschrijving                    Daemon?
    "main":      ("mikkie_agent.py",         "Gumroad monitor + tweets",         True),
    "artistly":  ("mikkie_artistly_agent.py","Artistly content generator",       True),
    "heart":     ("mikkie_heart.py",         "Merkbewaker (COPPA/WWJD filter)",  False),
    "post":      ("mikkie_post_draft.py",    "Post Draft generator",             False),
    "asset":     ("mikkie_asset_prompt.py",  "Asset Prompt generator",           False),
    "logger":    ("mikkie_engagement_logger.py","Engagement tracker",            False),
    "gumroad":   ("mikkie_gumroad.py",       "Gumroad CLI",                      False),
    "tweet":     ("mikkie_tweet.py",         "Twitter/X poster",                 False),
    "dashboard": ("mikkie_dashboard.py",     "Terminal dashboard",               False),
    "launch":    ("mikkie_launch.py",        "Pre-launch emails",                False),
    "quest":     ("mikkie_quest_pdf.py",     "Quest PDF generator",              False),
}

DAEMON_AGENTS = [name for name, (_, _, is_daemon) in AGENTS.items() if is_daemon]

# ─── Kleuren voor terminal ────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
CYAN   = "\033[96m"

def c(text, color): return f"{color}{text}{RESET}"

# ─── PID management ──────────────────────────────────────────────
def get_pid(agent_name: str) -> int | None:
    pid_file = PID_DIR / f"{agent_name}.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            os.kill(pid, 0)  # check of process nog leeft
            return pid
        except (ProcessLookupError, ValueError):
            pid_file.unlink(missing_ok=True)
    return None

def save_pid(agent_name: str, pid: int):
    (PID_DIR / f"{agent_name}.pid").write_text(str(pid))

def remove_pid(agent_name: str):
    (PID_DIR / f"{agent_name}.pid").unlink(missing_ok=True)

def is_running(agent_name: str) -> bool:
    return get_pid(agent_name) is not None

# ─── Status overzicht ────────────────────────────────────────────
def cmd_status():
    print(f"\n{BOLD}{'═'*62}{RESET}")
    print(f"{BOLD}  ⚡ MIKKIE WORLD — Agent Status{RESET}  {datetime.now().strftime('%d %b %H:%M')}")
    print(f"{BOLD}{'═'*62}{RESET}")
    
    # Daemon agents
    print(f"\n  {BOLD}🔄 Daemons (24/7){RESET}")
    for name in DAEMON_AGENTS:
        script, desc, _ = AGENTS[name]
        script_path = BASE_DIR / script
        exists = script_path.exists()
        running = is_running(name)
        pid = get_pid(name)
        
        if running:
            status = c(f"● ACTIEF  (PID {pid})", GREEN)
        elif exists:
            status = c("○ GESTOPT", YELLOW)
        else:
            status = c("✗ NIET GEVONDEN", RED)
        
        print(f"  {name:<12} {status:<35} {desc}")
    
    # Tool agents
    print(f"\n  {BOLD}🛠️  Tools (on-demand){RESET}")
    for name, (script, desc, is_daemon) in AGENTS.items():
        if is_daemon:
            continue
        script_path = BASE_DIR / script
        exists = script_path.exists()
        status = c("✓ KLAAR", GREEN) if exists else c("✗ ONTBREEKT", RED)
        print(f"  {name:<12} {status:<35} {desc}")
    
    # Mappen
    print(f"\n  {BOLD}📁 Mappen{RESET}")
    folders = {
        "MIKKIE_WORLD": MIKKIE_ROOT,
        "SOCIAL/X":     MIKKIE_ROOT / "SOCIAL" / "X_Twitter",
        "CONTENT":      MIKKIE_ROOT / "CONTENT",
        "GUMROAD":      MIKKIE_ROOT / "GUMROAD",
    }
    for name, path in folders.items():
        exists = path.exists()
        count  = len(list(path.glob("*"))) if exists else 0
        status = c(f"✓ {count} bestanden", GREEN) if exists else c("✗ ONTBREEKT", RED)
        print(f"  {name:<16} {status}")
    
    # Env vars
    print(f"\n  {BOLD}🔑 Omgevingsvariabelen{RESET}")
    env_vars = [
        ("XAI_API_KEY",          "Grok AI"),
        ("GUMROAD_API_TOKEN",    "Gumroad"),
        ("TELEGRAM_BOT_TOKEN",   "Telegram"),
        ("TELEGRAM_CHAT_ID",     "Telegram Chat"),
        ("TWITTER_API_KEY",      "X/Twitter"),
        ("ARTISTLY_API_KEY",     "Artistly"),
    ]
    for var, label in env_vars:
        val = os.environ.get(var, "")
        if val:
            masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "***"
            status = c(f"✓ {masked}", GREEN)
        else:
            status = c("✗ NIET INGESTELD", RED)
        print(f"  {label:<20} {status}")
    
    print(f"\n{BOLD}{'═'*62}{RESET}\n")

# ─── Start agent daemon ──────────────────────────────────────────
def cmd_run(target: str):
    if target == "all":
        for name in DAEMON_AGENTS:
            start_daemon(name)
        return
    
    if target not in AGENTS:
        print(c(f"❌ Onbekende agent: {target}", RED))
        print(f"Beschikbaar: {', '.join(AGENTS.keys())}")
        return
    
    script, desc, is_daemon = AGENTS[target]
    script_path = BASE_DIR / script
    
    if not script_path.exists():
        print(c(f"❌ Script niet gevonden: {script_path}", RED))
        return
    
    if is_daemon:
        start_daemon(target)
    else:
        # Directe uitvoering voor tool agents
        print(c(f"▶ {target}: {desc}", BLUE))
        os.execv(sys.executable, [sys.executable, str(script_path)] + sys.argv[3:])

def start_daemon(name: str):
    script, desc, _ = AGENTS[name]
    script_path = BASE_DIR / script
    
    if not script_path.exists():
        print(c(f"  ✗ {name}: script niet gevonden", RED))
        return
    
    if is_running(name):
        pid = get_pid(name)
        print(c(f"  ● {name}: al actief (PID {pid})", YELLOW))
        return
    
    log_file = LOG_DIR / f"{name}_daemon.log"
    
    proc = subprocess.Popen(
        [sys.executable, str(script_path), "daemon"],
        stdout=open(log_file, "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True
    )
    
    save_pid(name, proc.pid)
    print(c(f"  ✓ {name}: gestart (PID {proc.pid})", GREEN))

# ─── Stop agent daemon ───────────────────────────────────────────
def cmd_stop(target: str):
    if target == "all":
        for name in DAEMON_AGENTS:
            stop_daemon(name)
        return
    
    stop_daemon(target)

def stop_daemon(name: str):
    pid = get_pid(name)
    if pid is None:
        print(c(f"  ○ {name}: niet actief", YELLOW))
        return
    
    try:
        os.kill(pid, signal.SIGTERM)
        remove_pid(name)
        print(c(f"  ✓ {name}: gestopt (PID {pid})", GREEN))
    except ProcessLookupError:
        remove_pid(name)
        print(c(f"  ○ {name}: was al gestopt", YELLOW))

# ─── Post genereren + HEART check ────────────────────────────────
def cmd_post():
    """Genereer een post, check met HEART, toon resultaat."""
    post_script = BASE_DIR / "mikkie_post_draft.py"
    heart_script = BASE_DIR / "mikkie_heart.py"
    
    if not post_script.exists():
        print(c("❌ mikkie_post_draft.py niet gevonden — bouw eerst de Post Draft agent", RED))
        return
    
    print(c("\n📝 Post genereren...", BLUE))
    result = subprocess.run(
        [sys.executable, str(post_script), "generate"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(c(f"❌ Post generatie mislukt:\n{result.stderr}", RED))
        return
    
    post_text = result.stdout.strip()
    print(f"\n  Gegenereerde post:\n  {post_text}\n")
    
    if not heart_script.exists():
        print(c("⚠️  HEART agent niet gevonden — post NIET gecheckt!", YELLOW))
        return
    
    print(c("❤️  HEART check...", BLUE))
    heart_result = subprocess.run(
        [sys.executable, str(heart_script), "check", post_text],
        capture_output=True, text=True
    )
    print(heart_result.stdout)
    
    if "GOEDGEKEURD" in heart_result.stdout:
        print(c("✅ Post goedgekeurd door HEART — klaar om te posten!", GREEN))
        # Sla op in SOCIAL/X_Twitter map
        output_dir = MIKKIE_ROOT / "SOCIAL" / "X_Twitter"
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        (output_dir / filename).write_text(post_text, encoding="utf-8")
        print(c(f"💾 Opgeslagen: SOCIAL/X_Twitter/{filename}", GREEN))
    else:
        print(c("❌ Post geblokkeerd door HEART — zie verbeterd voorstel hierboven", RED))

# ─── HEART check vanuit CLI ──────────────────────────────────────
def cmd_check(text: str):
    heart_script = BASE_DIR / "mikkie_heart.py"
    if not heart_script.exists():
        print(c("❌ mikkie_heart.py niet gevonden", RED))
        return
    
    os.execv(sys.executable, [sys.executable, str(heart_script), "check", text])

# ─── Dagelijkse run ──────────────────────────────────────────────
def cmd_daily():
    """Voer de dagelijkse routine uit: post genereren + covers check."""
    print(c(f"\n🌅 Dagelijkse MIKKIE WORLD run — {datetime.now().strftime('%d %b %Y %H:%M')}", BOLD))
    print("─"*50)
    
    # 1. Post genereren
    print(c("\n1/3 Post genereren...", BLUE))
    cmd_post()
    
    # 2. Artistly status check
    print(c("\n2/3 Artistly agent status...", BLUE))
    if is_running("artistly"):
        print(c("  ● Artistly agent actief", GREEN))
    else:
        print(c("  ○ Artistly agent niet actief — start met: mikkie run artistly", YELLOW))
    
    # 3. Stats
    print(c("\n3/3 Statistieken...", BLUE))
    cmd_stats()
    
    print(c("\n✅ Dagelijkse run voltooid!", GREEN))

# ─── Statistieken ────────────────────────────────────────────────
def cmd_stats():
    print(f"\n  {BOLD}📊 Statistieken{RESET}")
    
    # Content tellen
    content_dirs = {
        "X posts":      MIKKIE_ROOT / "SOCIAL" / "X_Twitter",
        "Covers":       MIKKIE_ROOT / "CONTENT" / "covers",
        "Kleurplaten":  MIKKIE_ROOT / "CONTENT" / "coloring",
        "Stickers":     MIKKIE_ROOT / "CONTENT" / "stickers",
        "Banners":      MIKKIE_ROOT / "CONTENT" / "banners",
    }
    
    for label, path in content_dirs.items():
        if path.exists():
            count = len([f for f in path.iterdir() if f.is_file() and not f.name.startswith(".")])
            print(f"  {label:<20} {count} bestanden")
        else:
            print(f"  {label:<20} {c('map ontbreekt', YELLOW)}")
    
    # HEART stats
    heart_log = BASE_DIR / "heart_decisions.json"
    if heart_log.exists():
        try:
            decisions = json.loads(heart_log.read_text(encoding="utf-8"))
            approved = sum(1 for d in decisions if d.get("approved"))
            print(f"\n  HEART checks:       {len(decisions)} totaal, {approved} goedgekeurd")
        except:
            pass
    
    # Engagement log
    eng_log = BASE_DIR / "engagement_log.csv"
    if eng_log.exists():
        lines = eng_log.read_text(encoding="utf-8").strip().split("\n")
        print(f"  Engagement logs:    {max(0, len(lines)-1)} entries")
    
    print()

# ─── Live logs ───────────────────────────────────────────────────
def cmd_logs(agent: str = "main"):
    log_map = {
        "main":     BASE_DIR / "agent.log",
        "artistly": BASE_DIR / "artistly_agent.log",
        "heart":    BASE_DIR / "heart_agent.log",
        "post":     BASE_DIR / "post_draft.log",
    }
    
    log_file = log_map.get(agent, BASE_DIR / f"{agent}.log")
    
    if not log_file.exists():
        print(c(f"❌ Log niet gevonden: {log_file}", RED))
        return
    
    print(c(f"📋 Live log: {log_file.name} (Ctrl+C om te stoppen)\n", BLUE))
    os.execv("/usr/bin/tail", ["tail", "-f", str(log_file)])

# ─── Setup ───────────────────────────────────────────────────────
def cmd_setup():
    """Eerste keer setup — mappen aanmaken + alias instellen."""
    print(c("\n⚙️  MIKKIE WORLD Setup\n", BOLD))
    
    # Mappen aanmaken
    dirs = [
        MIKKIE_ROOT / "SOCIAL" / "X_Twitter",
        MIKKIE_ROOT / "SOCIAL" / "Instagram",
        MIKKIE_ROOT / "SOCIAL" / "Pinterest",
        MIKKIE_ROOT / "SOCIAL" / "TikTok",
        MIKKIE_ROOT / "CONTENT" / "covers",
        MIKKIE_ROOT / "CONTENT" / "coloring",
        MIKKIE_ROOT / "CONTENT" / "stickers",
        MIKKIE_ROOT / "CONTENT" / "banners",
        MIKKIE_ROOT / "CONTENT" / "video",
        MIKKIE_ROOT / "GUMROAD",
        MIKKIE_ROOT / "LOGS",
        PID_DIR,
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(c(f"  ✓ {d.relative_to(Path.home())}", GREEN))
    
    # Alias suggestie
    zshrc = Path.home() / ".zshrc"
    alias_line = 'alias mikkie="python3 ~/mikkieworld/mikkie_cli.py"'
    
    if zshrc.exists() and alias_line not in zshrc.read_text():
        print(f"\n  {BOLD}Voeg deze alias toe aan ~/.zshrc:{RESET}")
        print(f"  {c(alias_line, CYAN)}")
        cmd_str = "echo '" + alias_line + "' >> ~/.zshrc && source ~/.zshrc"
        print(f"\n  Of voer dit uit:")
        print(f"  {c(cmd_str, CYAN)}")
    else:
        print(c("\n  ✓ Alias 'mikkie' al ingesteld", GREEN))
    
    print(c("\n✅ Setup klaar! Gebruik: python3 mikkie_cli.py status\n", GREEN))

# ─── Help ────────────────────────────────────────────────────────
def cmd_help():
    print(__doc__)
    print(f"  {BOLD}Beschikbare agents:{RESET}")
    for name, (script, desc, is_daemon) in AGENTS.items():
        daemon_tag = c(" [daemon]", CYAN) if is_daemon else ""
        print(f"  {name:<12} {desc}{daemon_tag}")
    print()

# ─── Main ────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ("--help", "-h", "help"):
        cmd_help()
        return
    
    command = args[0]
    
    if command == "status":
        cmd_status()
    
    elif command == "run":
        target = args[1] if len(args) > 1 else "all"
        cmd_run(target)
    
    elif command == "stop":
        target = args[1] if len(args) > 1 else "all"
        cmd_stop(target)
    
    elif command == "post":
        cmd_post()
    
    elif command == "daily":
        cmd_daily()
    
    elif command == "check":
        if len(args) < 2:
            print("Gebruik: mikkie check \"jouw tekst\"")
            return
        cmd_check(" ".join(args[1:]))
    
    elif command == "stats":
        cmd_stats()
    
    elif command == "logs":
        agent = args[1] if len(args) > 1 else "main"
        cmd_logs(agent)
    
    elif command == "setup":
        cmd_setup()
    
    else:
        # Probeer als agent naam
        if command in AGENTS:
            cmd_run(command)
        else:
            print(c(f"❌ Onbekend commando: {command}", RED))
            print("Gebruik: mikkie --help")

if __name__ == "__main__":
    main()

# ==================== MIKKIE VIDEO AGENT ====================
if len(sys.argv) > 1 and sys.argv[1] == "video":
    from mikkie_video import generate_video
    prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else input("Geef een prompt: ")
    generate_video(prompt)
    sys.exit(0)
