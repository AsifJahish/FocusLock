# #!/usr/bin/env python3

# import calendar
# from datetime import date

# from database import (
#     add_habit,
#     get_habits,
#     delete_habit,
#     deactivate_habit,
#     set_habit_completion,
#     is_habit_completed,
#     get_month_completions,
# )


# # ============================================================
# # HABIT MANAGER
# # ============================================================

# class HabitManager:

#     def __init__(self):
#         pass

#     # ========================================================
#     # CREATE HABIT
#     # ========================================================

#     def create_habit(self, name):

#         name = name.strip()

#         if not name:
#             return None

#         return add_habit(name)

#     # ========================================================
#     # GET HABITS
#     # ========================================================

#     def get_active_habits(self):

#         return get_habits(active_only=True)

#     def get_all_habits(self):

#         return get_habits(active_only=False)

#     # ========================================================
#     # DELETE HABIT
#     # ========================================================

#     def delete_habit(self, habit_id):

#         delete_habit(habit_id)

#     # ========================================================
#     # DEACTIVATE HABIT
#     # ========================================================

#     def deactivate_habit(self, habit_id):

#         deactivate_habit(habit_id)

#     # ========================================================
#     # SET COMPLETION
#     # ========================================================

#     def set_completion(
#         self,
#         habit_id,
#         completion_date,
#         completed=True
#     ):

#         if isinstance(completion_date, date):

#             completion_date = (
#                 completion_date.isoformat()
#             )

#         set_habit_completion(
#             habit_id,
#             completion_date,
#             completed
#         )

#     # ========================================================
#     # TOGGLE COMPLETION
#     # ========================================================

#     def toggle_completion(
#         self,
#         habit_id,
#         completion_date
#     ):

#         current = is_habit_completed(
#             habit_id,
#             completion_date
#         )

#         new_value = not current

#         self.set_completion(
#             habit_id,
#             completion_date,
#             new_value
#         )

#         return new_value

#     # ========================================================
#     # CHECK COMPLETION
#     # ========================================================

#     # def is_completed(
#     #     self,
#     #     habit_id,
#     #     completion_date
#     # ):

#     #     return is_habit_completed(
#     #         habit_id,
#     #         completion_date
#     #     )
#     def is_completed(
#         self,
#         habit_id,
#         completion_date
#     ):
#         return is_habit_completed(
#             habit_id,
#             completion_date
#         )
#     # ========================================================
#     # MONTH DATA
#     # ========================================================

#     def get_month_data(
#         self,
#         year,
#         month
#     ):

#         return get_month_completions(
#             year,
#             month
#         )

#     # ========================================================
#     # MONTH MATRIX
#     # ========================================================

#     def get_month_matrix(
#         self,
#         year,
#         month
#     ):

#         habits = self.get_active_habits()

#         days_in_month = calendar.monthrange(
#             year,
#             month
#         )[1]

#         completions = self.get_month_data(
#             year,
#             month
#         )

#         completion_lookup = {}

#         for item in completions:

#             key = (
#                 item["habit_id"],
#                 item["date"]
#             )

#             completion_lookup[key] = bool(
#                 item["completed"]
#             )

#         matrix = []

#         for habit in habits:

#             row = {
#                 "id": habit["id"],
#                 "name": habit["name"],
#                 "days": {}
#             }

#             for day_number in range(
#                 1,
#                 days_in_month + 1
#             ):

#                 current_date = date(
#                     year,
#                     month,
#                     day_number
#                 )

#                 date_string = (
#                     current_date.isoformat()
#                 )

#                 row["days"][day_number] = (
#                     completion_lookup.get(
#                         (
#                             habit["id"],
#                             date_string
#                         ),
#                         False
#                     )
#                 )

#             matrix.append(row)

#         return matrix

#     # ========================================================
#     # COMPLETION PERCENTAGE
#     # ========================================================

#     def get_month_percentage(
#         self,
#         year,
#         month
#     ):

#         habits = self.get_active_habits()

#         if not habits:

#             return 0

#         days_in_month = calendar.monthrange(
#             year,
#             month
#         )[1]

#         total_possible = (
#             len(habits)
#             * days_in_month
#         )

#         if total_possible == 0:

#             return 0

#         completions = self.get_month_data(
#             year,
#             month
#         )

#         completed_count = sum(
#             1
#             for item in completions
#             if item["completed"]
#         )

#         percentage = (
#             completed_count
#             / total_possible
#         ) * 100

#         return round(
#             percentage,
#             1
#         )

#     # ========================================================
#     # TODAY'S PROGRESS
#     # ========================================================

#     def get_today_progress(self):

#         today = date.today()

#         habits = self.get_active_habits()

#         if not habits:

#             return {
#                 "completed": 0,
#                 "total": 0,
#                 "percentage": 0
#             }

#         completed = 0

#         for habit in habits:

#             if self.is_completed(
#                 habit["id"],
#                 today
#             ):

#                 completed += 1

#         total = len(habits)

#         percentage = (
#             completed / total
#         ) * 100

#         return {
#             "completed": completed,
#             "total": total,
#             "percentage": round(
#                 percentage,
#                 1
#             )
#         }

#     # ========================================================
#     # CURRENT STREAK
#     # ========================================================

#     def get_current_streak(
#         self,
#         habit_id
#     ):

#         streak = 0

#         current_date = date.today()

#         while True:

#             completed = self.is_completed(
#                 habit_id,
#                 current_date
#             )

#             if not completed:

#                 break

#             streak += 1

#             current_date = (
#                 current_date
#                 - __import__("datetime").timedelta(
#                     days=1
#                 )
#             )

#         return streak

#     # ========================================================
#     # LONGEST STREAK
#     # ========================================================

#     def get_longest_streak(
#         self,
#         habit_id
#     ):

#         all_completions = []

#         today = date.today()

#         # Look back through the available
#         # habit history.
#         current_date = today

#         for _ in range(3650):

#             if self.is_completed(
#                 habit_id,
#                 current_date
#             ):

#                 all_completions.append(
#                     current_date
#                 )

#             current_date = (
#                 current_date
#                 - __import__("datetime").timedelta(
#                     days=1
#                 )
#             )

#         if not all_completions:

#             return 0

#         all_completions.sort()

#         longest = 1
#         current_streak = 1

#         for index in range(
#             1,
#             len(all_completions)
#         ):

#             difference = (
#                 all_completions[index]
#                 - all_completions[index - 1]
#             ).days

#             if difference == 1:

#                 current_streak += 1

#             else:

#                 current_streak = 1

#             longest = max(
#                 longest,
#                 current_streak
#             )

#         return longest


# # ============================================================
# # SIMPLE FUNCTIONS
# # ============================================================

# _manager = HabitManager()


# def create_habit(name):

#     return _manager.create_habit(name)


# def get_active_habits():

#     return _manager.get_active_habits()


# def get_all_habits():

#     return _manager.get_all_habits()


# def delete_habit(habit_id):

#     return _manager.delete_habit(
#         habit_id
#     )


# def deactivate_habit(habit_id):

#     return _manager.deactivate_habit(
#         habit_id
#     )


# def set_completion(
#     habit_id,
#     completion_date,
#     completed=True
# ):

#     return _manager.set_completion(
#         habit_id,
#         completion_date,
#         completed
#     )


# def toggle_completion(
#     habit_id,
#     completion_date
# ):

#     return _manager.toggle_completion(
#         habit_id,
#         completion_date
#     )


# def is_completed(
#     habit_id,
#     completion_date
# ):

#     return _manager.is_completed(
#         habit_id,
#         completion_date
#     )


# def get_month_matrix(
#     year,
#     month
# ):

#     return _manager.get_month_matrix(
#         year,
#         month
#     )


# def get_month_percentage(
#     year,
#     month
# ):

#     return _manager.get_month_percentage(
#         year,
#         month
#     )


# def get_today_progress():

#     return _manager.get_today_progress()


# def get_current_streak(
#     habit_id
# ):

#     return _manager.get_current_streak(
#         habit_id
#     )


# def get_longest_streak(
#     habit_id
# ):

#     return _manager.get_longest_streak(
#         habit_id
#     )


# # ============================================================
# # TEST
# # ============================================================

# if __name__ == "__main__":

#     print("Habit module loaded successfully.")
#     print()

#     habits = get_active_habits()

#     print(
#         f"Active habits: {len(habits)}"
#     )

#     progress = get_today_progress()

#     print(
#         f"Today's progress: "
#         f"{progress['completed']}/"
#         f"{progress['total']} "
#         f"({progress['percentage']}%)"
#     )



#!/usr/bin/env python3

import calendar
from datetime import date, timedelta

from database import (
    add_habit,
    get_habits,
    delete_habit as delete_habit_record,
    deactivate_habit as deactivate_habit_record,
    set_habit_completion,
    is_habit_completed,
    get_month_completions,
    update_habit as update_habit_record,
)


# ============================================================
# HABIT MANAGER
# ============================================================

class HabitManager:

    def __init__(self):
        pass

    # ========================================================
    # CREATE HABIT
    # ========================================================

    def create_habit(self, name):
        if not isinstance(name, str):
            raise ValueError("Habit name must be text.")

        name = name.strip()

        if not name:
            return None

        return add_habit(name)

    # ========================================================
    # UPDATE HABIT
    # ========================================================

    def update_habit(self, habit_id, name):
        if not isinstance(name, str):
            raise ValueError("Habit name must be text.")

        name = name.strip()

        if not name:
            raise ValueError("Habit name cannot be empty.")

        return update_habit_record(habit_id, name)

    # ========================================================
    # GET HABITS
    # ========================================================

    def get_active_habits(self):
        return get_habits(active_only=True)

    def get_all_habits(self):
        return get_habits(active_only=False)

    # ========================================================
    # DELETE HABIT
    # ========================================================

    def delete_habit(self, habit_id):
        return delete_habit_record(habit_id)

    # ========================================================
    # DEACTIVATE HABIT
    # ========================================================

    def deactivate_habit(self, habit_id):
        return deactivate_habit_record(habit_id)

    # ========================================================
    # SET COMPLETION
    # ========================================================

    def set_completion(
        self,
        habit_id,
        completion_date,
        completed=True
    ):
        if isinstance(completion_date, date):
            completion_date = completion_date.isoformat()

        set_habit_completion(
            habit_id,
            completion_date,
            completed
        )

    # ========================================================
    # TOGGLE COMPLETION
    # ========================================================

    def toggle_completion(self, habit_id, completion_date):
        current = self.is_completed(
            habit_id,
            completion_date
        )

        new_value = not current

        self.set_completion(
            habit_id,
            completion_date,
            new_value
        )

        return new_value

    # ========================================================
    # CHECK COMPLETION
    # ========================================================

    def is_completed(self, habit_id, completion_date):
        if isinstance(completion_date, date):
            completion_date = completion_date.isoformat()

        return is_habit_completed(
            habit_id,
            completion_date
        )

    # ========================================================
    # MONTH DATA
    # ========================================================

    def get_month_data(self, year, month):
        return get_month_completions(year, month)

    # ========================================================
    # MONTHLY MATRIX
    # ========================================================

    def get_month_matrix(self, year, month):
        habits = self.get_active_habits()

        days_in_month = calendar.monthrange(
            year,
            month
        )[1]

        completions = self.get_month_data(year, month)

        completion_lookup = {}

        for item in completions:
            key = (
                item["habit_id"],
                item["date"]
            )

            completion_lookup[key] = bool(
                item["completed"]
            )

        matrix = []

        for habit in habits:
            row = {
                "id": habit["id"],
                "name": habit["name"],
                "days": {}
            }

            for day_number in range(1, days_in_month + 1):
                current_date = date(
                    year,
                    month,
                    day_number
                ).isoformat()

                row["days"][day_number] = completion_lookup.get(
                    (habit["id"], current_date),
                    False
                )

            matrix.append(row)

        return matrix

    # ========================================================
    # MONTHLY COMPLETION PERCENTAGE
    # ========================================================

    def get_month_percentage(self, year, month):
        habits = self.get_active_habits()

        if not habits:
            return 0

        days_in_month = calendar.monthrange(
            year,
            month
        )[1]

        total_possible = len(habits) * days_in_month

        if total_possible == 0:
            return 0

        completions = self.get_month_data(year, month)

        completed_count = sum(
            1
            for item in completions
            if item["completed"]
        )

        return round(
            (completed_count / total_possible) * 100,
            1
        )

    # ========================================================
    # TODAY'S PROGRESS
    # ========================================================

    def get_today_progress(self):
        today = date.today()
        habits = self.get_active_habits()

        total = len(habits)

        completed = sum(
            1
            for habit in habits
            if self.is_completed(habit["id"], today)
        )

        percentage = (
            (completed / total) * 100
            if total else 0
        )

        return {
            "completed": completed,
            "total": total,
            "percentage": round(percentage, 1)
        }

    # ========================================================
    # CURRENT STREAK
    # ========================================================

    def get_current_streak(self, habit_id):
        streak = 0
        current_date = date.today()

        while self.is_completed(habit_id, current_date):
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    # ========================================================
    # LONGEST STREAK
    # ========================================================

    def get_longest_streak(self, habit_id):
        today = date.today()
        completed_dates = []

        # Check the last ten years.
        for days_ago in range(3650):
            current_date = today - timedelta(days=days_ago)

            if self.is_completed(habit_id, current_date):
                completed_dates.append(current_date)

        if not completed_dates:
            return 0

        completed_dates.sort()

        longest = 1
        current_streak = 1

        for index in range(1, len(completed_dates)):
            difference = (
                completed_dates[index] -
                completed_dates[index - 1]
            ).days

            if difference == 1:
                current_streak += 1
            else:
                current_streak = 1

            longest = max(longest, current_streak)

        return longest


# ============================================================
# SIMPLE FUNCTIONS
# These functions are imported by habits_view.py
# ============================================================

_manager = HabitManager()


def create_habit(name):
    return _manager.create_habit(name)


def update_habit(habit_id, name):
    return _manager.update_habit(habit_id, name)


def get_active_habits():
    return _manager.get_active_habits()


def get_all_habits():
    return _manager.get_all_habits()


def delete_habit(habit_id):
    return _manager.delete_habit(habit_id)


def deactivate_habit(habit_id):
    return _manager.deactivate_habit(habit_id)


def set_completion(habit_id, completion_date, completed=True):
    return _manager.set_completion(
        habit_id,
        completion_date,
        completed
    )


def toggle_completion(habit_id, completion_date):
    return _manager.toggle_completion(
        habit_id,
        completion_date
    )


def is_completed(habit_id, completion_date):
    return _manager.is_completed(
        habit_id,
        completion_date
    )


def get_month_matrix(year, month):
    return _manager.get_month_matrix(year, month)


def get_month_percentage(year, month):
    return _manager.get_month_percentage(year, month)


def get_today_progress():
    return _manager.get_today_progress()


def get_current_streak(habit_id):
    return _manager.get_current_streak(habit_id)


def get_longest_streak(habit_id):
    return _manager.get_longest_streak(habit_id)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("Habit module loaded successfully.")

    habits = get_active_habits()
    print(f"Active habits: {len(habits)}")

    progress = get_today_progress()

    print(
        f"Today's progress: "
        f"{progress['completed']}/"
        f"{progress['total']} "
        f"({progress['percentage']}%)"
    )
