

#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox
import calendar
from datetime import date

from todo import (
    add_task,
    get_tasks,
    update_task,
    set_task_status,
    delete_task,
    get_task_summary,
)


class TodoView(tk.Frame):
    THEMES = {
        "dark": {
            "BG": "#0F1117",
            "CARD": "#1B1F2A",
            "BORDER": "#303747",
            "TEXT": "#F1F5F9",
            "MUTED": "#8B93A7",
            "ACCENT": "#7C5CFC",
            "INPUT": "#151821",
            "GREEN": "#35D07F",
            "RED": "#FF6875",
            "ROW": "#171B24",
            "SELECTED": "#30275A",
        },
        "light": {
            "BG": "#F5F7FB",
            "CARD": "#FFFFFF",
            "BORDER": "#DFE3EC",
            "TEXT": "#202538",
            "MUTED": "#687086",
            "ACCENT": "#6366F1",
            "INPUT": "#F0F2F7",
            "GREEN": "#168B50",
            "RED": "#D93649",
            "ROW": "#F8F9FC",
            "SELECTED": "#E9E7FF",
        },
    }

    def __init__(self, parent, theme="dark"):
        self.theme_name = theme if theme in self.THEMES else "dark"
        self.colors = self.THEMES[self.theme_name]
        self.selected_date = date.today()
        self.display_year = self.selected_date.year
        self.display_month = self.selected_date.month

        super().__init__(parent, bg=self.c("BG"))

        self.build_ui()
        self.refresh()

    def c(self, name):
        return self.colors[name]

    def make_label(
        self, parent, text, size=10, color="TEXT",
        bold=False, **kwargs
    ):
        return tk.Label(
            parent,
            text=text,
            font=("DejaVu Sans", size, "bold" if bold else "normal"),
            bg=kwargs.pop("bg", self.c("BG")),
            fg=self.c(color),
            **kwargs,
        )

    def make_button(self, parent, text, command, primary=False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("DejaVu Sans", 9, "bold"),
            bg=self.c("ACCENT") if primary else self.c("CARD"),
            fg="white" if primary else self.c("TEXT"),
            activebackground=self.c("ACCENT"),
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
        )

    def build_ui(self):
        # ---------------- HEADER ----------------
        header = tk.Frame(self, bg=self.c("BG"))
        header.pack(fill="x", padx=22, pady=(20, 14))

        heading = tk.Frame(header, bg=self.c("BG"))
        heading.pack(side="left", fill="x", expand=True)

        self.make_label(
            heading, "My To-Do List", 23, bold=True
        ).pack(anchor="w")

        self.make_label(
            heading,
            "Plan your day. Make progress. Finish what matters.",
            9,
            "MUTED",
        ).pack(anchor="w", pady=(4, 0))

        self.make_button(
            header, "+ Add task", self.open_add_dialog, primary=True
        ).pack(side="right")

        # ---------------- SUMMARY ----------------
        summary_frame = tk.Frame(self, bg=self.c("BG"))
        summary_frame.pack(fill="x", padx=18, pady=(0, 14))

        self.summary_values = {}

        summaries = [
            ("total", "TOTAL"),
            ("remaining", "TO DO"),
            ("in_progress", "IN PROGRESS"),
            ("completed", "DONE"),
            ("percentage", "PROGRESS"),
        ]

        for key, heading in summaries:
            card = tk.Frame(
                summary_frame,
                bg=self.c("CARD"),
                highlightbackground=self.c("BORDER"),
                highlightthickness=1,
            )
            card.pack(side="left", fill="both", expand=True, padx=4)

            self.make_label(
                card, heading, 8, "MUTED", bold=True,
                bg=self.c("CARD")
            ).pack(anchor="w", padx=11, pady=(11, 4))

            value = self.make_label(
                card, "0", 18, bold=True, bg=self.c("CARD")
            )
            value.pack(anchor="w", padx=11, pady=(0, 10))
            self.summary_values[key] = value

        # ---------------- MAIN CONTENT ----------------
        content = tk.Frame(self, bg=self.c("BG"))
        content.pack(
            fill="both", expand=True, padx=22, pady=(0, 20)
        )

        content.grid_columnconfigure(0, weight=4, uniform="main")
        content.grid_columnconfigure(1, weight=6, uniform="main")
        content.grid_rowconfigure(0, weight=1)

        self.calendar_panel = tk.Frame(
            content,
            bg=self.c("CARD"),
            highlightbackground=self.c("BORDER"),
            highlightthickness=1,
        )
        self.calendar_panel.grid(
            row=0, column=0, sticky="nsew", padx=(0, 8)
        )

        self.tasks_panel = tk.Frame(
            content,
            bg=self.c("CARD"),
            highlightbackground=self.c("BORDER"),
            highlightthickness=1,
        )
        self.tasks_panel.grid(
            row=0, column=1, sticky="nsew", padx=(8, 0)
        )

        self.build_calendar_panel()
        self.build_tasks_panel()

    # ========================================================
    # CALENDAR
    # ========================================================

    def build_calendar_panel(self):
        top = tk.Frame(self.calendar_panel, bg=self.c("CARD"))
        top.pack(fill="x", padx=14, pady=(15, 10))

        self.make_label(
            top, "Calendar", 14, bold=True, bg=self.c("CARD")
        ).pack(side="left")

        month_nav = tk.Frame(top, bg=self.c("CARD"))
        month_nav.pack(side="right")

        self.make_button(
            month_nav, "‹", self.previous_month
        ).pack(side="left", padx=2)

        self.make_button(
            month_nav, "Today", self.go_today
        ).pack(side="left", padx=2)

        self.make_button(
            month_nav, "›", self.next_month
        ).pack(side="left", padx=2)

        self.month_title = self.make_label(
            self.calendar_panel, "", 12, bold=True, bg=self.c("CARD")
        )
        self.month_title.pack(anchor="w", padx=16, pady=(3, 12))

        self.calendar_grid = tk.Frame(
            self.calendar_panel, bg=self.c("CARD")
        )
        self.calendar_grid.pack(fill="both", expand=True, padx=10)

        self.make_label(
            self.calendar_panel,
            "Select a date to see its tasks.",
            9,
            "MUTED",
            bg=self.c("CARD"),
        ).pack(anchor="w", padx=15, pady=(10, 15))

    def draw_calendar(self):
        for child in self.calendar_grid.winfo_children():
            child.destroy()

        self.month_title.config(
            text=f"{calendar.month_name[self.display_month]} "
                 f"{self.display_year}"
        )

        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for column, weekday in enumerate(weekdays):
            self.make_label(
                self.calendar_grid,
                weekday,
                8,
                "MUTED",
                bold=True,
                bg=self.c("CARD"),
            ).grid(row=0, column=column, sticky="nsew", pady=(0, 8))

            self.calendar_grid.grid_columnconfigure(column, weight=1)

        for row_index, week in enumerate(
            calendar.monthcalendar(self.display_year, self.display_month),
            start=1,
        ):
            self.calendar_grid.grid_rowconfigure(row_index, weight=1)

            for column, day_number in enumerate(week):
                if day_number == 0:
                    tk.Frame(
                        self.calendar_grid, bg=self.c("CARD")
                    ).grid(
                        row=row_index, column=column,
                        sticky="nsew", padx=2, pady=2
                    )
                    continue

                chosen_date = date(
                    self.display_year, self.display_month, day_number
                )

                is_selected = chosen_date == self.selected_date
                is_today = chosen_date == date.today()

                if is_selected:
                    bg = self.c("SELECTED")
                    fg = self.c("ACCENT")
                else:
                    bg = self.c("ROW")
                    fg = self.c("TEXT")

                day_frame = tk.Frame(
                    self.calendar_grid,
                    bg=bg,
                    highlightbackground=(
                        self.c("ACCENT")
                        if is_today or is_selected
                        else self.c("BORDER")
                    ),
                    highlightthickness=1 if is_today or is_selected else 0,
                )
                day_frame.grid(
                    row=row_index, column=column,
                    sticky="nsew", padx=2, pady=2
                )

                day_button = tk.Button(
                    day_frame,
                    text=str(day_number),
                    command=lambda d=chosen_date: self.select_date(d),
                    bg=bg,
                    fg=fg,
                    activebackground=self.c("ACCENT"),
                    activeforeground="white",
                    font=("DejaVu Sans", 10, "bold"),
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                )
                day_button.pack(fill="both", expand=True, pady=(2, 0))

                # A small marker indicates that the date has tasks.
                task_count = len(get_tasks(chosen_date))
                if task_count:
                    marker = self.make_label(
                        day_frame,
                        f"• {task_count}",
                        7,
                        "ACCENT",
                        bold=True,
                        bg=bg,
                    )
                    marker.pack(pady=(0, 3))

    def select_date(self, chosen_date):
        self.selected_date = chosen_date
        self.display_year = chosen_date.year
        self.display_month = chosen_date.month
        self.refresh()

    def previous_month(self):
        if self.display_month == 1:
            self.display_month = 12
            self.display_year -= 1
        else:
            self.display_month -= 1

        self.refresh()

    def next_month(self):
        if self.display_month == 12:
            self.display_month = 1
            self.display_year += 1
        else:
            self.display_month += 1

        self.refresh()

    def go_today(self):
        self.selected_date = date.today()
        self.display_year = self.selected_date.year
        self.display_month = self.selected_date.month
        self.refresh()

    # ========================================================
    # TASK LIST
    # ========================================================

    def build_tasks_panel(self):
        header = tk.Frame(self.tasks_panel, bg=self.c("CARD"))
        header.pack(fill="x", padx=16, pady=(16, 10))

        self.task_date_label = self.make_label(
            header, "", 15, bold=True, bg=self.c("CARD")
        )
        self.task_date_label.pack(anchor="w")

        self.task_subtitle = self.make_label(
            header, "", 9, "MUTED", bg=self.c("CARD")
        )
        self.task_subtitle.pack(anchor="w", pady=(4, 0))

        self.task_list = tk.Frame(self.tasks_panel, bg=self.c("CARD"))
        self.task_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def refresh(self):
        self.draw_calendar()

        summary = get_task_summary(self.selected_date)

        for key in self.summary_values:
            value = summary.get(key, 0)
            if key == "percentage":
                value = f"{value}%"
            self.summary_values[key].config(text=str(value))

        self.task_date_label.config(
            text=self.selected_date.strftime("%A, %d %B")
        )

        tasks = get_tasks(self.selected_date)
        total = len(tasks)

        self.task_subtitle.config(
            text=f"{total} task{'s' if total != 1 else ''} planned"
        )

        for child in self.task_list.winfo_children():
            child.destroy()

        if not tasks:
            empty = tk.Frame(self.task_list, bg=self.c("CARD"))
            empty.pack(fill="both", expand=True, pady=30)

            self.make_label(
                empty, "Your day is clear", 15, bold=True,
                bg=self.c("CARD")
            ).pack(pady=(20, 6))

            self.make_label(
                empty,
                "Add a task to decide what matters today.",
                9,
                "MUTED",
                bg=self.c("CARD"),
            ).pack()

            self.make_button(
                empty, "+ Add your first task",
                self.open_add_dialog, primary=True
            ).pack(pady=16)

            return

        for task in tasks:
            self.draw_task(task)

    def draw_task(self, task):
        status = task.get("status", "To Do")
        if task.get("completed"):
            status = "Done"

        card = tk.Frame(
            self.task_list,
            bg=self.c("ROW"),
            highlightbackground=self.c("BORDER"),
            highlightthickness=1,
        )
        card.pack(fill="x", pady=5)

        left = tk.Frame(card, bg=self.c("ROW"))
        left.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        title_color = self.c("MUTED") if status == "Done" else self.c("TEXT")
        title_font = (
            "DejaVu Sans", 10,
            "overstrike" if status == "Done" else "bold"
        )

        title_label = tk.Label(
            left,
            text=task["title"],
            font=title_font,
            bg=self.c("ROW"),
            fg=title_color,
            anchor="w",
            justify="left",
            wraplength=400,
        )
        title_label.pack(anchor="w", fill="x")

        priority_colors = {
            "High": self.c("RED"),
            "Medium": self.c("ACCENT"),
            "Low": self.c("GREEN"),
        }

        meta = tk.Frame(left, bg=self.c("ROW"))
        meta.pack(anchor="w", pady=(6, 0))

        tk.Label(
            meta,
            text=f'{task["priority"]} priority',
            font=("DejaVu Sans", 8, "bold"),
            bg=self.c("ROW"),
            fg=priority_colors.get(task["priority"], self.c("MUTED")),
        ).pack(side="left")

        if task.get("notes"):
            self.make_label(
                left,
                task["notes"],
                9,
                "MUTED",
                bg=self.c("ROW"),
                anchor="w",
                justify="left",
                wraplength=420,
            ).pack(anchor="w", pady=(6, 0))

        right = tk.Frame(card, bg=self.c("ROW"))
        right.pack(side="right", padx=8, pady=8)

        status_box = ttk.Combobox(
            right,
            values=("To Do", "In Progress", "Done"),
            state="readonly",
            width=13,
            font=("DejaVu Sans", 8),
        )
        status_box.set(status)
        status_box.pack(pady=(0, 6))

        status_box.bind(
            "<<ComboboxSelected>>",
            lambda _event, task_id=task["id"], box=status_box:
                self.change_status(task_id, box.get())
        )

        tk.Button(
            right,
            text="Edit",
            command=lambda t=task: self.open_edit_dialog(t),
            font=("DejaVu Sans", 8),
            bg=self.c("ROW"),
            fg=self.c("TEXT"),
            activebackground=self.c("CARD"),
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left", padx=2)

        tk.Button(
            right,
            text="Delete",
            command=lambda t=task: self.remove_task(t),
            font=("DejaVu Sans", 8),
            bg=self.c("ROW"),
            fg=self.c("RED"),
            activebackground=self.c("CARD"),
            relief="flat",
            bd=0,
            cursor="hand2",
        ).pack(side="left", padx=2)

    def change_status(self, task_id, status):
        try:
            set_task_status(task_id, status)
            self.refresh()
        except Exception as error:
            messagebox.showerror(
                "Could not update task", str(error), parent=self
            )

    def remove_task(self, task):
        confirmed = messagebox.askyesno(
            "Delete task",
            f'Delete "{task["title"]}"?',
            parent=self,
        )

        if not confirmed:
            return

        try:
            delete_task(task["id"])
            self.refresh()
        except Exception as error:
            messagebox.showerror(
                "Could not delete task", str(error), parent=self
            )

    # ========================================================
    # ADD / EDIT TASK
    # ========================================================

    def open_add_dialog(self):
        self.open_task_dialog()

    def open_edit_dialog(self, task):
        self.open_task_dialog(task)

    def open_task_dialog(self, task=None):
        win = tk.Toplevel(self)
        win.title("Edit task" if task else "Add task")
        win.configure(bg=self.c("BG"))
        win.resizable(False, False)
        win.transient(self.winfo_toplevel())
        win.grab_set()
        # win.geometry("430x440")

        win.geometry("460x650")
        win.minsize(460, 600)

        body = tk.Frame(win, bg=self.c("BG"))
        body.pack(fill="both", expand=True, padx=22, pady=18)

        self.make_label(
            body,
            "Edit task" if task else "Add a new task",
            18,
            bold=True,
        ).pack(anchor="w", pady=(0, 12))

        def make_entry(label_text, initial=""):
            self.make_label(
                body, label_text, 9, "MUTED", bold=True
            ).pack(anchor="w", pady=(8, 4))

            entry = tk.Entry(
                body,
                font=("DejaVu Sans", 10),
                bg=self.c("INPUT"),
                fg=self.c("TEXT"),
                insertbackground=self.c("TEXT"),
                relief="flat",
                highlightthickness=1,
                highlightbackground=self.c("BORDER"),
            )
            entry.pack(fill="x", ipady=7)
            entry.insert(0, initial)
            return entry

        title_entry = make_entry(
            "TASK NAME", task["title"] if task else ""
        )

        date_entry = make_entry(
            "DATE (YYYY-MM-DD)",
            task["task_date"] if task else self.selected_date.isoformat(),
        )

        self.make_label(
            body, "PRIORITY", 9, "MUTED", bold=True
        ).pack(anchor="w", pady=(9, 4))

        priority_box = ttk.Combobox(
            body,
            values=("Low", "Medium", "High"),
            state="readonly",
            font=("DejaVu Sans", 10),
        )
        priority_box.set(task["priority"] if task else "Medium")
        priority_box.pack(fill="x", ipady=4)

        self.make_label(
            body, "STATUS", 9, "MUTED", bold=True
        ).pack(anchor="w", pady=(9, 4))

        status_box = ttk.Combobox(
            body,
            values=("To Do", "In Progress", "Done"),
            state="readonly",
            font=("DejaVu Sans", 10),
        )
        status_box.set(
            task.get("status", "Done" if task.get("completed") else "To Do")
            if task else "To Do"
        )
        status_box.pack(fill="x", ipady=4)

        notes_entry = make_entry(
            "NOTES (OPTIONAL)", task.get("notes", "") if task else ""
        )

        def save():
            try:
                title = title_entry.get().strip()
                chosen_date = date.fromisoformat(date_entry.get().strip())
                priority = priority_box.get()
                status = status_box.get()
                notes = notes_entry.get().strip()

                if not title:
                    raise ValueError("Please enter a task name.")

                if task:
                    update_task(
                        task["id"],
                        title,
                        chosen_date,
                        priority,
                        notes,
                        status,
                    )
                else:
                    add_task(
                        title,
                        chosen_date,
                        priority,
                        notes,
                        status,
                    )

                self.selected_date = chosen_date
                self.display_year = chosen_date.year
                self.display_month = chosen_date.month

                win.destroy()
                self.refresh()

            except ValueError as error:
                messagebox.showwarning(
                    "Check task details", str(error), parent=win
                )
            except Exception as error:
                messagebox.showerror(
                    "Could not save task", str(error), parent=win
                )

        # buttons = tk.Frame(body, bg=self.c("BG"))
        # buttons.pack(fill="x", pady=(15, 0))

        # self.make_button(
        #     buttons, "Cancel", win.destroy
        # ).pack(side="right", padx=(8, 0))

        # self.make_button(
        #     buttons, "Save task", save, primary=True
        # ).pack(side="right")

        buttons = tk.Frame(body, bg=self.c("BG"))
        buttons.pack(fill="x", pady=(20, 5))

        self.make_button(
            buttons,
            "Cancel",
            win.destroy,
        ).pack(side="right", padx=(8, 0))

        self.make_button(
            buttons,
            "💾 Save task",
            save,
            primary=True,
        ).pack(side="right")

        title_entry.focus_set()
        win.bind("<Escape>", lambda _event: win.destroy())
        win.bind("<Control-Return>", lambda _event: save())


