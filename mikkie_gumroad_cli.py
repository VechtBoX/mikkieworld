#!/usr/bin/env python3
"""
MIKKIE WORLD — Gumroad CLI Agent
Beheer Gumroad producten, sales en statistieken via de terminal.
Tagline: Blijf Altijd Kind. Met je kids. | Always Be a Kid. With your kids.
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── Configuratie ────────────────────────────────────────────────────────────
GUMROAD_TOKEN = os.getenv("GUMROAD_API_TOKEN", "4FWiHVPVy4NJ7xfhqkA9Vm8Kq7QwV9BcrqXi7vU6y1E")
BASE_URL = "https://api.gumroad.com/v2"
BASE_DIR = Path(__file__).parent
LOGS_DIR = Path.home() / "MIKKIE_WORLD" / "LOGS"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"Authorization": f"Bearer {GUMROAD_TOKEN}"}

KARAKTERS = ["MIKKIE", "BUBBLES", "KNOEST", "FIDO", "NYX", "ZERA", "ORA"]

# ─── API Helpers ─────────────────────────────────────────────────────────────

def api_get(endpoint, params=None):
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params, timeout=15)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def api_post(endpoint, data=None):
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", headers=HEADERS, data=data, timeout=15)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

# ─── Commando's ──────────────────────────────────────────────────────────────

def cmd_products():
    """Toon alle Gumroad producten"""
    print("\n═══════════════════════════════════════════════════════")
    print("  MIKKIE WORLD — Gumroad Producten")
    print(f"  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print("═══════════════════════════════════════════════════════\n")

    data = api_get("/products")
    if not data.get("success"):
        print(f"❌ Fout: {data.get('message', 'Onbekende fout')}")
        return

    products = data.get("products", [])
    if not products:
        print("⚠️  Geen producten gevonden")
        return

    print(f"📦 {len(products)} producten gevonden:\n")
    total_sales = 0
    total_revenue = 0.0

    for p in products:
        name = p.get("name", "Onbekend")
        price = p.get("price", 0) / 100
        sales = p.get("sales_count", 0)
        revenue = sales * price
        total_sales += sales
        total_revenue += revenue
        published = "✅" if p.get("published") else "⚫"
        pid = p.get("id", "")[:8]

        print(f"  {published} {name}")
        print(f"     💰 €{price:.2f}  |  🛒 {sales} verkopen  |  💵 €{revenue:.2f}  |  ID: {pid}...")
        print()

    print(f"  ─────────────────────────────────────────────")
    print(f"  📊 Totaal: {total_sales} verkopen  |  💵 €{total_revenue:.2f} omzet")
    print()

def cmd_sales(days=7):
    """Toon recente sales"""
    print("\n═══════════════════════════════════════════════════════")
    print(f"  MIKKIE WORLD — Sales (laatste {days} dagen)")
    print(f"  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print("═══════════════════════════════════════════════════════\n")

    data = api_get("/sales")
    if not data.get("success"):
        print(f"❌ Fout: {data.get('message', 'Onbekende fout')}")
        return

    sales = data.get("sales", [])
    cutoff = datetime.now() - timedelta(days=days)

    recent = []
    for s in sales:
        try:
            sale_date = datetime.strptime(s.get("created_at", ""), "%Y-%m-%dT%H:%M:%SZ")
            if sale_date >= cutoff:
                recent.append(s)
        except:
            pass

    if not recent:
        print(f"  📭 Geen sales in de laatste {days} dagen")
        return

    total = sum(s.get("price", 0) for s in recent) / 100
    print(f"  🛒 {len(recent)} sales  |  💵 €{total:.2f}\n")

    for s in recent[:10]:
        name = s.get("product_name", "Onbekend")
        price = s.get("price", 0) / 100
        buyer = s.get("email", "anoniem")
        date = s.get("created_at", "")[:10]
        print(f"  ✅ {date}  {name}  €{price:.2f}  ({buyer})")

    if len(recent) > 10:
        print(f"\n  ... en {len(recent) - 10} meer")
    print()

def cmd_stats():
    """Toon statistieken dashboard"""
    print("\n═══════════════════════════════════════════════════════")
    print("  MIKKIE WORLD — Gumroad Dashboard")
    print(f"  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print("═══════════════════════════════════════════════════════\n")

    # Producten ophalen
    data = api_get("/products")
    if not data.get("success"):
        print(f"❌ Fout: {data.get('message', 'Onbekende fout')}")
        return

    products = data.get("products", [])
    total_products = len(products)
    published = sum(1 for p in products if p.get("published"))
    total_sales = sum(p.get("sales_count", 0) for p in products)
    total_revenue = sum(p.get("sales_count", 0) * p.get("price", 0) / 100 for p in products)

    print(f"  📦 Producten:    {total_products} totaal  |  {published} gepubliceerd")
    print(f"  🛒 Verkopen:     {total_sales} totaal")
    print(f"  💵 Omzet:        €{total_revenue:.2f} totaal")
    print()

    # Top 3 producten
    sorted_products = sorted(products, key=lambda p: p.get("sales_count", 0), reverse=True)
    if sorted_products:
        print("  🏆 Top producten:")
        for i, p in enumerate(sorted_products[:3], 1):
            name = p.get("name", "Onbekend")
            sales = p.get("sales_count", 0)
            revenue = sales * p.get("price", 0) / 100
            print(f"     {i}. {name}  —  {sales} verkopen  —  €{revenue:.2f}")
    print()

    # Lancering countdown
    launch = datetime(2026, 7, 7, 7, 7, 0)
    now = datetime.now()
    days_left = (launch - now).days
    print(f"  🚀 Lancering 7 juli 2026: nog {days_left} dagen")
    print(f"  💡 Tagline: Blijf Altijd Kind. Met je kids.")
    print()

def cmd_create_bundle():
    """Maak een Complete Bundle product aan"""
    print("\n🛒 Complete Bundle aanmaken op Gumroad...")

    bundle_data = {
        "name": "MIKKIE WORLD — Complete Bundle",
        "price": 2900,  # €29.00
        "description": """🌟 De Complete MIKKIE WORLD Bundle — Blijf Altijd Kind. Met je kids.

Alles wat je nodig hebt om avontuur te beleven met je kinderen:

✅ MIKKIE — Het Grote Avontuur (PDF)
✅ BUBBLES — De Trouwe Sidekick (PDF)
✅ KNOEST — De Boswachter (PDF)
✅ FIDO — De Draak (PDF)
✅ NYX — De Nachtprinses (PDF)
✅ ZERA — De Beschermengel (PDF)
✅ ORA — De Wijze Uil (PDF)
✅ 25 Kleurplaten (printbaar)
✅ Buitenmissie Kaarten (7 stuks)
✅ MIKKIE WORLD Sticker Pack (digitaal)

🎯 Voor kinderen van 4-10 jaar
🌿 Buiten spelen, avontuur en karakter
🔮 Magie die verbindt

mikkie.world | lancering 7 juli 2026""",
        "published": "false",
        "tags": "kinderen,avontuur,buiten,magie,bundle",
    }

    data = api_post("/products", bundle_data)
    if data.get("success"):
        product = data.get("product", {})
        print(f"  ✅ Bundle aangemaakt: {product.get('name')}")
        print(f"     ID: {product.get('id')}")
        print(f"     URL: {product.get('short_url')}")
    else:
        print(f"  ❌ Fout: {data.get('message', 'Onbekende fout')}")
    print()

def cmd_report():
    """Sla dagrapport op"""
    data = api_get("/products")
    if not data.get("success"):
        print(f"❌ Kan rapport niet ophalen: {data.get('message')}")
        return

    products = data.get("products", [])
    total_sales = sum(p.get("sales_count", 0) for p in products)
    total_revenue = sum(p.get("sales_count", 0) * p.get("price", 0) / 100 for p in products)

    report = {
        "datum": datetime.now().isoformat(),
        "producten": len(products),
        "gepubliceerd": sum(1 for p in products if p.get("published")),
        "totaal_sales": total_sales,
        "totaal_omzet": round(total_revenue, 2),
        "producten_detail": [
            {
                "naam": p.get("name"),
                "prijs": p.get("price", 0) / 100,
                "sales": p.get("sales_count", 0),
                "gepubliceerd": p.get("published", False)
            }
            for p in products
        ]
    }

    report_file = LOGS_DIR / f"gumroad_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ Rapport opgeslagen: {report_file}")
    print(f"   📦 {len(products)} producten  |  🛒 {total_sales} sales  |  💵 €{total_revenue:.2f}")

def print_help():
    launch = datetime(2026, 7, 7, 7, 7, 0)
    days_left = (launch - datetime.now()).days
    print(f"""
  MIKKIE WORLD Gumroad CLI | {days_left} dagen tot launch
  ─────────────────────────────────────────────────────
  mikkie-gumroad products       Toon alle producten
  mikkie-gumroad sales          Toon recente sales (7 dagen)
  mikkie-gumroad sales 30       Toon sales van laatste 30 dagen
  mikkie-gumroad stats          Dashboard met statistieken
  mikkie-gumroad bundle         Maak Complete Bundle aan
  mikkie-gumroad report         Sla dagrapport op in LOGS/
  mikkie-gumroad help           Toon dit menu
""")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "help"

    if cmd == "products":
        cmd_products()
    elif cmd == "sales":
        days = int(args[1]) if len(args) > 1 else 7
        cmd_sales(days)
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "bundle":
        cmd_create_bundle()
    elif cmd == "report":
        cmd_report()
    elif cmd in ("help", "--help", "-h"):
        print_help()
    else:
        print(f"❌ Onbekend commando: {cmd}")
        print_help()

if __name__ == "__main__":
    main()
