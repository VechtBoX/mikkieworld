#!/usr/bin/env python3
"""
MIKKIE WORLD — Website Test Agent
===================================
Test alle pagina's, API endpoints, response times en structuur van mikkie.world.
Logt resultaten, detecteert problemen, stuurt Telegram alert bij fouten.

Gebruik:
  python3 mikkie_test_website.py          — Volledige test suite
  python3 mikkie_test_website.py quick    — Snelle health check (30 sec)
  python3 mikkie_test_website.py pages    — Alleen pagina's testen
  python3 mikkie_test_website.py api      — Alleen API endpoints testen
  python3 mikkie_test_website.py watch    — Continu testen (elke 10 min)
"""

import sys, json, time, os, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

BASE_URL   = "https://mikkie.world"
LOGS_DIR   = Path.home() / "MIKKIE_WORLD" / "LOGS" / "tests"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "")

GREEN  = "\033[92m"; RED    = "\033[91m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; BOLD   = "\033[1m";  RESET  = "\033[0m"
CYAN   = "\033[96m"; GOLD   = "\033[33m"

UA = "MikkieTestAgent/1.0 (mikkie.world)"

PAGES = [
    ("/",               "Homepage"),
    ("/discover",       "Karakters"),
    ("/wall",           "MIKKIE Wall"),
    ("/backgrounds",    "Magische Werelden"),
    ("/story",          "Merkverhaal"),
    ("/books",          "Boeken"),
    ("/animations",     "Animaties"),
    ("/shop",           "Webshop"),
    ("/token/buy",      "Token Kopen"),
    ("/prelaunch",      "Pre-launch"),
    ("/magical-north",  "Magical North"),
    ("/privacy",        "Privacy"),
    ("/coppa",          "COPPA"),
    ("/terms",          "Terms"),
]

API_TESTS = [
    {
        "name":     "Health Check",
        "path":     "/api/health",
        "method":   "GET",
        "expect_key": "status",
        "expect_val": "healthy",
        "critical": True,
    },
    {
        "name":     "Wall Stats",
        "path":     "/api/trpc/wall.getStats",
        "method":   "GET",
        "expect_key": "result",
        "critical": True,
    },
    {
        "name":     "Wall Tile ophalen",
        "path":     '/api/trpc/wall.getTile?input={"json":{"tileNumber":1}}',
        "method":   "GET",
        "expect_key": "result",
        "critical": False,
    },
    {
        "name":     "Stripe Endpoint bereikbaar",
        "path":     "/api/stripe/create-checkout",
        "method":   "POST",
        "body":     "{}",
        "expect_status": [200, 400],   # 400 = endpoint werkt maar body ontbreekt
        "critical": True,
    },
    {
        "name":     "GDPR Export endpoint",
        "path":     "/api/trpc/gdpr.requestExport",
        "method":   "POST",
        "body":     '{"json":{"email":"test@mikkie.world"}}',
        "expect_status": [200, 400, 500],
        "critical": False,
    },
]

results = []

def req(path, method="GET", body=None, timeout=10):
    url = BASE_URL + path
    data = body.encode() if body else None
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if body:
        headers["Content-Type"] = "application/json"
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        t0 = time.time()
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            ms = int((time.time() - t0) * 1000)
            raw = resp.read().decode(errors="replace")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {}
            return {"status": resp.status, "ms": ms, "body": parsed, "error": None}
    except urllib.error.HTTPError as e:
        ms = int((time.time() - t0) * 1000) if 't0' in dir() else 0
        try:
            raw = e.read().decode(errors="replace")
            parsed = json.loads(raw)
        except Exception:
            parsed = {}
        return {"status": e.code, "ms": 0, "body": parsed, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"status": 0, "ms": 0, "body": {}, "error": str(e)}

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT:
        return
    try:
        url  = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "HTML"}).encode()
        r    = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(r, timeout=5)
    except Exception:
        pass

def test_pages(verbose=True):
    if verbose:
        print(f"\n{BOLD}📄 Pagina Tests ({len(PAGES)} pagina's){RESET}")
        print(f"   {CYAN}{BASE_URL}{RESET}\n")

    page_results = []
    for path, name in PAGES:
        r = req(path, timeout=15)
        ok  = r["status"] == 200
        ms  = r["ms"]
        slow = ms > 3000

        status_icon = f"{GREEN}✅" if ok else f"{RED}❌"
        speed_icon  = f"{YELLOW}⚠️ " if slow and ok else ""

        if verbose:
            speed_str = f"{YELLOW}{ms}ms ← TRAAG{RESET}" if slow else f"{ms}ms"
            print(f"   {status_icon} {name:<22} {RESET}HTTP {r['status']}  {speed_str}")

        page_results.append({
            "name": name, "path": path,
            "status": r["status"], "ms": ms,
            "ok": ok, "slow": slow,
            "error": r["error"],
        })

    failed = [p for p in page_results if not p["ok"]]
    slow_p = [p for p in page_results if p["slow"] and p["ok"]]

    if verbose:
        print(f"\n   {'─'*45}")
        ok_count = len(page_results) - len(failed)
        col = GREEN if not failed else RED
        print(f"   {col}{BOLD}{ok_count}/{len(page_results)} pagina's online{RESET}", end="")
        if slow_p:
            print(f"  {YELLOW}| {len(slow_p)} traag (>3s){RESET}", end="")
        print()

    return page_results

def test_api(verbose=True):
    if verbose:
        print(f"\n{BOLD}🔌 API Endpoint Tests ({len(API_TESTS)} tests){RESET}\n")

    api_results = []
    for t in API_TESTS:
        r = req(t["path"], method=t.get("method","GET"), body=t.get("body"))

        # Check pass criteria
        passed = False
        if "expect_status" in t:
            passed = r["status"] in t["expect_status"]
        elif "expect_key" in t:
            if "expect_val" in t:
                passed = (r["body"].get(t["expect_key"]) == t["expect_val"])
            else:
                passed = (t["expect_key"] in r["body"])
        else:
            passed = r["status"] in [200, 201]

        icon = f"{GREEN}✅" if passed else (f"{RED}❌" if t.get("critical") else f"{YELLOW}⚠️ ")

        if verbose:
            crit_tag = f" {RED}[KRITIEK]{RESET}" if t.get("critical") and not passed else ""
            print(f"   {icon} {t['name']:<30}{RESET}  HTTP {r['status']}  {r['ms']}ms{crit_tag}")

        api_results.append({
            "name": t["name"], "path": t["path"],
            "status": r["status"], "ms": r["ms"],
            "passed": passed, "critical": t.get("critical", False),
            "error": r["error"],
        })

    if verbose:
        failed = [a for a in api_results if not a["passed"]]
        crit_failed = [a for a in failed if a["critical"]]
        print(f"\n   {'─'*45}")
        ok_count = len(api_results) - len(failed)
        col = GREEN if not crit_failed else RED
        print(f"   {col}{BOLD}{ok_count}/{len(api_results)} API tests geslaagd{RESET}")
        if crit_failed:
            print(f"   {RED}⚠️  {len(crit_failed)} kritieke failures!{RESET}")

    return api_results

def test_performance(verbose=True):
    """Test response times van de 3 kritieke pagina's."""
    if verbose:
        print(f"\n{BOLD}⚡ Performance Tests{RESET}\n")

    perf_paths = [("/", "Homepage"), ("/wall", "Wall"), ("/api/health", "API Health")]
    perf_results = []

    for path, name in perf_paths:
        times = []
        for _ in range(3):
            r = req(path, timeout=15)
            if r["status"] == 200:
                times.append(r["ms"])
            time.sleep(0.5)

        if times:
            avg = sum(times) // len(times)
            best = min(times)
            worst = max(times)
            rating = GREEN if avg < 1500 else (YELLOW if avg < 3000 else RED)
            grade  = "✅ Goed" if avg < 1500 else ("⚠️  Matig" if avg < 3000 else "❌ Traag")
            if verbose:
                print(f"   {name:<20} gem: {rating}{avg}ms{RESET}  best: {best}ms  worst: {worst}ms  {grade}")
            perf_results.append({"name": name, "avg_ms": avg, "best_ms": best, "worst_ms": worst})
        else:
            if verbose:
                print(f"   {name:<20} {RED}❌ Niet bereikbaar{RESET}")
            perf_results.append({"name": name, "avg_ms": 9999, "error": "unreachable"})

    return perf_results

def generate_suggestions(page_res, api_res, perf_res):
    """Genereer concrete verbeteringsuggesties op basis van testresultaten."""
    suggestions = []

    # Trage pagina's
    for p in page_res:
        if p.get("slow") and p["ok"]:
            suggestions.append(f"⚡ '{p['name']}' laadt traag ({p['ms']}ms) — overweeg lazy loading of caching")

    # Neergevallen pagina's
    for p in page_res:
        if not p["ok"]:
            suggestions.append(f"🔴 '{p['name']}' ({p['path']}) geeft HTTP {p['status']} — pagina is down!")

    # Kritieke API failures
    for a in api_res:
        if not a["passed"] and a["critical"]:
            suggestions.append(f"🚨 Kritieke API fout: '{a['name']}' — HTTP {a['status']} — betalingen kunnen falen!")

    # Performance
    for p in perf_res:
        if p.get("avg_ms", 0) > 3000:
            suggestions.append(f"🐌 '{p['name']}' gemiddeld {p['avg_ms']}ms — gebruikers haken af boven 3 seconden")

    # Positieve suggesties als alles goed is
    if not suggestions:
        suggestions.append("✅ Alles werkt optimaal — geen verbeteringen nodig op dit moment")
        suggestions.append("💡 Overweeg Lighthouse audit voor SEO en accessibility score")
        suggestions.append("💡 Test de betaalflow handmatig met een Stripe testkaart: 4242 4242 4242 4242")

    return suggestions

def run_full(verbose=True):
    now = datetime.now()
    if verbose:
        print(f"\n{'═'*55}")
        print(f"  {GOLD}{BOLD}MIKKIE WORLD — Website Test Suite{RESET}")
        print(f"  {now.strftime('%d %b %Y %H:%M:%S')}")
        print(f"{'═'*55}")

    page_res = test_pages(verbose)
    api_res  = test_api(verbose)
    perf_res = test_performance(verbose)
    suggestions = generate_suggestions(page_res, api_res, perf_res)

    # Samenvatting
    pages_ok   = sum(1 for p in page_res if p["ok"])
    api_ok     = sum(1 for a in api_res if a["passed"])
    crit_fail  = [a for a in api_res if not a["passed"] and a["critical"]]
    pages_fail = [p for p in page_res if not p["ok"]]

    overall_ok = not crit_fail and not pages_fail

    if verbose:
        print(f"\n{'═'*55}")
        print(f"  {BOLD}Samenvatting{RESET}")
        print(f"  {'─'*45}")
        col = GREEN if pages_ok == len(PAGES) else RED
        print(f"  {col}📄 Pagina's:  {pages_ok}/{len(PAGES)} online{RESET}")
        col = GREEN if api_ok == len(API_TESTS) else (YELLOW if not crit_fail else RED)
        print(f"  {col}🔌 API tests: {api_ok}/{len(API_TESTS)} geslaagd{RESET}")
        overall_icon = f"{GREEN}✅ ALLES OK" if overall_ok else f"{RED}❌ PROBLEMEN GEVONDEN"
        print(f"\n  {overall_icon}{RESET}")
        print(f"\n  {BOLD}Verbeteringsuggesties:{RESET}")
        for s in suggestions:
            print(f"  {s}")
        print(f"{'═'*55}\n")

    # Log opslaan
    log = {
        "timestamp": now.isoformat(),
        "overall_ok": overall_ok,
        "pages": page_res,
        "api": api_res,
        "performance": perf_res,
        "suggestions": suggestions,
    }
    log_file = LOGS_DIR / f"website_{now.strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(log, indent=2, ensure_ascii=False))

    # Telegram alert bij kritieke problemen
    if not overall_ok:
        msg_lines = ["🚨 <b>MIKKIE WORLD — Website Probleem!</b>"]
        for p in pages_fail:
            msg_lines.append(f"❌ Pagina down: {p['name']} ({p['path']})")
        for a in crit_fail:
            msg_lines.append(f"🔴 API kritiek: {a['name']} — HTTP {a['status']}")
        msg_lines.append(f"\n⏰ {now.strftime('%H:%M')} — mikkie.world")
        send_telegram("\n".join(msg_lines))

    return log

def run_quick():
    """Snelle check — alleen health + 3 kritieke pagina's."""
    print(f"\n{BOLD}⚡ Snelle Health Check{RESET}")
    r = req("/api/health", timeout=8)
    status = r["body"].get("status", "unknown") if r["status"] == 200 else "DOWN"
    col = GREEN if status == "healthy" else RED
    print(f"   {col}● Site: {status.upper()}  ({r['ms']}ms){RESET}")

    for path, name in [("/", "Homepage"), ("/wall", "Wall"), ("/prelaunch", "Pre-launch")]:
        r2 = req(path, timeout=10)
        col2 = GREEN if r2["status"] == 200 else RED
        print(f"   {col2}● {name:<15} HTTP {r2['status']}  {r2['ms']}ms{RESET}")
    print()

def run_watch():
    """Continu testen — elke 10 minuten."""
    print(f"\n{BOLD}👁️  Watch mode — test elke 10 minuten{RESET}")
    print(f"   Druk Ctrl+C om te stoppen\n")
    try:
        while True:
            os.system("clear")
            run_full(verbose=True)
            print(f"   {CYAN}Volgende test over 10 minuten...{RESET}")
            time.sleep(600)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Watch mode gestopt.{RESET}\n")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "full"
    if cmd == "quick":
        run_quick()
    elif cmd == "pages":
        test_pages()
    elif cmd == "api":
        test_api()
    elif cmd == "watch":
        run_watch()
    else:
        run_full()
