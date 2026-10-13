

#!/usr/bin/env python3

import calendar
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, datetime, timedelta
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

EVENT_FILE = Path(__file__).with_name("calendar_events.json")

THEMES = {
    "light": {
        "bg": "#F3F6FC",
        "surface": "#FFFFFF",
        "text": "#19345C",
        "muted": "#7185A5",
        "border": "#DFE8F5",
        "accent": "#1765C0",
        "selected": "#E4EEFC",
        "grid": "#E8EFF8",
        "sidebar": "#F7F9FD",
        "green": "#13AE68",
    },
    "dark": {
        "bg": "#10141D",
        "surface": "#1B2230",
        "text": "#EDF3FF",
        "muted": "#9AAAC4",
        "border": "#303B50",
        "accent": "#669EFF",
        "selected": "#263B5B",
        "grid": "#2B3548",
        "sidebar": "#151B27",
        "green": "#35D68A",
    },
}

EVENT_COLORS = [
    ("#DDF7E8", "#23764B"),
    ("#DDEBFF", "#205DA8"),
    ("#EEE5FF", "#6740B6"),
    ("#FFF0CC", "#93630B"),
    ("#D7F5F7", "#087F91"),
    ("#FFE1E8", "#B52E53"),
]


def load_events():
    try:
        with EVENT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_events(events):
    with EVENT_FILE.open("w", encoding="utf-8") as file:
        json.dump(events, file, indent=2, ensure_ascii=False)


# ============================================================
# CALENDAR UI
# ============================================================

class CalendarView(tk.Frame):

    def __init__(self, parent, theme="light", **kwargs):
        super().__init__(parent, **kwargs)

        self.parent = parent
        self.theme_name = self.normalize_theme(theme)
        self.colors = THEMES[self.theme_name]

        self.selected_date = date.today()
        self.view_mode = "Day"
        self.events = load_events()
        self._resize_job = None

        self.configure(bg=self.colors["bg"])
        self.build_ui()
        self.refresh()

    # --------------------------------------------------------
    # THEME
    # --------------------------------------------------------

    @staticmethod
    def normalize_theme(theme):
        return "dark" if str(theme).lower().startswith("dark") else "light"

    def apply_theme(self, theme):
        theme = self.normalize_theme(theme)

        if theme == self.theme_name:
            return

        self.theme_name = theme
        self.colors = THEMES[theme]

        for child in self.winfo_children():
            child.destroy()

        self.configure(bg=self.colors["bg"])
        self.build_ui()
        self.refresh()

    def color(self, name):
        return self.colors[name]

    def make_label(self, parent, text, size=10, bold=False,
                   color=None, bg=None, **kwargs):
        return tk.Label(
            parent,
            text=text,
            font=("DejaVu Sans", size, "bold" if bold else "normal"),
            fg=color or self.color("text"),
            bg=bg or self.color("surface"),
            **kwargs,
        )

    def make_button(self, parent, text, command, primary=False):
        bg = self.color("accent") if primary else self.color("surface")
        fg = "#FFFFFF" if primary else self.color("text")

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=self.color("selected"),
            activeforeground=self.color("text"),
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("DejaVu Sans", 9, "bold"),
            padx=11,
            pady=7,
        )

    # --------------------------------------------------------
    # BUILD MAIN INTERFACE
    # --------------------------------------------------------

    def build_ui(self):
        c = self.colors

        # Header
        header = tk.Frame(self, bg=c["bg"])
        header.pack(fill="x", padx=16, pady=(14, 10))

        self.make_label(
            header, "▣  Social Lock", 17, True,
            color=c["accent"], bg=c["bg"]
        ).pack(side="left")

        self.search_var = tk.StringVar()
        search = tk.Entry(
            header,
            textvariable=self.search_var,
            font=("DejaVu Sans", 10),
            bg=c["surface"],
            fg=c["text"],
            insertbackground=c["text"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=c["border"],
        )
        search.pack(side="left", fill="x", expand=True, padx=24, ipady=9)
        search.insert(0, "")
        search.bind("<Return>", lambda _e: self.refresh())

        self.make_button(
            header,
            "☀ / ☾",
            lambda: self.apply_theme(
                "dark" if self.theme_name == "light" else "light"
            ),
        ).pack(side="right")

        # Main content: left sidebar, central calendar, right sidebar
        content = tk.Frame(self, bg=c["bg"])
        content.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        content.grid_columnconfigure(0, weight=0, minsize=175)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=0, minsize=245)
        content.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(content, bg=c["sidebar"], width=175)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.sidebar.grid_propagate(False)

        self.center = tk.Frame(
            content, bg=c["surface"],
            highlightbackground=c["border"], highlightthickness=1
        )
        self.center.grid(row=0, column=1, sticky="nsew", padx=(0, 10))

        self.right = tk.Frame(content, bg=c["bg"], width=245)
        self.right.grid(row=0, column=2, sticky="nsew")

        # self.build_sidebar()
        self.build_center()
        self.build_right()

    # --------------------------------------------------------
    # LEFT SIDEBAR
    # --------------------------------------------------------



    # --------------------------------------------------------
    # CENTRAL CALENDAR
    # --------------------------------------------------------

    def build_center(self):
        c = self.colors

        toolbar = tk.Frame(self.center, bg=c["surface"])
        toolbar.pack(fill="x", padx=14, pady=12)

        self.make_button(
            toolbar, "‹", lambda: self.move_period(-1)
        ).pack(side="left")

        self.make_button(
            toolbar, "›", lambda: self.move_period(1)
        ).pack(side="left", padx=(4, 10))

        self.period_title = self.make_label(
            toolbar, "", 15, True
        )
        self.period_title.pack(side="left", padx=3)

        self.make_button(
            toolbar, "Today", self.go_today
        ).pack(side="right", padx=(5, 0))

        for mode in ("Month", "Week", "Day"):
            self.make_button(
                toolbar,
                mode,
                lambda m=mode: self.set_view(m),
                primary=(self.view_mode == mode),
            ).pack(side="right", padx=2)

        self.body = tk.Frame(self.center, bg=c["surface"])
        self.body.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def set_view(self, mode):
        self.view_mode = mode
        self.refresh()

    def move_period(self, direction):
        if self.view_mode == "Day":
            self.selected_date += timedelta(days=direction)
        elif self.view_mode == "Week":
            self.selected_date += timedelta(days=7 * direction)
        else:
            year, month = self.selected_date.year, self.selected_date.month
            month += direction
            if month < 1:
                month, year = 12, year - 1
            elif month > 12:
                month, year = 1, year + 1
            self.selected_date = self.selected_date.replace(
                year=year, month=month,
                day=min(
                    self.selected_date.day,
                    calendar.monthrange(year, month)[1]
                )
            )
        self.refresh()

    def go_today(self):
        self.selected_date = date.today()
        self.refresh()

    # --------------------------------------------------------
    # RIGHT SIDEBAR
    # --------------------------------------------------------

    def build_right(self):
        c = self.colors

        mini = tk.Frame(
            self.right, bg=c["surface"],
            highlightbackground=c["border"], highlightthickness=1
        )
        mini.pack(fill="x", pady=(0, 9))

        mini_header = tk.Frame(mini, bg=c["surface"])
        mini_header.pack(fill="x", padx=8, pady=8)

        self.make_button(
            mini_header, "‹", lambda: self.move_mini_month(-1)
        ).pack(side="left")

        self.mini_title = self.make_label(
            mini_header, "", 10, True
        )
        self.mini_title.pack(side="left", expand=True)

        self.make_button(
            mini_header, "›", lambda: self.move_mini_month(1)
        ).pack(side="right")

        self.mini_grid = tk.Frame(mini, bg=c["surface"])
        self.mini_grid.pack(fill="x", padx=7, pady=(0, 9))

        overview = tk.Frame(
            self.right, bg=c["surface"],
            highlightbackground=c["border"], highlightthickness=1
        )
        overview.pack(fill="x", pady=(0, 9))

        self.make_label(
            overview, "Day Overview", 12, True
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.overview_value = self.make_label(
            overview, "", 10, color=c["muted"]
        )
        self.overview_value.pack(anchor="w", padx=12, pady=(4, 12))

        today_box = tk.Frame(
            self.right, bg=c["surface"],
            highlightbackground=c["border"], highlightthickness=1
        )
        today_box.pack(fill="both", expand=True)

        self.make_label(
            today_box, "Time Blocks", 12, True
        ).pack(anchor="w", padx=12, pady=(12, 5))

        self.event_list = tk.Frame(today_box, bg=c["surface"])
        self.event_list.pack(fill="both", expand=True, padx=8, pady=5)

        self.make_button(
            today_box, "+ Add time block", self.add_event, primary=True
        ).pack(fill="x", padx=10, pady=10)

    def move_mini_month(self, direction):
        year, month = self.selected_date.year, self.selected_date.month
        month += direction

        if month < 1:
            month, year = 12, year - 1
        elif month > 12:
            month, year = 1, year + 1

        self.selected_date = self.selected_date.replace(
            year=year,
            month=month,
            day=min(
                self.selected_date.day,
                calendar.monthrange(year, month)[1]
            ),
        )
        self.refresh()

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    def refresh(self):
        if not self.winfo_exists():
            return

        for child in self.body.winfo_children():
            child.destroy()

        if self.view_mode == "Day":
            self.period_title.config(
                text=self.selected_date.strftime("%B %Y")
            )
            self.draw_day()
        elif self.view_mode == "Week":
            start = self.selected_date - timedelta(
                days=self.selected_date.weekday()
            )
            end = start + timedelta(days=6)
            self.period_title.config(
                text=f"{start:%d %b} – {end:%d %b %Y}"
            )
            self.draw_week(start)
        else:
            self.period_title.config(
                text=self.selected_date.strftime("%B %Y")
            )
            self.draw_month()

        self.draw_mini_calendar()
        self.draw_event_list()
        self.update_overview()

    # --------------------------------------------------------
    # DAY VIEW: GOOGLE CALENDAR-STYLE TIME GRID
    # --------------------------------------------------------

    def draw_day(self):
        c = self.colors
        day = self.selected_date
        day_key = day.isoformat()

        heading = tk.Frame(self.body, bg=c["surface"])
        heading.pack(fill="x", padx=8, pady=(4, 10))

        self.make_label(
            heading, day.strftime("%a"), 10, True, c["muted"]
        ).pack(anchor="w", padx=70)

        self.make_label(
            heading, str(day.day), 22, True, c["accent"]
        ).pack(anchor="w", padx=70)

        canvas = tk.Canvas(
            self.body,
            bg=c["surface"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            self.body, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        grid = tk.Frame(canvas, bg=c["surface"])
        window_id = canvas.create_window(
            (0, 0), window=grid, anchor="nw"
        )

        def update_scroll(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(window_id, width=canvas.winfo_width())

        grid.bind("<Configure>", update_scroll)
        canvas.bind("<Configure>", update_scroll)

        # for hour in range(6, 24):
        for hour in list(range(1, 24)) + [0]:
            row = tk.Frame(grid, bg=c["surface"], height=62)
            row.pack(fill="x")
            row.pack_propagate(False)

            self.make_label(
                row, datetime.strptime(
                    f"{hour:02d}:00", "%H:%M"
                ).strftime("%I:%M %p").lstrip("0"),
                8, color=c["muted"], width=10, anchor="n"
            ).pack(side="left", padx=(2, 5), pady=(2, 0))

            line_area = tk.Frame(
                row, bg=c["surface"],
                highlightbackground=c["grid"], highlightthickness=1
            )
            line_area.pack(side="left", fill="both", expand=True)

            line_area.bind(
                "<Double-Button-1>",
                lambda _e, h=hour: self.add_event(default_hour=h)
            )

            for event in self.events.get(day_key, []):
                start_hour, start_minute = self.parse_time(
                    event.get("start", "09:00")
                )
                end_hour, end_minute = self.parse_time(
                    event.get("end", "09:30")
                )

                if start_hour != hour:
                    continue

                color_index = event.get("color", 0) % len(EVENT_COLORS)
                event_bg, event_fg = EVENT_COLORS[color_index]

                if self.theme_name == "dark":
                    event_bg = c["selected"]
                    event_fg = c["text"]

                block = tk.Frame(line_area, bg=event_bg)
                block.pack(fill="x", padx=5, pady=2)

                self.make_label(
                    block,
                    f"{event['start']}–{event['end']}   {event['title']}",
                    9, True, event_fg, event_bg, anchor="w"
                ).pack(fill="x", padx=7, pady=5)

                block.bind(
                    "<Double-Button-1>",
                    lambda _e, ev=event: self.edit_event(ev)
                )

            self.make_button(
                line_area, "+",
                lambda h=hour: self.add_event(default_hour=h)
            ).pack(side="right", padx=4, pady=2)

    # --------------------------------------------------------
    # WEEK VIEW
    # --------------------------------------------------------

    def draw_week(self, start):
        c = self.colors

        header = tk.Frame(self.body, bg=c["surface"])
        header.pack(fill="x")

        self.make_label(header, "TIME", 8, True, c["muted"]).grid(
            row=0, column=0, padx=4, pady=6
        )

        for index in range(7):
            day = start + timedelta(days=index)
            self.make_button(
                header,
                day.strftime("%a\n%d"),
                lambda d=day: self.select_date(d),
                primary=(day == self.selected_date),
            ).grid(row=0, column=index + 1, sticky="ew", padx=1)

            header.grid_columnconfigure(index + 1, weight=1)

        canvas = tk.Canvas(self.body, bg=c["surface"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self.body, orient="vertical", command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        grid = tk.Frame(canvas, bg=c["surface"])
        wid = canvas.create_window((0, 0), window=grid, anchor="nw")

        grid.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(wid, width=e.width)
        )

        # for hour in range(6, 24):
        for hour in list(range(1, 24)) + [0]:
            self.make_label(
                grid, datetime.strptime(
                    f"{hour:02d}:00", "%H:%M"
                ).strftime("%I %p").lstrip("0"),
                7, color=c["muted"]
            # ).grid(row=hour - 6, column=0, sticky="n", padx=4, pady=5)
            ).grid(row=list(range(1, 24)).index(hour) if hour != 0 else 23,
                column=0, sticky="n", padx=4, pady=5)

            for index in range(7):
                day = start + timedelta(days=index)
                cell = tk.Frame(
                    grid, bg=c["surface"], height=48,
                    highlightbackground=c["grid"], highlightthickness=1
                )
                cell.grid(
                    # row=hour - 6, column=index + 1,
                    row=list(range(1, 24)).index(hour) if hour != 0 else 23,
                    column=index + 1,
                    sticky="nsew"
                )
                cell.grid_propagate(False)

                for event in self.events.get(day.isoformat(), []):
                    event_hour, _ = self.parse_time(event.get("start", "09:00"))
                    if event_hour == hour:
                        bg, fg = EVENT_COLORS[
                            event.get("color", 0) % len(EVENT_COLORS)
                        ]
                        if self.theme_name == "dark":
                            bg, fg = c["selected"], c["text"]

                        self.make_label(
                            cell, event["title"], 7, True, fg, bg,
                            wraplength=95
                        ).pack(fill="x", padx=1, pady=1)

                cell.bind(
                    "<Double-Button-1>",
                    lambda _e, d=day, h=hour: self.select_and_add(d, h)
                )

        for column in range(8):
            grid.grid_columnconfigure(column, weight=1)

    # --------------------------------------------------------
    # MONTH VIEW
    # --------------------------------------------------------

    def draw_month(self):
        c = self.colors
        year, month = self.selected_date.year, self.selected_date.month

        for column, name in enumerate(
            ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        ):
            self.make_label(
                self.body, name, 9, True, c["muted"]
            ).grid(row=0, column=column, sticky="ew", pady=8)

            self.body.grid_columnconfigure(column, weight=1, uniform="month")

        weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(
            year, month
        )

        for row_index, week in enumerate(weeks, start=1):
            self.body.grid_rowconfigure(row_index, weight=1, minsize=68)

            for col_index, day in enumerate(week):
                bg = c["selected"] if day == self.selected_date else c["surface"]
                cell = tk.Frame(
                    self.body, bg=bg,
                    highlightbackground=c["grid"], highlightthickness=1
                )
                cell.grid(
                    row=row_index, column=col_index,
                    sticky="nsew", padx=1, pady=1
                )

                fg = c["text"] if day.month == month else c["muted"]
                self.make_label(
                    cell, str(day.day), 9, day == date.today(), fg, bg
                ).pack(anchor="w", padx=4, pady=3)

                for event in self.events.get(day.isoformat(), [])[:2]:
                    self.make_label(
                        cell,
                        event["start"] + " " + event["title"],
                        7, True, c["accent"], bg,
                        anchor="w", wraplength=100
                    ).pack(fill="x", padx=2)

                cell.bind(
                    "<Button-1>",
                    lambda _e, d=day: self.select_date(d)
                )

    # --------------------------------------------------------
    # MINI MONTH CALENDAR
    # --------------------------------------------------------

    def draw_mini_calendar(self):
        c = self.colors

        for child in self.mini_grid.winfo_children():
            child.destroy()

        year, month = self.selected_date.year, self.selected_date.month
        self.mini_title.config(text=f"{calendar.month_name[month]} {year}")

        for col, day_name in enumerate(("M", "T", "W", "T", "F", "S", "S")):
            self.make_label(
                self.mini_grid, day_name, 8, True, c["muted"]
            ).grid(row=0, column=col, padx=3, pady=4)

        for row, week in enumerate(
            calendar.Calendar(firstweekday=0).monthdatescalendar(year, month),
            start=1
        ):
            for col, day in enumerate(week):
                is_selected = day == self.selected_date
                is_today = day == date.today()

                bg = c["accent"] if is_selected else c["surface"]
                fg = "#FFFFFF" if is_selected else (
                    c["text"] if day.month == month else c["muted"]
                )

                btn = tk.Button(
                    self.mini_grid,
                    text=str(day.day),
                    command=lambda d=day: self.select_date(d),
                    bg=bg, fg=fg,
                    activebackground=c["selected"],
                    activeforeground=c["text"],
                    relief="flat", bd=0,
                    font=("DejaVu Sans", 8, "bold" if is_today else "normal"),
                    width=3, pady=4,
                )
                btn.grid(row=row, column=col, padx=1, pady=1)

    # --------------------------------------------------------
    # EVENT LIST AND OVERVIEW
    # --------------------------------------------------------

    def draw_event_list(self):
        c = self.colors

        for child in self.event_list.winfo_children():
            child.destroy()

        events = sorted(
            self.events.get(self.selected_date.isoformat(), []),
            key=lambda event: event.get("start", "00:00")
        )

        if not events:
            self.make_label(
                self.event_list, "No time blocks yet.", 9, color=c["muted"]
            ).pack(anchor="w", padx=5, pady=10)
            return

        for event in events:
            row = tk.Frame(self.event_list, bg=c["surface"])
            row.pack(fill="x", pady=3)

            self.make_label(
                row, "●", 12, True, c["accent"]
            ).pack(side="left", padx=(3, 7))

            details = tk.Frame(row, bg=c["surface"])
            details.pack(side="left", fill="x", expand=True)

            self.make_label(
                details, event["title"], 9, True
            ).pack(anchor="w")

            self.make_label(
                details, f"{event['start']} – {event['end']}",
                8, color=c["muted"]
            ).pack(anchor="w")

            self.make_button(
                row, "⋯", lambda ev=event: self.edit_event(ev)
            ).pack(side="right")

    def update_overview(self):
        events = self.events.get(self.selected_date.isoformat(), [])
        self.overview_value.config(
            text=(
                f"{self.selected_date:%A, %d %B}\n"
                f"{len(events)} scheduled time block(s)"
            )
        )

    # --------------------------------------------------------
    # ADD / EDIT / DELETE EVENTS
    # --------------------------------------------------------

    @staticmethod
    def parse_time(value):
        hour, minute = map(int, value.split(":"))
        return hour, minute

    def add_event(self, default_hour=9):
        title = simpledialog.askstring(
            "New time block", "What do you want to schedule?",
            parent=self
        )
        if not title or not title.strip():
            return

        start = simpledialog.askstring(
            "Start time", "Enter start time (24-hour HH:MM):",
            initialvalue=f"{default_hour:02d}:00", parent=self
        )
        if not start:
            return

        end_hour = (default_hour + 1) % 24
        end = simpledialog.askstring(
            "End time", "Enter end time (24-hour HH:MM):",
            initialvalue=f"{end_hour:02d}:00", parent=self
        )
        if not end:
            return

        try:
            start_minutes = self.to_minutes(start)
            end_minutes = self.to_minutes(end)
            if end_minutes <= start_minutes:
                raise ValueError("End time must be later than start time.")
        except ValueError as exc:
            messagebox.showerror("Invalid time", str(exc), parent=self)
            return

        key = self.selected_date.isoformat()
        self.events.setdefault(key, []).append({
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "title": title.strip(),
            "start": start,
            "end": end,
            "color": len(self.events.get(key, [])) % len(EVENT_COLORS),
            "completed": False,
        })

        save_events(self.events)
        self.refresh()

    @staticmethod
    def to_minutes(value):
        parsed = datetime.strptime(value.strip(), "%H:%M")
        return parsed.hour * 60 + parsed.minute

    def edit_event(self, event):
        key = self.selected_date.isoformat()
        actions = tk.Toplevel(self)
        actions.title("Time block")
        actions.configure(bg=self.color("bg"))
        actions.resizable(False, False)
        actions.transient(self.winfo_toplevel())
        actions.grab_set()

        self.make_label(
            actions, event["title"], 12, True, bg=self.color("bg")
        ).pack(anchor="w", padx=16, pady=(16, 10))

        self.make_button(
            actions, "Rename", lambda: self.rename_event(event, actions)
        ).pack(fill="x", padx=16, pady=4)

        self.make_button(
            actions, "Change time", lambda: self.change_event_time(event, actions)
        ).pack(fill="x", padx=16, pady=4)

        self.make_button(
            actions, "Delete time block",
            lambda: self.delete_event(key, event, actions)
        ).pack(fill="x", padx=16, pady=4)

        self.make_button(
            actions, "Close", actions.destroy
        ).pack(fill="x", padx=16, pady=(4, 16))

    def rename_event(self, event, window):
        title = simpledialog.askstring(
            "Rename time block", "New title:",
            initialvalue=event["title"], parent=window
        )
        if title and title.strip():
            event["title"] = title.strip()
            save_events(self.events)
            window.destroy()
            self.refresh()

    def change_event_time(self, event, window):
        start = simpledialog.askstring(
            "Start time", "New start time (HH:MM):",
            initialvalue=event["start"], parent=window
        )
        if not start:
            return

        end = simpledialog.askstring(
            "End time", "New end time (HH:MM):",
            initialvalue=event["end"], parent=window
        )
        if not end:
            return

        try:
            if self.to_minutes(end) <= self.to_minutes(start):
                raise ValueError("End time must be later than start time.")
        except ValueError as exc:
            messagebox.showerror("Invalid time", str(exc), parent=window)
            return

        event["start"] = start
        event["end"] = end
        save_events(self.events)
        window.destroy()
        self.refresh()

    def delete_event(self, key, event, window):
        if messagebox.askyesno(
            "Delete time block",
            f"Delete '{event['title']}'?",
            parent=window
        ):
            self.events[key] = [
                item for item in self.events.get(key, [])
                if item.get("id") != event.get("id")
            ]
            if not self.events[key]:
                self.events.pop(key, None)

            save_events(self.events)
            window.destroy()
            self.refresh()

    # --------------------------------------------------------
    # NAVIGATION HELPERS
    # --------------------------------------------------------

    def select_date(self, chosen_date):
        self.selected_date = chosen_date
        self.view_mode = "Day"
        self.refresh()

    def select_and_add(self, chosen_date, hour):
        self.selected_date = chosen_date
        self.view_mode = "Day"
        self.refresh()
        self.add_event(default_hour=hour)


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Social Lock — Calendar")
    root.geometry("1400x850")
    root.minsize(1000, 650)

    calendar_view = CalendarView(root, theme="light")
    calendar_view.pack(fill="both", expand=True)

    root.mainloop()
