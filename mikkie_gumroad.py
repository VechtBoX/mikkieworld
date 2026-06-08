#!/usr/bin/env python3
"""
MIKKIE WORLD - Gumroad CLI
Gebruik: mikkie-gumroad <commando>

Commando's:
  products                    -> Toon alle producten
  sales                       -> Toon alle verkopen
  create <naam> <prijs>       -> Maak nieuw product (prijs in centen)
  update <id> <veld> <waarde> -> Update product veld
  setup                       -> Maak alle MIKKIE producten aan
  sync                        -> Sync Gumroad kopers naar Mailchimp
  token-check                 -> Controleer of API token werkt
  help                        -> Toon dit menu
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import base64

GUMROAD_TOKEN = os.environ.get('GUMROAD_API_TOKEN', '')
MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY', '')
MAILCHIMP_SERVER = os.environ.get('MAILCHIMP_SERVER', 'us14')
MAILCHIMP_LIST_ID = '75412e3953'

PRODUCTS = [
    {
        'name': 'MIKKIE World: 91 Magische Karakter Illustraties',
        'price': 999,
        'existing_id': 'uiRWcbhQH-1Omdqzl1wQ7w==',
        'description': (
            '<h2>91 Magische MIKKIE Illustraties</h2>'
            '<p>Geef jouw kind een wereld vol avontuur, moed en magie. '
            'In dit pakket zitten <strong>91 unieke illustraties</strong> van alle MIKKIE WORLD karakters.</p>'
            '<h3>Inhoud</h3><ul>'
            '<li>MIKKIE de moedige avonturier (15 illustraties)</li>'
            '<li>BUBBLES de vrolijke watergeest (13 illustraties)</li>'
            '<li>KNOEST de wijze boswachter (13 illustraties)</li>'
            '<li>NYX de mysterieuze nachtelf (13 illustraties)</li>'
            '<li>ORA de slimme vossin (13 illustraties)</li>'
            '<li>FIDO de trouwe hond (12 illustraties)</li>'
            '<li>ZERA de energieke bliksem (12 illustraties)</li>'
            '</ul>'
            '<p>PNG (transparante achtergrond) + JPG hoge resolutie. '
            'Ideaal voor knutselen, verjaardagskaarten, posters en meer.</p>'
            '<p><em>Lancering: 7 juli 2026 om 07:07</em></p>'
        ),
    },
    {
        'name': 'BUBBLES Quest Bundle - Wateravonturen voor Kinderen',
        'price': 700,
        'description': (
            '<h2>BUBBLES Quest Bundle - 5 Wateravonturen</h2>'
            '<p>BUBBLES is de vrolijke watergeest. 5 buitenmissies voor kinderen van 4-10 jaar.</p>'
            '<ul><li>5 missiekaarten (A5, full-color)</li>'
            '<li>13 BUBBLES illustraties (PNG + JPG)</li>'
            '<li>Ouderhandleiding met veiligheidstips</li></ul>'
            '<p>Voorbeeldmissies: Vind 3 soorten waterinsecten - Bouw een minivlot - Maak een regenmeter</p>'
            '<p>Leeftijd: 4-10 jaar | Duur: 20-45 min | Locatie: Buiten</p>'
        ),
    },
    {
        'name': 'KNOEST Quest Bundle - Bosavonturen voor Kinderen',
        'price': 700,
        'description': (
            '<h2>KNOEST Quest Bundle - 5 Bosavonturen</h2>'
            '<p>KNOEST is de wijze eik die de geheimen van het bos kent. 5 bosavonturen voor nieuwsgierige kinderen.</p>'
            '<ul><li>5 missiekaarten (A5, full-color)</li>'
            '<li>13 KNOEST illustraties (PNG + JPG)</li>'
            '<li>Natuur-identificatiekaarten (bomen, paddenstoelen)</li></ul>'
            '<p>Voorbeeldmissies: Identificeer 5 boomsoorten - Zoek een oud vogelnest - Maak bladafdrukken</p>'
            '<p>Leeftijd: 5-12 jaar | Duur: 30-60 min | Locatie: Bos of park</p>'
        ),
    },
    {
        'name': 'NYX Quest Bundle - Nachtavonturen voor Kinderen',
        'price': 700,
        'description': (
            '<h2>NYX Quest Bundle - 5 Nachtavonturen</h2>'
            '<p>NYX is de mysterieuze nachtelf die de sterren bewaakt. 5 avondavonturen voor dappere kinderen.</p>'
            '<ul><li>5 missiekaarten (A5, full-color)</li>'
            '<li>13 NYX illustraties (PNG + JPG)</li>'
            '<li>Sterrenkaart (zomer/winter)</li></ul>'
            '<p>Voorbeeldmissies: Vind de Grote Beer - Luister naar 5 nachtgeluiden - Maak een maanfase-dagboek</p>'
            '<p>Leeftijd: 6-12 jaar | Duur: 20-40 min | Locatie: Tuin of park (avond)</p>'
        ),
    },
    {
        'name': 'ORA Quest Bundle - Slimme Speurtochten voor Kinderen',
        'price': 700,
        'description': (
            '<h2>ORA Quest Bundle - 5 Slimme Speurtochten</h2>'
            '<p>ORA is de slimme vossin die van raadsels en geheime paden houdt. 5 speurtochten die het denkvermogen prikkelen.</p>'
            '<ul><li>5 speurtochten (A5, full-color)</li>'
            '<li>13 ORA illustraties (PNG + JPG)</li>'
            '<li>Codeboekje met geheimschrift</li></ul>'
            '<p>Voorbeeldmissies: Ontcijfer ORA geheimschrift - Zoek 7 verborgen tekens - Los het bosraadsel op</p>'
            '<p>Leeftijd: 6-12 jaar | Duur: 30-60 min | Locatie: Buiten</p>'
        ),
    },
    {
        'name': 'FIDO Quest Bundle - Dierenspoor Avonturen voor Kinderen',
        'price': 700,
        'description': (
            '<h2>FIDO Quest Bundle - 5 Dierenspoor Avonturen</h2>'
            '<p>FIDO is de trouwe hond die overal sporen ruikt en vindt. 5 dierenspoor-missies voor avontuurlijke kinderen.</p>'
            '<ul><li>5 missiekaarten (A5, full-color)</li>'
            '<li>12 FIDO illustraties (PNG + JPG)</li>'
            '<li>Dierensporen-identificatiekaart</li></ul>'
            '<p>Voorbeeldmissies: Vind en teken 3 dierensporen - Bouw een dierenval - Maak een gipsen pootafdruk</p>'
            '<p>Leeftijd: 4-10 jaar | Duur: 30-60 min | Locatie: Bos, park of tuin</p>'
        ),
    },
    {
        'name': 'ZERA Quest Bundle - Energie en Weermissies voor Kinderen',
        'price': 700,
        'description': (
            '<h2>ZERA Quest Bundle - 5 Energie en Weermissies</h2>'
            '<p>ZERA is de energieke bliksem die van wind, regen en onweer houdt. 5 weermissies voor energieke kinderen.</p>'
            '<ul><li>5 missiekaarten (A5, full-color)</li>'
            '<li>12 ZERA illustraties (PNG + JPG)</li>'
            '<li>Weerstation-bouwhandleiding (DIY)</li></ul>'
            '<p>Voorbeeldmissies: Bouw een windvaan - Meet de regenval van een week - Zoek statische elektriciteit</p>'
            '<p>Leeftijd: 6-12 jaar | Duur: 30-60 min | Locatie: Buiten</p>'
        ),
    },
    {
        'name': 'MIKKIE Founders Pack - Compleet Avontuurspakket',
        'price': 4700,
        'description': (
            '<h2>MIKKIE Founders Pack - Het Complete Avontuurspakket</h2>'
            '<p>Voor de echte MIKKIE fan: het <strong>Founders Pack</strong> bevat ALLES. '
            'Jij bent een van de eerste 100 Founders!</p>'
            '<ul>'
            '<li>91 MIKKIE illustraties (alle 7 karakters, PNG + JPG)</li>'
            '<li>35 buitenmissies (5 per karakter)</li>'
            '<li>7 Quest Bundles (alle karakters)</li>'
            '<li>Founders Badge - digitaal certificaat</li>'
            '<li>Vroeg toegang tot alle nieuwe missies (1 jaar)</li>'
            '<li>Naam in het MIKKIE WORLD Founders Boek</li>'
            '</ul>'
            '<p><strong>Slechts 100 Founders Packs beschikbaar.</strong></p>'
            '<p><em>Lancering: 7 juli 2026 om 07:07</em></p>'
        ),
    },
]


def gumroad_req(method, endpoint, data=None):
    if not GUMROAD_TOKEN:
        print("FOUT: GUMROAD_API_TOKEN niet gevonden.")
        print("  Maak nieuw token: https://app.gumroad.com/settings/advanced")
        print("  Voeg toe aan ~/.zshrc: export GUMROAD_API_TOKEN=jouw_token")
        print("  Herlaad: source ~/.zshrc")
        sys.exit(1)
    url = "https://api.gumroad.com/v2" + endpoint
    if data:
        data['access_token'] = GUMROAD_TOKEN
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    else:
        qs = urllib.parse.urlencode({'access_token': GUMROAD_TOKEN})
        if method == 'GET':
            url = url + "?" + qs
            encoded_data = None
        else:
            encoded_data = qs.encode('utf-8')
    req = urllib.request.Request(url, data=encoded_data, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print("Gumroad API Error " + str(e.code) + ": " + body[:200])
        if e.code == 401:
            print("")
            print("Token verlopen of ingetrokken!")
            print("  Maak nieuw token: https://app.gumroad.com/settings/advanced")
            print("  Update ~/.zshrc: export GUMROAD_API_TOKEN=nieuw_token")
            print("  Herlaad: source ~/.zshrc")
        sys.exit(1)


def token_check():
    print("Token check...")
    res = gumroad_req('GET', '/products')
    if res.get('success'):
        n = len(res.get('products', []))
        print("OK - Token werkt! " + str(n) + " product(en) gevonden.")
    else:
        print("FOUT: " + str(res))


def get_products():
    res = gumroad_req('GET', '/products')
    products = res.get('products', [])
    if not products:
        print("Geen producten gevonden.")
        return
    print("")
    print("{:<45} {:<10} {:<6} {}".format("Naam", "Prijs", "Sales", "ID"))
    print("-" * 90)
    for p in products:
        price = "EUR" + str(p['price']/100)
        name = p['name'][:43]
        print("{:<45} {:<10} {:<6} {}".format(name, price, p['sales_count'], p['id']))
    print("")
    print("Totaal: " + str(len(products)) + " producten")


def create_product(name, price_cents, desc=None):
    if desc is None:
        desc = "<p>" + name + " - onderdeel van MIKKIE WORLD. Avontuur voor elk kind!</p>"
    data = {
        'name': name,
        'price': str(price_cents),
        'description': desc,
        'currency': 'eur',
        'require_shipping': 'false',
        'published': 'false',
    }
    res = gumroad_req('POST', '/products', data)
    if res.get('success'):
        p = res['product']
        print("Aangemaakt: " + p['name'])
        print("  ID:  " + p['id'])
        print("  URL: " + p.get('short_url', 'n/a'))
        return p['id']
    else:
        print("FOUT: " + str(res))
        return None


def update_product(product_id, field, value):
    data = {field: value}
    pid_encoded = urllib.parse.quote(product_id, safe='')
    res = gumroad_req('PUT', '/products/' + pid_encoded, data)
    if res.get('success'):
        preview = value[:60] if len(value) > 60 else value
        print("Bijgewerkt: " + field + " = " + preview)
    else:
        print("Update mislukt: " + str(res))


def setup_all_products():
    print("MIKKIE WORLD - Gumroad Setup")
    print("=" * 50)
    print("Aanmaken van " + str(len(PRODUCTS)) + " producten...")
    print("")
    existing_res = gumroad_req('GET', '/products')
    existing = {}
    for p in existing_res.get('products', []):
        existing[p['name']] = p['id']
    for prod in PRODUCTS:
        name = prod['name']
        price = prod['price']
        desc = prod['description']
        if name in existing:
            pid = existing[name]
            print("Bestaat al: " + name[:50])
            update_product(pid, 'description', desc)
        elif 'existing_id' in prod:
            pid = prod['existing_id']
            print("Update bestaand: " + name[:50])
            update_product(pid, 'description', desc)
            update_product(pid, 'name', name)
        else:
            print("Aanmaken: " + name[:50])
            create_product(name, price, desc)
        print("")
    print("=" * 50)
    print("Setup compleet!")
    print("Controleer: mikkie-gumroad products")
    print("Dashboard:  https://app.gumroad.com/products")


def get_sales():
    res = gumroad_req('GET', '/sales')
    sales = res.get('sales', [])
    if not sales:
        print("Nog geen verkopen.")
        return []
    print("")
    print("{:<12} {:<28} {:<25} {}".format("Datum", "Email", "Product", "Prijs"))
    print("-" * 75)
    emails = []
    for s in sales:
        date = s['created_at'][:10]
        price = "EUR" + str(s['price']/100)
        pname = s.get('product_name', '')[:23]
        print("{:<12} {:<28} {:<25} {}".format(date, s['email'], pname, price))
        full = s.get('full_name', '')
        parts = full.split(' ', 1)
        fname = parts[0] if parts else ''
        lname = parts[1] if len(parts) > 1 else ''
        emails.append((s['email'], fname, lname))
    print("")
    print("Totaal: " + str(len(sales)) + " verkopen")
    return emails


def sync_mailchimp():
    if not MAILCHIMP_API_KEY:
        print("FOUT: MAILCHIMP_API_KEY niet gevonden.")
        sys.exit(1)
    emails = get_sales()
    if not emails:
        print("Geen kopers om te syncen.")
        return
    print("")
    print("Syncing " + str(len(emails)) + " kopers naar Mailchimp...")
    url = "https://" + MAILCHIMP_SERVER + ".api.mailchimp.com/3.0/lists/" + MAILCHIMP_LIST_ID + "/members"
    creds = base64.b64encode(('anystring:' + MAILCHIMP_API_KEY).encode()).decode()
    headers = {
        'Authorization': 'Basic ' + creds,
        'Content-Type': 'application/json'
    }
    added = 0
    for email, fname, lname in emails:
        data = json.dumps({
            'email_address': email,
            'status': 'subscribed',
            'tags': ['gumroad-koper'],
            'merge_fields': {'FNAME': fname, 'LNAME': lname}
        }).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            urllib.request.urlopen(req)
            added += 1
            print("OK: " + email)
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print("Al in lijst: " + email)
            else:
                print("FOUT " + email + ": HTTP " + str(e.code))
    print("")
    print("Sync compleet: " + str(added) + " nieuwe abonnees toegevoegd.")


def print_help():
    print(__doc__)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    if cmd == 'token-check':
        token_check()
    elif cmd == 'products':
        get_products()
    elif cmd == 'sales':
        get_sales()
    elif cmd == 'create':
        if len(sys.argv) < 4:
            print("Gebruik: mikkie-gumroad create Naam 999")
            sys.exit(1)
        create_product(sys.argv[2], int(sys.argv[3]))
    elif cmd == 'update':
        if len(sys.argv) < 5:
            print("Gebruik: mikkie-gumroad update <id> <veld> <waarde>")
            sys.exit(1)
        update_product(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'setup':
        setup_all_products()
    elif cmd == 'sync':
        sync_mailchimp()
    else:
        print_help()


if __name__ == "__main__":
    main()
