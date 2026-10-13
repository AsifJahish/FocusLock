
#!/usr/bin/env python3

from datetime import date
from database import get_connection


STATUSES = ("To Do", "In Progress", "Done")
PRIORITIES = ("Low", "Medium", "High")


def _date_string(task_date=None):
    if task_date is None:
        return date.today().isoformat()
    if isinstance(task_date, date):
        return task_date.isoformat()
    return date.fromisoformat(str(task_date)).isoformat()


def _ensure_todo_schema():
    """Create the To-Do table and safely migrate older versions."""
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS todo_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                task_date TEXT NOT NULL,
                start_time TEXT NOT NULL DEFAULT '09:00',
                end_time TEXT NOT NULL DEFAULT '10:00',
                priority TEXT NOT NULL DEFAULT 'Medium',
                notes TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'To Do'
            )
        """)

        columns = {
            row[1] for row in connection.execute(
                "PRAGMA table_info(todo_tasks)"
            ).fetchall()
        }

        if "status" not in columns:
            connection.execute("""
                ALTER TABLE todo_tasks
                ADD COLUMN status TEXT NOT NULL DEFAULT 'To Do'
            """)

        # Keep the new status consistent with previously completed tasks.
        connection.execute("""
            UPDATE todo_tasks
            SET status = 'Done'
            WHERE completed = 1
              AND status = 'To Do'
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_todo_tasks_date
            ON todo_tasks (task_date)
        """)

        connection.commit()

    finally:
        connection.close()


def add_task(
    title,
    task_date=None,
    priority="Medium",
    notes="",
    status="To Do",
):
    title = title.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    task_date = _date_string(task_date)

    if priority not in PRIORITIES:
        priority = "Medium"

    if status not in STATUSES:
        status = "To Do"

    connection = get_connection()

    try:
        cursor = connection.execute("""
            INSERT INTO todo_tasks (
                title, task_date, start_time, end_time,
                priority, notes, completed, status
            )
            VALUES (?, ?, '09:00', '10:00', ?, ?, ?, ?)
        """, (
            title,
            task_date,
            priority,
            notes.strip(),
            1 if status == "Done" else 0,
            status,
        ))

        connection.commit()
        return cursor.lastrowid

    finally:
        connection.close()


def get_tasks(task_date=None):
    task_date = _date_string(task_date)
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT *
            FROM todo_tasks
            WHERE task_date = ?
            ORDER BY
                CASE status
                    WHEN 'In Progress' THEN 1
                    WHEN 'To Do' THEN 2
                    WHEN 'Done' THEN 3
                    ELSE 4
                END,
                CASE priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    WHEN 'Low' THEN 3
                    ELSE 4
                END,
                id DESC
        """, (task_date,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_all_tasks():
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT *
            FROM todo_tasks
            ORDER BY task_date, id DESC
        """).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def update_task(
    task_id,
    title,
    task_date,
    priority="Medium",
    notes="",
    status="To Do",
):
    title = title.strip()

    if not title:
        raise ValueError("Task title cannot be empty.")

    task_date = _date_string(task_date)

    if priority not in PRIORITIES:
        priority = "Medium"

    if status not in STATUSES:
        status = "To Do"

    connection = get_connection()

    try:
        connection.execute("""
            UPDATE todo_tasks
            SET title = ?,
                task_date = ?,
                priority = ?,
                notes = ?,
                status = ?,
                completed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            title,
            task_date,
            priority,
            notes.strip(),
            status,
            1 if status == "Done" else 0,
            task_id,
        ))

        connection.commit()

    finally:
        connection.close()


def set_task_status(task_id, status):
    if status not in STATUSES:
        raise ValueError("Invalid task status.")

    connection = get_connection()

    try:
        connection.execute("""
            UPDATE todo_tasks
            SET status = ?,
                completed = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            status,
            1 if status == "Done" else 0,
            task_id,
        ))

        connection.commit()

    finally:
        connection.close()


def set_task_completed(task_id, completed):
    """Compatibility helper for any older checkbox code."""
    set_task_status(task_id, "Done" if completed else "To Do")


def delete_task(task_id):
    connection = get_connection()

    try:
        connection.execute(
            "DELETE FROM todo_tasks WHERE id = ?",
            (task_id,),
        )
        connection.commit()

    finally:
        connection.close()


def get_task_summary(task_date=None):
    tasks = get_tasks(task_date)

    total = len(tasks)
    completed = sum(1 for task in tasks if task["status"] == "Done")
    in_progress = sum(
        1 for task in tasks if task["status"] == "In Progress"
    )
    remaining = total - completed
    percentage = round(completed / total * 100) if total else 0

    return {
        "total": total,
        "remaining": remaining,
        "completed": completed,
        "in_progress": in_progress,
        "percentage": percentage,
    }


# Ensure the table and status migration are ready when this module loads.
_ensure_todo_schema()
