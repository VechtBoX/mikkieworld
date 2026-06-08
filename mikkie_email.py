#!/usr/bin/env python3
import os, sys, json, urllib.request, urllib.error, base64

API_KEY = os.environ.get('MAILCHIMP_API_KEY', '')
SERVER  = os.environ.get('MAILCHIMP_SERVER', 'us14')
LIST_ID = '75412e3953'

def req(method, endpoint, data=None):
    url = f"https://{SERVER}.api.mailchimp.com/3.0{endpoint}"
    creds = base64.b64encode(f'anystring:{API_KEY}'.encode()).decode()
    headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read().decode().strip()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"Error {e.code}: {e.read().decode()}")
        sys.exit(1)

def html_template(subject, body):
    img = "https://files.manuscdn.com/user_upload_by_module/session_file/310519663047764814/YXNyAwFDcSXEsHID.webp"
    css = ("body{font-family:Arial,sans-serif;background:#f4f4f4;margin:0}"
           ".w{max-width:600px;margin:20px auto;background:#fff;border-radius:12px;overflow:hidden}"
           ".h{background:#3B82F6;color:#fff;padding:30px;text-align:center}"
           ".h h1{margin:0;font-size:24px}"
           ".b{padding:30px;font-size:16px;line-height:1.7;color:#333}"
           ".btn{display:inline-block;background:#F59E0B;color:#fff;padding:12px 28px;"
           "text-decoration:none;border-radius:50px;font-weight:bold;margin-top:20px}"
           ".f{background:#f9fafb;padding:20px;text-align:center;font-size:12px;"
           "color:#6b7280;border-top:1px solid #e5e7eb}")
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head>'
            f'<body><div class="w">'
            f'<img src="{img}" style="width:100%;max-height:200px;object-fit:cover;display:block" alt="MIKKIE">'
            f'<div class="h"><h1>{subject}</h1></div>'
            f'<div class="b">{body}'
            f'<br><a href="https://mikkieworld.manus.space" class="btn">Ga naar MIKKIE WORLD</a></div>'
            f'<div class="f"><p>Waar Elk Kind een Held Is - 7/7/2026</p>'
            f'<a href="*|UNSUB|*" style="color:#6b7280">Uitschrijven</a></div>'
            f'</div></body></html>')

cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'

if cmd == 'test':
    d = req('GET', '/')
    print(f"Verbonden: {d['account_name']} | {d['email']} | Pro: {d['pro_enabled']}")

elif cmd == 'lists':
    d = req('GET', '/lists?count=20')
    print(f"{'ID':<15} {'Naam':<30} {'Subs':>6}")
    print('-' * 55)
    for l in d.get('lists', []):
        print(f"{l['id']:<15} {l['name']:<30} {l['stats']['member_count']:>6}")

elif cmd == 'campaigns':
    d = req('GET', '/campaigns?count=10&sort_field=create_time&sort_dir=DESC')
    print(f"{'ID':<15} {'Status':<10} {'Titel':<35}")
    print('-' * 65)
    for c in d.get('campaigns', []):
        print(f"{c['id']:<15} {c['status']:<10} {c['settings'].get('title',''):<35}")

elif cmd == 'send-draft':
    if len(sys.argv) < 3:
        print("Gebruik: mikkie-email send-draft <campaign_id>")
        sys.exit(1)
    cid = sys.argv[2]
    req('POST', f'/campaigns/{cid}/actions/send')
    print(f"Verstuurd: {cid}")

elif cmd == 'send':
    subject = sys.argv[2] if len(sys.argv) > 2 else 'MIKKIE WORLD Nieuws'
    preview = sys.argv[3] if len(sys.argv) > 3 else 'Avontuur wacht!'

    # Body: 4th arg as file path, or stdin, or default
    if len(sys.argv) > 4 and os.path.isfile(sys.argv[4]):
        with open(sys.argv[4], 'r') as f:
            body = f.read().strip()
    elif not sys.stdin.isatty():
        body = sys.stdin.read().strip()
    else:
        body = '<p>Welkom bij MIKKIE WORLD! Ga mee op avontuur.</p>'

    html = html_template(subject, body)
    c = req('POST', '/campaigns', {
        'type': 'regular',
        'recipients': {'list_id': LIST_ID},
        'settings': {
            'subject_line': subject, 'preview_text': preview,
            'title': f'MIKKIE: {subject}',
            'from_name': 'MIKKIE WORLD', 'reply_to': 'hello@mikkie.world'
        }
    })
    cid = c['id']
    req('PUT', f'/campaigns/{cid}/content', {'html': html})
    print(f"Campaign aangemaakt: {cid}")

    # Always read confirmation from /dev/tty, not stdin
    try:
        with open('/dev/tty', 'r') as tty:
            sys.stdout.write("Versturen? (y/n): ")
            sys.stdout.flush()
            confirm = tty.readline().strip()
    except Exception:
        confirm = 'n'

    if confirm.lower() == 'y':
        req('POST', f'/campaigns/{cid}/actions/send')
        print(f"Verstuurd! {cid}")
    else:
        print(f"Draft opgeslagen: {cid}")
        print(f"Stuur later met: mikkie-email send-draft {cid}")

else:
    print("MIKKIE WORLD Mailchimp CLI v2")
    print("  mikkie-email test")
    print("  mikkie-email lists")
    print("  mikkie-email campaigns")
    print("  mikkie-email send subject preview")
    print("  mikkie-email send subject preview ~/body.html")
    print("  mikkie-email send-draft <campaign_id>")
