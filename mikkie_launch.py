#!/usr/bin/env python3
"""MIKKIE WORLD Pre-launch Email Sequence Builder"""
import os, sys, json, urllib.request, urllib.error, base64
from datetime import datetime

MAILCHIMP_KEY    = os.environ.get('MAILCHIMP_API_KEY', '')
MAILCHIMP_SERVER = os.environ.get('MAILCHIMP_SERVER', 'us14')
MAILCHIMP_LIST   = '75412e3953'
LAUNCH_DATE      = datetime(2026, 7, 7, 7, 7)

def days_to_launch():
    return (LAUNCH_DATE - datetime.now()).days

def mc_req(method, endpoint, data=None):
    url = f"https://{MAILCHIMP_SERVER}.api.mailchimp.com/3.0{endpoint}"
    creds = base64.b64encode(f'anystring:{MAILCHIMP_KEY}'.encode()).decode()
    headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode().strip()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"Mailchimp Error {e.code}: {err}")
        return {}

SEQUENCE = [
    {
        "day": 0,
        "subject": "Welkom bij MIKKIE WORLD! Jouw avontuur begint nu",
        "preview": "7 gratis missies wachten op jou",
        "body": """<h2>Welkom, avonturier!</h2>
<p>Je bent er! MIKKIE WORLD is een wereld vol avontuur, moed en magie — speciaal voor kinderen die buiten willen spelen en dromen.</p>
<p>Ik ben Hendrik, de vader achter MIKKIE WORLD. Ik bouw dit voor mijn zoon Mikkie en alle kinderen die verdienen om held te zijn in hun eigen verhaal.</p>
<h3>Jouw 7 gratis buitenmissies</h3>
<p>Als welkomstcadeau krijg je de <strong>MIKKIE 7 Gratis Buitenmissies</strong> — download hem hieronder en ga vandaag nog naar buiten!</p>
<p><a href="https://mikkieworld.gumroad.com" style="background:#F59E0B;color:#fff;padding:12px 24px;text-decoration:none;border-radius:50px;font-weight:bold">Download Gratis Missies</a></p>
<p>Op 7 juli 2026 om 07:07 opent MIKKIE WORLD officieel. Jij bent er als eerste bij.</p>
<p>Avontuurlijk groet,<br><strong>Hendrik & MIKKIE</strong></p>"""
    },
    {
        "day": 3,
        "subject": "Maak kennis met MIKKIE en zijn 6 vrienden",
        "preview": "7 karakters, 77 missies, 1 magische wereld",
        "body": """<h2>De 7 Helden van MIKKIE WORLD</h2>
<p>Elke held heeft zijn eigen kracht. Welke past bij jouw kind?</p>
<ul>
<li><strong>MIKKIE</strong> — Avontuurlijk en moedig. Hij springt altijd als eerste.</li>
<li><strong>BUBBLES</strong> — Vrolijk en kleurrijk. Brengt overal vreugde.</li>
<li><strong>KNOEST</strong> — Stoer en eigenzinnig. Kent alle geheimen van het bos.</li>
<li><strong>FIDO</strong> — Trouw en sterk. De beste vriend die je kunt hebben.</li>
<li><strong>NYX</strong> — Mysterieus en wijs. Ziet dingen die anderen missen.</li>
<li><strong>ZERA</strong> — Snel en slim. Vindt altijd een oplossing.</li>
<li><strong>ORA</strong> — Warm en zorgzaam. Houdt de groep bij elkaar.</li>
</ul>
<p>Elk karakter heeft zijn eigen illustratiepakket, missies en verhalen. Alles komt beschikbaar op 7/7/2026.</p>
<p><a href="https://mikkieworld.gumroad.com" style="background:#3B82F6;color:#fff;padding:12px 24px;text-decoration:none;border-radius:50px;font-weight:bold">Bekijk de karakters</a></p>"""
    },
    {
        "day": 7,
        "subject": "De 777 Founders Tiles — claim de jouwe voor 7/7",
        "preview": "Slechts 777 beschikbaar. Bijna op.",
        "body": """<h2>Word een MIKKIE WORLD Founder</h2>
<p>Er zijn slechts <strong>777 Founders Tiles</strong> beschikbaar. Elk tile is een uniek stukje van de MIKKIE WORLD kaart.</p>
<p>Als Founder krijg je:</p>
<ul>
<li>Toegang tot alle 77 buitenmissies op launch</li>
<li>Alle 7 karakterpakketten (91 illustraties per karakter)</li>
<li>Jouw naam in de MIKKIE WORLD Hall of Heroes</li>
<li>Early access tot nieuwe content</li>
</ul>
<p>Launch: <strong>7 juli 2026 om 07:07</strong></p>
<p><a href="https://mikkieworld.gumroad.com" style="background:#8B5CF6;color:#fff;padding:12px 24px;text-decoration:none;border-radius:50px;font-weight:bold">Claim jouw Founders Tile</a></p>"""
    },
    {
        "day": 14,
        "subject": "Buitenmissie van de week: De Boomhutbouwer",
        "preview": "Pak je rugzak. KNOEST roept je naar buiten.",
        "body": """<h2>Missie van de Week: De Boomhutbouwer</h2>
<p>KNOEST, de stoere kabouter van MIKKIE WORLD, heeft een speciale missie voor jou:</p>
<blockquote style="border-left:4px solid #F59E0B;padding:10px 20px;background:#FEF3C7">
<strong>Bouw een mini-huisje van takjes en bladeren.</strong><br>
Wie woont erin? Teken de bewoner en geef hem een naam!
</blockquote>
<p>Tip van KNOEST: zoek takjes van verschillende lengtes. De langste worden de muren, de kortste het dak.</p>
<p>Deel je boomhut foto op Instagram met <strong>#MIKKIEWORLD</strong> — de mooiste foto wint een verrassing!</p>
<p><a href="https://mikkieworld.gumroad.com" style="background:#34C759;color:#fff;padding:12px 24px;text-decoration:none;border-radius:50px;font-weight:bold">Download alle 7 missies gratis</a></p>"""
    },
    {
        "day": 21,
        "subject": "16 dagen te gaan — MIKKIE WORLD bijna live!",
        "preview": "De countdown begint. Ben jij klaar?",
        "body": """<h2>16 Dagen te Gaan!</h2>
<p>Op <strong>7 juli 2026 om 07:07</strong> opent MIKKIE WORLD zijn poorten. Nog 16 dagen.</p>
<p>Wat er op launch dag beschikbaar komt:</p>
<ul>
<li>77 complete buitenmissies voor alle 7 karakters</li>
<li>7 illustratiepakketten (637 illustraties totaal)</li>
<li>De MIKKIE WORLD interactieve kaart</li>
<li>De eerste MIKKIE WORLD missie-app</li>
</ul>
<p>De 777 Founders Tiles zijn voor <strong>80% vergeven</strong>. Er zijn nog maar een paar beschikbaar.</p>
<p><a href="https://mikkieworld.gumroad.com" style="background:#EF4444;color:#fff;padding:12px 24px;text-decoration:none;border-radius:50px;font-weight:bold">Laatste kans: Founders Tile</a></p>
<p>Avontuurlijk groet,<br><strong>Hendrik & MIKKIE</strong></p>"""
    },
]

def create_campaign(seq_item):
    days = days_to_launch()
    html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{font-family:Arial,sans-serif;background:#f4f4f4;margin:0}}
.w{{max-width:600px;margin:20px auto;background:#fff;border-radius:12px;overflow:hidden}}
.h{{background:#3B82F6;color:#fff;padding:30px;text-align:center}}
.h h1{{margin:0;font-size:22px}}
.b{{padding:30px;font-size:16px;line-height:1.7;color:#333}}
.b h2{{color:#3B82F6}}
.b blockquote{{border-left:4px solid #F59E0B;padding:10px 20px;background:#FEF3C7;margin:20px 0}}
.f{{background:#f9fafb;padding:20px;text-align:center;font-size:12px;color:#6b7280;border-top:1px solid #e5e7eb}}
</style></head><body>
<div class="w">
<div class="h"><h1>MIKKIE WORLD</h1><p style="margin:5px 0;opacity:0.9">{days} dagen tot launch | 7/7/2026 07:07</p></div>
<div class="b">{seq_item['body']}</div>
<div class="f">
<p>Waar Elk Kind een Held Is</p>
<p><a href="https://mikkieworld.com">mikkieworld.com</a></p>
<a href="*|UNSUB|*" style="color:#6b7280">Uitschrijven</a>
</div></div></body></html>"""

    c = mc_req('POST', '/campaigns', {
        'type': 'regular',
        'recipients': {'list_id': MAILCHIMP_LIST},
        'settings': {
            'subject_line': seq_item['subject'],
            'preview_text': seq_item['preview'],
            'title': f"Sequence Dag {seq_item['day']}: {seq_item['subject'][:30]}",
            'from_name': 'MIKKIE WORLD',
            'reply_to': 'hello@mikkie.world'
        }
    })
    if not c.get('id'):
        print(f"Fout bij aanmaken: {c}")
        return None
    cid = c['id']
    mc_req('PUT', f'/campaigns/{cid}/content', {'html': html})
    return cid

def cmd_build():
    print(f"Pre-launch email sequence bouwen ({len(SEQUENCE)} emails)...")
    print(f"Dagen tot launch: {days_to_launch()}\n")
    for item in SEQUENCE:
        print(f"Dag {item['day']:2d}: {item['subject'][:50]}...")
        cid = create_campaign(item)
        if cid:
            print(f"        Campaign ID: {cid} (draft)")
        else:
            print(f"        FOUT!")
    print(f"\nSequence klaar! Ga naar Mailchimp om de automation in te stellen.")
    print("Of gebruik: mikkie-launch send <dag> om een specifieke email te sturen")

def cmd_send(day):
    item = next((s for s in SEQUENCE if s['day'] == int(day)), None)
    if not item:
        print(f"Geen email voor dag {day}. Beschikbaar: {[s['day'] for s in SEQUENCE]}")
        sys.exit(1)
    print(f"Email aanmaken: {item['subject']}")
    cid = create_campaign(item)
    if not cid:
        sys.exit(1)
    print(f"Campaign aangemaakt: {cid}")
    with open('/dev/tty', 'r') as tty:
        sys.stdout.write("Versturen? (y/n): ")
        sys.stdout.flush()
        confirm = tty.readline().strip()
    if confirm.lower() == 'y':
        mc_req('POST', f'/campaigns/{cid}/actions/send')
        print(f"Verstuurd!")
    else:
        print(f"Draft: {cid}")

def cmd_status():
    days = days_to_launch()
    print(f"\nMIKKIE WORLD Launch Status")
    print(f"Dagen tot launch: {days}")
    print(f"Launch: 7 juli 2026 om 07:07")
    print(f"\nAanbevolen email vandaag:")
    for item in SEQUENCE:
        if days >= (29 - item['day']):
            print(f"  Dag {item['day']}: {item['subject']}")

def print_help():
    print("\nMIKKIE WORLD Launch Sequence CLI")
    print("  mikkie-launch build         Maak alle 5 sequence emails als draft")
    print("  mikkie-launch send <dag>    Stuur specifieke email (dag: 0,3,7,14,21)")
    print("  mikkie-launch status        Toon launch status en aanbevolen email")

cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'

if cmd == 'build':
    cmd_build()
elif cmd == 'send':
    if len(sys.argv) < 3:
        print("Gebruik: mikkie-launch send <dag>")
        sys.exit(1)
    cmd_send(sys.argv[2])
elif cmd == 'status':
    cmd_status()
else:
    print_help()
