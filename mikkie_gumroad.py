#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error

# API Tokens
GUMROAD_TOKEN = os.environ.get('GUMROAD_API_TOKEN', os.environ.get('GUMROAD_API_TOKEN', ''))
MAILCHIMP_API_KEY = os.environ.get('MAILCHIMP_API_KEY', os.environ.get('MAILCHIMP_API_KEY', ''))
MAILCHIMP_SERVER = os.environ.get('MAILCHIMP_SERVER', 'us14')
MAILCHIMP_LIST_ID = '75412e3953'

def gumroad_req(method, endpoint, data=None):
    url = f"https://api.gumroad.com/v2{endpoint}"
    
    # Gumroad API expects form-encoded data, not JSON
    if data:
        data['access_token'] = GUMROAD_TOKEN
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    else:
        encoded_data = urllib.parse.urlencode({'access_token': GUMROAD_TOKEN}).encode('utf-8')
        if method == 'GET':
            url = f"{url}?{encoded_data.decode('utf-8')}"
            encoded_data = None
            
    req = urllib.request.Request(url, data=encoded_data, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Gumroad API Error {e.code}: {e.read().decode()}")
        sys.exit(1)

def get_products():
    res = gumroad_req('GET', '/products')
    products = res.get('products', [])
    print(f"{'ID':<25} {'Prijs':<8} {'Sales':<6} {'Naam':<30}")
    print("-" * 75)
    for p in products:
        price = f"€{p['price']/100:.2f}"
        print(f"{p['id']:<25} {price:<8} {p['sales_count']:<6} {p['name']:<30}")

def create_product(name, price, desc="Jouw kind verdient avontuur."):
    data = {
        'name': name,
        'price': price, # In cents (e.g., 999 = €9.99)
        'description': desc,
        'currency': 'eur',
        'require_shipping': False
    }
    res = gumroad_req('POST', '/products', data)
    p = res['product']
    print(f"✅ Product aangemaakt: {p['name']} (ID: {p['id']})")
    print(f"🔗 URL: {p['short_url']}")
    return p['id']

def get_sales():
    res = gumroad_req('GET', '/sales')
    sales = res.get('sales', [])
    print(f"{'Datum':<12} {'Email':<25} {'Product':<20} {'Prijs'}")
    print("-" * 70)
    
    emails = []
    for s in sales:
        date = s['created_at'][:10]
        price = f"€{s['price']/100:.2f}"
        print(f"{date:<12} {s['email']:<25} {s['product_name'][:18]:<20} {price}")
        emails.append((s['email'], s['first_name'], s['last_name']))
        
    return emails

def sync_mailchimp(emails):
    if not emails:
        print("Geen kopers om te syncen.")
        return
        
    print(f"\n🔄 Syncing {len(emails)} kopers naar Mailchimp...")
    import base64
    
    url = f"https://{MAILCHIMP_SERVER}.api.mailchimp.com/3.0/lists/{MAILCHIMP_LIST_ID}/members"
    creds = base64.b64encode(f'anystring:{MAILCHIMP_API_KEY}'.encode()).decode()
    headers = {'Authorization': f'Basic {creds}', 'Content-Type': 'application/json'}
    
    added = 0
    for email, fname, lname in emails:
        data = {
            'email_address': email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': fname or '',
                'LNAME': lname or ''
            }
        }
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        try:
            urllib.request.urlopen(req)
            added += 1
            print(f"✅ {email} toegevoegd")
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print(f"ℹ️ {email} staat al in de lijst")
            else:
                print(f"❌ Error voor {email}: {e.code}")
                
    print(f"Sync compleet: {added} nieuwe abonnees toegevoegd.")

def print_help():
    print("MIKKIE WORLD Gumroad CLI")
    print("  mikkie-gumroad products               → Toon alle producten")
    print("  mikkie-gumroad sales                  → Toon alle verkopen")
    print("  mikkie-gumroad create <naam> <prijs>  → Maak nieuw product (prijs in centen, bv 999)")
    print("  mikkie-gumroad sync                   → Voeg alle Gumroad kopers toe aan Mailchimp")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if cmd == 'products':
        get_products()
    elif cmd == 'sales':
        get_sales()
    elif cmd == 'create':
        if len(sys.argv) < 4:
            print("Gebruik: mikkie-gumroad create \"Naam\" 999")
            sys.exit(1)
        create_product(sys.argv[2], int(sys.argv[3]))
    elif cmd == 'sync':
        emails = get_sales()
        sync_mailchimp(emails)
    else:
        print_help()

if __name__ == "__main__":
    main()
