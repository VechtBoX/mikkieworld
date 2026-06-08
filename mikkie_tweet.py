#!/usr/bin/env python3
"""MIKKIE WORLD Twitter/X Automation CLI"""
import os, sys, json, urllib.request, urllib.error, urllib.parse
import base64, hmac, hashlib, time, uuid, random
from datetime import datetime, timedelta

# Twitter OAuth 1.0a credentials
CK  = os.environ.get('TWITTER_API_KEY', '')
CS  = os.environ.get('TWITTER_API_SECRET', '')
AT  = os.environ.get('TWITTER_ACCESS_TOKEN', '')
ATS = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '')

LAUNCH_DATE = datetime(2026, 7, 7, 7, 7)

MISSION_TWEETS = [
    "Missie 1: Zoek een steen die op een dier lijkt. Teken hem na. Klaar? Deel je tekening! #MIKKIEWORLD #Buitenmissie",
    "Missie 2: Bouw een mini-huisje van takjes en bladeren. Wie woont erin? #MIKKIEWORLD #Natuur",
    "Missie 3: Tel hoeveel verschillende vogels je vandaag hoort. Schrijf ze op! #MIKKIEWORLD #Avontuur",
    "Missie 4: Maak een regenboog met krijtjes op de stoep. Elke kleur een wens! #MIKKIEWORLD #Kleur",
    "Missie 5: Zoek iets in de tuin dat kleiner is dan je pink. Wat vind je? #MIKKIEWORLD #Ontdekken",
    "Missie 6: Ren zo snel als je kan naar de dichtstbijzijnde boom en terug. Tijd jezelf! #MIKKIEWORLD #Sport",
    "Missie 7: Maak een geluid als een dier. Welk dier ben jij vandaag? #MIKKIEWORLD #Spelen",
    "Missie 8: Vind een plek buiten waar je 5 minuten stil kunt zitten. Wat hoor je? #MIKKIEWORLD #Rust",
    "Missie 9: Bouw een dam in een plas of beek. Werkt hij? #MIKKIEWORLD #Bouwen",
    "Missie 10: Schrijf een brief aan een boom. Wat wil je hem vertellen? #MIKKIEWORLD #Schrijven",
    "Missie 11: Zoek 7 dingen die beginnen met de letter M. MIKKIE helpt je! #MIKKIEWORLD #Spel",
    "Missie 12: Maak een krans van bloemen of bladeren. Voor wie is hij? #MIKKIEWORLD #Creatief",
    "Missie 13: Lig op je rug in het gras. Welke figuren zie je in de wolken? #MIKKIEWORLD #Dromen",
    "Missie 14: Bouw een parcours in de tuin. Hoe snel kom jij erdoorheen? #MIKKIEWORLD #Uitdaging",
    "Missie 15: Zoek iets roods, iets gels en iets groens buiten. Raak ze aan! #MIKKIEWORLD #Kleuren",
]

COUNTDOWN_TWEETS = [
    "7 weken te gaan tot MIKKIE WORLD launch! 7/7/2026 om 07:07. Ben jij erbij? mikkieworld.com #MIKKIEWORLD",
    "6 weken te gaan! MIKKIE, BUBBLES, KNOEST, FIDO, NYX, ZERA en ORA wachten op jou. 7/7/2026 #MIKKIEWORLD",
    "5 weken te gaan! 777 magische tiles. 77 buitenmissies. 7 karakters. 1 wereld. #MIKKIEWORLD 7/7/2026",
    "4 weken te gaan! Jouw kind verdient avontuur. Niet op een scherm. Buiten. #MIKKIEWORLD 7/7/2026",
    "3 weken te gaan! De Founders tiles zijn bijna op. Claim de jouwe. mikkieworld.com #MIKKIEWORLD",
    "2 weken te gaan! MIKKIE WORLD opent de poorten op 7/7/2026 om 07:07. Klaar? #MIKKIEWORLD",
    "1 week te gaan! Morgen begint het avontuur. 7/7/2026 07:07. #MIKKIEWORLD",
]

def oauth_header(method, url, params):
    """Generate OAuth 1.0a header"""
    oauth_params = {
        'oauth_consumer_key': CK,
        'oauth_nonce': uuid.uuid4().hex,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': AT,
        'oauth_version': '1.0'
    }
    all_params = {**params, **oauth_params}
    sorted_params = '&'.join(f"{urllib.parse.quote(k,'')  }={urllib.parse.quote(str(v),'')}" 
                             for k, v in sorted(all_params.items()))
    base = f"{method}&{urllib.parse.quote(url,'')}&{urllib.parse.quote(sorted_params,'')}"
    signing_key = f"{urllib.parse.quote(CS,'')}&{urllib.parse.quote(ATS,'')}"
    sig = base64.b64encode(hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    oauth_params['oauth_signature'] = sig
    header = 'OAuth ' + ', '.join(f'{k}="{urllib.parse.quote(str(v),"")}"' 
                                   for k, v in sorted(oauth_params.items()))
    return header

def post_tweet(text):
    """Post a tweet via Twitter API v2"""
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
        print(f"Twitter Error {e.code}: {e.read().decode()}")
        return None

def days_to_launch():
    return (LAUNCH_DATE - datetime.now()).days

def cmd_mission():
    """Post een willekeurige buitenmissie tweet"""
    mission = random.choice(MISSION_TWEETS)
    days = days_to_launch()
    tweet = f"{mission}\n\n{days} dagen tot launch 7/7/2026 07:07"
    print(f"Tweet ({len(tweet)} tekens):\n{tweet}\n")
    confirm = input("Versturen? (y/n): ")
    if confirm.lower() == 'y':
        tid = post_tweet(tweet)
        if tid:
            print(f"Verstuurd! https://x.com/i/web/status/{tid}")
        else:
            print("Fout bij versturen.")

def cmd_countdown():
    """Post een countdown tweet op basis van weken tot launch"""
    days = days_to_launch()
    weeks = days // 7
    idx = max(0, min(weeks, len(COUNTDOWN_TWEETS) - 1))
    tweet = COUNTDOWN_TWEETS[idx]
    print(f"Tweet ({len(tweet)} tekens):\n{tweet}\n")
    confirm = input("Versturen? (y/n): ")
    if confirm.lower() == 'y':
        tid = post_tweet(tweet)
        if tid:
            print(f"Verstuurd! https://x.com/i/web/status/{tid}")

def cmd_custom(text):
    """Post een custom tweet"""
    if len(text) > 280:
        print(f"Te lang: {len(text)}/280 tekens")
        sys.exit(1)
    print(f"Tweet ({len(text)} tekens):\n{text}\n")
    confirm = input("Versturen? (y/n): ")
    if confirm.lower() == 'y':
        tid = post_tweet(text)
        if tid:
            print(f"Verstuurd! https://x.com/i/web/status/{tid}")

def cmd_schedule():
    """Toon het tweet schema voor de komende week"""
    print("\nMIKKIE WORLD Tweet Schema")
    print("-" * 40)
    for i in range(7):
        day = datetime.now() + timedelta(days=i)
        day_name = day.strftime('%A %d/%m')
        if i % 2 == 0:
            print(f"{day_name}: Buitenmissie tweet")
        else:
            print(f"{day_name}: Countdown tweet")
    print("\nRun dagelijks: mikkie-tweet mission")

def print_help():
    days = days_to_launch()
    print(f"\nMIKKIE WORLD Twitter CLI | {days} dagen tot launch")
    print("  mikkie-tweet mission          Post willekeurige buitenmissie")
    print("  mikkie-tweet countdown        Post countdown tweet")
    print("  mikkie-tweet custom Tekst     Post custom tweet")
    print("  mikkie-tweet schedule         Toon tweet schema")

cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'

if cmd == 'mission':
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
