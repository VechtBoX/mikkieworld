#!/usr/bin/env python3
"""
MIKKIE WORLD - Gumroad Volledige Configuratie
Bijwerkt alle producten: naam, prijs, beschrijving, publicatiestatus
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import time

TOKEN = "9byVxzgAYPnwnhL3jPjZiVxOQrSvmQrweISCtzr00RI"

# ─── Definitieve productlijn ─────────────────────────────────────────────────
# Prijsstrategie:
#   - Gratis PDF: leadmagnet, e-mail capture
#   - €9.99: illustraties pakket (laagdrempelig, impuls aankoop)
#   - €12.00: Quest Bundle per karakter (5 missies + illustraties)
#   - €49.00: Founders Pack (alles + exclusief)
#
# Ratio: gratis → €9.99 → €12 × 6 = €72 → €49 founders
# Max per klant: €9.99 + €72 + €49 = €130.99

UPDATES = [
    # ── GRATIS LEADMAGNET ────────────────────────────────────────────────────
    {
        'id': '59BL9uT7Q5geTu0RrM0PuA==',
        'name': 'MIKKIE 7 Gratis Buitenmissies',
        'price': 0,
        'published': False,  # Pas publiceren als PDF geupload is
        'description': (
            '<h2>7 Gratis Buitenmissies voor Avontuurlijke Kinderen</h2>'
            '<p>Jouw kind is een held. Ze hoeven alleen maar naar buiten te gaan.</p>'
            '<p>Dit gratis PDF-boekje bevat <strong>7 echte buitenmissies</strong> '
            'die kinderen van 4 tot 12 jaar zelfstandig kunnen uitvoeren — '
            'in de tuin, het park of het bos.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>Missie 1: De Bladendetective (zoek 5 verschillende bladeren)</li>'
            '<li>Missie 2: De Wolkenkijker (teken 3 wolkenvormen)</li>'
            '<li>Missie 3: De Steenzoeker (bouw een steentorntje)</li>'
            '<li>Missie 4: De Regenboogkunstenaar (maak een krijtregenboog)</li>'
            '<li>Missie 5: De Insectenspion (vind 5 insecten)</li>'
            '<li>Missie 6: De Windmeter (bouw een windvaan)</li>'
            '<li>Missie 7: De Sterrenzoeker (vind de Grote Beer)</li>'
            '</ul>'
            '<p>Elke missie past op een A4 en heeft een tekenvak voor jouw kind.</p>'
            '<p><strong>100% gratis. Geen creditcard nodig.</strong></p>'
            '<p><em>Van MIKKIE WORLD — avontuur voor elk kind. Lancering: 7 juli 2026 om 07:07</em></p>'
        ),
    },

    # ── ILLUSTRATIES PAKKET ──────────────────────────────────────────────────
    {
        'id': 'uiRWcbhQH-1Omdqzl1wQ7w==',
        'name': 'MIKKIE WORLD: 91 Magische Karakter Illustraties',
        'price': 999,  # EUR 9.99
        'published': True,  # Al gepubliceerd, blijft live
        'description': (
            '<h2>91 Magische Illustraties van alle MIKKIE WORLD Karakters</h2>'
            '<p>Geef jouw kind een wereld vol avontuur, moed en magie. '
            'Dit digitale pakket bevat <strong>91 unieke illustraties</strong> '
            'van alle 7 MIKKIE WORLD karakters — direct te downloaden.</p>'
            '<h3>De 7 karakters</h3>'
            '<ul>'
            '<li><strong>MIKKIE</strong> — de moedige avonturier in pyjama (15 illustraties)</li>'
            '<li><strong>BUBBLES</strong> — de vrolijke watergeest (13 illustraties)</li>'
            '<li><strong>KNOEST</strong> — de wijze boswachter (13 illustraties)</li>'
            '<li><strong>NYX</strong> — de mysterieuze nachtelf (13 illustraties)</li>'
            '<li><strong>ORA</strong> — de slimme vossin (13 illustraties)</li>'
            '<li><strong>FIDO</strong> — de trouwe hond (12 illustraties)</li>'
            '<li><strong>ZERA</strong> — de energieke bliksem (12 illustraties)</li>'
            '</ul>'
            '<h3>Formaten inbegrepen</h3>'
            '<p>PNG met transparante achtergrond + JPG hoge resolutie (300dpi). '
            'Klaar voor print, digitaal gebruik, knutselen en meer.</p>'
            '<h3>Ideaal voor</h3>'
            '<p>Verjaardagskaarten, posters, knutselprojecten, schoolprojecten, '
            'digitale stickers, uitnodigingen en meer.</p>'
            '<p><strong>Direct downloaden na betaling.</strong></p>'
            '<p><em>MIKKIE WORLD — avontuur voor elk kind | mikkieworld.com</em></p>'
        ),
    },

    # ── QUEST BUNDLES (€12 per stuk) ────────────────────────────────────────
    {
        'id': 'o4xaqMsL1b9dQ4Gga2nA7Q==',
        'name': 'BUBBLES Quest Bundle — 5 Wateravonturen + 13 Illustraties',
        'price': 1200,  # EUR 12.00
        'published': False,
        'description': (
            '<h2>BUBBLES Quest Bundle — 5 Wateravonturen</h2>'
            '<p>BUBBLES is de vrolijke watergeest die van plassen, rivieren en regen houdt. '
            'Met dit pakket gaat jouw kind op <strong>5 echte wateravonturen</strong>.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>5 missiekaarten (A5, full-color, printklaar PDF)</li>'
            '<li>13 BUBBLES illustraties (PNG transparant + JPG 300dpi)</li>'
            '<li>Ouderhandleiding met veiligheidstips</li>'
            '<li>Missie-stickers voor het avontuurboekje</li>'
            '</ul>'
            '<h3>De 5 missies</h3>'
            '<p>Vind 3 soorten waterinsecten — Bouw een minivlot van takjes — '
            'Maak een regenmeter van een fles — Zoek dierensporen langs het water — '
            'Teken de weerspiegeling in een plas</p>'
            '<p><strong>Leeftijd:</strong> 4-10 jaar | '
            '<strong>Duur per missie:</strong> 20-45 minuten | '
            '<strong>Locatie:</strong> Buiten (water, regen, plas)</p>'
            '<p><em>MIKKIE WORLD — avontuur voor elk kind | Lancering 7/7/2026</em></p>'
        ),
    },
    {
        'id': 'fsuPN7_ca1c2bKcdvNeRKg==',
        'name': 'KNOEST Quest Bundle — 5 Bosavonturen + 13 Illustraties',
        'price': 1200,  # EUR 12.00
        'published': False,
        'description': (
            '<h2>KNOEST Quest Bundle — 5 Bosavonturen</h2>'
            '<p>KNOEST is de oude, wijze eik die de geheimen van het bos kent. '
            'Met dit pakket ontdekt jouw kind de <strong>magie van het bos</strong>.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>5 missiekaarten (A5, full-color, printklaar PDF)</li>'
            '<li>13 KNOEST illustraties (PNG transparant + JPG 300dpi)</li>'
            '<li>Natuur-identificatiekaarten (bomen, paddenstoelen, sporen)</li>'
            '<li>Ouderhandleiding</li>'
            '</ul>'
            '<h3>De 5 missies</h3>'
            '<p>Identificeer 5 boomsoorten — Zoek een oud vogelnest — '
            'Maak bladafdrukken van 10 verschillende bladeren — '
            'Vind een paddenstoel en teken hem na — '
            'Bouw een schuilplaats van takken</p>'
            '<p><strong>Leeftijd:</strong> 5-12 jaar | '
            '<strong>Duur per missie:</strong> 30-60 minuten | '
            '<strong>Locatie:</strong> Bos of park</p>'
            '<p><em>MIKKIE WORLD — avontuur voor elk kind | Lancering 7/7/2026</em></p>'
        ),
    },
    {
        'id': 'T9LpDUWWeVLPmKgDbeOSeg==',
        'name': 'NYX Quest Bundle — 5 Nachtavonturen + 13 Illustraties',
        'price': 1200,  # EUR 12.00
        'published': False,
        'description': (
            '<h2>NYX Quest Bundle — 5 Nachtavonturen</h2>'
            '<p>NYX is de mysterieuze nachtelf die de sterren en de maan bewaakt. '
            'Met dit pakket gaat jouw kind op <strong>5 magische avondavonturen</strong>.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>5 missiekaarten (A5, full-color, printklaar PDF)</li>'
            '<li>13 NYX illustraties (PNG transparant + JPG 300dpi)</li>'
            '<li>Sterrenkaart (zomer + winter)</li>'
            '<li>Ouderhandleiding met nacht-veiligheidstips</li>'
            '</ul>'
            '<h3>De 5 missies</h3>'
            '<p>Vind de Grote Beer en de Poolster — Luister naar 5 nachtgeluiden en teken ze — '
            'Maak een maanfase-dagboek van 1 week — '
            'Zoek 3 nachtdieren in de tuin — '
            'Bouw een lantaarn van een pot en een kaars</p>'
            '<p><strong>Leeftijd:</strong> 6-12 jaar | '
            '<strong>Duur per missie:</strong> 20-40 minuten | '
            '<strong>Locatie:</strong> Tuin of park (avond/nacht)</p>'
            '<p><em>MIKKIE WORLD — avontuur voor elk kind | Lancering 7/7/2026</em></p>'
        ),
    },
    {
        'id': 'vL8TxyAqnUslfH9Ilw9FNg==',
        'name': 'ORA Quest Bundle — 5 Slimme Speurtochten + 13 Illustraties',
        'price': 1200,  # EUR 12.00
        'published': False,
        'description': (
            '<h2>ORA Quest Bundle — 5 Slimme Speurtochten</h2>'
            '<p>ORA is de slimme vossin die van raadsels, puzzels en geheime paden houdt. '
            'Met dit pakket prikkelt jouw kind zijn <strong>denkvermogen en nieuwsgierigheid</strong>.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>5 speurtochten (A5, full-color, printklaar PDF)</li>'
            '<li>13 ORA illustraties (PNG transparant + JPG 300dpi)</li>'
            '<li>Codeboekje met ORA geheimschrift</li>'
            '<li>Ouderhandleiding</li>'
            '</ul>'
            '<h3>De 5 missies</h3>'
            '<p>Ontcijfer ORA geheimschrift — Zoek 7 verborgen tekens in de buurt — '
            'Los het bosraadsel op — Maak een schatkaart van jouw tuin — '
            'Vind de geheime route van ORA</p>'
            '<p><strong>Leeftijd:</strong> 6-12 jaar | '
            '<strong>Duur per missie:</strong> 30-60 minuten | '
            '<strong>Locatie:</strong> Buiten (tuin, park, straat)</p>'
            '<p><em>MIKKIE WORLD — avontuur voor elk kind | Lancering 7/7/2026</em></p>'
        ),
    },
    {
        'id': 'E5a-iHShBzCckrz6BHY6Xw==',
        'name': 'FIDO Quest Bundle — 5 Dierenspoor Avonturen + 12 Illustraties',
        'price': 1200,  # EUR 12.00
        'published': False,
        'description': (
            '<h2>FIDO Quest Bundle — 5 Dierenspoor Avonturen</h2>'
            '<p>FIDO is de trouwe hond die overal sporen ruikt en vindt. '
            'Met dit pakket wordt jouw kind een echte <strong>dierenspoordetective</strong>.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>5 missiekaarten (A5, full-color, printklaar PDF)</li>'
            '<li>12 FIDO illustraties (PNG transparant + JPG 300dpi)</li>'
            '<li>Dierensporen-identificatiekaart (20 soorten)</li>'
            '<li>Ouderhandleiding</li>'
            '</ul>'
            '<h3>De 5 missies</h3>'
            '<p>Vind en teken 3 dierensporen — Bouw een dierencamera val — '
            'Maak een gipsen afdruk van een pootje — '
            'Zoek een dierenhol of nest — '
            'Maak een dierensporen-dagboek van 1 week</p>'
            '<p><strong>Leeftijd:</strong> 4-10 jaar | '
            '<strong>Duur per missie:</strong> 30-60 minuten | '
            '<strong>Locatie:</strong> Bos, park of tuin</p>'
            '<p><em>MIKKIE WORLD — avontuur voor elk kind | Lancering 7/7/2026</em></p>'
        ),
    },
    {
        'id': 'RMA17VrScb8R6dsXQeZtSg==',
        'name': 'ZERA Quest Bundle — 5 Energie en Weermissies + 12 Illustraties',
        'price': 1200,  # EUR 12.00
        'published': False,
        'description': (
            '<h2>ZERA Quest Bundle — 5 Energie en Weermissies</h2>'
            '<p>ZERA is de energieke bliksem die van wind, regen en onweer houdt. '
            'Met dit pakket onderzoekt jouw kind de <strong>krachten van de natuur</strong>.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>5 missiekaarten (A5, full-color, printklaar PDF)</li>'
            '<li>12 ZERA illustraties (PNG transparant + JPG 300dpi)</li>'
            '<li>DIY weerstation bouwhandleiding</li>'
            '<li>Ouderhandleiding</li>'
            '</ul>'
            '<h3>De 5 missies</h3>'
            '<p>Bouw een windvaan van karton — Meet de regenval van een week — '
            'Zoek statische elektriciteit in de natuur — '
            'Maak een zonnewijzer — '
            'Bouw een mini-weerstation en houd het bij</p>'
            '<p><strong>Leeftijd:</strong> 6-12 jaar | '
            '<strong>Duur per missie:</strong> 30-60 minuten | '
            '<strong>Locatie:</strong> Buiten (tuin, park)</p>'
            '<p><em>MIKKIE WORLD — avontuur voor elk kind | Lancering 7/7/2026</em></p>'
        ),
    },

    # ── FOUNDERS PACK ────────────────────────────────────────────────────────
    {
        'id': 'kS7vevDiRqM4KyuauDKUzQ==',
        'name': 'MIKKIE WORLD Founders Pack — Alles + Exclusief (100 stuks)',
        'price': 4900,  # EUR 49.00 (was 47, afgerond naar logische prijs)
        'published': False,
        'description': (
            '<h2>MIKKIE WORLD Founders Pack — Het Complete Avontuurspakket</h2>'
            '<p>Voor de echte MIKKIE fan: het <strong>Founders Pack</strong> '
            'bevat ALLES wat MIKKIE WORLD te bieden heeft. '
            'Jij bent een van de <strong>eerste 100 Founders</strong> — '
            'en dat is voor altijd.</p>'
            '<h3>Wat zit erin?</h3>'
            '<ul>'
            '<li>91 MIKKIE illustraties (alle 7 karakters, PNG + JPG 300dpi)</li>'
            '<li>35 buitenmissies (5 per karakter, alle 7 Quest Bundles)</li>'
            '<li>Alle identificatiekaarten, codeboekjes en handleidingen</li>'
            '<li>Digitaal Founders Certificaat (gepersonaliseerd)</li>'
            '<li>Vroeg toegang tot alle nieuwe missies (1 jaar gratis)</li>'
            '<li>Naam in het MIKKIE WORLD Founders Boek (eerste editie)</li>'
            '<li>Directe toegang tot de MIKKIE Founders community</li>'
            '</ul>'
            '<h3>Founders voordelen</h3>'
            '<p>Als Founder steun je de lancering van MIKKIE WORLD op 7 juli 2026. '
            'Je krijgt alle toekomstige updates gratis en je naam staat in het eerste MIKKIE boek. '
            'Dit pakket is nooit meer voor deze prijs beschikbaar.</p>'
            '<p><strong>Normaal: €9.99 + 6 x €12 + extras = €81.99</strong><br>'
            '<strong>Founders prijs: €49 — bespaar €33</strong></p>'
            '<p><strong>Slechts 100 Founders Packs beschikbaar. Op = op.</strong></p>'
            '<p><em>Lancering: 7 juli 2026 om 07:07 — MIKKIE WORLD gaat live!</em></p>'
        ),
    },
]


def gumroad_put(product_id, data):
    token = TOKEN
    data['access_token'] = token
    pid = urllib.parse.quote(product_id, safe='')
    url = f"https://api.gumroad.com/v2/products/{pid}"
    encoded = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded, method='PUT')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  FOUT {e.code}: {e.read().decode()[:100]}")
        return None


def main():
    print("MIKKIE WORLD — Gumroad Volledige Configuratie")
    print("=" * 60)
    print(f"Bijwerken van {len(UPDATES)} producten...\n")

    ok = 0
    for prod in UPDATES:
        pid = prod['id']
        name = prod['name']
        price = prod['price']
        desc = prod['description']
        pub = prod.get('published', False)

        print(f"Bijwerken: {name[:55]}")
        print(f"  Prijs: EUR{price/100:.2f} | Gepubliceerd: {pub}")

        data = {
            'name': name,
            'price': str(price),
            'description': desc,
            'published': 'true' if pub else 'false',
        }
        res = gumroad_put(pid, data)
        if res and res.get('success'):
            p = res['product']
            print(f"  OK — {p.get('short_url', '')}")
            ok += 1
        else:
            print(f"  MISLUKT")
        print()
        time.sleep(0.5)  # Voorkom rate limiting

    print("=" * 60)
    print(f"Klaar: {ok}/{len(UPDATES)} producten bijgewerkt")
    print()
    print("Productoverzicht:")
    print(f"  Gratis:   MIKKIE 7 Gratis Buitenmissies (leadmagnet)")
    print(f"  EUR 9.99: 91 Magische Illustraties")
    print(f"  EUR12.00: 6x Quest Bundle (BUBBLES/KNOEST/NYX/ORA/FIDO/ZERA)")
    print(f"  EUR49.00: Founders Pack (100 stuks, alles inbegrepen)")
    print()
    print("Max omzet per klant: EUR9.99 + 6x12 + 49 = EUR130.99")
    print()
    print("Volgende stap: PDF uploaden bij gratis product")
    print("  https://app.gumroad.com/products")


if __name__ == "__main__":
    main()
