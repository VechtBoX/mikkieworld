#!/usr/bin/env python3
"""
📱 MIKKIE WORLD — Telegram Commander
Stuur je Mac en alle agents aan via je telefoon.
"""

import os, json, time, subprocess, threading, urllib.request, datetime, sys, re

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID   = str(os.environ.get("TELEGRAM_CHAT_ID", ""))
AGENTS_DIR = os.path.expanduser("~/mikkieworld")
WORLD_DIR  = os.path.expanduser("~/MIKKIE_WORLD")

def tg_send(text):
    if not BOT_TOKEN: return
    try:
        payload = json.dumps({"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except: pass

def tg_updates(offset=0):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
        resp = urllib.request.urlopen(url, timeout=35)
        return json.loads(resp.read()).get("result", [])
    except: return []

def run_agent(script, args=[]):
    cmd = [sys.executable, os.path.join(AGENTS_DIR, script)] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=AGENTS_DIR, env={**os.environ})
        out = r.stdout.strip() or r.stderr.strip()
        return re.sub(r'\033\[[0-9;]*m', '', out)[:3000] or "✅ Klaar"
    except subprocess.TimeoutExpired: return "⏱ Timeout na 120s"
    except Exception as e: return f"❌ Fout: {e}"

def cmd_status():
    nu = datetime.datetime.now().strftime("%d %b %H:%M")
    x_dir = os.path.join(WORLD_DIR, "SOCIAL", "X_Twitter")
    dl_dir = os.path.join(AGENTS_DIR, "artistly_output")
    x_posts = len([f for f in os.listdir(x_dir) if f.endswith('.txt')]) if os.path.exists(x_dir) else 0
    images  = len([f for f in os.listdir(dl_dir) if f.endswith('.png')]) if os.path.exists(dl_dir) else 0
    return f"🎮 *MIKKIE WORLD* — {nu}\n\n📁 X posts: {x_posts}\n🖼 Afbeeldingen: {images}\n\n🌐 mikkie.world ✅\n📅 Lancering: 7 juli 2026\n\n/help voor alle commando's"

def cmd_post():
    out = run_agent("mikkie_post_draft.py", ["x"])
    lines = [l for l in out.split('\n') if l.strip() and '═' not in l and '─' not in l]
    return "✍️ *Nieuwe post:*\n\n" + '\n'.join(lines[:20])

def cmd_heart(tekst):
    out = run_agent("mikkie_heart.py", ["check", tekst])
    return f"❤️ *HEART check:*\n\n{out[:1500]}"

def cmd_repurpose():
    x_dir = os.path.join(WORLD_DIR, "SOCIAL", "X_Twitter")
    if not os.path.exists(x_dir): return "❌ Geen posts. Gebruik /post eerst."
    bestanden = sorted([f for f in os.listdir(x_dir) if f.endswith('.txt')])
    if not bestanden: return "❌ Geen posts. Gebruik /post eerst."
    with open(os.path.join(x_dir, bestanden[-1])) as f: tekst = f.read()[:500]
    out = run_agent("mikkie_repurpose.py", ["repurpose", tekst])
    return f"🔄 *Repurpose klaar:*\n\n{out[:2000]}"

def cmd_analytics():
    out = run_agent("mikkie_analytics.py", ["report"])
    lines = [l for l in out.split('\n') if l.strip() and '═' not in l]
    return "📊 *Analytics:*\n\n" + '\n'.join(lines[:30])

def cmd_backup():
    out = run_agent("mikkie_backup.py", ["run"])
    return f"💾 *Backup:*\n\n{out[:1500]}"

def cmd_brain():
    dag = datetime.datetime.now().strftime("%A")
    dag_nl = {"Monday":"Maandag","Tuesday":"Dinsdag","Wednesday":"Woensdag","Thursday":"Donderdag","Friday":"Vrijdag","Saturday":"Zaterdag","Sunday":"Zondag"}.get(dag, dag)
    schema = {"Maandag":"🎨 Covers","Dinsdag":"📄 Kleurplaten","Woensdag":"🏷️ Stickers","Donderdag":"📱 Social posts","Vrijdag":"🖼️ Banners","Zaterdag":"📊 Analytics","Zondag":"🔄 Repurpose"}
    return f"🧠 *BRAIN — {dag_nl}*\n\nVandaag: *{schema.get(dag_nl,'Vrij')}*\n\n⏰ Schema:\n• 07:00 Post → X\n• 09:00 Repurpose\n• 12:00 Middag post\n• 13:00 Artistly\n• 17:00 Avond post\n• 19:00 Prime time\n• 23:55 Dagrapport"

def cmd_help():
    return """📱 *MIKKIE WORLD Commander*

*Content:*
/post — X post genereren
/instagram — Instagram post
/repurpose — 7 platform varianten
/daily — Dagelijkse routine

*Check & Data:*
/status — Systeem overzicht
/brain — Schema vandaag
/analytics — Statistieken
/heart [tekst] — Merkcheck

*Beheer:*
/backup — Backup uitvoeren
/help — Dit overzicht

*Voorbeeld:*
`/heart Mikkie speelt buiten`"""

COMMANDS = {
    "/start": lambda _: cmd_help(),
    "/help":  lambda _: cmd_help(),
    "/status":lambda _: cmd_status(),
    "/post":  lambda _: cmd_post(),
    "/instagram": lambda _: run_agent("mikkie_post_draft.py", ["instagram"]),
    "/repurpose": lambda _: cmd_repurpose(),
    "/analytics": lambda _: cmd_analytics(),
    "/backup":lambda _: cmd_backup(),
    "/brain": lambda _: cmd_brain(),
    "/daily": lambda _: cmd_post(),
}

def handle(text):
    text = text.strip()
    if text.lower().startswith("/heart "):
        return cmd_heart(text[7:].strip())
    cmd = text.split()[0].lower()
    if cmd in COMMANDS: return COMMANDS[cmd](text)
    return f"❓ Onbekend: `{cmd}`\n\n/help voor alle commando's"

def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN niet ingesteld!")
        sys.exit(1)
    print("📱 MIKKIE WORLD Telegram Commander gestart!")
    print(f"   Wacht op commando's van Chat ID: {CHAT_ID}")
    tg_send("🎮 *MIKKIE WORLD Commander Online!*\n\nJe Mac luistert nu naar je telefoon.\n\n/help voor alle commando's")
    offset = 0
    while True:
        try:
            for update in tg_updates(offset):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                if not msg: continue
                if str(msg.get("from", {}).get("id", "")) != CHAT_ID: continue
                tekst = msg.get("text", "").strip()
                if not tekst: continue
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {tekst}")
                def process(t=tekst):
                    tg_send(handle(t))
                threading.Thread(target=process, daemon=True).start()
        except KeyboardInterrupt:
            print("\n👋 Commander gestopt.")
            tg_send("🔴 *Commander offline.*")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
