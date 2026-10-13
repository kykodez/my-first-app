"""Save headlines in a small SQLite file so history builds up over time.

Google News only returns recent headlines, so running the app regularly
keeps older news around for analysis.
"""

import sqlite3
from datetime import datetime

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    link TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT,
    published TEXT NOT NULL,
    score INTEGER
)
"""


def _connect(path=None):
    conn = sqlite3.connect(path or config.DB_PATH)
    conn.execute(SCHEMA)
    return conn


def save_events(events: list[dict], path=None) -> None:
    with _connect(path) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO events VALUES (?, ?, ?, ?, ?)",
            [(e["link"], e["title"], e.get("source", ""), e["published"].isoformat(), e.get("score"))
             for e in events],
        )


def load_events(path=None) -> list[dict]:
    with _connect(path) as conn:
        rows = conn.execute(
            "SELECT link, title, source, published, score FROM events ORDER BY published DESC"
        ).fetchall()
    return [
        {"link": r[0], "title": r[1], "source": r[2],
         "published": datetime.fromisoformat(r[3]), "score": r[4]}
        for r in rows
    ]
