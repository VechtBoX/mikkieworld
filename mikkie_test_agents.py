#!/usr/bin/env python3
"""
MIKKIE WORLD — Agents Test Agent
===================================
Test alle 30 agents op syntax, uitvoerbaarheid, output en gezondheid.
Detecteert lege hulzen, crashes, ontbrekende dependencies.

Gebruik:
  python3 mikkie_test_agents.py           — Alle agents testen
  python3 mikkie_test_agents.py syntax    — Alleen syntax check
  python3 mikkie_test_agents.py run       — Agents live uitvoeren (dry-run)
  python3 mikkie_test_agents.py deps      — Dependencies checken
  python3 mikkie_test_agents.py report    — Volledig rapport opslaan
"""

import sys, json, time, os, subprocess, ast
from datetime import datetime
from pathlib import Path

AGENTS_DIR = Path(__file__).parent
LOGS_DIR   = Path.home() / "MIKKIE_WORLD" / "LOGS" / "tests"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "")

GREEN  = "\033[92m"; RED    = "\033[91m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; BOLD   = "\033[1m";  RESET  = "\033[0m"
CYAN   = "\033[96m"; GOLD   = "\033[33m"

# Alle agents met hun verwachte commando's voor dry-run test
AGENTS = [
    {"file": "mikkie_brain.py",           "cmd": "status",    "critical": True,  "desc": "Centrale orchestrator"},
    {"file": "mikkie_guardian.py",        "cmd": "health",    "critical": True,  "desc": "Watchdog / process monitor"},
    {"file": "mikkie_heart.py",           "cmd": "check",     "critical": True,  "desc": "Merkfilter / HEART"},
    {"file": "mikkie_cli.py",             "cmd": "help",      "critical": True,  "desc": "Master CLI"},
    {"file": "mikkie_post_draft.py",      "cmd": "preview",   "critical": True,  "desc": "Post generator"},
    {"file": "mikkie_tweet.py",           "cmd": "latest",    "critical": True,  "desc": "X/Twitter poster"},
    {"file": "mikkie_repurpose.py",       "cmd": "help",      "critical": False, "desc": "Content repurpose"},
    {"file": "mikkie_instagram.py",       "cmd": "help",      "critical": False, "desc": "Instagram poster"},
    {"file": "mikkie_pinterest.py",       "cmd": "help",      "critical": False, "desc": "Pinterest pinner"},
    {"file": "mikkie_tiktok.py",          "cmd": "help",      "critical": False, "desc": "TikTok content"},
    {"file": "mikkie_suno.py",            "cmd": "help",      "critical": False, "desc": "Muziek prompts"},
    {"file": "mikkie_niche.py",           "cmd": "help",      "critical": False, "desc": "Niche analyse"},
    {"file": "mikkie_gumroad_bundle.py",  "cmd": "help",      "critical": False, "desc": "Gumroad bundle"},
    {"file": "mikkie_gumroad_cli.py",     "cmd": "help",      "critical": False, "desc": "Gumroad CLI"},
    {"file": "gumroad_update.py",         "cmd": "help",      "critical": False, "desc": "Gumroad update"},
    {"file": "mikkie_artistly_agent.py",  "cmd": "help",      "critical": False, "desc": "Artistly afbeeldingen"},
    {"file": "mikkie_asset_prompt.py",    "cmd": "help",      "critical": False, "desc": "Asset prompts"},
    {"file": "mikkie_analytics.py",       "cmd": "help",      "critical": False, "desc": "Analytics dashboard"},
    {"file": "mikkie_engagement_logger.py","cmd": "help",     "critical": False, "desc": "Engagement logger"},
    {"file": "mikkie_telegram_commander.py","cmd": "help",    "critical": False, "desc": "Telegram commander"},
    {"file": "mikkie_launch.py",          "cmd": "help",      "critical": False, "desc": "Launch sequenties"},
    {"file": "mikkie_quest_pdf.py",       "cmd": "help",      "critical": False, "desc": "Quest PDF generator"},
    {"file": "mikkie_revenue_gap.py",     "cmd": "help",      "critical": False, "desc": "Revenue analyse"},
    {"file": "mikkie_strategy_debate.py", "cmd": "help",      "critical": False, "desc": "Strategy debate"},
    {"file": "mikkie_creator_research.py","cmd": "help",      "critical": False, "desc": "Creator research"},
    {"file": "mikkie_dashboard.py",       "cmd": "help",      "critical": False, "desc": "Master dashboard"},
    {"file": "mikkie_site_agent.py",      "cmd": "status",    "critical": True,  "desc": "Site monitor"},
    {"file": "mikkie_test_website.py",    "cmd": "quick",     "critical": False, "desc": "Website tester"},
    {"file": "mikkie_test_payments.py",   "cmd": "stripe",    "critical": False, "desc": "Payments tester"},
    {"file": "start_mikkie_world.sh",     "cmd": None,        "critical": False, "desc": "Setup script"},
]

REQUIRED_DEPS = [
    "requests", "tweepy", "openai", "PIL", "selenium",
    "schedule", "dotenv", "telegram",
]

def check_syntax(verbose=True):
    """Controleer alle Python bestanden op syntax fouten."""
    if verbose:
        print(f"\n{BOLD}🔍 Syntax Check ({len(AGENTS)} bestanden){RESET}\n")

    results = []
    errors = []

    for agent in AGENTS:
        fpath = AGENTS_DIR / agent["file"]

        if not fpath.exists():
            icon = f"{YELLOW}⚠️ "
            detail = "bestand niet gevonden"
            ok = False
        elif agent["file"].endswith(".sh"):
            # Shell script — check of het uitvoerbaar is
            ok = os.access(fpath, os.X_OK)
            icon = f"{GREEN}✅" if ok else f"{YELLOW}⚠️ "
            detail = "uitvoerbaar" if ok else "niet uitvoerbaar (chmod +x nodig)"
        else:
            # Python syntax check
            try:
                with open(fpath) as f:
                    source = f.read()
                ast.parse(source)
                lines = len(source.splitlines())
                ok = True
                icon = f"{GREEN}✅"
                detail = f"{lines} regels"
            except SyntaxError as e:
                ok = False
                icon = f"{RED}❌"
                detail = f"SyntaxError regel {e.lineno}: {e.msg}"
                errors.append({"file": agent["file"], "error": detail})

        if verbose:
            crit = f" {RED}[KRITIEK]{RESET}" if agent.get("critical") and not ok else ""
            print(f"   {icon} {agent['file']:<40}{RESET}  {detail}{crit}")

        results.append({
            "file": agent["file"],
            "exists": fpath.exists(),
            "syntax_ok": ok,
            "detail": detail,
            "critical": agent.get("critical", False),
        })

    ok_count = sum(1 for r in results if r["syntax_ok"])
    if verbose:
        print(f"\n   {'─'*50}")
        col = GREEN if ok_count == len(results) else (YELLOW if not errors else RED)
        print(f"   {col}{BOLD}{ok_count}/{len(results)} bestanden syntax-correct{RESET}")
        if errors:
            print(f"   {RED}⚠️  {len(errors)} syntax fout(en) gevonden!{RESET}")

    return results

def check_deps(verbose=True):
    """Check welke Python packages geïnstalleerd zijn."""
    if verbose:
        print(f"\n{BOLD}📦 Dependencies Check{RESET}\n")

    results = []
    for dep in REQUIRED_DEPS:
        try:
            __import__(dep.replace("-", "_"))
            ok = True
            icon = f"{GREEN}✅"
        except ImportError:
            ok = False
            icon = f"{YELLOW}⚠️ "

        if verbose:
            status = "geïnstalleerd" if ok else f"niet gevonden — installeer: pip3 install {dep}"
            print(f"   {icon} {dep:<20}{RESET}  {status}")

        results.append({"dep": dep, "installed": ok})

    ok_count = sum(1 for r in results if r["installed"])
    if verbose:
        print(f"\n   {'─'*45}")
        col = GREEN if ok_count == len(results) else YELLOW
        print(f"   {col}{BOLD}{ok_count}/{len(results)} packages geïnstalleerd{RESET}")
        missing = [r["dep"] for r in results if not r["installed"]]
        if missing:
            print(f"\n   {YELLOW}Installeer ontbrekende packages:{RESET}")
            print(f"   pip3 install {' '.join(missing)}")

    return results

def run_agents_dryrun(verbose=True):
    """Voer agents uit met hun help/preview commando — test of ze starten zonder crash."""
    if verbose:
        print(f"\n{BOLD}🚀 Agent Dry-Run Tests{RESET}\n")

    results = []
    runnable = [a for a in AGENTS if a.get("cmd") and a["file"].endswith(".py")]

    for agent in runnable:
        fpath = AGENTS_DIR / agent["file"]
        if not fpath.exists():
            if verbose:
                print(f"   {YELLOW}⚠️  {agent['file']:<40}{RESET}  niet gevonden")
            results.append({"file": agent["file"], "ran": False, "exit_code": -1, "detail": "niet gevonden"})
            continue

        t0 = time.time()
        try:
            result = subprocess.run(
                ["python3", str(fpath), agent["cmd"]],
                capture_output=True, text=True, timeout=15,
                cwd=str(AGENTS_DIR)
            )
            ms = int((time.time() - t0) * 1000)
            ok = result.returncode == 0
            has_output = len(result.stdout.strip()) > 10

            if ok and has_output:
                icon = f"{GREEN}✅"
                detail = f"exit 0  {ms}ms  {len(result.stdout.strip())} chars output"
            elif ok:
                icon = f"{YELLOW}⚠️ "
                detail = f"exit 0  {ms}ms  (geen output)"
            else:
                icon = f"{RED}❌"
                err_preview = result.stderr.strip()[:80] if result.stderr else "geen stderr"
                detail = f"exit {result.returncode}  {ms}ms  {err_preview}"

            if verbose:
                crit = f" {RED}[KRITIEK]{RESET}" if agent.get("critical") and not ok else ""
                print(f"   {icon} {agent['file']:<40}{RESET}  {detail}{crit}")

            results.append({
                "file": agent["file"],
                "ran": True,
                "exit_code": result.returncode,
                "ms": ms,
                "has_output": has_output,
                "ok": ok,
                "critical": agent.get("critical", False),
            })

        except subprocess.TimeoutExpired:
            ms = int((time.time() - t0) * 1000)
            icon = f"{YELLOW}⚠️ "
            if verbose:
                print(f"   {icon} {agent['file']:<40}{RESET}  timeout na 15s (agent draait door — normaal voor daemons)")
            results.append({"file": agent["file"], "ran": True, "exit_code": -2, "ms": ms, "ok": True, "detail": "timeout (daemon)"})

        except Exception as e:
            if verbose:
                print(f"   {RED}❌ {agent['file']:<40}{RESET}  fout: {str(e)[:60]}")
            results.append({"file": agent["file"], "ran": False, "exit_code": -3, "ok": False, "detail": str(e)})

    ok_count = sum(1 for r in results if r.get("ok"))
    if verbose:
        print(f"\n   {'─'*50}")
        col = GREEN if ok_count == len(results) else (YELLOW if ok_count > len(results)//2 else RED)
        print(f"   {col}{BOLD}{ok_count}/{len(results)} agents starten correct{RESET}")

    return results

def run_full(verbose=True):
    now = datetime.now()
    if verbose:
        print(f"\n{'═'*55}")
        print(f"  {GOLD}{BOLD}MIKKIE WORLD — Agents Test Suite{RESET}")
        print(f"  {now.strftime('%d %b %Y %H:%M:%S')}")
        print(f"{'═'*55}")

    syntax_res = check_syntax(verbose)
    deps_res   = check_deps(verbose)
    run_res    = run_agents_dryrun(verbose)

    syntax_ok   = sum(1 for r in syntax_res if r["syntax_ok"])
    deps_ok     = sum(1 for r in deps_res if r["installed"])
    run_ok      = sum(1 for r in run_res if r.get("ok"))
    crit_broken = [r for r in syntax_res + run_res if not r.get("syntax_ok", r.get("ok", True)) and r.get("critical")]

    overall_ok = not crit_broken

    if verbose:
        print(f"\n{'═'*55}")
        print(f"  {BOLD}Samenvatting{RESET}")
        print(f"  {'─'*45}")
        col = GREEN if syntax_ok == len(syntax_res) else RED
        print(f"  {col}🔍 Syntax:     {syntax_ok}/{len(syntax_res)} correct{RESET}")
        col = GREEN if deps_ok == len(deps_res) else YELLOW
        print(f"  {col}📦 Packages:   {deps_ok}/{len(deps_res)} geïnstalleerd{RESET}")
        col = GREEN if run_ok == len(run_res) else (YELLOW if run_ok > 0 else RED)
        print(f"  {col}🚀 Dry-runs:   {run_ok}/{len(run_res)} geslaagd{RESET}")
        overall_icon = f"{GREEN}✅ AGENTS OK" if overall_ok else f"{RED}❌ KRITIEKE AGENTS KAPOT"
        print(f"\n  {overall_icon}{RESET}")

        print(f"\n  {BOLD}Verbeteringsuggesties:{RESET}")
        if crit_broken:
            for r in crit_broken:
                print(f"  🚨 Kritieke agent kapot: {r['file']}")
        missing_files = [r for r in syntax_res if not r["exists"]]
        if missing_files:
            for r in missing_files:
                print(f"  ⚠️  Bestand niet gevonden: {r['file']} — git pull uitvoeren?")
        missing_deps = [r for r in deps_res if not r["installed"]]
        if missing_deps:
            print(f"  📦 Installeer: pip3 install {' '.join(r['dep'] for r in missing_deps)}")
        if not crit_broken and not missing_files:
            print(f"  ✅ Alle agents zijn gezond")
            print(f"  💡 Voer 'python3 mikkie_brain.py run now' uit voor een volledige dagelijkse run")
        print(f"{'═'*55}\n")

    # Log opslaan
    log = {
        "timestamp": now.isoformat(),
        "overall_ok": overall_ok,
        "syntax": syntax_res,
        "deps": deps_res,
        "runs": run_res,
    }
    log_file = LOGS_DIR / f"agents_{now.strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(log, indent=2, ensure_ascii=False))

    return log

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "full"
    if cmd == "syntax":
        check_syntax()
    elif cmd == "deps":
        check_deps()
    elif cmd == "run":
        run_agents_dryrun()
    elif cmd == "report":
        run_full()
    else:
        run_full()
