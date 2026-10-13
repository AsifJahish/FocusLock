


#!/usr/bin/env python3
"""Responsive spreadsheet-style habit tracker with dark/light themes."""

import calendar
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import date

from database import get_connection
from habits import (
    get_active_habits,
    get_all_habits,
    create_habit,
    deactivate_habit,
    delete_habit,
    is_completed,
    get_month_percentage,
    get_today_progress,
    set_completion,
)


class HabitsView:
    FONT = "DejaVu Sans"

    THEMES = {
        "light": {
            "BG": "#F3F6FB",
            "WHITE": "#FFFFFF",
            "NAVY": "#0C2F78",
            "BLUE": "#155DA8",
            "BLUE2": "#398BDD",
            "CYAN": "#08A9D9",
            "GREEN": "#00A653",
            "GREEN_LIGHT": "#DDF8E8",
            "GREEN_BORDER": "#00A653",
            "TEXT": "#17243A",
            "MUTED": "#748197",
            "BORDER": "#DCE4EF",
            "RED": "#D94A58",
            "ROW_ALT": "#F8FAFD",
            "BUTTON_BG": "#EAF0F8",
            "BUTTON_FG": "#0C2F78",
            "GRID": "#E9EEF5",
            "MENU_ACTIVE_BG": "#EAF0F8",
            "MENU_ACTIVE_FG": "#0C2F78",
        },
        "dark": {
            "BG": "#10141D",
            "WHITE": "#191F2B",
            "NAVY": "#273A5E",
            "BLUE": "#244A78",
            "BLUE2": "#326A9E",
            "CYAN": "#167D9A",
            "GREEN": "#35D07F",
            "GREEN_LIGHT": "#203D32",
            "GREEN_BORDER": "#35D07F",
            "TEXT": "#F0F3F9",
            "MUTED": "#A0AABD",
            "BORDER": "#30394A",
            "RED": "#FF6875",
            "ROW_ALT": "#1D2431",
            "BUTTON_BG": "#273246",
            "BUTTON_FG": "#E5EDFF",
            "GRID": "#30394A",
            "MENU_ACTIVE_BG": "#303D53",
            "MENU_ACTIVE_FG": "#FFFFFF",
        },
    }

    def __init__(self, parent, theme=None):
        self.parent = parent
        self.theme_name = self._normalize_theme(
            theme if theme is not None else self._get_parent_theme()
        )
        self._set_theme_colors(self.theme_name)

        today = date.today()
        self.year, self.month = today.year, today.month
        self._refresh_after_resize = None
        self._last_layout_width = None
        self._destroyed = False

        self.main_frame = tk.Frame(parent, bg=self.BG)
        self.main_frame.pack(fill="both", expand=True)

        self._build()
        self.refresh()

    # ========================================================
    # THEME
    # ========================================================

    def _normalize_theme(self, name):
        name = str(name or "light").strip().lower()
        if name in ("dark", "dark mode"):
            return "dark"
        return "light"

    def _get_parent_theme(self):
        objects = [self.parent]

        try:
            objects.append(self.parent.master)
            objects.append(self.parent.winfo_toplevel())
        except (tk.TclError, AttributeError):
            pass

        for obj in objects:
            if obj is None:
                continue

            for attr in ("theme_name", "current_theme", "theme"):
                value = getattr(obj, attr, None)

                if isinstance(value, str):
                    value = value.strip().lower()
                    if value in ("dark", "dark mode"):
                        return "dark"
                    if value in ("light", "light mode", "white", "white mode"):
                        return "light"

                if isinstance(value, dict):
                    value = str(
                        value.get("name", value.get("mode", ""))
                    ).strip().lower()
                    if value in ("dark", "dark mode"):
                        return "dark"
                    if value in ("light", "light mode", "white", "white mode"):
                        return "light"

        return "light"

    def _set_theme_colors(self, theme_name):
        self.theme_name = self._normalize_theme(theme_name)
        for name, value in self.THEMES[self.theme_name].items():
            setattr(self, name, value)

    def apply_theme(self, theme_name=None):
        """Apply a new theme while keeping habit data in the database."""
        if self._destroyed:
            return

        new_theme = self._normalize_theme(
            theme_name if theme_name is not None else self._get_parent_theme()
        )

        if new_theme == self.theme_name:
            return

        self._set_theme_colors(new_theme)

        # Rebuild the view so all existing widgets, including table cells,
        # chart, buttons, and popup colors, use the selected palette.
        try:
            self._cancel_resize_refresh()
            self.table_canvas.unbind_all("<Shift-MouseWheel>")
            self.main_frame.destroy()
        except (tk.TclError, AttributeError):
            pass

        self._last_layout_width = None
        self.main_frame = tk.Frame(self.parent, bg=self.BG)
        self.main_frame.pack(fill="both", expand=True)

        self._build()
        self.refresh()

    # ========================================================
    # UI HELPERS
    # ========================================================

    def _label(
        self, parent, text, size=20, color=None, bold=False, **kwargs
    ):
        bg = kwargs.pop("bg", self.WHITE)
        return tk.Label(
            parent,
            text=text,
            font=(self.FONT, size, "bold" if bold else "normal"),
            fg=color or self.TEXT,
            bg=bg,
            **kwargs,
        )

    def _button(self, parent, text, command, primary=False, compact=False):
        bg = self.NAVY if primary else self.BUTTON_BG
        fg = "#FFFFFF" if primary else self.BUTTON_FG

        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(self.FONT, 15, "bold"),
            fg=fg,
            bg=bg,
            activeforeground=fg,
            activebackground=bg,
            relief="flat",
            bd=0,
            padx=10 if compact else 15,
            pady=5 if compact else 8,
            cursor="hand2",
        )

    # ========================================================
    # LAYOUT
    # ========================================================

    def _build(self):
        header = tk.Frame(self.main_frame, bg=self.BG)
        header.pack(fill="x", padx=18, pady=(14, 8))

        title_box = tk.Frame(header, bg=self.BG)
        title_box.pack(side="left", fill="x", expand=True)

        self._label(
            title_box, "Habit Tracker", 22, self.NAVY, True, bg=self.BG
        ).pack(anchor="w")

        self._label(
            title_box,
            "Build consistency one day at a time.",
            9, self.MUTED, bg=self.BG,
        ).pack(anchor="w", pady=(2, 0))

        self._button(header, "History", self.show_archived).pack(
            side="right", padx=(7, 0)
        )
        self._button(
            header, "+ Add habit", self.add_habit, primary=True
        ).pack(side="right")

        # Summary cards
        overview = tk.Frame(self.main_frame, bg=self.BG)
        overview.pack(fill="x", padx=14, pady=(0, 8))

        for col in range(4):
            overview.grid_columnconfigure(col, weight=1, uniform="summary")

        self.summary_values = []
        summaries = [
            "HABITS START DATE",
            "BEST HABIT",
            "TODAY'S COMPLETION",
            "MONTH COMPLETION",
        ]

        for col, heading in enumerate(summaries):
            card = tk.Frame(
                overview,
                bg=self.WHITE,
                highlightbackground=self.BORDER,
                highlightthickness=1,
            )
            card.grid(row=0, column=col, sticky="nsew", padx=3, pady=2)

            self._label(
                card, heading, 8, "#FFFFFF", True,
                bg=self.NAVY, anchor="center",
            ).pack(fill="x", padx=8, pady=(8, 0))

            value = self._label(
                card, "—", 12, self.TEXT, True,
                bg=self.WHITE, anchor="center",
            )
            value.pack(fill="x", padx=8, pady=(6, 9))
            self.summary_values.append(value)

        # Chart and month navigation
        chart_card = tk.Frame(
            self.main_frame,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        chart_card.pack(fill="x", padx=18, pady=(0, 8))

        chart_header = tk.Frame(chart_card, bg=self.WHITE)
        chart_header.pack(fill="x", padx=12, pady=(7, 1))

        self._label(
            chart_header, "Daily completion trend", 10, self.NAVY, True
        ).pack(side="left")

        self._button(
            chart_header, "›", lambda: self.change_month(1), compact=True
        ).pack(side="right")

        self.month_title = self._label(
            chart_header, "", 9, self.NAVY, True
        )
        self.month_title.pack(side="right", padx=8)

        self._button(
            chart_header, "‹", lambda: self.change_month(-1), compact=True
        ).pack(side="right")

        self.chart = tk.Canvas(
            chart_card, height=200, bg=self.WHITE, highlightthickness=0
        )
        self.chart.pack(fill="x", padx=10, pady=(0, 5))
        self.chart.bind(
            "<Configure>",
            lambda _e: self._draw_chart(get_active_habits()),
        )

        # Monthly table
        tracker_card = tk.Frame(
            self.main_frame,
            bg=self.WHITE,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        tracker_card.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        tracker_header = tk.Frame(tracker_card, bg=self.WHITE)
        tracker_header.pack(fill="x", padx=11, pady=(8, 5))

        self._label(
            tracker_header, "Monthly habit checklist", 11, self.NAVY, True
        ).pack(side="left")

        self._label(
            tracker_header,
            "Click a cell or checkbox to mark it complete",
            8, self.MUTED,
        ).pack(side="right")

        scroll_frame = tk.Frame(tracker_card, bg=self.WHITE)
        scroll_frame.pack(fill="both", expand=True, padx=7, pady=(0, 7))

        self.table_canvas = tk.Canvas(
            scroll_frame, bg=self.WHITE, highlightthickness=0
        )
        self.v_scroll = tk.Scrollbar(
            scroll_frame, orient="vertical",
            command=self.table_canvas.yview,
        )
        self.h_scroll = tk.Scrollbar(
            scroll_frame, orient="horizontal",
            command=self.table_canvas.xview,
        )

        self.table_canvas.configure(
            yscrollcommand=self.v_scroll.set,
            xscrollcommand=self.h_scroll.set,
        )

        self.v_scroll.pack(side="right", fill="y")
        self.h_scroll.pack(side="bottom", fill="x")
        self.table_canvas.pack(side="left", fill="both", expand=True)

        self.table_inner = tk.Frame(self.table_canvas, bg=self.WHITE)
        self.table_window = self.table_canvas.create_window(
            (0, 0), window=self.table_inner, anchor="nw"
        )

        self.table_inner.bind(
            "<Configure>", self._update_scrollregion
        )
        self.table_canvas.bind(
            "<Configure>", self._canvas_resized
        )
        self.table_canvas.bind_all(
            "<Shift-MouseWheel>", self._horizontal_wheel
        )

    # ========================================================
    # RESIZING AND SCROLLING
    # ========================================================

    def _update_scrollregion(self, _event=None):
        self.table_canvas.configure(
            scrollregion=self.table_canvas.bbox("all")
        )

    def _canvas_resized(self, event):
        self._update_scrollregion()
        width = event.width
        previous = self._last_layout_width

        if previous is None:
            self._last_layout_width = width
        elif abs(width - previous) >= 35:
            self._last_layout_width = width
            if self._refresh_after_resize is not None:
                self.main_frame.after_cancel(self._refresh_after_resize)

            self._refresh_after_resize = self.main_frame.after(
                120, self._refresh_for_resize
            )

    def _refresh_for_resize(self):
        self._refresh_after_resize = None
        if self.main_frame.winfo_exists():
            self.refresh()

    def _horizontal_wheel(self, event):
        self.table_canvas.xview_scroll(
            int(-event.delta / 120), "units"
        )
        return "break"

    def _cancel_resize_refresh(self):
        if self._refresh_after_resize is not None:
            try:
                self.main_frame.after_cancel(self._refresh_after_resize)
            except tk.TclError:
                pass
            self._refresh_after_resize = None

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(self):
        habits = get_active_habits()
        today = date.today()

        try:
            progress = get_today_progress()
        except Exception:
            completed = sum(
                1 for h in habits if is_completed(h["id"], today)
            )
            progress = {
                "completed": completed,
                "total": len(habits),
            }

        try:
            percentage = get_month_percentage(self.year, self.month)
        except Exception:
            percentage = 0

        start_dates = []
        for habit in habits:
            raw = habit.get("created_date")
            if raw:
                try:
                    start_dates.append(date.fromisoformat(str(raw)[:10]))
                except (ValueError, TypeError):
                    pass

        start_text = (
            min(start_dates).strftime("%-d %b")
            if start_dates else "No habits"
        )

        counts = {
            habit["id"]: self._completion_count(
                habit["id"], self.year, self.month
            )
            for habit in habits
        }

        best = max(
            habits,
            key=lambda h: counts.get(h["id"], 0),
            default=None,
        )
        best_text = best["name"] if best else "—"
        if len(best_text) > 20:
            best_text = best_text[:17] + "…"

        self.summary_values[0].config(text=start_text)
        self.summary_values[1].config(text=best_text)
        self.summary_values[2].config(
            text=f"{progress.get('completed', 0)} / "
                 f"{progress.get('total', 0)}"
        )
        self.summary_values[3].config(text=f"{percentage:.0f}%")

        self.month_title.config(
            text=date(self.year, self.month, 1).strftime("%B %Y")
        )

        self._draw_chart(habits)
        self._draw_tracker(habits)

    def _completion_count(self, habit_id, year, month):
        con = get_connection()
        try:
            first_day = date(year, month, 1).isoformat()
            last_day = date(
                year, month, calendar.monthrange(year, month)[1]
            ).isoformat()

            row = con.execute(
                """
                SELECT COUNT(*) AS n
                FROM habit_days
                WHERE habit_id = ? AND completed = 1
                  AND date >= ? AND date <= ?
                """,
                (habit_id, first_day, last_day),
            ).fetchone()

            return int(row["n"] if row else 0)
        finally:
            con.close()

    # ========================================================
    # CHART
    # ========================================================

    def _draw_chart(self, habits):
        if not hasattr(self, "chart") or not self.chart.winfo_exists():
            return

        self.chart.delete("all")
        width = max(self.chart.winfo_width(), 420)
        left, right, top, bottom = 38, width - 12, 10, 72
        days = calendar.monthrange(self.year, self.month)[1]

        for label, y in [
            ("100%", top),
            ("50%", (top + bottom) / 2),
            ("0%", bottom),
        ]:
            self.chart.create_text(
                2, y, text=label, anchor="w", fill=self.MUTED,
                font=(self.FONT, 7),
            )
            self.chart.create_line(
                left, y, right, y,
                fill=self.GRID, dash=(2, 3),
            )

        points = []
        for number in range(1, days + 1):
            chosen = date(self.year, self.month, number)
            completed = sum(
                1 for habit in habits
                if is_completed(habit["id"], chosen)
            )
            percent = completed / len(habits) * 100 if habits else 0

            x = left + (number - 1) * (right - left) / max(days - 1, 1)
            y = bottom - percent / 100 * (bottom - top)
            points.extend((x, y))

            self.chart.create_text(
                x, bottom + 13, text=str(number),
                fill=self.MUTED, font=(self.FONT, 7),
            )

        if len(points) >= 4:
            self.chart.create_line(
                *points, fill=self.GREEN, width=2, smooth=False
            )
            for i in range(0, len(points), 2):
                x, y = points[i], points[i + 1]
                self.chart.create_oval(
                    x - 2.5, y - 2.5, x + 2.5, y + 2.5,
                    fill=self.GREEN, outline=self.GREEN,
                )

    # ========================================================
    # MONTHLY TRACKER
    # ========================================================

    def _draw_tracker(self, habits):
        for child in self.table_inner.winfo_children():
            child.destroy()

        days = calendar.monthrange(self.year, self.month)[1]
        self.table_canvas.update_idletasks()
        available = max(self.table_canvas.winfo_width(), 720)

        name_width = max(140, min(220, int(available * 0.19)))
        total_width = max(88, min(120, int(available * 0.10)))
        day_width = max(
            27, min(73, (available - name_width - total_width) // days)
        )
        row_height = 35
        total_col = days + 1

        name_header = tk.Frame(
            self.table_inner, bg=self.NAVY,
            width=name_width, height=63,
        )
        name_header.grid(row=0, column=0, rowspan=2, sticky="nsew")
        name_header.grid_propagate(False)

        self._label(
            name_header, "HABIT NAME", 10, "#FFFFFF", True,
            bg=self.NAVY, anchor="w",
        ).pack(side="bottom", anchor="w", padx=8, pady=7)

        week_colors = [
            self.BLUE, self.BLUE2, self.CYAN, self.NAVY, self.BLUE
        ]

        for start in range(1, days + 1, 7):
            end = min(start + 6, days)
            week_index = (start - 1) // 7
            color = week_colors[week_index % len(week_colors)]

            band = tk.Frame(
                self.table_inner, bg=color, height=27
            )
            band.grid(
                row=0, column=start,
                columnspan=end - start + 1, sticky="nsew",
            )

            self._label(
                band, f"WEEK {week_index + 1}",
                8, "#FFFFFF", True, bg=color,
            ).pack(fill="both", expand=True, pady=3)

        total_header = tk.Frame(
            self.table_inner, bg=self.NAVY,
            width=total_width, height=63,
        )
        total_header.grid(
            row=0, column=total_col, rowspan=2, sticky="nsew"
        )
        total_header.grid_propagate(False)

        self._label(
            total_header, "TOTAL\nDONE", 8, "#FFFFFF", True,
            bg=self.NAVY, justify="center",
        ).pack(expand=True)

        for day_num in range(1, days + 1):
            chosen = date(self.year, self.month, day_num)
            week_index = (day_num - 1) // 7
            color = week_colors[week_index % len(week_colors)]

            header_cell = tk.Frame(
                self.table_inner,
                bg=color,
                width=day_width,
                height=36,
            )
            header_cell.grid(row=1, column=day_num, sticky="nsew")
            header_cell.grid_propagate(False)

            self._label(
                header_cell,
                f"{chosen.strftime('%a')[:3]}\n{day_num}",
                7, "#FFFFFF", True, bg=color, justify="center",
            ).pack(expand=True)

        if not habits:
            empty = tk.Frame(self.table_inner, bg=self.WHITE)
            empty.grid(
                row=2, column=0, columnspan=days + 2,
                sticky="ew", pady=24,
            )

            self._label(
                empty, "Start with one small habit.",
                12, self.NAVY, True,
            ).pack(pady=(8, 4))

            self._label(
                empty,
                "Click “+ Add habit” to create your first daily checklist.",
                9, self.MUTED,
            ).pack(pady=(0, 8))

            self._configure_columns(
                days, name_width, day_width, total_col, total_width
            )
            self._update_scrollregion()
            return

        for row_number, habit in enumerate(habits, start=2):
            base_bg = (
                self.WHITE if row_number % 2 == 0 else self.ROW_ALT
            )

            name_cell = tk.Frame(
                self.table_inner,
                bg=base_bg,
                width=name_width,
                height=row_height,
                highlightbackground=self.BORDER,
                highlightthickness=1,
            )
            name_cell.grid(row=row_number, column=0, sticky="nsew")
            name_cell.grid_propagate(False)

            name_row = tk.Frame(name_cell, bg=base_bg)
            name_row.pack(fill="both", expand=True, padx=6)

            self._label(
                name_row, habit["name"], 8, self.TEXT, True,
                bg=base_bg, anchor="w",
            ).pack(side="left", fill="x", expand=True)

            self._button(
                name_row, "⋯",
                lambda h=habit: self.habit_menu(h),
                compact=True,
            ).pack(side="right", padx=(2, 0), pady=2)

            total = 0

            for day_num in range(1, days + 1):
                chosen = date(self.year, self.month, day_num)
                done = is_completed(habit["id"], chosen)
                total += int(done)

                cell_bg = self.GREEN_LIGHT if done else base_bg
                border = self.GREEN_BORDER if done else self.BORDER

                cell = tk.Frame(
                    self.table_inner,
                    bg=cell_bg,
                    width=day_width,
                    height=row_height,
                    highlightbackground=border,
                    highlightthickness=1,
                    cursor="hand2",
                )
                cell.grid(
                    row=row_number, column=day_num, sticky="nsew"
                )
                cell.grid_propagate(False)

                variable = tk.BooleanVar(value=done)

                check = tk.Checkbutton(
                    cell,
                    variable=variable,
                    command=lambda h=habit, d=chosen, v=variable:
                        self.set_day_completion(
                            h["id"], d, v.get()
                        ),
                    bg=cell_bg,
                    activebackground=cell_bg,
                    selectcolor=self.GREEN,
                    fg=self.GREEN,
                    activeforeground=self.GREEN,
                    bd=0,
                    highlightthickness=0,
                    cursor="hand2",
                    padx=0,
                    pady=0,
                )
                check.pack(expand=True)

                cell.bind(
                    "<Button-1>",
                    lambda _event, h=habit, d=chosen, v=variable:
                        self.set_day_completion(
                            h["id"], d, not v.get()
                        ),
                )

            total_cell = tk.Frame(
                self.table_inner,
                bg=base_bg,
                width=total_width,
                height=row_height,
                highlightbackground=self.BORDER,
                highlightthickness=1,
            )
            total_cell.grid(
                row=row_number, column=total_col, sticky="nsew"
            )
            total_cell.grid_propagate(False)

            self._label(
                total_cell, f"{total}/{days}", 8,
                self.GREEN if total else self.MUTED,
                True, bg=base_bg,
            ).pack(expand=True)

        self._configure_columns(
            days, name_width, day_width, total_col, total_width
        )
        self._update_scrollregion()

    def _configure_columns(
        self, days, name_width, day_width, total_col, total_width
    ):
        self.table_inner.grid_columnconfigure(
            0, minsize=name_width, weight=0
        )

        for col in range(1, days + 1):
            self.table_inner.grid_columnconfigure(
                col, minsize=day_width, weight=0
            )

        self.table_inner.grid_columnconfigure(
            total_col, minsize=total_width, weight=0
        )

    # ========================================================
    # HABIT MANAGEMENT
    # ========================================================

    def add_habit(self):
        name = simpledialog.askstring(
            "Add habit",
            "What habit would you like to track?",
            parent=self.main_frame,
        )

        if name is None:
            return

        name = name.strip()
        if not name:
            messagebox.showwarning(
                "Name required", "Please enter a habit name.",
                parent=self.main_frame,
            )
            return

        if any(
            h["name"].casefold() == name.casefold()
            for h in get_active_habits()
        ):
            messagebox.showinfo(
                "Already exists", "That active habit already exists.",
                parent=self.main_frame,
            )
            return

        try:
            create_habit(name)
            self.refresh()
        except Exception as exc:
            messagebox.showerror(
                "Could not add habit", str(exc),
                parent=self.main_frame,
            )

    def set_day_completion(self, habit_id, chosen_date, completed):
        try:
            set_completion(habit_id, chosen_date, completed)
        except Exception as exc:
            messagebox.showerror(
                "Could not update completion", str(exc),
                parent=self.main_frame,
            )

        self.refresh()

    def habit_menu(self, habit):
        menu = tk.Menu(
            self.main_frame,
            tearoff=0,
            bg=self.WHITE,
            fg=self.TEXT,
            activebackground=self.MENU_ACTIVE_BG,
            activeforeground=self.MENU_ACTIVE_FG,
        )

        menu.add_command(
            label="Rename",
            command=lambda: self.rename_habit(habit),
        )
        menu.add_command(
            label="Archive",
            command=lambda: self.archive_habit(habit),
        )
        menu.add_command(
            label="Delete permanently…",
            command=lambda: self.permanently_delete(habit),
        )

        try:
            menu.tk_popup(
                self.main_frame.winfo_pointerx(),
                self.main_frame.winfo_pointery(),
            )
        finally:
            menu.grab_release()

    def rename_habit(self, habit):
        name = simpledialog.askstring(
            "Rename habit",
            "New habit name:",
            initialvalue=habit["name"],
            parent=self.main_frame,
        )

        if name is None:
            return

        name = name.strip()
        if not name:
            messagebox.showwarning(
                "Name required", "Habit name cannot be empty.",
                parent=self.main_frame,
            )
            return

        try:
            con = get_connection()
            try:
                con.execute(
                    "UPDATE habits SET name = ? WHERE id = ?",
                    (name, habit["id"]),
                )
                con.commit()
            finally:
                con.close()

            self.refresh()
        except Exception as exc:
            messagebox.showerror(
                "Could not rename habit", str(exc),
                parent=self.main_frame,
            )

    def archive_habit(self, habit):
        if not messagebox.askyesno(
            "Archive habit",
            f"Archive “{habit['name']}”? Your history will be kept.",
            parent=self.main_frame,
        ):
            return

        try:
            deactivate_habit(habit["id"])
            self.refresh()
        except Exception as exc:
            messagebox.showerror(
                "Could not archive habit", str(exc),
                parent=self.main_frame,
            )

    def permanently_delete(self, habit):
        if not messagebox.askyesno(
            "Delete permanently",
            f"Delete “{habit['name']}” and its completion history? "
            "This cannot be undone.",
            parent=self.main_frame,
        ):
            return

        try:
            delete_habit(habit["id"])
            self.refresh()
        except Exception as exc:
            messagebox.showerror(
                "Could not delete habit", str(exc),
                parent=self.main_frame,
            )

    # ========================================================
    # ARCHIVED HABITS
    # ========================================================

    def show_archived(self):
        try:
            archived = [
                h for h in get_all_habits()
                if not h.get("active", 1)
            ]
        except Exception as exc:
            messagebox.showerror(
                "Could not load history", str(exc),
                parent=self.main_frame,
            )
            return

        win = tk.Toplevel(self.main_frame)
        win.title("Archived habits")
        win.configure(bg=self.BG)
        win.geometry("460x420")
        win.minsize(340, 260)

        self._label(
            win, "Archived habits", 16, self.NAVY, True, bg=self.BG
        ).pack(anchor="w", padx=18, pady=(16, 10))

        if not archived:
            self._label(
                win, "No archived habits yet.",
                10, self.MUTED, bg=self.BG,
            ).pack(anchor="w", padx=18)
            return

        for habit in archived:
            row = tk.Frame(
                win,
                bg=self.WHITE,
                highlightbackground=self.BORDER,
                highlightthickness=1,
            )
            row.pack(fill="x", padx=14, pady=4)

            self._label(
                row, habit["name"], 9, bg=self.WHITE
            ).pack(side="left", padx=10, pady=9)

            self._button(
                row,
                "Restore",
                lambda h=habit, w=win: self.restore_habit(h, w),
                primary=True,
                compact=True,
            ).pack(side="right", padx=7, pady=4)

    def restore_habit(self, habit, window):
        try:
            con = get_connection()
            try:
                con.execute(
                    "UPDATE habits SET active = 1 WHERE id = ?",
                    (habit["id"],),
                )
                con.commit()
            finally:
                con.close()

            window.destroy()
            self.refresh()
        except Exception as exc:
            messagebox.showerror(
                "Could not restore habit", str(exc),
                parent=window,
            )

    # ========================================================
    # MONTH NAVIGATION
    # ========================================================

    def change_month(self, offset):
        month = self.month + offset
        year = self.year

        if month < 1:
            month, year = 12, year - 1
        elif month > 12:
            month, year = 1, year + 1

        self.month, self.year = month, year
        self.refresh()

    # ========================================================
    # CLEANUP
    # ========================================================

    def destroy(self):
        self._cancel_resize_refresh()

        try:
            self.table_canvas.unbind_all("<Shift-MouseWheel>")
        except (tk.TclError, AttributeError):
            pass

        self._destroyed = True

        try:
            if self.main_frame.winfo_exists():
                self.main_frame.destroy()
        except tk.TclError:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Social Lock — Habit Tracker")
    root.geometry("1200x800")
    root.minsize(800, 550)

    view = HabitsView(root)

    def close_app():
        view.destroy()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()
