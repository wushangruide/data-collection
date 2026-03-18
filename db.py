"""
SQLite database for deduplication of seen postdoc jobs.
"""
import sqlite3
import hashlib
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id TEXT PRIMARY KEY,
            title TEXT,
            url TEXT,
            source TEXT,
            seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def job_id(title: str, url: str) -> str:
    return hashlib.md5(f"{title}|{url}".encode()).hexdigest()


def is_new(conn, title: str, url: str) -> bool:
    jid = job_id(title, url)
    row = conn.execute("SELECT id FROM seen_jobs WHERE id=?", (jid,)).fetchone()
    return row is None


def mark_seen(conn, title: str, url: str, source: str):
    jid = job_id(title, url)
    conn.execute(
        "INSERT OR IGNORE INTO seen_jobs(id, title, url, source) VALUES(?,?,?,?)",
        (jid, title, url, source)
    )
    conn.commit()
