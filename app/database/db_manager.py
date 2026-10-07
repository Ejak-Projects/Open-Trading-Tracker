import sqlite3
import os
from pathlib import Path

DB_DIR = Path.home() / ".local" / "share" / "OpenTradingTracker"
DB_PATH = DB_DIR / "tracker.db"

def init_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create base tables if not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            ticker TEXT NOT NULL,
            quantity TEXT NOT NULL,
            price TEXT NOT NULL,
            commission TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            date_out TEXT,
            price_out TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_investment TEXT NOT NULL,
            current_value TEXT NOT NULL,
            profit_loss TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    conn.commit()

    # --- v2.0 MIGRATIONS ---
    _run_migrations(cursor)
    
    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DB_PATH}")

def _run_migrations(cursor):
    """
    Safely adds new fields for v2.0 without altering existing data.
    """
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # v2.0 Fields
    if 'buy_taxes' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN buy_taxes TEXT DEFAULT '0.0'")
        print("[DB] Migration v2.0: Added 'buy_taxes' column.")
        
    if 'shares_sold' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN shares_sold TEXT DEFAULT '0.0'")
        print("[DB] Migration v2.0: Added 'shares_sold' column.")
        
    if 'sell_taxes' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN sell_taxes TEXT DEFAULT '0.0'")
        print("[DB] Migration v2.0: Added 'sell_taxes' column.")
        
    if 'sell_commissions' not in columns:
        cursor.execute("ALTER TABLE transactions ADD COLUMN sell_commissions TEXT DEFAULT '0.0'")
        print("[DB] Migration v2.0: Added 'sell_commissions' column.")
        
    cursor.execute("PRAGMA table_info(snapshots)")
    columns_snapshots = [col[1] for col in cursor.fetchall()]
    if 'portfolio_json' not in columns_snapshots:
        cursor.execute("ALTER TABLE snapshots ADD COLUMN portfolio_json TEXT DEFAULT '[]'")
        print("[DB] Migration v2.0: Added 'portfolio_json' column to snapshots.")
