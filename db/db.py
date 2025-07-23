# db.py

import sqlite3


def init_db():
    conn = sqlite3.connect("generations.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            company TEXT,
            job_offer TEXT,
            language TEXT,
            country TEXT,
            city TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_generation(company, job_offer, language, country, city):
    conn = sqlite3.connect("generations.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO generations (timestamp, company, job_offer, language, country, city)
        VALUES (datetime('now'), ?, ?, ?, ?, ?)
    """, (company, job_offer, language, country, city))
    conn.commit()
    conn.close()
