import sqlite3
from modules.db_config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_qr (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    qr_id TEXT UNIQUE,
    encrypted_data TEXT,
    payload_hash TEXT,
    created_at TEXT,
    expiry TEXT
);
    """)

    conn.commit()
    conn.close()