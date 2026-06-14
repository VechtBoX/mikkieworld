#!/usr/bin/env python3
import argparse
import sqlite3
import hashlib
import getpass
import json
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from ayrshare import SocialPost

console = Console()
DB_FILE = "smm.db"
SESSION_FILE = ".smm_session"
CONFIG_FILE = ".smm_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, bio TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user_id INTEGER, content TEXT, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, platforms TEXT, media TEXT);
    ''')
    conn.commit()
    conn.close()

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def save_session(uid, uname):
    with open(SESSION_FILE, "w") as f:
        json.dump({"user_id": uid, "username": uname}, f)

def load_session():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE) as f:
                return json.load(f)
        except:
            return None
    return None

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# ====================== COMMANDS ======================
def setup_ayrshare(args):
    config = load_config()
    key = getpass.getpass("Ayrshare API Key: ")
    config["ayrshare_key"] = key
    save_config(config)
    rprint("[green]✅ Ayrshare key opgeslagen![/green]")

def register(args):
    init_db()
    pw = getpass.getpass("Wachtwoord: ")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, bio) VALUES (?,?,?)", 
                  (args.username, hash_password(pw), args.bio or ""))
        conn.commit()
        rprint(f"[green]✅ Account '{args.username}' aangemaakt![/green]")
    except:
        rprint("[red]❌ Gebruikersnaam bestaat al![/red]")
    conn.close()

def login(args):
    init_db()
    pw = getpass.getpass("Wachtwoord: ")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE username=? AND password_hash=?", 
              (args.username, hash_password(pw)))
    user = c.fetchone()
    conn.close()
    if user:
        save_session(user[0], user[1])
        rprint(f"[green]✅ Ingelogd als {user[1]}[/green]")
    else:
        rprint("[red]❌ Verkeerd wachtwoord[/red]")

def logout(args):
    clear_session()
    rprint("[yellow]👋 Uitgelogd[/yellow]")

def post(args):
    session = load_session()
    if not session:
        rprint("[red]❌ Log eerst in met: ./smm.py login hendrik[/red]")
        return

    config = load_config()
    if not config.get("ayrshare_key"):
        rprint("[red]❌ Geen Ayrshare key. Doe eerst: ./smm.py setup-ayrshare[/red]")
        return

    client = SocialPost(config["ayrshare_key"])

    media = []
    if args.image: media.append({"type": "image", "url": args.image})
    if args.video: media.append({"type": "video", "url": args.video})
    if args.pdf:   media.append({"type": "document", "url": args.pdf})

    platforms = [p.strip() for p in args.platforms.split(",")] if args.platforms else ["twitter","instagram","linkedin"]

    try:
        result = client.post({
            "post": args.text,
            "platforms": platforms,
            "media": media if media else None
        })
        rprint(f"[green]✅ Gepost naar {', '.join(platforms)} ![/green]")
        rprint(f"   Ayrshare ID: {result.get('id', 'onbekend')}")
    except Exception as e:
        rprint(f"[red]❌ Fout: {e}[/red]")

def feed(args):
    session = load_session()
    if not session:
        rprint("[red]❌ Log eerst in[/red]")
        return
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, content, timestamp, platforms FROM posts ORDER BY timestamp DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    if not rows:
        rprint("[dim]Nog geen posts.[/dim]")
        return
    table = Table(title="📡 Jouw MIKKIE WORLD Posts", title_style="bold cyan")
    table.add_column("ID", style="cyan")
    table.add_column("Content", style="white", width=70)
    table.add_column("Platforms", style="magenta")
    table.add_column("Tijd", style="dim")
    for r in rows:
        table.add_row(str(r[0]), r[1][:80]+"..." if len(r[1])>80 else r[1], r[3] or "-", r[2][:16])
    console.print(table)

def main():
    init_db()
    parser = argparse.ArgumentParser(description="🚀 MIKKIE WORLD Central Social Poster")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup-ayrshare").set_defaults(func=setup_ayrshare)
    reg = sub.add_parser("register")
    reg.add_argument("username")
    reg.add_argument("--bio", default="")
    reg.set_defaults(func=register)
    log = sub.add_parser("login")
    log.add_argument("username")
    log.set_defaults(func=login)
    sub.add_parser("logout").set_defaults(func=logout)

    p = sub.add_parser("post")
    p.add_argument("text")
    p.add_argument("--image", help="URL foto")
    p.add_argument("--video", help="URL video")
    p.add_argument("--pdf", help="URL PDF")
    p.add_argument("--platforms", default="twitter,instagram,linkedin", help="comma gescheiden")
    p.set_defaults(func=post)

    sub.add_parser("feed").set_defaults(func=feed)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
