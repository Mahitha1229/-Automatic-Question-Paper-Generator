import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "qpg.db"
COLS = ["id", "question", "topic", "marks", "true_bloom_level",
        "bloom_level", "bloom_confidence", "bloom_source",
        "qtype", "options", "answer", "image_path"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    bank TEXT NOT NULL,              -- 'sample' | 'upload' | 'topics'
    id TEXT NOT NULL,                -- Q001, Q002 ...
    question TEXT NOT NULL,
    topic TEXT DEFAULT 'General',
    marks INTEGER DEFAULT 5,
    true_bloom_level TEXT,           -- ground truth (analytics only)
    bloom_level TEXT,                -- cached LLM label
    bloom_confidence REAL,
    bloom_source TEXT,               -- 'llm'
    qtype TEXT DEFAULT 'short',      -- reserved for later (question types)
    options TEXT, answer TEXT, image_path TEXT,
    PRIMARY KEY (bank, id)
);
"""


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.executescript(SCHEMA)


def load_raw(bank):
    with _conn() as c:
        return pd.read_sql_query(
            f"SELECT {','.join(COLS)} FROM questions WHERE bank=? ORDER BY id",
            c, params=(bank,))


def save_raw(df, bank):
    d = df[COLS].copy()
    d["marks"] = d["marks"].astype(int)
    d = d.astype(object).where(d.notna(), None)
    with _conn() as c:
        c.execute("DELETE FROM questions WHERE bank=?", (bank,))
        c.executemany(
            f"INSERT INTO questions (bank,{','.join(COLS)}) "
            f"VALUES (?,{','.join('?' * len(COLS))})",
            [(bank, *row) for row in d.values.tolist()])