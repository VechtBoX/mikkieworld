#!/usr/bin/env python3
"""
🐦 MIKKIE WORLD — X/Twitter Auto-Post Agent v2.0
=================================================
Post automatisch gegenereerde MIKKIE WORLD content op X.

Gebruik:
  python3 mikkie_tweet.py auto       → Post de laatste gegenereerde post (geen bevestiging)
  python3 mikkie_tweet.py latest     → Toon de laatste post zonder te posten
  python3 mikkie_tweet.py mission    → Post een willekeurige buitenmissie
  python3 mikkie_tweet.py countdown  → Post een countdown tweet
  python3 mikkie_tweet.py custom Tekst → Post een custom tweet
  python3 mikkie_tweet.py schedule   → Toon het tweet schema
"""

import os, sys, json, urllib.request, urllib.error, urllib.parse
import base64, hmac, hashlib, time, uuid, random
from datetime import datetime, timedelta
from pathlib import Path

# X API Credentials (env vars hebben voorkeur, fallback naar ingebakken waarden)
CK  = os.environ.get('TWITTER_API_KEY',             'rP6K529qPSroj1KFC7FNQN80P')
CS  = os.environ.get('TWITTER_API_SECRET',          'MaY3c0s90YX3I4uYqgxuHWeoBhuOMHfdvEJnApvzK1HXRbPnq1')
AT  = os.environ.get('TWITTER_ACCESS_TOKEN',        '4823501650-p8MFQkkdPQ1xnJs1ymlnSeqdsKEG4ZveGBy1BM3')
ATS = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', 'n1nXUMi9ANKy1Dk1n5bwC5jBYgNFAVJ7awKNjJLgTGEWu')

SOCIAL_DIR  = Path.home() / "MIKKIE_WORLD" / "SOCIAL" / "X_Twitter"
POSTED_LOG  = Path.home() / "MIKKIE_WORLD" / "LOGS" / "posted_tweets.json"
LAUNCH_DATE = datetime(2026, 7, 7, 7, 7)

SOCIAL_DIR.mkdir(parents=True, exist_ok=True)
POSTED_LOG.parent.mkdir(parents=True, exist_ok=True)

MISSION_TWEETS = [
    "Missie 1: Zoek een steen die op een dier lijkt. Teken hem na! #MikkieWorld #Buitenmissie",
    "Missie 2: Bouw een mini-huisje van takjes en bladeren. Wie woont erin? #MikkieWorld #Natuur",
    "Missie 3: Tel hoeveel verschillende vogels je vandaag hoort. Schrijf ze op! #MikkieWorld #Avontuur",
    "Missie 4: Maak een regenboog met krijtjes op de stoep. Elke kleur een wens! #MikkieWorld #Kleur",
    "Missie 5: Zoek iets in de tuin dat kleiner is dan je pink. Wat vind je? #MikkieWorld #Ontdekken",
    "Missie 6: Ren zo snel als je kan naar de dichtstbijzijnde boom en terug! #MikkieWorld #Sport",
    "Missie 7: Maak een geluid als een dier. Welk dier ben jij vandaag? #MikkieWorld #Spelen",
    "Missie 8: Vind een plek buiten waar je 5 minuten stil kunt zitten. Wat hoor je? #MikkieWorld #Rust",
    "Missie 9: Bouw een dam in een plas of beek. Werkt hij? #MikkieWorld #Bouwen",
    "Missie 10: Schrijf een brief aan een boom. Wat wil je hem vertellen? #MikkieWorld #Schrijven",
    "Missie 11: Zoek 7 dingen die beginnen met de letter M. MIKKIE helpt je! #MikkieWorld #Spel",
    "Missie 12: Maak een krans van bloemen of bladeren. Voor wie is hij? #MikkieWorld #Creatief",
    "Missie 13: Lig op je rug in het gras. Welke figuren zie je in de wolken? #MikkieWorld #Dromen",
    "Missie 14: Bouw een parcours in de tuin. Hoe snel kom jij erdoorheen? #MikkieWorld #Uitdaging",
    "Missie 15: Zoek iets roods, iets gels en iets groens buiten. Raak ze aan! #MikkieWorld #Kleuren",
]

COUNTDOWN_TWEETS = [
    "7 weken te gaan tot MIKKIE WORLD launch! 7/7/2026 om 07:07. Ben jij erbij? mikkie.world #MikkieWorld",
    "6 weken te gaan! MIKKIE, BUBBLES, KNOEST, FIDO, NYX, ZERA en ORA wachten op jou. 7/7/2026 #MikkieWorld",
    "5 weken te gaan! 777 magische tiles. 77 buitenmissies. 7 karakters. 1 wereld. #MikkieWorld 7/7/2026",
    "4 weken te gaan! Jouw kind verdient avontuur. Niet op een scherm. Buiten. #MikkieWorld 7/7/2026",
    "3 weken te gaan! De Founders tiles zijn bijna op. Claim de jouwe. mikkie.world #MikkieWorld",
    "2 weken te gaan! MIKKIE WORLD opent de poorten op 7/7/2026 om 07:07. Klaar? #MikkieWorld",
    "1 week te gaan! Morgen begint het avontuur. 7/7/2026 07:07. #MikkieWorld",
]

def oauth_header(method, url, params):
    oauth_params = {
        'oauth_consumer_key': CK,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': AT,
        'oauth_version': '1.0'
    }
    all_params = {**params, **oauth_params}
    sorted_params = '&'.join(
        f"{urllib.parse.quote(str(k), '')}={urllib.parse.quote(str(v), '')}"
        for k, v in sorted(all_params.items())
    )
    base = f"{method}&{urllib.parse.quote(url, '')}&{urllib.parse.quote(sorted_params, '')}"
    signing_key = f"{urllib.parse.quote(CS, '')}&{urllib.parse.quote(ATS, '')}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params['oauth_signature'] = sig
    return 'OAuth ' + ', '.join(
        f'{k}="{urllib.parse.quote(str(v), "")}"'
        for k, v in sorted(oauth_params.items())
    )

def post_tweet(text):
    url = 'https://api.twitter.com/2/tweets'
    body = json.dumps({'text': text}).encode()
    header = oauth_header('POST', url, {})
    req = urllib.request.Request(url, data=body, headers={
        'Authorization': header,
        'Content-Type': 'application/json'
    }, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            d = json.loads(resp.read().decode())
            return d.get('data', {}).get('id', '')
    except urllib.error.HTTPError as e:
        print(f"❌ Twitter Error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"❌ Fout: {e}")
        return None

def load_posted():
    if POSTED_LOG.exists():
        try:
            return json.loads(POSTED_LOG.read_text())
        except Exception:
            pass
    return []

def save_posted(log):
    POSTED_LOG.write_text(json.dumps(log, indent=2, ensure_ascii=False))

def already_posted(filepath):
    posted = load_posted()
    return any(p.get('file') == filepath for p in posted)

def mark_posted(filepath, tweet_id):
    log = load_posted()
    log.append({"file": filepath, "tweet_id": tweet_id, "posted_at": datetime.now().isoformat()})
    save_posted(log)

def get_latest_post():
    files = sorted(SOCIAL_DIR.glob("*.txt"), key=lambda f: f.stat().st_mtime, reverse=True)
    for f in files:
        if already_posted(str(f)):
            continue
        content = f.read_text(encoding='utf-8')
        lines = content.split('\n')
        sep_idx = None
        for i, line in enumerate(lines):
            if line.count('\u2500') > 5:
                sep_idx = i
        if sep_idx is not None:
            post_text = '\n'.join(lines[sep_idx + 1:]).strip()
        else:
            post_lines = []
            in_post = False
            for line in lines:
                if in_post and line.strip():
                    post_lines.append(line)
                if 'HEART:' in line:
                    in_post = True
            post_text = '\n'.join(post_lines).strip()
        if post_text:
            if len(post_text) > 280:
                post_text = post_text[:277] + '...'
            return str(f), post_text
    return None, None

def cmd_auto():
    """Post de laatste gegenereerde post automatisch — geen bevestiging (voor BRAIN)."""
    filepath, text = get_latest_post()
    if not filepath:
        print("ℹ️  Geen nieuwe posts gevonden om te plaatsen")
        return
    print(f"🐦 Auto-post: {Path(filepath).name}")
    print(f"   Tekens: {len(text)}")
    tweet_id = post_tweet(text)
    if tweet_id:
        mark_posted(filepath, tweet_id)
        print(f"✅ Geplaatst! https://x.com/mikkieworld777/status/{tweet_id}")
    else:
        print("❌ Post mislukt")

def cmd_latest():
    filepath, text = get_latest_post()
    if not filepath:
        print("ℹ️  Geen nieuwe posts gevonden")
        return
    print(f"\n📄 {Path(filepath).name}")
    print("─" * 50)
    print(text)
    print("─" * 50)
    print(f"Tekens: {len(text)}")

def cmd_mission():
    mission = random.choice(MISSION_TWEETS)
    days = (LAUNCH_DATE - datetime.now()).days
    tweet = f"{mission}\n\n{days} dagen tot launch 7/7/2026 07:07"
    print(f"Tweet ({len(tweet)} tekens):\n{tweet}\n")
    confirm = input("Versturen? (y/n): ")
    if confirm.lower() == 'y':
        tid = post_tweet(tweet)
        if tid:
            print(f"✅ Verstuurd! https://x.com/mikkieworld777/status/{tid}")

def cmd_countdown():
    days = (LAUNCH_DATE - datetime.now()).days
    weeks = days // 7
    idx = max(0, min(weeks, len(COUNTDOWN_TWEETS) - 1))
    tweet = COUNTDOWN_TWEETS[idx]
    print(f"Tweet ({len(tweet)} tekens):\n{tweet}\n")
    confirm = input("Versturen? (y/n): ")
    if confirm.lower() == 'y':
        tid = post_tweet(tweet)
        if tid:
            print(f"✅ Verstuurd! https://x.com/mikkieworld777/status/{tid}")

def cmd_custom(text):
    if len(text) > 280:
        print(f"❌ Te lang: {len(text)}/280 tekens")
        sys.exit(1)
    print(f"Tweet ({len(text)} tekens):\n{text}\n")
    confirm = input("Versturen? (y/n): ")
    if confirm.lower() == 'y':
        tid = post_tweet(text)
        if tid:
            print(f"✅ Verstuurd! https://x.com/mikkieworld777/status/{tid}")

def cmd_schedule():
    print("\nMIKKIE WORLD Tweet Schema")
    print("-" * 40)
    for i in range(7):
        day = datetime.now() + timedelta(days=i)
        day_name = day.strftime('%A %d/%m')
        print(f"{day_name}: {'Buitenmissie' if i % 2 == 0 else 'Countdown'} tweet")
    print("\nAuto-post via BRAIN of: mikkie-tweet auto")

def print_help():
    days = (LAUNCH_DATE - datetime.now()).days
    print(f"\n🐦 MIKKIE WORLD Twitter CLI | {days} dagen tot launch")
    print("  mikkie-tweet auto             Auto-post laatste post (BRAIN-modus)")
    print("  mikkie-tweet latest           Toon laatste post zonder te posten")
    print("  mikkie-tweet mission          Post willekeurige buitenmissie")
    print("  mikkie-tweet countdown        Post countdown tweet")
    print("  mikkie-tweet custom Tekst     Post custom tweet")
    print("  mikkie-tweet schedule         Toon tweet schema")

cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
if cmd == 'auto':
    cmd_auto()
elif cmd == 'latest':
    cmd_latest()
elif cmd == 'mission':
    cmd_mission()
elif cmd == 'countdown':
    cmd_countdown()
elif cmd == 'custom':
    if len(sys.argv) < 3:
        print("Gebruik: mikkie-tweet custom Jouw tekst hier")
        sys.exit(1)
    cmd_custom(' '.join(sys.argv[2:]))
elif cmd == 'schedule':
    cmd_schedule()
else:
    print_help()
