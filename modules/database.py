import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_qr (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qr_id TEXT,
        owner_id TEXT,
        created_at TEXT,
        expiry TEXT,
        hash TEXT,
        file_path TEXT
    )
    """)

    conn.commit()
    conn.close()