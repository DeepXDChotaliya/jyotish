"""
Persistence. SQLite with full-text search over reading notes.

The point of this layer: charts are recomputable from birth data, so the only
thing worth storing is birth data plus what you observed. FTS on notes lets you
ask "every reading where I mentioned Sade Sati and the client was in Saturn
mahadasha" across years of consultations.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".jyotish" / "practice.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    year INTEGER, month INTEGER, day INTEGER,
    hour INTEGER, minute INTEGER, second INTEGER DEFAULT 0,
    latitude REAL, longitude REAL,
    place TEXT, tz_name TEXT,
    ayanamsa TEXT DEFAULT 'Lahiri',
    birth_time_accuracy TEXT DEFAULT 'stated',
    created_at TEXT,
    tags TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    session_date TEXT,
    dasha_context TEXT,
    transit_context TEXT,
    body TEXT,
    created_at TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS readings_fts USING fts5(
    body, dasha_context, transit_context,
    content='readings', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS readings_ai AFTER INSERT ON readings BEGIN
    INSERT INTO readings_fts(rowid, body, dasha_context, transit_context)
    VALUES (new.id, new.body, new.dasha_context, new.transit_context);
END;

CREATE TRIGGER IF NOT EXISTS readings_ad AFTER DELETE ON readings BEGIN
    INSERT INTO readings_fts(readings_fts, rowid, body, dasha_context, transit_context)
    VALUES ('delete', old.id, old.body, old.dasha_context, old.transit_context);
END;

CREATE TRIGGER IF NOT EXISTS readings_au AFTER UPDATE ON readings BEGIN
    INSERT INTO readings_fts(readings_fts, rowid, body, dasha_context, transit_context)
    VALUES ('delete', old.id, old.body, old.dasha_context, old.transit_context);
    INSERT INTO readings_fts(rowid, body, dasha_context, transit_context)
    VALUES (new.id, new.body, new.dasha_context, new.transit_context);
END;
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn


def save_client(conn, birth, accuracy="stated", tags="") -> int:
    cur = conn.execute(
        """INSERT INTO clients
           (name, year, month, day, hour, minute, second, latitude, longitude,
            place, tz_name, ayanamsa, birth_time_accuracy, created_at, tags)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (birth.name, birth.year, birth.month, birth.day, birth.hour,
         birth.minute, birth.second, birth.latitude, birth.longitude,
         birth.place, birth.tz_name, birth.ayanamsa, accuracy,
         datetime.now().isoformat(), tags),
    )
    conn.commit()
    return cur.lastrowid


def load_client(conn, client_id: int):
    from .engine import BirthData
    r = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    if not r:
        return None
    return BirthData(
        name=r["name"], year=r["year"], month=r["month"], day=r["day"],
        hour=r["hour"], minute=r["minute"], second=r["second"],
        latitude=r["latitude"], longitude=r["longitude"], place=r["place"],
        tz_name=r["tz_name"], ayanamsa=r["ayanamsa"],
    )


def list_clients(conn):
    return conn.execute(
        "SELECT id, name, place, year, month, day, tags FROM clients ORDER BY name"
    ).fetchall()


def save_reading(conn, client_id, body, dasha_context="",
                 transit_context="", session_date=None) -> int:
    cur = conn.execute(
        """INSERT INTO readings
           (client_id, session_date, dasha_context, transit_context, body, created_at)
           VALUES (?,?,?,?,?,?)""",
        (client_id, session_date or datetime.now().date().isoformat(),
         dasha_context, transit_context, body, datetime.now().isoformat()),
    )
    conn.commit()
    return cur.lastrowid


def readings_for(conn, client_id):
    return conn.execute(
        "SELECT * FROM readings WHERE client_id = ? ORDER BY session_date DESC",
        (client_id,),
    ).fetchall()


def search_readings(conn, query: str):
    """FTS5 query across every reading you have ever written."""
    return conn.execute(
        """SELECT r.*, c.name AS client_name
           FROM readings_fts f
           JOIN readings r ON r.id = f.rowid
           JOIN clients c ON c.id = r.client_id
           WHERE readings_fts MATCH ?
           ORDER BY rank""",
        (query,),
    ).fetchall()
