"""
Database utilities — connection helpers for the SQLite database.
"""

import os
import sqlite3

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "campaign_reports.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection to the campaign reports database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
