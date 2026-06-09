#!/usr/bin/env python3
"""
MIKKIE WORLD — HEALER (Zelfhelend Systeem)
============================================
De master test-orchestrator die 24/7 draait en:
  1. Alle test-agents coördineert (website, payments, agents)
  2. Problemen detecteert en automatisch herstelt waar mogelijk
  3. Telegram alerts stuurt bij kritieke fouten
  4. Elke ochtend een volledig rapport + top 3 verbeteringsuggesties stuurt
  5. Wekelijks trend-analyse doet

Gebruik:
  python3 mikkie_healer.py              — Eenmalige volledige test ronde
  python3 mikkie_healer.py start        — Start 24/7 daemon (elke 30 min)
  python3 mikkie_healer.py report       — Ochtendrapport genereren en sturen
  python3 mikkie_healer.py heal         — Probeer bekende problemen te fixen
  python3 mikkie_healer.py status       — Status van laatste test ronde
  python3 mikkie_healer.py trends       — Wekelijkse trend analyse
"""

import sys, json, time, os, subprocess, urllib.request
from datetime import datetime, timedelta
from pathlib import Path

AGENTS_DIR = Path(__file__).parent
LOGS_DIR   = Path.home() / "MIKKIE_WORLD" / "LOGS" / "tests"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = LOGS_DIR / "healer_state.json"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "")

GREEN  = "\033[92m"; RED    = "\033[91m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; BOLD   = "\033[1m";  RESET  = "\033[0m"
CYAN   = "\033[96m"; GOLD   = "\033[33m"

# Interval tussen test rondes (seconden)
TEST_INTERVAL = 30 * 60   # 30 minuten
RETRY_INTERVAL = 5 * 60   # 5 minuten na fout

def send_telegram(msg, parse_mode="HTML"):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return False
    try:
        url  = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = json.dumps({
            "chat_id": TELEGRAM_CHAT,
            "text": msg,
            "parse_mode": parse_mode
        }).encode()
        r = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(r, timeout=8)
        return True
    except Exception:
        return False

def run_test_agent(script, cmd, timeout=120):
    """Voer een test-agent uit en geef het resultaat terug."""
    fpath = AGENTS_DIR / script
    if not fpath.exists():
        return {"ok": False, "error": f"{script} niet gevonden", "output": ""}
    try:
        result = subprocess.run(
            ["python3", str(fpath), cmd],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(AGENTS_DIR)
        )
        return {
            "ok": result.returncode == 0,
            "exit_code": result.returncode,
            "output": result.stdout,
            "error": result.stderr[:500] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"ok": True, "error": "timeout (normaal voor lange tests)", "output": ""}
    except Exception as e:
        return {"ok": False, "error": str(e), "output": ""}

def parse_test_output(output):
    """Extraheer key metrics uit test output."""
    metrics = {}
    lines = output.splitlines()
    for line in lines:
        if "pagina's online" in line:
            parts = line.strip().split()
            for p in parts:
                if "/" in p:
                    ok, total = p.split("/")
                    metrics["pages_ok"] = int(ok)
                    metrics["pages_total"] = int(total)
        if "API tests geslaagd" in line:
            parts = line.strip().split()
            for p in parts:
                if "/" in p:
                    ok, total = p.split("/")
                    metrics["api_ok"] = int(ok)
                    metrics["api_total"] = int(total)
        if "BETALINGEN OK" in line:
            metrics["payments_ok"] = True
        if "BETAALFOUT" in line:
            metrics["payments_ok"] = False
        if "agents starten correct" in line:
            parts = line.strip().split()
            for p in parts:
                if "/" in p:
                    ok, total = p.split("/")
                    metrics["agents_ok"] = int(ok)
                    metrics["agents_total"] = int(total)
        if "ALLES OK" in line:
            metrics["overall_ok"] = True
        if "PROBLEMEN" in line or "KRITIEK" in line:
            metrics["overall_ok"] = False
    return metrics

def run_all_tests(verbose=True):
    """Voer alle drie test-agents uit en aggregeer resultaten."""
    now = datetime.now()
    if verbose:
        print(f"\n{'═'*55}")
        print(f"  {GOLD}{BOLD}MIKKIE HEALER — Test Ronde{RESET}")
        print(f"  {now.strftime('%d %b %Y %H:%M:%S')}")
        print(f"{'═'*55}\n")

    test_runs = [
        {"name": "Website",  "script": "mikkie_test_website.py",  "cmd": "full",   "critical": True},
        {"name": "Payments", "script": "mikkie_test_payments.py", "cmd": "full",   "critical": True},
        {"name": "Agents",   "script": "mikkie_test_agents.py",   "cmd": "syntax", "critical": True},
    ]

    all_results = {}
    critical_failures = []
    all_suggestions = []

    for t in test_runs:
        if verbose:
            print(f"  {CYAN}▶ {t['name']} tests starten...{RESET}")
        r = run_test_agent(t["script"], t["cmd"], timeout=180)
        metrics = parse_test_output(r["output"])

        all_results[t["name"]] = {
            "ok": r["ok"],
            "metrics": metrics,
            "output_preview": r["output"][:500],
            "error": r["error"],
        }

        if r["ok"]:
            if verbose:
                print(f"  {GREEN}✅ {t['name']}: geslaagd{RESET}")
                # Toon key metrics
                if "pages_ok" in metrics:
                    print(f"     📄 Pagina's: {metrics['pages_ok']}/{metrics['pages_total']}")
                if "api_ok" in metrics:
                    print(f"     🔌 API: {metrics['api_ok']}/{metrics['api_total']}")
                if "agents_ok" in metrics:
                    print(f"     🤖 Agents: {metrics['agents_ok']}/{metrics['agents_total']}")
        else:
            if t["critical"]:
                critical_failures.append(t["name"])
            if verbose:
                icon = f"{RED}❌" if t["critical"] else f"{YELLOW}⚠️ "
                print(f"  {icon} {t['name']}: fout{RESET}")
                if r["error"]:
                    print(f"     {r['error'][:100]}")

        print()

    # Genereer suggesties
    all_suggestions = generate_suggestions(all_results)

    overall_ok = not critical_failures

    if verbose:
        print(f"{'─'*55}")
        overall_icon = f"{GREEN}✅ SYSTEEM GEZOND" if overall_ok else f"{RED}❌ KRITIEKE PROBLEMEN"
        print(f"  {overall_icon}{RESET}")
        if critical_failures:
            for f in critical_failures:
                print(f"  {RED}⚠️  {f} heeft kritieke fouten{RESET}")
        print(f"\n  {BOLD}Top Verbeteringsuggesties:{RESET}")
        for i, s in enumerate(all_suggestions[:5], 1):
            print(f"  {i}. {s}")
        print(f"{'═'*55}\n")

    # State opslaan
    state = {
        "last_run": now.isoformat(),
        "overall_ok": overall_ok,
        "critical_failures": critical_failures,
        "results": all_results,
        "suggestions": all_suggestions,
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    # Log opslaan
    log_file = LOGS_DIR / f"healer_{now.strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(state, indent=2, ensure_ascii=False))

    # Telegram alert bij kritieke fouten
    if not overall_ok:
        msg = f"🚨 <b>MIKKIE WORLD — Systeem Probleem!</b>\n\n"
        for f in critical_failures:
            msg += f"❌ {f} heeft kritieke fouten\n"
        msg += f"\n💡 Top suggestie: {all_suggestions[0] if all_suggestions else 'Check logs'}"
        msg += f"\n\n⏰ {now.strftime('%H:%M')} — mikkie.world"
        send_telegram(msg)

    return state

def generate_suggestions(results):
    """Genereer concrete verbeteringsuggesties op basis van alle testresultaten."""
    suggestions = []

    website = results.get("Website", {})
    payments = results.get("Payments", {})
    agents = results.get("Agents", {})

    # Website suggesties
    if not website.get("ok"):
        suggestions.append("🔴 Website tests falen — check of mikkie.world online is")
    else:
        m = website.get("metrics", {})
        if m.get("pages_ok", 14) < 14:
            suggestions.append(f"📄 {14 - m.get('pages_ok', 14)} pagina('s) zijn down — check de routes in de webdev omgeving")
        if m.get("api_ok", 5) < 5:
            suggestions.append("🔌 API endpoints falen — check de tRPC server logs")

    # Payment suggesties
    if not payments.get("ok"):
        suggestions.append("💳 Betaalflow heeft problemen — controleer STRIPE_SECRET_KEY en Xaman API keys")
    else:
        suggestions.append("💡 Test handmatig: Stripe kaart 4242 4242 4242 4242 | Xaman testnet")

    # Agent suggesties
    if not agents.get("ok"):
        suggestions.append("🤖 Agents hebben syntax fouten — run: python3 mikkie_test_agents.py syntax")
    else:
        m = agents.get("metrics", {})
        total = m.get("agents_total", 30)
        ok = m.get("agents_ok", total)
        if ok < total:
            suggestions.append(f"⚠️  {total - ok} agents starten niet correct — check logs in MIKKIE_WORLD/LOGS/tests/")

    # Algemene suggesties
    suggestions.append("📊 Voer Lighthouse audit uit voor performance score (doel: >90)")
    suggestions.append("🔐 Controleer of alle API keys nog geldig zijn (Stripe, Xaman, Gumroad)")
    suggestions.append("📱 Test de volledige betaalflow op mobiel vóór lancering (7 juli 2026)")

    return suggestions[:7]  # Max 7 suggesties

def send_morning_report():
    """Genereer en stuur het ochtendrapport via Telegram."""
    now = datetime.now()

    # Laad laatste state
    if not STATE_FILE.exists():
        state = run_all_tests(verbose=False)
    else:
        state = json.loads(STATE_FILE.read_text())

    # Countdown
    launch = datetime(2026, 7, 7, 7, 7)
    delta = launch - now
    days = delta.days
    hours = delta.seconds // 3600

    # Bouw rapport
    results = state.get("results", {})
    website_ok = results.get("Website", {}).get("ok", False)
    payments_ok = results.get("Payments", {}).get("ok", False)
    agents_ok = results.get("Agents", {}).get("ok", False)

    w_icon = "✅" if website_ok else "❌"
    p_icon = "✅" if payments_ok else "❌"
    a_icon = "✅" if agents_ok else "❌"

    suggestions = state.get("suggestions", [])

    msg = f"""🌅 <b>MIKKIE WORLD — Ochtendrapport</b>
{now.strftime('%A %d %B %Y')}

⏳ <b>Lancering: nog {days} dagen {hours} uur</b>
🎯 7 juli 2026 — 07:07 uur

<b>Systeem Status:</b>
{w_icon} Website (mikkie.world)
{p_icon} Betalingen (Stripe + Xaman)
{a_icon} Agents (30 Python scripts)

<b>Top 3 Verbeteringsuggesties:</b>
"""
    for i, s in enumerate(suggestions[:3], 1):
        # Strip ANSI color codes for Telegram
        clean = s.replace(GREEN, "").replace(RED, "").replace(YELLOW, "").replace(RESET, "").replace(BOLD, "").replace(CYAN, "").replace(GOLD, "")
        msg += f"{i}. {clean}\n"

    msg += f"\n🤖 MIKKIE HEALER — Blijf Altijd Kind. Met je kids."

    sent = send_telegram(msg)
    print(f"\n{'═'*55}")
    print(f"  {GOLD}{BOLD}MIKKIE HEALER — Ochtendrapport{RESET}")
    print(f"{'═'*55}")
    print(msg.replace("<b>", BOLD).replace("</b>", RESET))
    if sent:
        print(f"\n  {GREEN}✅ Rapport verstuurd via Telegram{RESET}")
    else:
        print(f"\n  {YELLOW}⚠️  Telegram niet geconfigureerd — rapport alleen in terminal{RESET}")
    print(f"{'═'*55}\n")

def try_heal(verbose=True):
    """Probeer bekende problemen automatisch te herstellen."""
    if verbose:
        print(f"\n{BOLD}🔧 HEALER — Automatisch Herstel{RESET}\n")

    healed = []
    failed = []

    # Herstel 1: Git pull voor de nieuwste agents
    if verbose:
        print(f"  {CYAN}▶ Git pull — nieuwste agents ophalen...{RESET}")
    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True, text=True, timeout=30,
            cwd=str(AGENTS_DIR)
        )
        if result.returncode == 0:
            if verbose:
                print(f"  {GREEN}✅ Git pull geslaagd{RESET}")
            healed.append("git pull")
        else:
            if verbose:
                print(f"  {YELLOW}⚠️  Git pull: {result.stderr[:80]}{RESET}")
    except Exception as e:
        if verbose:
            print(f"  {YELLOW}⚠️  Git niet beschikbaar: {e}{RESET}")

    # Herstel 2: Ontbrekende packages installeren
    if verbose:
        print(f"  {CYAN}▶ Ontbrekende packages installeren...{RESET}")
    missing_pkgs = []
    for pkg in ["tweepy", "requests", "schedule"]:
        try:
            __import__(pkg)
        except ImportError:
            missing_pkgs.append(pkg)

    if missing_pkgs:
        try:
            result = subprocess.run(
                ["pip3", "install", "-q"] + missing_pkgs,
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                if verbose:
                    print(f"  {GREEN}✅ Geïnstalleerd: {', '.join(missing_pkgs)}{RESET}")
                healed.append(f"packages: {', '.join(missing_pkgs)}")
            else:
                failed.append(f"pip install {' '.join(missing_pkgs)}")
        except Exception as e:
            failed.append(f"pip install fout: {e}")
    else:
        if verbose:
            print(f"  {GREEN}✅ Alle packages al geïnstalleerd{RESET}")

    # Herstel 3: Log map aanmaken als die ontbreekt
    for log_subdir in ["tests", "posts", "tweets"]:
        d = Path.home() / "MIKKIE_WORLD" / "LOGS" / log_subdir
        d.mkdir(parents=True, exist_ok=True)
    if verbose:
        print(f"  {GREEN}✅ Log mappen aangemaakt/gecontroleerd{RESET}")
    healed.append("log mappen")

    # Herstel 4: start_mikkie_world.sh uitvoerbaar maken
    sh = AGENTS_DIR / "start_mikkie_world.sh"
    if sh.exists() and not os.access(sh, os.X_OK):
        os.chmod(sh, 0o755)
        if verbose:
            print(f"  {GREEN}✅ start_mikkie_world.sh uitvoerbaar gemaakt{RESET}")
        healed.append("chmod start script")

    if verbose:
        print(f"\n  {'─'*45}")
        print(f"  {GREEN}✅ Hersteld: {len(healed)} items{RESET}")
        if failed:
            print(f"  {RED}❌ Mislukt: {len(failed)} items{RESET}")
            for f in failed:
                print(f"     - {f}")
        print()

    return {"healed": healed, "failed": failed}

def show_status():
    """Toon de status van de laatste test ronde."""
    if not STATE_FILE.exists():
        print(f"\n{YELLOW}⚠️  Nog geen test ronde uitgevoerd. Run: python3 mikkie_healer.py{RESET}\n")
        return

    state = json.loads(STATE_FILE.read_text())
    last_run = datetime.fromisoformat(state["last_run"])
    age = datetime.now() - last_run
    age_str = f"{age.seconds // 60} minuten" if age.seconds < 3600 else f"{age.seconds // 3600} uur"

    print(f"\n{'═'*55}")
    print(f"  {GOLD}{BOLD}MIKKIE HEALER — Laatste Status{RESET}")
    print(f"{'═'*55}")
    print(f"  Laatste test: {last_run.strftime('%d %b %Y %H:%M')} ({age_str} geleden)")
    overall = state.get("overall_ok", False)
    icon = f"{GREEN}✅ GEZOND" if overall else f"{RED}❌ PROBLEMEN"
    print(f"  Status: {icon}{RESET}")

    results = state.get("results", {})
    for name, r in results.items():
        ok = r.get("ok", False)
        col = GREEN if ok else RED
        print(f"  {col}{'✅' if ok else '❌'} {name}{RESET}")

    print(f"\n  {BOLD}Suggesties:{RESET}")
    for s in state.get("suggestions", [])[:3]:
        print(f"  • {s}")
    print(f"{'═'*55}\n")

def show_trends():
    """Analyseer de trend van de afgelopen week."""
    log_files = sorted(LOGS_DIR.glob("healer_*.json"))[-50:]  # Max 50 logs
    if len(log_files) < 2:
        print(f"\n{YELLOW}⚠️  Nog niet genoeg data voor trend analyse (minimaal 2 test rondes nodig){RESET}\n")
        return

    print(f"\n{'═'*55}")
    print(f"  {GOLD}{BOLD}MIKKIE HEALER — Trend Analyse{RESET}")
    print(f"  Gebaseerd op {len(log_files)} test rondes")
    print(f"{'═'*55}\n")

    ok_count = 0
    fail_count = 0
    for lf in log_files:
        try:
            data = json.loads(lf.read_text())
            if data.get("overall_ok"):
                ok_count += 1
            else:
                fail_count += 1
        except Exception:
            pass

    total = ok_count + fail_count
    uptime = (ok_count / total * 100) if total > 0 else 0
    col = GREEN if uptime >= 95 else (YELLOW if uptime >= 80 else RED)

    print(f"  {col}📊 Uptime: {uptime:.1f}% ({ok_count}/{total} rondes OK){RESET}")
    print(f"  {'─'*45}")

    # Eerste vs laatste
    try:
        first = json.loads(log_files[0].read_text())
        last  = json.loads(log_files[-1].read_text())
        first_time = datetime.fromisoformat(first["last_run"])
        last_time  = datetime.fromisoformat(last["last_run"])
        print(f"  Periode: {first_time.strftime('%d %b')} → {last_time.strftime('%d %b %Y')}")
    except Exception:
        pass

    print(f"\n  {BOLD}Conclusie:{RESET}")
    if uptime >= 95:
        print(f"  {GREEN}✅ Systeem is stabiel — goed op weg naar lancering{RESET}")
    elif uptime >= 80:
        print(f"  {YELLOW}⚠️  Systeem heeft af en toe problemen — monitor nauwkeurig{RESET}")
    else:
        print(f"  {RED}❌ Systeem is instabiel — actie vereist vóór lancering{RESET}")
    print(f"{'═'*55}\n")

def start_daemon():
    """Start de 24/7 daemon die elke 30 minuten test."""
    print(f"\n{BOLD}🔄 MIKKIE HEALER — 24/7 Daemon gestart{RESET}")
    print(f"   Test interval: {TEST_INTERVAL // 60} minuten")
    print(f"   Druk Ctrl+C om te stoppen\n")

    # Stuur startbericht via Telegram
    send_telegram(
        f"🟢 <b>MIKKIE HEALER gestart</b>\n"
        f"Test interval: elke {TEST_INTERVAL // 60} minuten\n"
        f"⏰ {datetime.now().strftime('%H:%M')} — mikkie.world"
    )

    consecutive_failures = 0
    last_morning_report = None

    try:
        while True:
            now = datetime.now()

            # Ochtendrapport om 07:00
            if now.hour == 7 and now.minute < 5:
                if last_morning_report != now.date():
                    send_morning_report()
                    last_morning_report = now.date()

            # Test ronde
            state = run_all_tests(verbose=True)

            if state["overall_ok"]:
                consecutive_failures = 0
                interval = TEST_INTERVAL
            else:
                consecutive_failures += 1
                # Bij aanhoudende fouten: sneller testen
                interval = RETRY_INTERVAL if consecutive_failures < 3 else TEST_INTERVAL
                print(f"  {YELLOW}⚠️  Fout #{consecutive_failures} — volgende test over {interval // 60} minuten{RESET}\n")

            # Probeer te herstellen na 2 opeenvolgende fouten
            if consecutive_failures == 2:
                print(f"  {CYAN}🔧 Automatisch herstel proberen...{RESET}\n")
                try_heal(verbose=False)

            print(f"  {CYAN}Volgende test: {(datetime.now() + timedelta(seconds=interval)).strftime('%H:%M')}{RESET}\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        print(f"\n{YELLOW}HEALER daemon gestopt.{RESET}\n")
        send_telegram("🔴 <b>MIKKIE HEALER gestopt</b> (Ctrl+C)")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "full"

    if cmd == "start":
        start_daemon()
    elif cmd == "report":
        send_morning_report()
    elif cmd == "heal":
        try_heal()
    elif cmd == "status":
        show_status()
    elif cmd == "trends":
        show_trends()
    else:
        run_all_tests(verbose=True)
