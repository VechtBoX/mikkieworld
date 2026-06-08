#!/usr/bin/env python3
"""
MIKKIE WORLD — 24/7 AI Agent
==============================
Volledig autonome agent die draait op de achtergrond op jouw Mac.

MODULES:
  1. GUMROAD CONFIGURATIE  — producten aanmaken/bijwerken, prijzen, beschrijvingen
  2. SALES MONITOR         — elke 5 min nieuwe verkopen detecteren
  3. MAILCHIMP SYNC        — kopers automatisch toevoegen
  4. AI CONTENT GENERATOR  — Grok schrijft tweets, beschrijvingen, emails, promoties
  5. TWITTER AUTOMATIE     — dagelijkse posts + verkoop-tweets
  6. CONTENT KALENDER      — wekelijkse content-cyclus
  7. DAGRAPPORT            — dagelijks overzicht in log

Start:    python3 ~/mikkieworld/mikkie_agent.py
Stop:     mikkie-agent stop
Status:   mikkie-agent status
Log:      mikkie-agent log
Eenmalig: mikkie-agent setup     (Gumroad volledig configureren)
          mikkie-agent content   (nieuwe content genereren)
          mikkie-agent tweet     (nu een tweet posten)
"""

import os, sys, json, time, urllib.request, urllib.parse, urllib.error
import base64, hashlib, datetime, logging, random, signal, hmac

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
TELEGRAM_TOKEN   = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

POLL_INTERVAL    = 300   # 5 minuten
LOG_FILE         = os.path.expanduser('~/mikkieworld/agent.log')
STATE_FILE       = os.path.expanduser('~/mikkieworld/agent_state.json')
CONTENT_FILE     = os.path.expanduser('~/mikkieworld/agent_content.json')
LAUNCH_DATE      = datetime.datetime(2026, 7, 7, 7, 7, 0)

# ─── Gumroad product definities ───────────────────────────────────────────────
GUMROAD_PRODUCTS = [
    {
        'id': '59BL9uT7Q5geTu0RrM0PuA==',
        'name': 'MIKKIE 7 Gratis Buitenmissies',
        'price': 0,
        'published': False,
        'character': 'MIKKIE',
        'type': 'leadmagnet',
    },
    {
        'id': 'uiRWcbhQH-1Omdqzl1wQ7w==',
        'name': 'MIKKIE WORLD: 91 Magische Karakter Illustraties',
        'price': 999,
        'published': True,
        'character': 'ALL',
        'type': 'illustraties',
    },
    {
        'id': 'o4xaqMsL1b9dQ4Gga2nA7Q==',
        'name': 'BUBBLES Quest Bundle — 5 Wateravonturen + 13 Illustraties',
        'price': 1200,
        'published': False,
        'character': 'BUBBLES',
        'type': 'quest_bundle',
        'element': 'water',
    },
    {
        'id': 'fsuPN7_ca1c2bKcdvNeRKg==',
        'name': 'KNOEST Quest Bundle — 5 Bosavonturen + 13 Illustraties',
        'price': 1200,
        'published': False,
        'character': 'KNOEST',
        'type': 'quest_bundle',
        'element': 'bos',
    },
    {
        'id': 'T9LpDUWWeVLPmKgDbeOSeg==',
        'name': 'NYX Quest Bundle — 5 Nachtavonturen + 13 Illustraties',
        'price': 1200,
        'published': False,
        'character': 'NYX',
        'type': 'quest_bundle',
        'element': 'nacht',
    },
    {
        'id': 'vL8TxyAqnUslfH9Ilw9FNg==',
        'name': 'ORA Quest Bundle — 5 Slimme Speurtochten + 13 Illustraties',
        'price': 1200,
        'published': False,
        'character': 'ORA',
        'type': 'quest_bundle',
        'element': 'raadsels',
    },
    {
        'id': 'E5a-iHShBzCckrz6BHY6Xw==',
        'name': 'FIDO Quest Bundle — 5 Dierenspoor Avonturen + 12 Illustraties',
        'price': 1200,
        'published': False,
        'character': 'FIDO',
        'type': 'quest_bundle',
        'element': 'dieren',
    },
    {
        'id': 'RMA17VrScb8R6dsXQeZtSg==',
        'name': 'ZERA Quest Bundle — 5 Energie en Weermissies + 12 Illustraties',
        'price': 1200,
        'published': False,
        'character': 'ZERA',
        'type': 'quest_bundle',
        'element': 'weer',
    },
    {
        'id': 'kS7vevDiRqM4KyuauDKUzQ==',
        'name': 'MIKKIE WORLD Founders Pack — Alles + Exclusief (100 stuks)',
        'price': 4900,
        'published': False,
        'character': 'ALL',
        'type': 'founders_pack',
    },
]

# ─── Logging ──────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AGENT] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)

# ─── Telegram Alert Functie ───────────────────────────────────────────────────────────────────────────
def telegram_alert(message: str, level: str = "INFO") -> bool:
    """Stuur een alert naar Telegram. Faalt stil als niet geconfigureerd."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    emoji = {"SUCCESS": "✅", "ERROR": "🚨", "WARNING": "⚠️", "INFO": "ℹ️"}.get(level, "ℹ️")
    timestamp = datetime.datetime.now().strftime('%d-%m %H:%M')
    text = f"{emoji} *MIKKIE WORLD*\n`{timestamp}`\n\n{message}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}).encode('utf-8')
    try:
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception as e:
        log.warning(f"Telegram alert mislukt (niet kritiek): {e}")
        return False

# ─── State ────────────────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        'processed_sales': [],
        'last_daily_report': '',
        'last_weekly_content': '',
        'last_tweet_date': '',
        'last_gumroad_setup': '',
        'total_revenue': 0.0,
        'total_sales': 0,
        'generated_descriptions': {},
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def load_content():
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE) as f:
            return json.load(f)
    return {'tweets': [], 'descriptions': {}, 'email_subjects': [], 'promo_texts': {}}

def save_content(content):
    with open(CONTENT_FILE, 'w') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)

# ─── Grok AI ──────────────────────────────────────────────────────────────────
def grok(prompt, max_tokens=500, temperature=0.85):
    if not XAI_KEY:
        return None
    url = 'https://api.x.ai/v1/chat/completions'
    body = json.dumps({
        'model': 'grok-3-mini',
        'messages': [
            {
                'role': 'system',
                'content': (
                    'Je bent de AI-assistent van MIKKIE WORLD — een magisch kindermerk. '
                    'MIKKIE is een 7-jarig avontuurlijk jongetje. Kernwaarden: avontuurlijk, moedig, magisch. '
                    'Schrijf altijd in het Nederlands. Warm, enthousiast, kindvriendelijk maar ook aantrekkelijk voor ouders. '
                    'Nooit crypto of tokens noemen tenzij expliciet gevraagd.'
                )
            },
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': max_tokens,
        'temperature': temperature,
    }).encode()
    req = urllib.request.Request(url, data=body, headers={
        'Authorization': f'Bearer {XAI_KEY}',
        'Content-Type': 'application/json',
    }, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data['choices'][0]['message']['content'].strip()
    except Exception as e:
        log.error(f"Grok fout: {e}")
        return None

# ─── MODULE 1: GUMROAD CONFIGURATIE ──────────────────────────────────────────
def gumroad_req(method, endpoint, data=None):
    if not GUMROAD_TOKEN:
        log.warning('GUMROAD_API_TOKEN niet ingesteld')
        return None
    url = f"https://api.gumroad.com/v2{endpoint}"
    if data:
        data['access_token'] = GUMROAD_TOKEN
        encoded = urllib.parse.urlencode(data).encode('utf-8')
    else:
        qs = urllib.parse.urlencode({'access_token': GUMROAD_TOKEN})
        if method == 'GET':
            url = f"{url}?{qs}"
            encoded = None
        else:
            encoded = qs.encode('utf-8')
    req = urllib.request.Request(url, data=encoded, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        log.error(f"Gumroad {method} {endpoint}: HTTP {e.code}")
        return None
    except Exception as e:
        log.error(f"Gumroad fout: {e}")
        return None

def ai_generate_description(product):
    """Genereer een AI-beschrijving voor een Gumroad product."""
    char = product.get('character', 'MIKKIE')
    ptype = product.get('type', 'quest_bundle')
    element = product.get('element', 'natuur')
    name = product['name']
    price = product['price'] / 100

    if ptype == 'leadmagnet':
        prompt = (
            f"Schrijf een Gumroad productbeschrijving (HTML, max 400 woorden) voor een GRATIS PDF: "
            f"'MIKKIE 7 Gratis Buitenmissies'. "
            f"Dit is een leadmagnet voor ouders van kinderen 4-12 jaar. "
            f"Doel: e-mailadres ophalen. Benadruk dat het gratis is, direct te downloaden, "
            f"en dat kinderen er echt mee naar buiten gaan. Eindig met een call-to-action. "
            f"Gebruik <h2>, <p>, <ul>, <li> tags."
        )
    elif ptype == 'illustraties':
        prompt = (
            f"Schrijf een Gumroad productbeschrijving (HTML, max 500 woorden) voor: "
            f"'91 Magische MIKKIE WORLD Illustraties' (EUR{price:.2f}). "
            f"7 karakters: MIKKIE, BUBBLES, KNOEST, NYX, ORA, FIDO, ZERA. "
            f"PNG + JPG hoge resolutie. Ideaal voor knutselen, verjaardagskaarten, posters. "
            f"Doelgroep: ouders, leerkrachten, creatieve kinderen. "
            f"Gebruik <h2>, <p>, <ul>, <li> tags. Eindig met urgentie (lancering 7/7/2026)."
        )
    elif ptype == 'quest_bundle':
        prompt = (
            f"Schrijf een Gumroad productbeschrijving (HTML, max 500 woorden) voor: "
            f"'{name}' (EUR{price:.2f}). "
            f"Karakter: {char}. Thema: {element}. "
            f"Bevat: 5 printklare missiekaarten + illustraties + handleiding. "
            f"Doelgroep: ouders van kinderen 4-12 jaar. "
            f"Schrijf 5 concrete voorbeeldmissies passend bij het thema '{element}'. "
            f"Gebruik <h2>, <p>, <ul>, <li> tags. Eindig met call-to-action en lancering 7/7/2026."
        )
    elif ptype == 'founders_pack':
        prompt = (
            f"Schrijf een Gumroad productbeschrijving (HTML, max 600 woorden) voor: "
            f"'MIKKIE WORLD Founders Pack' (EUR{price:.2f}). "
            f"Dit is het ultieme pakket: alle 91 illustraties + alle 35 missies + exclusieve voordelen. "
            f"Slechts 100 stuks. Founders krijgen: certificaat, naam in boek, vroeg toegang, community. "
            f"Normaalprijs: EUR81.99. Founders: EUR49. Besparing: EUR33. "
            f"Creeer urgentie en exclusiviteit. Gebruik <h2>, <p>, <ul>, <li> tags."
        )
    else:
        return None

    desc = grok(prompt, max_tokens=800)
    return desc

def gumroad_setup_all(state, force=False):
    """Configureer alle Gumroad producten met AI-beschrijvingen."""
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    if not force and state.get('last_gumroad_setup') == today:
        log.info("Gumroad setup al gedaan vandaag, skip")
        return

    log.info("GUMROAD SETUP — alle producten configureren...")
    content = load_content()
    ok = 0

    for prod in GUMROAD_PRODUCTS:
        pid = prod['id']
        name = prod['name']
        log.info(f"  Bijwerken: {name[:50]}")

        # AI beschrijving genereren (of uit cache)
        desc = content['descriptions'].get(pid)
        if not desc:
            log.info(f"    Grok beschrijving genereren...")
            desc = ai_generate_description(prod)
            if desc:
                content['descriptions'][pid] = desc
                save_content(content)
                log.info(f"    Beschrijving gegenereerd ({len(desc)} tekens)")
            else:
                log.warning(f"    Grok niet beschikbaar, gebruik fallback")
                desc = f"<p>{name} — onderdeel van MIKKIE WORLD. Avontuur voor elk kind! mikkieworld.com</p>"

        data = {
            'name': name,
            'price': str(prod['price']),
            'description': desc,
            'published': 'true' if prod.get('published') else 'false',
        }
        res = gumroad_req('PUT', f"/products/{urllib.parse.quote(pid, safe='')}", data)
        if res and res.get('success'):
            log.info(f"    OK — {res['product'].get('short_url', '')}")
            ok += 1
        else:
            log.warning(f"    Mislukt")
        time.sleep(0.5)

    state['last_gumroad_setup'] = today
    save_state(state)
    log.info(f"Gumroad setup klaar: {ok}/{len(GUMROAD_PRODUCTS)} producten bijgewerkt")

# ─── MODULE 2: SALES MONITOR ──────────────────────────────────────────────────
def get_new_sales(state):
    res = gumroad_req('GET', '/sales')
    if not res or not res.get('success'):
        return []
    sales = res.get('sales', [])
    new_sales = []
    for s in sales:
        sid = s.get('id', s.get('order_id', ''))
        if sid and sid not in state['processed_sales']:
            new_sales.append(s)
    return new_sales

# ─── MODULE 3: MAILCHIMP ──────────────────────────────────────────────────────
def mailchimp_add(email, fname, lname, product_name, tags=None):
    if not MAILCHIMP_KEY:
        return False
    url = f"https://{MAILCHIMP_SERVER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST}/members"
    creds = base64.b64encode(f'anystring:{MAILCHIMP_KEY}'.encode()).decode()
    all_tags = ['gumroad-koper'] + (tags or [])
    data = json.dumps({
        'email_address': email,
        'status': 'subscribed',
        'tags': all_tags,
        'merge_fields': {'FNAME': fname or '', 'LNAME': lname or ''},
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        'Authorization': f'Basic {creds}',
        'Content-Type': 'application/json',
    }, method='POST')
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except urllib.error.HTTPError as e:
        return e.code == 400  # 400 = al in lijst = OK
    except Exception:
        return False

# ─── MODULE 4: AI CONTENT GENERATOR ──────────────────────────────────────────
def generate_weekly_content(state):
    """Genereer een week aan content: tweets, promo-teksten, email onderwerpen."""
    week = datetime.datetime.now().strftime('%Y-W%W')
    if state.get('last_weekly_content') == week:
        return
    log.info("WEEKLY CONTENT — AI genereert content voor deze week...")
    content = load_content()
    now = datetime.datetime.now()
    days_left = (LAUNCH_DATE - now).days

    # 7 tweets voor de week
    log.info("  7 tweets genereren...")
    prompt = (
        f"Genereer 7 unieke Nederlandse tweets voor MIKKIE WORLD voor de komende week. "
        f"Nog {days_left} dagen tot lancering op 7 juli 2026 om 07:07. "
        f"Mix van: buitenmissies, karakterintroducties (MIKKIE/BUBBLES/KNOEST/NYX/ORA/FIDO/ZERA), "
        f"countdown, inspiratie voor ouders, avontuurlijke oproepen. "
        f"Elke tweet max 240 tekens. Gebruik #MIKKIEWORLD. "
        f"Geef output als JSON array: [\"tweet1\", \"tweet2\", ...]"
    )
    result = grok(prompt, max_tokens=1000)
    if result:
        try:
            start = result.find('[')
            end = result.rfind(']') + 1
            tweets = json.loads(result[start:end])
            content['tweets'] = tweets
            log.info(f"  {len(tweets)} tweets gegenereerd")
        except Exception:
            log.warning("  Tweet parsing mislukt")

    # Promo-teksten per product
    log.info("  Promo-teksten genereren...")
    for prod in GUMROAD_PRODUCTS:
        if prod['type'] in ('quest_bundle', 'founders_pack', 'illustraties'):
            prompt = (
                f"Schrijf een korte Nederlandse promotietekst (max 150 woorden) voor: "
                f"'{prod['name']}' (EUR{prod['price']/100:.2f}). "
                f"Voor gebruik op social media en in emails. "
                f"Warm, enthousiast, gericht op ouders. Eindig met de Gumroad URL hint."
            )
            promo = grok(prompt, max_tokens=300)
            if promo:
                content['promo_texts'][prod['id']] = promo

    # Email onderwerpen voor Mailchimp
    log.info("  Email onderwerpen genereren...")
    prompt = (
        f"Genereer 5 pakkende Nederlandse email onderwerpen voor MIKKIE WORLD nieuwsbrief. "
        f"Doelgroep: ouders van kinderen 4-12 jaar. "
        f"Nog {days_left} dagen tot lancering. Mix van nieuwsgierigheid, urgentie en warmte. "
        f"Geef output als JSON array: [\"onderwerp1\", ...]"
    )
    result = grok(prompt, max_tokens=400)
    if result:
        try:
            start = result.find('[')
            end = result.rfind(']') + 1
            subjects = json.loads(result[start:end])
            content['email_subjects'] = subjects
            log.info(f"  {len(subjects)} email onderwerpen gegenereerd")
        except Exception:
            log.warning("  Email onderwerp parsing mislukt")

    save_content(content)
    state['last_weekly_content'] = week
    save_state(state)
    log.info("Weekly content generatie klaar")

# ─── MODULE 5: TWITTER ────────────────────────────────────────────────────────
def make_oauth_header(method, url, params):
    oauth_params = {
        'oauth_consumer_key': TWITTER_KEY,
        'oauth_nonce': hashlib.md5(str(time.time()).encode()).hexdigest(),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_token': TWITTER_TOKEN,
        'oauth_version': '1.0',
    }
    all_params = {**params, **oauth_params}
    sorted_params = '&'.join(
        f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
        for k, v in sorted(all_params.items())
    )
    base = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"
    signing_key = f"{urllib.parse.quote(TWITTER_SECRET, safe='')}&{urllib.parse.quote(TWITTER_TOKEN_S, safe='')}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    ).decode()
    oauth_params['oauth_signature'] = sig
    return 'OAuth ' + ', '.join(
        f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(str(v), safe="")}"'
        for k, v in sorted(oauth_params.items())
    )

def post_tweet(text):
    if not all([TWITTER_KEY, TWITTER_SECRET, TWITTER_TOKEN, TWITTER_TOKEN_S]):
        log.warning('Twitter credentials ontbreken')
        return False
    if len(text) > 280:
        text = text[:277] + '...'
    url = 'https://api.twitter.com/2/tweets'
    body = json.dumps({'text': text}).encode()
    auth = make_oauth_header('POST', url, {})
    req = urllib.request.Request(url, data=body, headers={
        'Authorization': auth,
        'Content-Type': 'application/json',
    }, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            tid = result.get('data', {}).get('id', '')
            log.info(f"Tweet: https://x.com/i/web/status/{tid}")
            return True
    except Exception as e:
        log.error(f"Tweet fout: {e}")
        return False

def get_next_tweet(state):
    """Haal de volgende tweet op uit de content kalender."""
    content = load_content()
    tweets = content.get('tweets', [])
    if not tweets:
        # Fallback
        days_left = (LAUNCH_DATE - datetime.datetime.now()).days
        fallbacks = [
            f"Nog {days_left} dagen tot MIKKIE WORLD live gaat! Avontuur voor elk kind. #MIKKIEWORLD",
            f"MIKKIE zegt: het beste avontuur begint buiten de voordeur! #MIKKIEWORLD #Buiten",
            f"7 karakters. 777 tegels. 1 missie: elk kind een held. #MIKKIEWORLD",
            f"Vandaag de missie: vind 5 dingen die beginnen met de letter M! #MIKKIEWORLD",
            f"BUBBLES, KNOEST, NYX, ORA, FIDO, ZERA en MIKKIE wachten op jou! #MIKKIEWORLD",
        ]
        return random.choice(fallbacks)
    # Roteer door de tweets
    idx = state.get('tweet_index', 0) % len(tweets)
    state['tweet_index'] = idx + 1
    return tweets[idx]

def sale_tweet(product_name, total_sales):
    """AI tweet bij nieuwe verkoop."""
    prompt = (
        f"Schrijf een enthousiaste Nederlandse tweet (max 230 tekens) voor MIKKIE WORLD. "
        f"Zojuist verkocht: '{product_name}'. Totaal nu: {total_sales} verkopen. "
        f"Warm, magisch, motiverend. Gebruik #MIKKIEWORLD. Geen aanhalingstekens."
    )
    tweet = grok(prompt, max_tokens=100)
    if tweet and len(tweet) <= 280:
        return tweet
    return f"Weer een avonturier gevonden! '{product_name}' is verkocht. {total_sales} avontuurlijke kinderen op weg! #MIKKIEWORLD"

# ─── MODULE 6: VERKOOP VERWERKEN ─────────────────────────────────────────────
def process_sale(sale, state):
    sid = sale.get('id', sale.get('order_id', ''))
    email = sale.get('email', '')
    product = sale.get('product_name', 'MIKKIE product')
    price = sale.get('price', 0) / 100
    full_name = sale.get('full_name', '')
    parts = full_name.split(' ', 1)
    fname, lname = (parts[0] if parts else ''), (parts[1] if len(parts) > 1 else '')

    log.info(f"VERKOOP: {product} | {email} | EUR{price:.2f}")

    # Mailchimp
    if mailchimp_add(email, fname, lname, product):
        log.info(f"  Mailchimp OK: {email}")

    # State
    state['processed_sales'].append(sid)
    state['total_sales'] += 1
    state['total_revenue'] += price

    # Tweet
    tweet = sale_tweet(product, state['total_sales'])
    post_tweet(tweet)

    save_state(state)

# ─── MODULE 7: DAGRAPPORT ────────────────────────────────────────────────────
def daily_report(state):
    now = datetime.datetime.now()
    days_left = (LAUNCH_DATE - now).days
    pct = min(state['total_revenue'] / 10000 * 100, 100)
    log.info("=" * 60)
    log.info("DAGRAPPORT MIKKIE WORLD")
    log.info(f"  {now.strftime('%A %d %B %Y')}")
    log.info(f"  Dagen tot 7/7/2026:  {days_left}")
    log.info(f"  Totaal verkopen:     {state['total_sales']}")
    log.info(f"  Totaal omzet:        EUR{state['total_revenue']:.2f}")
    log.info(f"  Doel EUR10.000:      {pct:.1f}%")
    log.info(f"  Verwerkte sales:     {len(state['processed_sales'])}")
    log.info("=" * 60)
    state['last_daily_report'] = now.strftime('%Y-%m-%d')
    save_state(state)

# ─── HOOFD LOOP ───────────────────────────────────────────────────────────────
def run():
    log.info("MIKKIE WORLD 24/7 Agent gestart")
    log.info(f"  Gumroad:   {'OK' if GUMROAD_TOKEN else 'ONTBREEKT'}")
    log.info(f"  Mailchimp: {'OK' if MAILCHIMP_KEY else 'ONTBREEKT'}")
    log.info(f"  Twitter:   {'OK' if TWITTER_KEY else 'ONTBREEKT'}")
    log.info(f"  Grok AI:   {'OK' if XAI_KEY else 'ONTBREEKT'}")
    log.info("-" * 60)

    state = load_state()
    last_poll = 0

    def shutdown(sig, frame):
        log.info("Agent gestopt")
        sys.exit(0)
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # Startup: direct Gumroad setup + weekly content als nog niet gedaan
    gumroad_setup_all(state)
    generate_weekly_content(state)

    while True:
        now = datetime.datetime.now()
        ts = time.time()

        # ── Gumroad poll elke 5 min ────────────────────────────────────────
        if ts - last_poll >= POLL_INTERVAL:
            log.info(f"Poll {now.strftime('%H:%M')} — sales check...")
            new_sales = get_new_sales(state)
            if new_sales:
                log.info(f"  {len(new_sales)} nieuwe verkoop/verkopen!")
                for s in new_sales:
                    process_sale(s, state)
                # Telegram: alert bij nieuwe verkoop!
                for s in new_sales:
                    product = s.get('product_name', 'onbekend product')
                    price   = s.get('price', 0) / 100
                    buyer   = s.get('full_name', 'anoniem')
                    telegram_alert(
                        f"💰 *Nieuwe verkoop!*\n\n"
                        f"Product: {product}\n"
                        f"Bedrag: €{price:.2f}\n"
                        f"Koper: {buyer}\n"
                        f"Totaal ooit: €{state['total_revenue']:.2f}",
                        "SUCCESS"
                    )
            else:
                log.info(f"  Geen nieuwe sales. Totaal: {state['total_sales']} | EUR{state['total_revenue']:.2f}")
            last_poll = ts

        # ── Dagrapport om 08:00 ────────────────────────────────────────────
        if now.hour == 8 and now.minute == 0:
            today = now.strftime('%Y-%m-%d')
            if state.get('last_daily_report') != today:
                daily_report(state)

        # ── Dagelijkse tweet om 09:00 ──────────────────────────────────────
        if now.hour == 9 and now.minute == 0:
            today = now.strftime('%Y-%m-%d')
            if state.get('last_tweet_date') != today:
                tweet = get_next_tweet(state)
                if post_tweet(tweet):
                    state['last_tweet_date'] = today
                    save_state(state)

        # ── Wekelijkse content maandag om 07:00 ───────────────────────────
        if now.weekday() == 0 and now.hour == 7 and now.minute == 0:
            generate_weekly_content(state)

        # ── Wekelijkse Gumroad sync zondag om 06:00 ───────────────────────
        if now.weekday() == 6 and now.hour == 6 and now.minute == 0:
            gumroad_setup_all(state, force=True)

        time.sleep(60)

# ─── CLI ──────────────────────────────────────────────────────────────────────
def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'

    if cmd == 'run':
        run()

    elif cmd == 'status':
        state = load_state()
        content = load_content()
        print("")
        print("MIKKIE WORLD Agent Status")
        print("=" * 40)
        print(f"  Sales verwerkt:  {len(state['processed_sales'])}")
        print(f"  Totaal omzet:    EUR{state['total_revenue']:.2f}")
        print(f"  Totaal sales:    {state['total_sales']}")
        print(f"  Laatste rapport: {state.get('last_daily_report', 'nooit')}")
        print(f"  Laatste tweet:   {state.get('last_tweet_date', 'nooit')}")
        print(f"  Gumroad setup:   {state.get('last_gumroad_setup', 'nooit')}")
        print(f"  Weekly content:  {state.get('last_weekly_content', 'nooit')}")
        print(f"  Tweets klaar:    {len(content.get('tweets', []))}")
        print(f"  Promo teksten:   {len(content.get('promo_texts', {}))}")
        import subprocess
        r = subprocess.run(['pgrep', '-f', 'mikkie_agent.py'], capture_output=True, text=True)
        pids = [p for p in r.stdout.strip().split('\n') if p and p != str(os.getpid())]
        print(f"  Agent actief:    {'JA (PID: ' + ', '.join(pids) + ')' if pids else 'NEE'}")
        print("")

    elif cmd == 'setup':
        state = load_state()
        gumroad_setup_all(state, force=True)

    elif cmd == 'content':
        state = load_state()
        state['last_weekly_content'] = ''  # Force regeneratie
        generate_weekly_content(state)
        content = load_content()
        print("")
        print("Gegenereerde content:")
        print(f"  {len(content.get('tweets', []))} tweets")
        print(f"  {len(content.get('promo_texts', {}))} promo-teksten")
        print(f"  {len(content.get('email_subjects', []))} email onderwerpen")
        print(f"  {len(content.get('descriptions', {}))} product beschrijvingen")
        print(f"\nOpgeslagen in: {CONTENT_FILE}")

    elif cmd == 'tweet':
        state = load_state()
        tweet = get_next_tweet(state)
        print(f"\nTweet ({len(tweet)} tekens):\n{tweet}\n")
        ans = input("Versturen? (y/n): ").strip().lower()
        if ans == 'y':
            if post_tweet(tweet):
                state['last_tweet_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
                save_state(state)
                print("Verstuurd!")
            else:
                print("Mislukt")

    elif cmd == 'show-content':
        content = load_content()
        print("\nTWEETS:")
        for i, t in enumerate(content.get('tweets', []), 1):
            print(f"  {i}. {t}")
        print("\nEMAIL ONDERWERPEN:")
        for s in content.get('email_subjects', []):
            print(f"  - {s}")

    elif cmd == 'log':
        os.system(f'tail -50 {LOG_FILE}')

    elif cmd == 'stop':
        os.system('pkill -f mikkie_agent.py')
        print("Agent gestopt")

    elif cmd == 'reset':
        for f in [STATE_FILE, CONTENT_FILE]:
            if os.path.exists(f):
                os.remove(f)
        print("State en content gereset")

    else:
        print(__doc__)


if __name__ == '__main__':
    main()
