#!/usr/bin/env python3

from datetime import date, timedelta

from database import (
    get_habits,
    get_month_completions,
    get_daily_note,
    get_focus_sessions,
)


# ============================================================
# DASHBOARD MANAGER
# ============================================================

class DashboardManager:

    def __init__(self):
        pass

    # ========================================================
    # HABIT STATISTICS
    # ========================================================

    def get_habit_statistics(self):

        habits = get_habits(
            active_only=True
        )

        if not habits:

            return {
                "total_habits": 0,
                "completed_today": 0,
                "today_percentage": 0,
                "month_percentage": 0,
            }

        today = date.today()

        completed_today = 0

        for habit in habits:

            completions = get_month_completions(
                today.year,
                today.month
            )

            for item in completions:

                if (
                    item["habit_id"]
                    == habit["id"]
                    and item["date"]
                    == today.isoformat()
                    and item["completed"]
                ):

                    completed_today += 1

                    break

        total_habits = len(habits)

        today_percentage = (
            completed_today
            / total_habits
        ) * 100

        days_in_month = (
            __import__("calendar")
            .monthrange(
                today.year,
                today.month
            )[1]
        )

        completions = get_month_completions(
            today.year,
            today.month
        )

        completed_count = sum(
            1
            for item in completions
            if item["completed"]
        )

        total_possible = (
            total_habits
            * days_in_month
        )

        month_percentage = (
            completed_count
            / total_possible
            * 100
        ) if total_possible else 0

        return {
            "total_habits": total_habits,
            "completed_today": completed_today,
            "today_percentage": round(
                today_percentage,
                1
            ),
            "month_percentage": round(
                month_percentage,
                1
            ),
        }

    # ========================================================
    # NOTE STATISTICS
    # ========================================================

    def get_note_statistics(self):

        today = date.today()

        note = get_daily_note(
            today
        )

        today_has_note = bool(
            note
            and note.get(
                "note",
                ""
            ).strip()
        )

        return {
            "today_has_note": today_has_note,
            "today_note": (
                note.get("note", "")
                if note
                else ""
            ),
        }

    # ========================================================
    # FOCUS STATISTICS
    # ========================================================

    def get_focus_statistics(self):

        sessions = get_focus_sessions()

        today = date.today()

        today_sessions = []

        for session in sessions:

            start_time = session.get(
                "start_time",
                ""
            )

            if start_time.startswith(
                today.isoformat()
            ):

                today_sessions.append(
                    session
                )

        total_minutes = sum(
            session.get(
                "duration_minutes",
                0
            )
            for session in today_sessions
        )

        return {
            "today_sessions": len(
                today_sessions
            ),
            "today_minutes": total_minutes,
            "total_sessions": len(
                sessions
            ),
        }

    # ========================================================
    # CURRENT STREAK
    # ========================================================

    def get_current_streak(self):

        habits = get_habits(
            active_only=True
        )

        if not habits:

            return 0

        streak = 0

        current_date = date.today()

        while True:

            all_completed = True

            completions = get_month_completions(
                current_date.year,
                current_date.month
            )

            completion_lookup = {}

            for item in completions:

                completion_lookup[
                    (
                        item["habit_id"],
                        item["date"]
                    )
                ] = bool(
                    item["completed"]
                )

            date_string = (
                current_date.isoformat()
            )

            for habit in habits:

                if not completion_lookup.get(
                    (
                        habit["id"],
                        date_string
                    ),
                    False
                ):

                    all_completed = False

                    break

            if not all_completed:

                break

            streak += 1

            current_date -= timedelta(
                days=1
            )

            if streak >= 3650:

                break

        return streak

    # ========================================================
    # TODAY SUMMARY
    # ========================================================

    def get_today_summary(self):

        habit_stats = (
            self.get_habit_statistics()
        )

        note_stats = (
            self.get_note_statistics()
        )

        focus_stats = (
            self.get_focus_statistics()
        )

        return {
            "date": date.today().isoformat(),

            "habits": habit_stats,

            "notes": note_stats,

            "focus": focus_stats,

            "streak": (
                self.get_current_streak()
            ),
        }

    # ========================================================
    # FULL DASHBOARD DATA
    # ========================================================

    def get_dashboard_data(self):

        today = date.today()

        return {
            "today": today.isoformat(),

            "month": {
                "year": today.year,
                "month": today.month,
            },

            "summary": (
                self.get_today_summary()
            ),

            "habits": get_habits(
                active_only=True
            ),

            "focus_sessions": (
                get_focus_sessions()
            ),
        }


# ============================================================
# SIMPLE FUNCTIONS
# ============================================================

_manager = DashboardManager()


def get_habit_statistics():

    return _manager.get_habit_statistics()


def get_note_statistics():

    return _manager.get_note_statistics()


def get_focus_statistics():

    return _manager.get_focus_statistics()


def get_current_streak():

    return _manager.get_current_streak()


def get_today_summary():

    return _manager.get_today_summary()


def get_dashboard_data():

    return _manager.get_dashboard_data()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("Dashboard module loaded successfully.")
    print()

    data = get_dashboard_data()

    print(
        "Today's summary:"
    )

    print(
        data["summary"]
    )