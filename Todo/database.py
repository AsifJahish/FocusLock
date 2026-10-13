#!/usr/bin/env python3

import sqlite3
from pathlib import Path
from datetime import datetime, date


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_FILE = DATA_DIR / "social_lock.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # HABITS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_date TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # --------------------------------------------------------
    # HABIT COMPLETION BY DAY
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habit_days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            habit_id INTEGER NOT NULL,

            date TEXT NOT NULL,

            completed INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (habit_id)
                REFERENCES habits(id)
                ON DELETE CASCADE,

            UNIQUE(habit_id, date)
        )
    """)

    # --------------------------------------------------------
    # DAILY NOTES
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            date TEXT NOT NULL UNIQUE,

            note TEXT NOT NULL DEFAULT '',

            mood TEXT DEFAULT '',

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # FOCUS SESSIONS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            start_time TEXT NOT NULL,

            end_time TEXT,

            websites TEXT NOT NULL,

            duration_minutes INTEGER NOT NULL
        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# HABITS
# ============================================================

def add_habit(name):

    name = name.strip()

    if not name:
        return None

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO habits (
            name,
            created_date,
            active
        )
        VALUES (?, ?, 1)
    """, (
        name,
        date.today().isoformat()
    ))

    habit_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return habit_id


def get_habits(active_only=True):

    connection = get_connection()

    cursor = connection.cursor()

    if active_only:

        cursor.execute("""
            SELECT
                id,
                name,
                created_date,
                active
            FROM habits
            WHERE active = 1
            ORDER BY id ASC
        """)

    else:

        cursor.execute("""
            SELECT
                id,
                name,
                created_date,
                active
            FROM habits
            ORDER BY id ASC
        """)

    habits = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return habits


def delete_habit(habit_id):

    connection = get_connection()

    connection.execute("""
        DELETE FROM habits
        WHERE id = ?
    """, (habit_id,))

    connection.commit()

    connection.close()


def deactivate_habit(habit_id):

    connection = get_connection()

    connection.execute("""
        UPDATE habits
        SET active = 0
        WHERE id = ?
    """, (habit_id,))

    connection.commit()

    connection.close()


# ============================================================
# HABIT COMPLETION
# ============================================================

def set_habit_completion(
    habit_id,
    completion_date,
    completed
):

    if isinstance(completion_date, date):

        completion_date = completion_date.isoformat()

    completed = 1 if completed else 0

    connection = get_connection()

    connection.execute("""
        INSERT INTO habit_days (
            habit_id,
            date,
            completed
        )
        VALUES (?, ?, ?)

        ON CONFLICT(habit_id, date)
        DO UPDATE SET
            completed = excluded.completed
    """, (
        habit_id,
        completion_date,
        completed
    ))

    connection.commit()

    connection.close()


def is_habit_completed(
    habit_id,
    completion_date
):

    if isinstance(completion_date, date):

        completion_date = completion_date.isoformat()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT completed
        FROM habit_days
        WHERE habit_id = ?
        AND date = ?
    """, (
        habit_id,
        completion_date
    ))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return False

    return bool(row["completed"])

def update_habit(habit_id, name):
    """Update the name of an active habit."""
    name = name.strip()

    if not name:
        raise ValueError("Habit name cannot be empty.")

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE habits
            SET name = ?
            WHERE id = ? AND active = 1
            """,
            (name, habit_id)
        )

        connection.commit()
        return cursor.rowcount > 0

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_month_completions(
    year,
    month
):

    start_date = date(
        year,
        month,
        1
    )

    if month == 12:

        end_date = date(
            year + 1,
            1,
            1
        )

    else:

        end_date = date(
            year,
            month + 1,
            1
        )

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            habit_id,
            date,
            completed
        FROM habit_days
        WHERE date >= ?
        AND date < ?
        ORDER BY date ASC
    """, (
        start_date.isoformat(),
        end_date.isoformat()
    ))

    results = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return results


# ============================================================
# DAILY NOTES
# ============================================================

def save_daily_note(
    note_date,
    note,
    mood=""
):

    if isinstance(note_date, date):

        note_date = note_date.isoformat()

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    connection = get_connection()

    connection.execute("""
        INSERT INTO daily_notes (
            date,
            note,
            mood,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(date)
        DO UPDATE SET
            note = excluded.note,
            mood = excluded.mood,
            updated_at = excluded.updated_at
    """, (
        note_date,
        note,
        mood,
        now,
        now
    ))

    connection.commit()

    connection.close()


def get_daily_note(note_date):

    if isinstance(note_date, date):

        note_date = note_date.isoformat()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            date,
            note,
            mood,
            created_at,
            updated_at
        FROM daily_notes
        WHERE date = ?
    """, (note_date,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


# ============================================================
# FOCUS SESSIONS
# ============================================================

def save_focus_session(
    start_time,
    end_time,
    websites,
    duration_minutes
):

    if isinstance(start_time, datetime):

        start_time = start_time.isoformat(
            timespec="seconds"
        )

    if isinstance(end_time, datetime):

        end_time = end_time.isoformat(
            timespec="seconds"
        )

    if isinstance(websites, list):

        websites = ",".join(websites)

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO focus_sessions (
            start_time,
            end_time,
            websites,
            duration_minutes
        )
        VALUES (?, ?, ?, ?)
    """, (
        start_time,
        end_time,
        websites,
        duration_minutes
    ))

    session_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return session_id


def get_focus_sessions():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            start_time,
            end_time,
            websites,
            duration_minutes
        FROM focus_sessions
        ORDER BY start_time DESC
    """)

    sessions = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return sessions


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("Database initialized successfully.")

    print(
        f"Database location: {DATABASE_FILE}"
    )

    print(
        f"Habits: {len(get_habits(active_only=False))}"
    )

    print(
        f"Focus sessions: {len(get_focus_sessions())}"
    )