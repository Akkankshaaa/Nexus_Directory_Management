import sqlite3

def connect_db():
    conn = sqlite3.connect("data/contacts.db")  # stored in /data folder
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            birthday TEXT,
            category TEXT,
            favorite INTEGER DEFAULT 0,
            notes TEXT
        );
    """)

    conn.commit()
    conn.close()

connect_db()
