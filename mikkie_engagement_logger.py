#!/usr/bin/env python3
"""
MIKKIE WORLD — 📊 Engagement Logger v1.0
════════════════════════════════════════════════════════════════
Logt social media engagement (likes, retweets, views, comments)
in een lokaal CSV bestand. Stuurt dagrapport via Telegram.
Geeft inzicht in welke karakters en thema's het beste werken.

GEBRUIK:
  python3 mikkie_engagement_logger.py log --platform x --post-id 123 --likes 42 --views 1200
  python3 mikkie_engagement_logger.py report          — dagrapport
  python3 mikkie_engagement_logger.py top             — top 10 beste posts
  python3 mikkie_engagement_logger.py stats           — statistieken per karakter
  python3 mikkie_engagement_logger.py export          — exporteer naar CSV
════════════════════════════════════════════════════════════════
"""

import os
import sys
import csv
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR    = Path.home() / "mikkieworld"
MIKKIE_ROOT = Path.home() / "MIKKIE_WORLD"
LOG_FILE    = BASE_DIR / "engagement_logger.log"
CSV_FILE    = BASE_DIR / "engagement_log.csv"
STATS_FILE  = BASE_DIR / "engagement_stats.json"

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("ENGAGE")

CSV_HEADERS = [
    "datum", "platform", "post_id", "karakter", "content_type",
    "thema", "likes", "retweets", "comments", "views", "saves",
    "engagement_rate", "post_tekst_preview", "bestand"
]

def init_csv():
    """Maak CSV aan als die nog niet bestaat."""
    if not CSV_FILE.exists():
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
        log.info(f"CSV aangemaakt: {CSV_FILE}")

def log_engagement(
    platform: str,
    post_id: str = "",
    karakter: str = "MIKKIE",
    content_type: str = "post",
    thema: str = "",
    likes: int = 0,
    retweets: int = 0,
    comments: int = 0,
    views: int = 0,
    saves: int = 0,
    post_tekst: str = "",
    bestand: str = ""
):
    """Log engagement data naar CSV."""
    init_csv()
    
    # Bereken engagement rate
    total_engagement = likes + retweets + comments + saves
    eng_rate = round((total_engagement / views * 100), 2) if views > 0 else 0
    
    row = {
        "datum": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "platform": platform,
        "post_id": post_id,
        "karakter": karakter.upper(),
        "content_type": content_type,
        "thema": thema,
        "likes": likes,
        "retweets": retweets,
        "comments": comments,
        "views": views,
        "saves": saves,
        "engagement_rate": eng_rate,
        "post_tekst_preview": post_tekst[:100].replace("\n", " "),
        "bestand": bestand
    }
    
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(row)
    
    log.info(f"Gelogd: {platform} | {karakter} | {likes} likes | {views} views | {eng_rate}% engagement")
    return row

def read_all_logs() -> list:
    """Lees alle engagement logs."""
    if not CSV_FILE.exists():
        return []
    
    rows = []
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Converteer getallen
            for field in ["likes", "retweets", "comments", "views", "saves"]:
                try:
                    row[field] = int(row[field])
                except:
                    row[field] = 0
            try:
                row["engagement_rate"] = float(row["engagement_rate"])
            except:
                row["engagement_rate"] = 0.0
            rows.append(row)
    return rows

def send_telegram(msg: str):
    """Stuur Telegram bericht."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        import urllib.request
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": msg}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

def cmd_report():
    """Genereer dagrapport."""
    logs = read_all_logs()
    if not logs:
        print("Nog geen engagement data.")
        return
    
    # Filter laatste 7 dagen
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = [r for r in logs if r["datum"][:10] >= week_ago]
    
    total_likes  = sum(r["likes"] for r in recent)
    total_views  = sum(r["views"] for r in recent)
    total_posts  = len(recent)
    avg_eng_rate = sum(r["engagement_rate"] for r in recent) / len(recent) if recent else 0
    
    # Beste karakter
    kar_likes = defaultdict(int)
    for r in recent:
        kar_likes[r["karakter"]] += r["likes"]
    beste_kar = max(kar_likes, key=kar_likes.get) if kar_likes else "N/A"
    
    report = f"""📊 MIKKIE WORLD — Weekrapport
{'─'*35}
Posts: {total_posts}
Views: {total_views:,}
Likes: {total_likes:,}
Gem. engagement: {avg_eng_rate:.1f}%
Beste karakter: {beste_kar} ⭐

Top post: {recent[-1]['post_tekst_preview'][:60] if recent else 'n.v.t.'}"""
    
    print(f"\n{report}\n")
    send_telegram(report)

def cmd_top(n: int = 10):
    """Toon top N posts op engagement rate."""
    logs = read_all_logs()
    if not logs:
        print("Nog geen engagement data.")
        return
    
    sorted_logs = sorted(logs, key=lambda x: x["engagement_rate"], reverse=True)
    
    print(f"\n  🏆 Top {n} posts (engagement rate)\n")
    print(f"  {'#':<4} {'Platform':<12} {'Karakter':<10} {'Likes':<8} {'Views':<10} {'Rate':<8} Preview")
    print(f"  {'─'*80}")
    
    for i, row in enumerate(sorted_logs[:n], 1):
        print(f"  {i:<4} {row['platform']:<12} {row['karakter']:<10} {row['likes']:<8} {row['views']:<10} {row['engagement_rate']:<8.1f}% {row['post_tekst_preview'][:30]}...")
    print()

def cmd_stats():
    """Statistieken per karakter en platform."""
    logs = read_all_logs()
    if not logs:
        print("Nog geen engagement data.")
        return
    
    # Per karakter
    kar_stats = defaultdict(lambda: {"posts": 0, "likes": 0, "views": 0, "eng_rates": []})
    for r in logs:
        k = r["karakter"]
        kar_stats[k]["posts"] += 1
        kar_stats[k]["likes"] += r["likes"]
        kar_stats[k]["views"] += r["views"]
        kar_stats[k]["eng_rates"].append(r["engagement_rate"])
    
    print(f"\n  📊 Statistieken per karakter\n")
    print(f"  {'Karakter':<12} {'Posts':<8} {'Likes':<10} {'Views':<12} {'Gem. Rate'}")
    print(f"  {'─'*55}")
    
    for karakter, stats in sorted(kar_stats.items()):
        avg_rate = sum(stats["eng_rates"]) / len(stats["eng_rates"]) if stats["eng_rates"] else 0
        print(f"  {karakter:<12} {stats['posts']:<8} {stats['likes']:<10} {stats['views']:<12} {avg_rate:.1f}%")
    
    # Per platform
    plat_stats = defaultdict(lambda: {"posts": 0, "likes": 0})
    for r in logs:
        p = r["platform"]
        plat_stats[p]["posts"] += 1
        plat_stats[p]["likes"] += r["likes"]
    
    print(f"\n  📱 Statistieken per platform\n")
    for platform, stats in sorted(plat_stats.items()):
        print(f"  {platform:<15} {stats['posts']} posts, {stats['likes']} likes")
    print()

def cmd_export():
    """Exporteer naar CSV in MIKKIE_WORLD/LOGS map."""
    if not CSV_FILE.exists():
        print("Geen data om te exporteren.")
        return
    
    export_dir = MIKKIE_ROOT / "LOGS"
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = export_dir / f"engagement_export_{timestamp}.csv"
    
    import shutil
    shutil.copy2(CSV_FILE, export_file)
    print(f"✅ Geëxporteerd naar: {export_file}")

def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return
    
    command = args[0]
    
    if command == "log":
        # Parse argumenten
        params = {}
        i = 1
        while i < len(args):
            if args[i].startswith("--") and i+1 < len(args):
                key = args[i][2:].replace("-", "_")
                val = args[i+1]
                # Converteer getallen
                if key in ("likes", "retweets", "comments", "views", "saves"):
                    try:
                        val = int(val)
                    except:
                        val = 0
                params[key] = val
                i += 2
            else:
                i += 1
        
        if "platform" not in params:
            print("❌ --platform is verplicht (x, instagram, pinterest, etc.)")
            return
        
        row = log_engagement(**params)
        print(f"✅ Gelogd: {row['platform']} | {row['karakter']} | {row['likes']} likes | {row['views']} views")
    
    elif command == "report":
        cmd_report()
    
    elif command == "top":
        n = int(args[1]) if len(args) > 1 else 10
        cmd_top(n)
    
    elif command == "stats":
        cmd_stats()
    
    elif command == "export":
        cmd_export()
    
    else:
        print(f"Onbekend commando: {command}")
        print("Gebruik: log | report | top | stats | export")

if __name__ == "__main__":
    main()
