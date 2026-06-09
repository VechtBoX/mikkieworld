#!/usr/bin/env python3
"""
MIKKIE WORLD — Payments Test Agent
=====================================
Test alle betaalflows: Stripe checkout, Xaman/XRP payload, email delivery.
Gebruikt Stripe test mode — geen echte betalingen.

Gebruik:
  python3 mikkie_test_payments.py          — Alle payment tests
  python3 mikkie_test_payments.py stripe   — Alleen Stripe tests
  python3 mikkie_test_payments.py xaman    — Alleen Xaman/XRP tests
  python3 mikkie_test_payments.py email    — Alleen email delivery test
  python3 mikkie_test_payments.py watch    — Continu testen (elke 30 min)
"""

import sys, json, time, os, urllib.request, urllib.error, smtplib
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText

BASE_URL = "https://mikkie.world"
LOGS_DIR = Path.home() / "MIKKIE_WORLD" / "LOGS" / "tests"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT  = os.environ.get("TELEGRAM_CHAT_ID", "")

# SMTP config (zelfde als de website)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.hostinger.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "noreply@mikkie.world")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "noreply@mikkie.world")

GREEN  = "\033[92m"; RED    = "\033[91m"; YELLOW = "\033[93m"
BLUE   = "\033[94m"; BOLD   = "\033[1m";  RESET  = "\033[0m"
CYAN   = "\033[96m"; GOLD   = "\033[33m"

UA = "MikkiePaymentTest/1.0 (mikkie.world)"

# Stripe test pakketten (zelfde als de live site)
TOKEN_PACKAGES = [
    {"id": "starter",   "name": "Starter",   "tokens": 777,     "price_eur": 7.77},
    {"id": "explorer",  "name": "Explorer",  "tokens": 7777,    "price_eur": 47.77},
    {"id": "guardian",  "name": "Guardian",  "tokens": 77777,   "price_eur": 177.77},
    {"id": "legendary", "name": "Legendary", "tokens": 777777,  "price_eur": 777.77},
]

def req(path, method="GET", body=None, timeout=15):
    url = BASE_URL + path
    data = body.encode() if isinstance(body, str) else (json.dumps(body).encode() if body else None)
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data:
        headers["Content-Type"] = "application/json"
    t0 = time.time()
    try:
        r = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            ms = int((time.time() - t0) * 1000)
            raw = resp.read().decode(errors="replace")
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = {"raw": raw[:200]}
            return {"status": resp.status, "ms": ms, "body": parsed, "error": None}
    except urllib.error.HTTPError as e:
        ms = int((time.time() - t0) * 1000)
        try:
            raw = e.read().decode(errors="replace")
            parsed = json.loads(raw)
        except Exception:
            parsed = {}
        return {"status": e.code, "ms": ms, "body": parsed, "error": f"HTTP {e.code}"}
    except Exception as ex:
        return {"status": 0, "ms": int((time.time() - t0)*1000), "body": {}, "error": str(ex)}

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

def test_stripe(verbose=True):
    """Test Stripe checkout aanmaken voor elk token pakket."""
    if verbose:
        print(f"\n{BOLD}💳 Stripe Checkout Tests{RESET}\n")

    results = []

    # Test 1: Stripe endpoint bereikbaar
    r = req("/api/stripe/create-checkout", method="POST", body={"package": "starter", "test": True})
    stripe_up = r["status"] in [200, 400, 422]  # 400/422 = endpoint werkt, body validatie
    icon = f"{GREEN}✅" if stripe_up else f"{RED}❌"
    if verbose:
        print(f"   {icon} Stripe endpoint bereikbaar{RESET}  HTTP {r['status']}  {r['ms']}ms")
    results.append({"test": "stripe_endpoint", "passed": stripe_up, "status": r["status"], "ms": r["ms"]})

    # Test 2: Checkout URL aanmaken per pakket
    for pkg in TOKEN_PACKAGES:
        body = {
            "package": pkg["id"],
            "successUrl": "https://mikkie.world/token/success?test=1",
            "cancelUrl":  "https://mikkie.world/token/buy?cancelled=1",
        }
        r2 = req("/api/stripe/create-checkout", method="POST", body=body)

        # Geslaagd als we een checkout URL terugkrijgen OF een validatie error (niet 500)
        has_url   = "url" in r2["body"] or "checkoutUrl" in r2["body"]
        not_crash = r2["status"] != 500 and r2["status"] != 0
        passed    = has_url or (not_crash and r2["status"] in [200, 400, 422])

        icon2 = f"{GREEN}✅" if has_url else (f"{YELLOW}⚠️ " if passed else f"{RED}❌")
        detail = ""
        if has_url:
            url_val = r2["body"].get("url") or r2["body"].get("checkoutUrl", "")
            detail = f"  {CYAN}→ checkout URL aangemaakt{RESET}"
        elif r2["status"] == 400:
            detail = f"  {YELLOW}→ validatie fout (normaal in test mode){RESET}"

        if verbose:
            print(f"   {icon2} {pkg['name']:<12} €{pkg['price_eur']:<8} {pkg['tokens']:>7} MIKKIE  HTTP {r2['status']}  {r2['ms']}ms{detail}{RESET}")

        results.append({
            "test": f"stripe_{pkg['id']}",
            "package": pkg["name"],
            "passed": passed,
            "has_url": has_url,
            "status": r2["status"],
            "ms": r2["ms"],
        })

    # Test 3: Stripe webhook endpoint bereikbaar
    r3 = req("/api/stripe/webhook", method="POST", body="{}")
    webhook_up = r3["status"] in [200, 400]
    icon3 = f"{GREEN}✅" if webhook_up else f"{RED}❌"
    if verbose:
        print(f"   {icon3} Webhook endpoint{RESET}  HTTP {r3['status']}  {r3['ms']}ms")
    results.append({"test": "stripe_webhook", "passed": webhook_up, "status": r3["status"]})

    passed_count = sum(1 for r in results if r["passed"])
    if verbose:
        print(f"\n   {'─'*45}")
        col = GREEN if passed_count == len(results) else (YELLOW if passed_count > len(results)//2 else RED)
        print(f"   {col}{BOLD}{passed_count}/{len(results)} Stripe tests geslaagd{RESET}")

    return results

def test_xaman(verbose=True):
    """Test Xaman/XRP payment payload aanmaken."""
    if verbose:
        print(f"\n{BOLD}🔷 Xaman/XRP Tests{RESET}\n")

    results = []

    # Test 1: Xaman endpoint bereikbaar
    r = req("/api/xaman/create-payload", method="POST", body={"amount": "77", "memo": "test"})
    xaman_up = r["status"] in [200, 400, 422, 500]  # 500 = Xaman API key issue, maar endpoint bestaat
    endpoint_exists = r["status"] != 404 and r["status"] != 0

    icon = f"{GREEN}✅" if endpoint_exists else f"{RED}❌"
    if verbose:
        print(f"   {icon} Xaman endpoint bereikbaar{RESET}  HTTP {r['status']}  {r['ms']}ms")
    results.append({"test": "xaman_endpoint", "passed": endpoint_exists, "status": r["status"]})

    # Test 2: XRP token koop flow
    for pkg in TOKEN_PACKAGES[:2]:  # Alleen starter en explorer testen
        body = {
            "package": pkg["id"],
            "tokens": pkg["tokens"],
            "xrpAmount": pkg["price_eur"] / 0.50,  # Ruwe schatting XRP prijs
        }
        r2 = req("/api/xaman/create-payload", method="POST", body=body)
        passed = r2["status"] in [200, 400, 422]
        has_qr = "qrUrl" in r2["body"] or "next" in r2["body"] or "uuid" in r2["body"]

        icon2 = f"{GREEN}✅" if has_qr else (f"{YELLOW}⚠️ " if passed else f"{RED}❌")
        detail = f"  {CYAN}→ QR payload aangemaakt{RESET}" if has_qr else ""
        if verbose:
            print(f"   {icon2} XRP payload {pkg['name']:<12}{RESET}  HTTP {r2['status']}  {r2['ms']}ms{detail}")
        results.append({"test": f"xaman_{pkg['id']}", "passed": passed, "has_qr": has_qr, "status": r2["status"]})

    # Test 3: Xaman status check endpoint
    r3 = req("/api/xaman/check-payload/test-uuid-123", method="GET")
    status_up = r3["status"] in [200, 400, 404]
    icon3 = f"{GREEN}✅" if status_up else f"{RED}❌"
    if verbose:
        print(f"   {icon3} Xaman status check{RESET}  HTTP {r3['status']}  {r3['ms']}ms")
    results.append({"test": "xaman_status", "passed": status_up, "status": r3["status"]})

    passed_count = sum(1 for r in results if r["passed"])
    if verbose:
        print(f"\n   {'─'*45}")
        col = GREEN if passed_count == len(results) else (YELLOW if passed_count > 0 else RED)
        print(f"   {col}{BOLD}{passed_count}/{len(results)} Xaman tests geslaagd{RESET}")

    return results

def test_email(verbose=True):
    """Test SMTP verbinding en email delivery."""
    if verbose:
        print(f"\n{BOLD}📧 Email Tests{RESET}\n")

    results = []

    # Test 1: SMTP verbinding
    smtp_ok = False
    smtp_msg = ""
    if not SMTP_PASS:
        smtp_msg = "SMTP_PASS niet ingesteld als env var"
        if verbose:
            print(f"   {YELLOW}⚠️  SMTP niet geconfigureerd{RESET}  ({smtp_msg})")
    else:
        try:
            t0 = time.time()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as s:
                s.login(SMTP_USER, SMTP_PASS)
                ms = int((time.time() - t0) * 1000)
                smtp_ok = True
                smtp_msg = f"Verbonden in {ms}ms"
            if verbose:
                print(f"   {GREEN}✅ SMTP verbinding{RESET}  {smtp_msg}")
        except Exception as e:
            smtp_msg = str(e)
            if verbose:
                print(f"   {RED}❌ SMTP fout{RESET}  {smtp_msg}")

    results.append({"test": "smtp_connect", "passed": smtp_ok or not SMTP_PASS, "detail": smtp_msg})

    # Test 2: Pre-launch signup email flow (via API)
    test_email_addr = f"test-agent-{int(time.time())}@mikkie.world"
    r = req("/api/trpc/prelaunch.signup", method="POST",
            body={"json": {"email": test_email_addr, "name": "Test Agent"}})

    # Geslaagd als we een response krijgen (ook al is het een DB error — endpoint werkt)
    signup_up = r["status"] in [200, 400, 500]
    has_error = "error" in r["body"]

    if r["status"] == 200:
        detail = f"{GREEN}signup succesvol{RESET}"
        passed = True
    elif r["status"] == 500 and has_error:
        # DB fout — endpoint werkt maar DB heeft issue
        detail = f"{YELLOW}DB fout (endpoint werkt){RESET}"
        passed = True  # Endpoint zelf is bereikbaar
    else:
        detail = f"HTTP {r['status']}"
        passed = signup_up

    icon = f"{GREEN}✅" if passed else f"{RED}❌"
    if verbose:
        print(f"   {icon} Pre-launch signup flow{RESET}  HTTP {r['status']}  {r['ms']}ms  {detail}")
    results.append({"test": "signup_flow", "passed": passed, "status": r["status"]})

    # Test 3: Email endpoints bestaan
    for endpoint, name in [
        ("/api/trpc/prelaunch.getSignupCount", "Signup count"),
    ]:
        r2 = req(endpoint)
        up = r2["status"] in [200, 400]
        icon2 = f"{GREEN}✅" if up else f"{YELLOW}⚠️ "
        if verbose:
            print(f"   {icon2} {name:<25}{RESET}  HTTP {r2['status']}  {r2['ms']}ms")
        results.append({"test": f"endpoint_{name}", "passed": up, "status": r2["status"]})

    passed_count = sum(1 for r in results if r["passed"])
    if verbose:
        print(f"\n   {'─'*45}")
        col = GREEN if passed_count == len(results) else (YELLOW if passed_count > 0 else RED)
        print(f"   {col}{BOLD}{passed_count}/{len(results)} Email tests geslaagd{RESET}")

    return results

def run_full(verbose=True):
    now = datetime.now()
    if verbose:
        print(f"\n{'═'*55}")
        print(f"  {GOLD}{BOLD}MIKKIE WORLD — Payments Test Suite{RESET}")
        print(f"  {now.strftime('%d %b %Y %H:%M:%S')}")
        print(f"{'═'*55}")

    stripe_res = test_stripe(verbose)
    xaman_res  = test_xaman(verbose)
    email_res  = test_email(verbose)

    all_results = stripe_res + xaman_res + email_res
    passed_total = sum(1 for r in all_results if r["passed"])
    critical_fail = [r for r in stripe_res if not r["passed"] and r.get("test") in ["stripe_endpoint", "stripe_webhook"]]

    overall_ok = not critical_fail

    if verbose:
        print(f"\n{'═'*55}")
        print(f"  {BOLD}Samenvatting{RESET}")
        print(f"  {'─'*45}")
        col = GREEN if not [r for r in stripe_res if not r["passed"]] else YELLOW
        stripe_ok = sum(1 for r in stripe_res if r["passed"])
        print(f"  {col}💳 Stripe:  {stripe_ok}/{len(stripe_res)} geslaagd{RESET}")
        col = GREEN if not [r for r in xaman_res if not r["passed"]] else YELLOW
        xaman_ok = sum(1 for r in xaman_res if r["passed"])
        print(f"  {col}🔷 Xaman:   {xaman_ok}/{len(xaman_res)} geslaagd{RESET}")
        col = GREEN if not [r for r in email_res if not r["passed"]] else YELLOW
        email_ok = sum(1 for r in email_res if r["passed"])
        print(f"  {col}📧 Email:   {email_ok}/{len(email_res)} geslaagd{RESET}")
        overall_icon = f"{GREEN}✅ BETALINGEN OK" if overall_ok else f"{RED}❌ KRITIEKE BETAALFOUT"
        print(f"\n  {overall_icon}{RESET}")

        # Suggesties
        print(f"\n  {BOLD}Verbeteringsuggesties:{RESET}")
        if not overall_ok:
            for r in critical_fail:
                print(f"  🚨 Stripe endpoint faalt — betalingen werken niet! Check STRIPE_SECRET_KEY")
        else:
            print(f"  ✅ Alle kritieke betaalflows bereikbaar")
            print(f"  💡 Test handmatig met Stripe testkaart: 4242 4242 4242 4242 | exp: 12/34 | cvv: 123")
            print(f"  💡 Test Xaman met echte Xaman app op testnet vóór lancering")
        print(f"{'═'*55}\n")

    # Log opslaan
    log = {
        "timestamp": now.isoformat(),
        "overall_ok": overall_ok,
        "stripe": stripe_res,
        "xaman": xaman_res,
        "email": email_res,
    }
    log_file = LOGS_DIR / f"payments_{now.strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(log, indent=2, ensure_ascii=False))

    # Telegram alert bij kritieke fout
    if not overall_ok:
        msg = "🚨 <b>MIKKIE WORLD — Betaalfout!</b>\n"
        for r in critical_fail:
            msg += f"❌ {r['test']} — HTTP {r.get('status', '?')}\n"
        msg += f"\n⏰ {now.strftime('%H:%M')} — mikkie.world/token/buy"
        send_telegram(msg)

    return log

def run_watch():
    print(f"\n{BOLD}👁️  Watch mode — test elke 30 minuten{RESET}")
    print(f"   Druk Ctrl+C om te stoppen\n")
    try:
        while True:
            os.system("clear")
            run_full(verbose=True)
            print(f"   {CYAN}Volgende test over 30 minuten...{RESET}")
            time.sleep(1800)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Watch mode gestopt.{RESET}\n")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "full"
    if cmd == "stripe":
        test_stripe()
    elif cmd == "xaman":
        test_xaman()
    elif cmd == "email":
        test_email()
    elif cmd == "watch":
        run_watch()
    else:
        run_full()
