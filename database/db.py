"""
database/db.py — SQLite database operations
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "localhero.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db():
    """Create the issues table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp        TEXT NOT NULL,
            issue_description TEXT NOT NULL,
            category         TEXT,
            severity         TEXT,
            authority        TEXT,
            suggested_action TEXT,
            source_type      TEXT DEFAULT 'text',
            image_path       TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_issue(
    issue_description: str,
    category: str,
    severity: str,
    authority: str,
    suggested_action: str,
    source_type: str = "text",
    image_path: str = "",
) -> int:
    """Insert a new issue record and return its id."""
    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO issues
            (timestamp, issue_description, category, severity, authority,
             suggested_action, source_type, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        issue_description,
        category,
        severity,
        authority,
        suggested_action,
        source_type,
        image_path,
    ))
    conn.commit()
    issue_id = cursor.lastrowid
    conn.close()
    return issue_id


def get_all_issues() -> list[dict]:
    """Return all issues as a list of dicts, newest first."""
    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM issues ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_stats() -> dict:
    """Return aggregate statistics for the dashboard."""
    initialize_db()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM issues")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM issues WHERE severity IN ('High', 'Critical')"
    )
    high_priority = cursor.fetchone()[0]

    cursor.execute("""
        SELECT category, COUNT(*) as cnt
        FROM issues
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY cnt DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    most_common = row[0] if row else "N/A"

    cursor.execute("""
        SELECT category, COUNT(*) as cnt
        FROM issues
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY cnt DESC
    """)
    category_dist = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("""
        SELECT severity, COUNT(*) as cnt
        FROM issues
        WHERE severity IS NOT NULL
        GROUP BY severity
    """)
    severity_dist = {r[0]: r[1] for r in cursor.fetchall()}

    conn.close()
    return {
        "total": total,
        "high_priority": high_priority,
        "most_common": most_common,
        "category_dist": category_dist,
        "severity_dist": severity_dist,
    }
