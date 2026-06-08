#!/usr/bin/env python3
"""MIKKIE WORLD Master Dashboard"""
import os, sys, json, urllib.request, urllib.error, base64
from datetime import datetime

MAILCHIMP_KEY    = os.environ.get('MAILCHIMP_API_KEY', '')
MAILCHIMP_SERVER = os.environ.get('MAILCHIMP_SERVER', 'us14')
MAILCHIMP_LIST   = '75412e3953'
GUMROAD_TOKEN    = os.environ.get('GUMROAD_API_TOKEN', '')
LAUNCH_DATE      = datetime(2026, 7, 7, 7, 7)

def days_to_launch():
    delta = LAUNCH_DATE - datetime.now()
    return delta.days

def mc_req(endpoint):
    url = f"https://{MAILCHIMP_SERVER}.api.mailchimp.com/3.0{endpoint}"
    creds = base64.b64encode(f'anystring:{MAILCHIMP_KEY}'.encode()).decode()
    req = urllib.request.Request(url, headers={'Authorization': f'Basic {creds}'})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except:
        return {}

def gr_req(endpoint):
    url = f"https://api.gumroad.com/v2{endpoint}"
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {GUMROAD_TOKEN}'})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except:
        return {}

def bar(value, max_val, width=20, char='█'):
    filled = int((value / max(max_val, 1)) * width)
    return char * filled + '░' * (width - filled)

def print_dashboard():
    days = days_to_launch()
    now = datetime.now().strftime('%d/%m/%Y %H:%M')

    print()
    print('╔══════════════════════════════════════════════════════════╗')
    print('║           MIKKIE WORLD — MISSION CONTROL                ║')
    print(f'║  {now:<20}  Launch: 7/7/2026 07:07              ║')
    print('╚══════════════════════════════════════════════════════════╝')

    # Countdown
    hours = (LAUNCH_DATE - datetime.now()).seconds // 3600
    print(f'\n  🚀 COUNTDOWN: {days} dagen, {hours} uur te gaan')
    progress = max(0, 29 - days)
    print(f'  [{bar(progress, 29)}] {int(progress/29*100)}% naar launch')

    # Mailchimp
    print('\n  📧 MAILCHIMP')
    list_data = mc_req(f'/lists/{MAILCHIMP_LIST}')
    subs = list_data.get('stats', {}).get('member_count', 0)
    campaigns = mc_req('/campaigns?count=5&sort_field=create_time&sort_dir=DESC')
    camp_list = campaigns.get('campaigns', [])
    print(f'  Subscribers: {subs}  {bar(subs, 1000, 15)} (doel: 1000)')
    print(f'  Campaigns:   {len(camp_list)} recent')
    for c in camp_list[:3]:
        status = c.get('status', '')
        title = c.get('settings', {}).get('title', '')[:35]
        print(f'    • {status:<10} {title}')

    # Gumroad
    print('\n  💰 GUMROAD')
    products = gr_req('/products')
    prod_list = products.get('products', [])
    total_sales = 0
    total_revenue = 0.0
    for p in prod_list:
        sales = p.get('sales_count', 0)
        price = p.get('price', 0) / 100
        revenue = sales * price
        total_sales += sales
        total_revenue += revenue
        name = p.get('name', '')[:35]
        print(f'  {name:<35} €{price:.2f}  {sales} sales  €{revenue:.2f}')
    print(f'  {"TOTAAL":<35}        {total_sales} sales  €{total_revenue:.2f}')
    print(f'  Doel €10.000: [{bar(total_revenue, 10000, 15)}] {total_revenue/10000*100:.1f}%')

    # Action items
    print('\n  ✅ VANDAAG DOEN')
    if subs < 100:
        print('  → mikkie-tweet mission       (gratis bereik)')
        print('  → mikkie-quest-pdf           (leadmagnet aanmaken)')
    if total_sales == 0:
        print('  → mikkie-gumroad update      (beschrijving verbeteren)')
        print('  → mikkie-launch build        (email sequence bouwen)')
    if days <= 7:
        print('  → mikkie-launch send 0       (LAUNCH EMAIL VERSTUREN!)')

    print('\n  📋 ALLE COMMANDO\'S')
    print('  mikkie-email     → Mailchimp campaigns')
    print('  mikkie-gumroad   → Gumroad producten & sales')
    print('  mikkie-tweet     → Twitter/X posts')
    print('  mikkie-launch    → Pre-launch email sequence')
    print('  mikkie-quest-pdf → Gratis PDF leadmagnet')
    print('  mikkie           → Dit dashboard')
    print()

print_dashboard()
