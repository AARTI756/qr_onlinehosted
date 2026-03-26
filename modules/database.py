import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # QR TABLE (UPDATED)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_qr (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE,
        data TEXT,
        owner_id INTEGER,
        created_at TEXT,
        expiry TEXT,
        status TEXT DEFAULT 'active',

        -- future modules (already prepared)
        is_protected INTEGER DEFAULT 0,
        password_hash TEXT,
        is_one_time INTEGER DEFAULT 0,
        is_used INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()