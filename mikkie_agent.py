#!/usr/bin/env python3
"""
MIKKIE WORLD — 24/7 Gumroad AI Agent
=====================================
Draait continu op de achtergrond op jouw Mac.

Wat doet deze agent:
  - Elke 5 minuten: controleert nieuwe Gumroad verkopen
  - Bij nieuwe verkoop: synct koper naar Mailchimp + stuurt tweet + logt
  - Elke dag om 08:00: stuurt dagrapport naar terminal log
  - Elke dag om 09:00: post een automatische missie-tweet
  - Elke week maandag: stuurt weekoverzicht

Start: python3 ~/mikkieworld/mikkie_agent.py
Stop:  Ctrl+C of: pkill -f mikkie_agent.py
Log:   tail -f ~/mikkieworld/agent.log
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import base64
import hashlib
import datetime
import logging
import random
import signal

# ─── Configuratie ─────────────────────────────────────────────────────────────
GUMROAD_TOKEN    = os.environ.get('GUMROAD_API_TOKEN', '')
MAILCHIMP_KEY    = os.environ.get('MAILCHIMP_API_KEY', '')
MAILCHIMP_SERVER = os.environ.get('MAILCHIMP_SERVER', 'us14')
MAILCHIMP_LIST   = '75412e3953'
TWITTER_KEY      = os.environ.get('TWITTER_API_KEY', '')
TWITTER_SECRET   = os.environ.get('TWITTER_API_SECRET', '')
TWITTER_TOKEN    = os.environ.get('TWITTER_ACCESS_TOKEN', '')
TWITTER_TOKEN_S  = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '')
XAI_KEY          = os.environ.get('XAI_API_KEY', '')

POLL_INTERVAL    = 300   # 5 minuten tussen Gumroad checks
LOG_FILE         = os.path.expanduser('~/mikkieworld/agent.log')
STATE_FILE       = os.path.expanduser('~/mikkieworld/agent_state.json')
LAUNCH_DATE      = datetime.datetime(2026, 7, 7, 7, 7, 0)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MIKKIE-AGENT] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)

# ─── State (welke sales al verwerkt) ──────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        'processed_sales': [],
        'last_daily_report': '',
        'last_weekly_report': '',
        'last_tweet_date': '',
        'total_revenue': 0.0,
        'total_sales': 0,
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

# ─── Gumroad API ──────────────────────────────────────────────────────────────
def gumroad_get(endpoint):
    if not GUMROAD_TOKEN:
        log.warning('GUMROAD_API_TOKEN niet ingesteld')
        return None
    url = f"https://api.gumroad.com/v2{endpoint}?access_token={GUMROAD_TOKEN}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        log.error(f"Gumroad API fout: {e}")
        return None

def get_new_sales(state):
    res = gumroad_get('/sales')
    if not res or not res.get('success'):
        return []
    sales = res.get('sales', [])
    new_sales = []
    for s in sales:
        sid = s.get('id', s.get('order_id', ''))
        if sid and sid not in state['processed_sales']:
            new_sales.append(s)
    return new_sales

# ─── Mailchimp ────────────────────────────────────────────────────────────────
def add_to_mailchimp(email, fname, lname, product_name):
    if not MAILCHIMP_KEY:
        return False
    url = f"https://{MAILCHIMP_SERVER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST}/members"
    creds = base64.b64encode(f'anystring:{MAILCHIMP_KEY}'.encode()).decode()
    headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}
    data = json.dumps({
        'email_address': email,
        'status': 'subscribed',
        'tags': ['gumroad-koper', 'buyer'],
        'merge_fields': {'FNAME': fname or '', 'LNAME': lname or ''},
        'notes': f'Gekocht: {product_name}'
    }).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except urllib.error.HTTPError as e:
        if e.code == 400:
            return True  # Al in lijst
        return False
    except Exception:
        return False

# ─── Twitter/X ────────────────────────────────────────────────────────────────
def make_oauth_header(method, url, params, key, secret, token, token_secret):
    import hmac
    import hashlib as hs
    oauth_params = {
        'oauth_consumer_key': key,
        'oauth_nonce': hashlib.md5(str(time.time()).encode()).hexdigest(),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': token,
        'oauth_version': '1.0',
    }
    all_params = {**params, **oauth_params}
    sorted_params = '&'.join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in sorted(all_params.items())
    )
    base = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
    signing_key = f"{urllib.parse.quote(secret, safe='')}&{urllib.parse.quote(token_secret, safe='')}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base.encode(), hs.sha1).digest()
    ).decode()
    oauth_params['oauth_signature'] = sig
    header = 'OAuth ' + ', '.join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(str(v), safe="")}"'
        for k, v in sorted(oauth_params.items())
    )
    return header

def post_tweet(text):
    if not all([TWITTER_KEY, TWITTER_SECRET, TWITTER_TOKEN, TWITTER_TOKEN_S]):
        log.warning('Twitter credentials niet ingesteld')
        return False
    url = 'https://api.twitter.com/2/tweets'
    body = json.dumps({'text': text}).encode()
    auth = make_oauth_header('POST', url, {}, TWITTER_KEY, TWITTER_SECRET, TWITTER_TOKEN, TWITTER_TOKEN_S)
    req = urllib.request.Request(url, data=body, headers={
        'Authorization': auth,
        'Content-Type': 'application/json',
    }, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            tweet_id = result.get('data', {}).get('id', '')
            log.info(f"Tweet verstuurd: https://x.com/i/web/status/{tweet_id}")
            return True
    except Exception as e:
        log.error(f"Tweet fout: {e}")
        return False

# ─── Grok AI ──────────────────────────────────────────────────────────────────
def grok_generate(prompt, max_tokens=280):
    if not XAI_KEY:
        return None
    url = 'https://api.x.ai/v1/chat/completions'
    body = json.dumps({
        'model': 'grok-3-mini',
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': 0.8,
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        'Authorization': f'Bearer {XAI_KEY}',
        'Content-Type': 'application/json',
    }, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        log.error(f"Grok fout: {e}")
        return None

def generate_sale_tweet(buyer_name, product_name, total_sales):
    prompt = (
        f"Schrijf een enthousiaste Nederlandse tweet (max 240 tekens) voor MIKKIE WORLD. "
        f"Iemand heeft zojuist '{product_name}' gekocht. "
        f"We hebben nu {total_sales} verkopen totaal. "
        f"Gebruik de hashtags #MIKKIEWORLD en #Avontuur. "
        f"Wees warm, magisch en motiverend. Geen aanhalingstekens in de output."
    )
    tweet = grok_generate(prompt)
    if tweet and len(tweet) <= 280:
        return tweet
    # Fallback als Grok niet beschikbaar is
    fallbacks = [
        f"Iemand heeft zojuist {product_name} ontdekt! Avontuur wacht. #MIKKIEWORLD #Avontuur",
        f"Nog {total_sales} avontuurlijke kinderen op weg naar buiten! #MIKKIEWORLD",
        f"MIKKIE WORLD groeit! {product_name} gevonden door een nieuwe avonturier. #MIKKIEWORLD",
    ]
    return random.choice(fallbacks)

def generate_daily_tweet():
    now = datetime.datetime.now()
    days_left = (LAUNCH_DATE - now).days
    prompt = (
        f"Schrijf een inspirerende Nederlandse tweet (max 240 tekens) voor MIKKIE WORLD. "
        f"Nog {days_left} dagen tot de lancering op 7 juli 2026 om 07:07. "
        f"MIKKIE is een avontuurlijk jongetje dat kinderen inspireert om buiten te spelen. "
        f"Gebruik #MIKKIEWORLD. Wees magisch en enthousiast. Geen aanhalingstekens."
    )
    tweet = grok_generate(prompt)
    if tweet and len(tweet) <= 280:
        return tweet
    missions = [
        f"Dag {now.strftime('%d/%m')}: Zoek vandaag 5 dingen die beginnen met de letter M. MIKKIE helpt je! #MIKKIEWORLD",
        f"Nog {days_left} dagen tot MIKKIE WORLD live gaat! Klaar voor het avontuur? #MIKKIEWORLD",
        f"Elke dag buiten spelen maakt een kind sterker, slimmer en gelukkiger. Dat is MIKKIE WORLD. #MIKKIEWORLD",
        f"MIKKIE zegt: het beste avontuur begint buiten de voordeur. Ga op ontdekking! #MIKKIEWORLD",
        f"7 karakters. 777 tegels. 1 missie: elk kind een held. {days_left} dagen te gaan. #MIKKIEWORLD",
    ]
    return random.choice(missions)

# ─── Acties bij nieuwe verkoop ────────────────────────────────────────────────
def process_sale(sale, state):
    sid = sale.get('id', sale.get('order_id', ''))
    email = sale.get('email', '')
    product = sale.get('product_name', 'MIKKIE product')
    price = sale.get('price', 0) / 100
    full_name = sale.get('full_name', '')
    parts = full_name.split(' ', 1)
    fname = parts[0] if parts else ''
    lname = parts[1] if len(parts) > 1 else ''

    log.info(f"NIEUWE VERKOOP: {product} | {email} | EUR{price:.2f}")

    # 1. Mailchimp sync
    if add_to_mailchimp(email, fname, lname, product):
        log.info(f"  Mailchimp: {email} toegevoegd")
    else:
        log.warning(f"  Mailchimp: sync mislukt voor {email}")

    # 2. State bijwerken
    state['processed_sales'].append(sid)
    state['total_sales'] += 1
    state['total_revenue'] += price

    # 3. AI tweet genereren en versturen
    tweet = generate_sale_tweet(fname or 'iemand', product, state['total_sales'])
    if post_tweet(tweet):
        log.info(f"  Tweet verstuurd")
    else:
        log.warning(f"  Tweet mislukt")

    save_state(state)

# ─── Dagrapport ───────────────────────────────────────────────────────────────
def daily_report(state):
    now = datetime.datetime.now()
    days_left = (LAUNCH_DATE - now).days
    log.info("=" * 60)
    log.info("DAGRAPPORT MIKKIE WORLD")
    log.info(f"  Datum:        {now.strftime('%d/%m/%Y')}")
    log.info(f"  Dagen tot 7/7: {days_left}")
    log.info(f"  Totaal sales: {state['total_sales']}")
    log.info(f"  Totaal omzet: EUR{state['total_revenue']:.2f}")
    log.info(f"  Doel EUR10k:  {state['total_revenue']/10000*100:.1f}%")
    log.info("=" * 60)
    state['last_daily_report'] = now.strftime('%Y-%m-%d')
    save_state(state)

# ─── Dagelijkse tweet ─────────────────────────────────────────────────────────
def daily_tweet(state):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if state.get('last_tweet_date') == today:
        return
    tweet = generate_daily_tweet()
    if post_tweet(tweet):
        log.info(f"Dagelijkse tweet verstuurd")
        state['last_tweet_date'] = today
        save_state(state)

# ─── Hoofd loop ───────────────────────────────────────────────────────────────
def run():
    log.info("MIKKIE WORLD Agent gestart")
    log.info(f"  Poll interval: {POLL_INTERVAL}s")
    log.info(f"  Log: {LOG_FILE}")
    log.info(f"  State: {STATE_FILE}")
    log.info(f"  Gumroad token: {'OK' if GUMROAD_TOKEN else 'ONTBREEKT'}")
    log.info(f"  Mailchimp key: {'OK' if MAILCHIMP_KEY else 'ONTBREEKT'}")
    log.info(f"  Twitter creds: {'OK' if TWITTER_KEY else 'ONTBREEKT'}")
    log.info(f"  Grok AI:       {'OK' if XAI_KEY else 'ONTBREEKT (fallback actief)'}")
    log.info("-" * 60)

    state = load_state()
    last_check = 0

    def shutdown(sig, frame):
        log.info("Agent gestopt (signaal ontvangen)")
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    while True:
        now = datetime.datetime.now()
        current_time = time.time()

        # ── Gumroad poll (elke 5 min) ──────────────────────────────────────
        if current_time - last_check >= POLL_INTERVAL:
            log.info(f"Gumroad check... ({now.strftime('%H:%M')})")
            new_sales = get_new_sales(state)
            if new_sales:
                log.info(f"  {len(new_sales)} nieuwe verkoop/verkopen gevonden!")
                for sale in new_sales:
                    process_sale(sale, state)
            else:
                log.info(f"  Geen nieuwe verkopen. Totaal: {state['total_sales']} | EUR{state['total_revenue']:.2f}")
            last_check = current_time

        # ── Dagrapport om 08:00 ────────────────────────────────────────────
        if now.hour == 8 and now.minute == 0:
            today = now.strftime('%Y-%m-%d')
            if state.get('last_daily_report') != today:
                daily_report(state)

        # ── Dagelijkse tweet om 09:00 ──────────────────────────────────────
        if now.hour == 9 and now.minute == 0:
            daily_tweet(state)

        time.sleep(60)  # Check elke minuut of het tijd is voor iets


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'status':
            state = load_state()
            print("MIKKIE WORLD Agent Status")
            print(f"  Verwerkte sales: {len(state['processed_sales'])}")
            print(f"  Totaal omzet:    EUR{state['total_revenue']:.2f}")
            print(f"  Laatste rapport: {state.get('last_daily_report', 'nooit')}")
            print(f"  Laatste tweet:   {state.get('last_tweet_date', 'nooit')}")
            # Check of agent draait
            import subprocess
            result = subprocess.run(['pgrep', '-f', 'mikkie_agent.py'], capture_output=True, text=True)
            pids = result.stdout.strip().split('\n')
            pids = [p for p in pids if p and p != str(os.getpid())]
            if pids:
                print(f"  Agent draait:    JA (PID: {', '.join(pids)})")
            else:
                print(f"  Agent draait:    NEE")
        elif cmd == 'log':
            os.system(f'tail -50 {LOG_FILE}')
        elif cmd == 'stop':
            os.system('pkill -f mikkie_agent.py')
            print("Agent gestopt")
        elif cmd == 'reset':
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
                print("State gereset")
        else:
            print("Gebruik: mikkie-agent [status|log|stop|reset]")
    else:
        run()


if __name__ == '__main__':
    main()
