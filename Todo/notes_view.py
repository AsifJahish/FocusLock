
# #!/usr/bin/env python3
# """
# Social Lock — Daily Notes
# Keeps the existing calendar and journal layout while supporting
# the dark/light theme selected by the parent application.
# """

# import calendar
# import tkinter as tk
# from tkinter import ttk, messagebox
# from datetime import date, timedelta

# from notes import save_note, get_note


# class NotesView:
#     # Default theme (used by the standalone test)
#     BG = "#0F1117"
#     SIDEBAR = "#151821"
#     CARD = "#1B1F2A"
#     INPUT = "#151821"
#     BORDER = "#292E3A"
#     TEXT = "#F4F6FA"
#     MUTED = "#8D94A6"
#     ACCENT = "#7C5CFC"
#     ACCENT_HOVER = "#6846EA"
#     GREEN = "#35D07F"
#     RED = "#FF5C68"
#     YELLOW = "#F4C76B"
#     FONT = "DejaVu Sans"

#     THEMES = {
#         "dark": {
#             "BG": "#0F1117",
#             "SIDEBAR": "#151821",
#             "CARD": "#1B1F2A",
#             "INPUT": "#151821",
#             "BORDER": "#292E3A",
#             "TEXT": "#F4F6FA",
#             "MUTED": "#8D94A6",
#             "ACCENT": "#7C5CFC",
#             "ACCENT_HOVER": "#6846EA",
#             "GREEN": "#35D07F",
#             "RED": "#FF5C68",
#             "YELLOW": "#F4C76B",
#             "TODAY_BG": "#263D36",
#             "TODAY_FG": "#35D07F",
#             "WHITE": "#FFFFFF",
#         },
#         "light": {
#             "BG": "#F4F6FA",
#             "SIDEBAR": "#E9ECF3",
#             "CARD": "#FFFFFF",
#             "INPUT": "#F8F9FC",
#             "BORDER": "#D9DEEA",
#             "TEXT": "#202433",
#             "MUTED": "#697386",
#             "ACCENT": "#7C5CFC",
#             "ACCENT_HOVER": "#6846EA",
#             "GREEN": "#168653",
#             "RED": "#D93648",
#             "YELLOW": "#9A6A00",
#             "TODAY_BG": "#DDF5E8",
#             "TODAY_FG": "#168653",
#             "WHITE": "#FFFFFF",
#         },
#     }

#     MOODS = [
#         "",
#         "😊 Happy",
#         "🎯 Focused",
#         "😌 Calm",
#         "💪 Motivated",
#         "😐 Okay",
#         "😔 Sad",
#         "😫 Stressed",
#         "😴 Tired",
#     ]

#     def __init__(self, parent):
#         self.parent = parent
#         self.selected_date = date.today()
#         self._loading = False
#         self._dirty = False
#         self._save_job = None
#         self._destroyed = False
#         self.calendar_year = self.selected_date.year
#         self.calendar_month = self.selected_date.month
#         self._widget_registry = []

#         self.theme_name = self._get_parent_theme()
#         self._set_theme_colors(self.theme_name)

#         self.main_frame = tk.Frame(parent, bg=self.BG)
#         self.main_frame.pack(fill="both", expand=True)

#         self._configure_styles()
#         self._build_layout()
#         self.render_calendar()
#         self.load_note()

#         # Watch for theme changes on the parent app, if it exposes a theme variable.
#         self._theme_poll_job = self.main_frame.after(400, self._watch_theme)

#     # ========================================================
#     # THEME INTEGRATION
#     # ========================================================

#     def _get_parent_theme(self):
#         """Find the current theme name from the main application if available."""
#         candidates = [
#             getattr(self.parent, "theme_name", None),
#             getattr(getattr(self.parent, "master", None), "theme_name", None),
#             getattr(getattr(self.parent, "winfo_toplevel", lambda: None)(), "theme_name", None),
#         ]

#         for candidate in candidates:
#             if isinstance(candidate, str):
#                 normalized = candidate.strip().lower()
#                 if normalized in ("light", "white", "light mode", "white mode"):
#                     return "light"
#                 if normalized in ("dark", "dark mode"):
#                     return "dark"

#         # Some apps store the theme in a dictionary.
#         for obj in (self.parent, getattr(self.parent, "master", None),
#                     getattr(self.parent, "winfo_toplevel", lambda: None)()):
#             if obj is None:
#                 continue
#             for attr in ("current_theme", "theme"):
#                 value = getattr(obj, attr, None)
#                 if isinstance(value, str):
#                     normalized = value.strip().lower()
#                     if normalized in ("light", "white", "light mode", "white mode"):
#                         return "light"
#                     if normalized in ("dark", "dark mode"):
#                         return "dark"
#                 if isinstance(value, dict):
#                     name = str(value.get("name", value.get("mode", ""))).lower()
#                     if name in ("light", "white", "light mode", "white mode"):
#                         return "light"
#                     if name in ("dark", "dark mode"):
#                         return "dark"

#         return "dark"

#     def _set_theme_colors(self, theme_name):
#         theme_name = str(theme_name or "dark").strip().lower()
#         if theme_name in ("white", "light mode", "white mode"):
#             theme_name = "light"
#         if theme_name not in self.THEMES:
#             theme_name = "dark"

#         self.theme_name = theme_name
#         palette = self.THEMES[theme_name]
#         for name, value in palette.items():
#             setattr(self, name, value)

#     def apply_theme(self, theme_name=None):
#         """
#         Call this from main.py immediately after the user changes theme:
#             notes_view.apply_theme("light")
#             notes_view.apply_theme("dark")
#         """
#         if self._destroyed:
#             return

#         if theme_name is None:
#             theme_name = self._get_parent_theme()

#         normalized = str(theme_name).strip().lower()
#         if normalized in ("white", "light mode", "white mode"):
#             normalized = "light"
#         elif normalized in ("dark mode",):
#             normalized = "dark"

#         if normalized not in self.THEMES:
#             normalized = self._get_parent_theme()

#         if normalized == self.theme_name and self._widget_registry:
#             return

#         self._set_theme_colors(normalized)
#         try:
#             self.main_frame.configure(bg=self.BG)
#         except tk.TclError:
#             pass
#         self._configure_styles()
#         self._apply_widget_colors()
#         self.render_calendar()

#     def _watch_theme(self):
#         if self._destroyed:
#             return
#         try:
#             latest = self._get_parent_theme()
#             if latest != self.theme_name:
#                 self.apply_theme(latest)
#             self._theme_poll_job = self.main_frame.after(400, self._watch_theme)
#         except tk.TclError:
#             self._theme_poll_job = None

#     def _register(self, widget, kind, base_bg=None, base_fg=None,
#                   hover_bg=None, primary=False):
#         self._widget_registry.append({
#             "widget": widget,
#             "kind": kind,
#             "base_bg": base_bg,
#             "base_fg": base_fg,
#             "hover_bg": hover_bg,
#             "primary": primary,
#         })
#         return widget

#     def _apply_widget_colors(self):
#         # Refresh all persistent widgets without rebuilding the editor,
#         # so the user's cursor position and draft text remain untouched.
#         for item in self._widget_registry:
#             widget = item["widget"]
#             try:
#                 if not widget.winfo_exists():
#                     continue
#                 kind = item["kind"]
#                 if kind == "frame":
#                     widget.configure(bg=self._color(item["base_bg"]))
#                 elif kind == "label":
#                     widget.configure(
#                         bg=self._color(item["base_bg"]),
#                         fg=self._color(item["base_fg"]),
#                     )
#                 elif kind == "button":
#                     primary = item["primary"]
#                     base = self.ACCENT if primary else self.CARD
#                     hover = self.ACCENT_HOVER if primary else self.BORDER
#                     widget.configure(
#                         bg=base,
#                         fg=self.WHITE if primary else self.TEXT,
#                         activebackground=hover,
#                         activeforeground=self.WHITE if primary else self.TEXT,
#                     )
#                 elif kind == "text":
#                     widget.configure(
#                         bg=self.INPUT,
#                         fg=self.TEXT,
#                         insertbackground=self.ACCENT,
#                         selectbackground=self.ACCENT_HOVER,
#                         selectforeground=self.WHITE,
#                     )
#                 elif kind == "separator":
#                     widget.configure(bg=self.BORDER)
#             except tk.TclError:
#                 pass

#         # Calendar-day buttons are recreated by render_calendar.
#         self._configure_styles()

#     def _color(self, name):
#         if not name:
#             return self.CARD
#         return getattr(self, name, name)

#     # ========================================================
#     # STYLES
#     # ========================================================

#     def _configure_styles(self):
#         style = ttk.Style(self.main_frame)
#         try:
#             style.theme_use("clam")
#         except tk.TclError:
#             pass

#         style.configure(
#             "Journal.TCombobox",
#             fieldbackground=self.INPUT,
#             background=self.CARD,
#             foreground=self.TEXT,
#             arrowcolor=self.ACCENT,
#             bordercolor=self.BORDER,
#             lightcolor=self.BORDER,
#             darkcolor=self.BORDER,
#             padding=8,
#         )
#         style.map(
#             "Journal.TCombobox",
#             fieldbackground=[("readonly", self.INPUT)],
#             foreground=[("readonly", self.TEXT)],
#             selectbackground=[("readonly", self.INPUT)],
#             selectforeground=[("readonly", self.TEXT)],
#         )
#         style.configure(
#             "Journal.Vertical.TScrollbar",
#             background=self.CARD,
#             troughcolor=self.INPUT,
#             bordercolor=self.BORDER,
#             arrowcolor=self.MUTED,
#         )

#     # ========================================================
#     # UI HELPERS
#     # ========================================================

#     def label(self, parent, text, size=10, color=None, bold=False,
#               bg=None, **kwargs):
#         bg_name = bg or "CARD"
#         fg_value = color or self.TEXT
#         # Existing call sites pass palette colors; retain them as literal colors.
#         widget = tk.Label(
#             parent,
#             text=text,
#             font=(self.FONT, size, "bold" if bold else "normal"),
#             fg=fg_value,
#             bg=self._color(bg_name),
#             **kwargs,
#         )
#         # Record palette key when it can be identified.
#         fg_name = next((key for key, value in self.THEMES[self.theme_name].items()
#                         if value == fg_value), fg_value)
#         self._register(widget, "label", bg_name, fg_name)
#         return widget

#     def button(self, parent, text, command, primary=False, width=None):
#         background = self.ACCENT if primary else self.CARD
#         foreground = self.WHITE if primary else self.TEXT
#         hover = self.ACCENT_HOVER if primary else self.BORDER
#         widget = tk.Button(
#             parent,
#             text=text,
#             command=command,
#             font=(self.FONT, 9, "bold"),
#             fg=foreground,
#             bg=background,
#             activeforeground=self.WHITE if primary else self.TEXT,
#             activebackground=hover,
#             relief="flat",
#             bd=0,
#             padx=12,
#             pady=9,
#             cursor="hand2",
#             width=width,
#             highlightthickness=0,
#         )
#         widget.bind("<Enter>", lambda event, b=widget, h=hover: b.config(bg=h))
#         widget.bind(
#             "<Leave>",
#             lambda event, b=widget, base=background: b.config(bg=base),
#         )
#         self._register(widget, "button", primary=primary)
#         return widget

#     def make_card(self, parent):
#         widget = tk.Frame(
#             parent,
#             bg=self.CARD,
#             highlightbackground=self.BORDER,
#             highlightthickness=1,
#         )
#         self._register(widget, "frame", "CARD")
#         return widget

#     def separator(self, parent):
#         widget = tk.Frame(parent, bg=self.BORDER, height=1)
#         widget.pack(fill="x")
#         self._register(widget, "separator")
#         return widget

#     def _frame(self, parent, color="CARD", **kwargs):
#         widget = tk.Frame(parent, bg=self._color(color), **kwargs)
#         self._register(widget, "frame", color)
#         return widget

#     # ========================================================
#     # MAIN LAYOUT
#     # ========================================================

#     def _build_layout(self):
#         header = self._frame(self.main_frame, "BG")
#         header.pack(fill="x", padx=28, pady=(24, 20))

#         title_area = self._frame(header, "BG")
#         title_area.pack(side="left", fill="x", expand=True)

#         self.label(title_area, "YOUR PERSONAL SPACE", 9, self.ACCENT, True, bg="BG").pack(anchor="w")
#         self.label(title_area, "Daily Notes", 25, self.TEXT, True, bg="BG").pack(anchor="w", pady=(5, 3))
#         self.label(title_area, "Clear your mind. Reflect on your day. Keep growing.", 10, self.MUTED, bg="BG").pack(anchor="w")
#         self.button(header, "↩ Today", self.go_to_today).pack(side="right", anchor="center")

#         content = self._frame(self.main_frame, "BG")
#         content.pack(fill="both", expand=True, padx=28, pady=(0, 20))
#         content.grid_columnconfigure(0, minsize=280, weight=0)
#         content.grid_columnconfigure(1, weight=1)
#         content.grid_rowconfigure(0, weight=1)

#         self.calendar_panel = self.make_card(content)
#         self.calendar_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
#         self._build_calendar_panel()

#         self.editor_panel = self.make_card(content)
#         self.editor_panel.grid(row=0, column=1, sticky="nsew")
#         self._build_editor_panel()

#     # ========================================================
#     # CALENDAR PANEL
#     # ========================================================

#     def _build_calendar_panel(self):
#         panel = self.calendar_panel

#         heading = self._frame(panel)
#         heading.pack(fill="x", padx=18, pady=(20, 8))
#         self.label(heading, "Calendar", 15, self.TEXT, True).pack(anchor="w")
#         self.label(heading, "Choose a day to open your notes", 9, self.MUTED).pack(anchor="w", pady=(5, 0))
#         self.separator(panel)

#         month_bar = self._frame(panel)
#         month_bar.pack(fill="x", padx=12, pady=(16, 12))
#         self.button(month_bar, "‹", self.previous_month, width=2).pack(side="left")
#         self.month_label = self.label(month_bar, "", 11, self.TEXT, True)
#         self.month_label.pack(side="left", fill="x", expand=True, padx=5)
#         self.button(month_bar, "›", self.next_month, width=2).pack(side="right")

#         self.calendar_grid = self._frame(panel)
#         self.calendar_grid.pack(fill="x", padx=10)
#         for column in range(7):
#             self.calendar_grid.grid_columnconfigure(column, weight=1, uniform="calendar")

#         self.separator(panel)
#         legend = self._frame(panel)
#         legend.pack(fill="x", padx=16, pady=16)
#         self.label(legend, "●", 10, self.ACCENT).pack(side="left")
#         self.label(legend, "Selected", 9, self.MUTED).pack(side="left", padx=(5, 12))
#         self.label(legend, "●", 10, self.GREEN).pack(side="left")
#         self.label(legend, "Today", 9, self.MUTED).pack(side="left", padx=5)

#         self.separator(panel)
#         summary = self._frame(panel)
#         summary.pack(fill="x", padx=18, pady=18)
#         self.label(summary, "SELECTED DATE", 8, self.MUTED, True).pack(anchor="w")
#         self.selected_date_label = self.label(summary, "", 12, self.TEXT, True)
#         self.selected_date_label.pack(anchor="w", pady=(7, 5))
#         self.selected_date_status = self.label(summary, "", 9, self.MUTED)
#         self.selected_date_status.pack(anchor="w")
#         self.button(summary, "Open today's notes", self.go_to_today).pack(fill="x", pady=(16, 0))

#     def render_calendar(self):
#         for widget in self.calendar_grid.winfo_children():
#             widget.destroy()

#         month_name = date(self.calendar_year, self.calendar_month, 1).strftime("%B %Y")
#         self.month_label.config(text=month_name)

#         weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
#         for column, day_name in enumerate(weekdays):
#             self.label(self.calendar_grid, day_name, 8, self.MUTED, True).grid(
#                 row=0, column=column, sticky="nsew", pady=(0, 10)
#             )

#         cal = calendar.Calendar(firstweekday=calendar.MONDAY)
#         weeks = cal.monthdayscalendar(self.calendar_year, self.calendar_month)

#         for row, week in enumerate(weeks, start=1):
#             for column, day_number in enumerate(week):
#                 if day_number == 0:
#                     tk.Frame(self.calendar_grid, bg=self.CARD, height=35).grid(
#                         row=row, column=column, sticky="nsew", padx=1, pady=2
#                     )
#                     continue

#                 current_date = date(self.calendar_year, self.calendar_month, day_number)
#                 is_selected = current_date == self.selected_date
#                 is_today = current_date == date.today()

#                 if is_selected:
#                     background, foreground = self.ACCENT, self.WHITE
#                 elif is_today:
#                     background, foreground = self.TODAY_BG, self.TODAY_FG
#                 else:
#                     background, foreground = self.CARD, self.TEXT

#                 day_button = tk.Button(
#                     self.calendar_grid,
#                     text=str(day_number),
#                     command=lambda d=current_date: self.select_date(d),
#                     font=(self.FONT, 9, "bold" if is_selected or is_today else "normal"),
#                     fg=foreground,
#                     bg=background,
#                     activeforeground=self.WHITE,
#                     activebackground=self.ACCENT_HOVER,
#                     relief="flat",
#                     bd=0,
#                     cursor="hand2",
#                     height=1,
#                     padx=0,
#                     pady=8,
#                     highlightthickness=0,
#                 )
#                 day_button.grid(row=row, column=column, sticky="nsew", padx=2, pady=2)

#                 if not is_selected and not is_today:
#                     day_button.bind("<Enter>", lambda event, b=day_button: b.config(bg=self.BORDER))
#                     day_button.bind("<Leave>", lambda event, b=day_button: b.config(bg=self.CARD))

#         self.selected_date_label.config(text=self.selected_date.strftime("%d %B %Y"))

#     # ========================================================
#     # CALENDAR NAVIGATION
#     # ========================================================

#     def previous_month(self):
#         if self.calendar_month == 1:
#             self.calendar_month = 12
#             self.calendar_year -= 1
#         else:
#             self.calendar_month -= 1
#         self.render_calendar()

#     def next_month(self):
#         if self.calendar_month == 12:
#             self.calendar_month = 1
#             self.calendar_year += 1
#         else:
#             self.calendar_month += 1
#         self.render_calendar()

#     def select_date(self, chosen_date):
#         if chosen_date == self.selected_date:
#             return
#         self._cancel_pending_save()
#         if self._dirty and not self._write_current_note():
#             return
#         self.selected_date = chosen_date
#         self.calendar_year = chosen_date.year
#         self.calendar_month = chosen_date.month
#         self.render_calendar()
#         self.load_note()

#     def go_to_today(self):
#         self.select_date(date.today())

#     # ========================================================
#     # EDITOR PANEL
#     # ========================================================

#     def _build_editor_panel(self):
#         panel = self.editor_panel

#         heading = self._frame(panel)
#         heading.pack(fill="x", padx=22, pady=(20, 15))
#         title_area = self._frame(heading)
#         title_area.pack(side="left", fill="x", expand=True)

#         self.note_title = self.label(title_area, "Daily reflection", 16, self.TEXT, True)
#         self.note_title.pack(anchor="w")
#         self.note_subtitle = self.label(title_area, "", 9, self.MUTED)
#         self.note_subtitle.pack(anchor="w", pady=(5, 0))

#         status_area = self._frame(heading)
#         status_area.pack(side="right")
#         self.status_dot = self.label(status_area, "●", 9, self.GREEN)
#         self.status_dot.pack(side="left")
#         self.status_label = self.label(status_area, "Saved", 9, self.MUTED)
#         self.status_label.pack(side="left", padx=(5, 0))

#         self.separator(panel)

#         mood_row = self._frame(panel)
#         mood_row.pack(fill="x", padx=22, pady=(16, 10))
#         self.label(mood_row, "MOOD", 9, self.MUTED, True).pack(side="left", padx=(0, 14))
#         self.mood_var = tk.StringVar(value="")
#         self.mood_box = ttk.Combobox(
#             mood_row, textvariable=self.mood_var, values=self.MOODS,
#             state="readonly", width=17, style="Journal.TCombobox",
#             font=(self.FONT, 9),
#         )
#         self.mood_box.pack(side="left")
#         self.mood_box.bind("<<ComboboxSelected>>", self._on_mood_changed)

#         editor_container = tk.Frame(
#             panel, bg=self.INPUT, highlightbackground=self.BORDER, highlightthickness=1
#         )
#         self._register(editor_container, "frame", "INPUT")
#         editor_container.pack(fill="both", expand=True, padx=22, pady=(8, 14))

#         self.note_text = tk.Text(
#             editor_container,
#             font=(self.FONT, 11),
#             fg=self.TEXT,
#             bg=self.INPUT,
#             insertbackground=self.ACCENT,
#             selectbackground=self.ACCENT_HOVER,
#             selectforeground=self.WHITE,
#             wrap="word",
#             undo=True,
#             relief="flat",
#             bd=0,
#             padx=18,
#             pady=18,
#             spacing1=3,
#             spacing3=6,
#             highlightthickness=0,
#         )
#         self.note_text.pack(side="left", fill="both", expand=True)
#         self._register(self.note_text, "text")

#         scrollbar = ttk.Scrollbar(
#             editor_container, orient="vertical", command=self.note_text.yview,
#             style="Journal.Vertical.TScrollbar",
#         )
#         scrollbar.pack(side="right", fill="y")
#         self.note_text.configure(yscrollcommand=scrollbar.set)

#         self.note_text.bind("<KeyRelease>", self._on_text_changed)
#         self.note_text.bind("<<Paste>>", self._on_text_changed)
#         self.note_text.bind("<Control-s>", self._save_shortcut)

#         self.label(
#             panel,
#             "What mattered today? What did you learn? What comes next?",
#             9, self.MUTED,
#         ).pack(anchor="w", padx=23, pady=(0, 12))

#         footer = self._frame(panel)
#         footer.pack(fill="x", padx=22, pady=(0, 18))
#         counts = self._frame(footer)
#         counts.pack(side="left", fill="x", expand=True)
#         self.word_count_label = self.label(counts, "0 words", 9, self.MUTED)
#         self.word_count_label.pack(side="left")
#         self.label(counts, "  ·  ", 9, self.BORDER).pack(side="left")
#         self.char_count_label = self.label(counts, "0 characters", 9, self.MUTED)
#         self.char_count_label.pack(side="left")

#         actions = self._frame(footer)
#         actions.pack(side="right")
#         self.button(actions, "Clear", self.clear_note).pack(side="left", padx=(0, 8))
#         self.button(actions, "Save note  ✓", self.save_current_note, primary=True).pack(side="left")

#     # ========================================================
#     # LOAD NOTE
#     # ========================================================

#     def load_note(self):
#         self._cancel_pending_save()
#         self._loading = True
#         try:
#             entry = get_note(self.selected_date)
#             self.note_text.delete("1.0", "end")

#             if entry:
#                 self.note_text.insert("1.0", entry.get("note", "") or "")
#                 mood = entry.get("mood", "") or ""
#                 self.mood_var.set(mood if mood in self.MOODS else "")
#             else:
#                 self.mood_var.set("")

#             self._dirty = False
#             if self.selected_date == date.today():
#                 title = "Today's reflection"
#             elif self.selected_date == date.today() - timedelta(days=1):
#                 title = "Yesterday's reflection"
#             else:
#                 title = "Daily reflection"

#             self.note_title.config(text=title)
#             self.note_subtitle.config(text=self.selected_date.strftime("%A, %d %B %Y"))
#             self._set_status("All changes saved", self.GREEN)
#             self.update_word_count()

#             if entry and (entry.get("note", "") or "").strip():
#                 self.selected_date_status.config(text="Journal entry available", fg=self.GREEN)
#             else:
#                 self.selected_date_status.config(text="No written entry yet", fg=self.MUTED)

#         except Exception as error:
#             self._set_status("Unable to load", self.RED)
#             messagebox.showerror(
#                 "Notes Error",
#                 f"Could not load this day's note.\n\n{error}",
#                 parent=self.parent,
#             )
#         finally:
#             self._loading = False

#     # ========================================================
#     # EDIT TRACKING
#     # ========================================================

#     def _on_text_changed(self, event=None):
#         if self._loading or self._destroyed:
#             return
#         self._dirty = True
#         self.update_word_count()
#         self._set_status("Unsaved changes", self.YELLOW)
#         self._schedule_autosave()

#     def _on_mood_changed(self, event=None):
#         if self._loading or self._destroyed:
#             return
#         self._dirty = True
#         self._set_status("Unsaved changes", self.YELLOW)
#         self._schedule_autosave()

#     def update_word_count(self):
#         content = self.note_text.get("1.0", "end-1c")
#         words = len(content.split())
#         characters = len(content)
#         self.word_count_label.config(text=f"{words} {'word' if words == 1 else 'words'}")
#         self.char_count_label.config(
#             text=f"{characters} {'character' if characters == 1 else 'characters'}"
#         )

#     # ========================================================
#     # AUTOSAVE
#     # ========================================================

#     def _schedule_autosave(self):
#         self._cancel_pending_save()
#         self._save_job = self.main_frame.after(1000, self._autosave)

#     def _cancel_pending_save(self):
#         if self._save_job is not None:
#             try:
#                 self.main_frame.after_cancel(self._save_job)
#             except tk.TclError:
#                 pass
#             self._save_job = None

#     def _autosave(self):
#         self._save_job = None
#         if self._destroyed or not self._dirty:
#             return
#         self._write_current_note()

#     # ========================================================
#     # SAVE NOTE
#     # ========================================================

#     def _write_current_note(self):
#         content = self.note_text.get("1.0", "end-1c")
#         mood = self.mood_var.get()
#         try:
#             save_note(self.selected_date, content, mood)
#             self._dirty = False
#             self._set_status("All changes saved", self.GREEN)
#             if content.strip():
#                 self.selected_date_status.config(text="Journal entry available", fg=self.GREEN)
#             else:
#                 self.selected_date_status.config(text="No written entry yet", fg=self.MUTED)
#             return True
#         except Exception as error:
#             self._set_status("Save failed — retry", self.RED)
#             print(f"[Notes] Failed to save entry: {error}")
#             return False

#     def save_current_note(self):
#         self._cancel_pending_save()
#         success = self._write_current_note()
#         if success:
#             messagebox.showinfo("Saved", "Your journal entry has been saved.", parent=self.parent)
#         else:
#             messagebox.showerror(
#                 "Save Failed",
#                 "Your entry could not be saved. Your current text remains on screen.",
#                 parent=self.parent,
#             )

#     def save_without_message(self):
#         self._cancel_pending_save()
#         if not self._dirty:
#             return True
#         return self._write_current_note()

#     def _save_shortcut(self, event=None):
#         self.save_current_note()
#         return "break"

#     # ========================================================
#     # CLEAR NOTE
#     # ========================================================

#     def clear_note(self):
#         confirm = messagebox.askyesno(
#             "Clear Journal",
#             "Clear the note and mood for this date?",
#             parent=self.parent,
#         )
#         if not confirm:
#             return

#         self._cancel_pending_save()
#         self._loading = True
#         try:
#             self.note_text.delete("1.0", "end")
#             self.mood_var.set("")
#         finally:
#             self._loading = False

#         self._dirty = True
#         self.update_word_count()
#         self._set_status("Unsaved changes", self.YELLOW)
#         self._cancel_pending_save()

#         if not self._write_current_note():
#             messagebox.showerror(
#                 "Clear Failed",
#                 "The entry could not be cleared in the database.",
#                 parent=self.parent,
#             )

#     # ========================================================
#     # STATUS
#     # ========================================================

#     def _set_status(self, message, color):
#         self.status_label.config(text=message)
#         self.status_dot.config(fg=color)

#     # ========================================================
#     # CLEANUP
#     # ========================================================

#     def destroy(self):
#         if self._destroyed:
#             return True

#         self._cancel_pending_save()
#         if getattr(self, "_theme_poll_job", None) is not None:
#             try:
#                 self.main_frame.after_cancel(self._theme_poll_job)
#             except tk.TclError:
#                 pass
#             self._theme_poll_job = None

#         if self._dirty and not self._write_current_note():
#             return False

#         self._destroyed = True
#         self.main_frame.destroy()
#         return True


# if __name__ == "__main__":
#     root = tk.Tk()
#     root.title("Social Lock — Daily Notes")
#     root.geometry("1180x800")
#     root.minsize(900, 650)
#     root.configure(bg=NotesView.BG)
#     view = NotesView(root)

#     def close_app():
#         if view.destroy():
#             root.destroy()

#     root.protocol("WM_DELETE_WINDOW", close_app)
#     root.mainloop()





#!/usr/bin/env python3
"""
Social Lock — Daily Notes
Keeps the existing calendar and journal layout while supporting
the dark/light theme selected by the parent application.
"""

import calendar
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta

from notes import save_note, get_note


class NotesView:
    # Default theme
    BG = "#0F1117"
    SIDEBAR = "#151821"
    CARD = "#1B1F2A"
    INPUT = "#151821"
    BORDER = "#292E3A"
    TEXT = "#F4F6FA"
    MUTED = "#8D94A6"
    ACCENT = "#7C5CFC"
    ACCENT_HOVER = "#6846EA"
    GREEN = "#35D07F"
    RED = "#FF5C68"
    YELLOW = "#F4C76B"
    FONT = "DejaVu Sans"

    THEMES = {
        "dark": {
            "BG": "#0F1117",
            "SIDEBAR": "#151821",
            "CARD": "#1B1F2A",
            "INPUT": "#151821",
            "BORDER": "#292E3A",
            "TEXT": "#F4F6FA",
            "MUTED": "#8D94A6",
            "ACCENT": "#7C5CFC",
            "ACCENT_HOVER": "#6846EA",
            "GREEN": "#35D07F",
            "RED": "#FF5C68",
            "YELLOW": "#F4C76B",
            "TODAY_BG": "#263D36",
            "TODAY_FG": "#35D07F",
            "WHITE": "#FFFFFF",
        },
        "light": {
            "BG": "#F4F6FA",
            "SIDEBAR": "#E9ECF3",
            "CARD": "#FFFFFF",
            "INPUT": "#F8F9FC",
            "BORDER": "#D9DEEA",
            "TEXT": "#202433",
            "MUTED": "#697386",
            "ACCENT": "#7C5CFC",
            "ACCENT_HOVER": "#6846EA",
            "GREEN": "#168653",
            "RED": "#D93648",
            "YELLOW": "#9A6A00",
            "TODAY_BG": "#DDF5E8",
            "TODAY_FG": "#168653",
            "WHITE": "#FFFFFF",
        },
    }

    MOODS = [
        "",
        "😊 Happy",
        "🎯 Focused",
        "😌 Calm",
        "💪 Motivated",
        "😐 Okay",
        "😔 Sad",
        "😫 Stressed",
        "😴 Tired",
    ]

    def __init__(self, parent, theme=None):
        self.parent = parent
        self.selected_date = date.today()
        self._loading = False
        self._dirty = False
        self._save_job = None
        self._destroyed = False
        self.calendar_year = self.selected_date.year
        self.calendar_month = self.selected_date.month
        self._widget_registry = []

        # Use the theme explicitly passed by main.py.
        # If none is passed, detect the theme from the parent.
        self._explicit_theme = theme is not None
        self.theme_name = (
            self._normalize_theme(theme)
            if theme is not None
            else self._get_parent_theme()
        )
        self._set_theme_colors(self.theme_name)

        self.main_frame = tk.Frame(parent, bg=self.BG)
        self.main_frame.pack(fill="both", expand=True)

        self._configure_styles()
        self._build_layout()
        self.render_calendar()
        self.load_note()

        # Only poll the parent when no theme was explicitly supplied.
        self._theme_poll_job = None
        if not self._explicit_theme:
            self._theme_poll_job = self.main_frame.after(
                400, self._watch_theme
            )

    # ========================================================
    # THEME INTEGRATION
    # ========================================================

    def _normalize_theme(self, theme_name):
        """Normalize common theme names to 'light' or 'dark'."""
        normalized = str(theme_name or "dark").strip().lower()

        if normalized in ("light", "white", "light mode", "white mode"):
            return "light"

        return "dark"

    def _get_parent_theme(self):
        """Find the current theme name from the parent application."""
        try:
            top_level = self.parent.winfo_toplevel()
        except (tk.TclError, AttributeError):
            top_level = None

        candidates = [
            getattr(self.parent, "theme_name", None),
            getattr(getattr(self.parent, "master", None), "theme_name", None),
            getattr(top_level, "theme_name", None),
        ]

        for candidate in candidates:
            if isinstance(candidate, str):
                normalized = candidate.strip().lower()

                if normalized in (
                    "light", "white", "light mode", "white mode"
                ):
                    return "light"

                if normalized in ("dark", "dark mode"):
                    return "dark"

        # Some applications store the theme as "theme" or
        # "current_theme", including a dictionary.
        objects = [
            self.parent,
            getattr(self.parent, "master", None),
            top_level,
        ]

        for obj in objects:
            if obj is None:
                continue

            for attr in ("current_theme", "theme"):
                value = getattr(obj, attr, None)

                if isinstance(value, str):
                    normalized = value.strip().lower()

                    if normalized in (
                        "light", "white", "light mode", "white mode"
                    ):
                        return "light"

                    if normalized in ("dark", "dark mode"):
                        return "dark"

                elif isinstance(value, dict):
                    name = str(
                        value.get("name", value.get("mode", ""))
                    ).strip().lower()

                    if name in (
                        "light", "white", "light mode", "white mode"
                    ):
                        return "light"

                    if name in ("dark", "dark mode"):
                        return "dark"

        return "dark"

    def _set_theme_colors(self, theme_name):
        theme_name = self._normalize_theme(theme_name)
        self.theme_name = theme_name

        palette = self.THEMES[theme_name]

        for name, value in palette.items():
            setattr(self, name, value)

    def apply_theme(self, theme_name=None):
        """
        Apply the selected theme without rebuilding the notes editor.

        Can be called from main.py:
            notes_view.apply_theme("light")
            notes_view.apply_theme("dark")
        """
        if self._destroyed:
            return

        if theme_name is None:
            theme_name = self._get_parent_theme()

        normalized = self._normalize_theme(theme_name)

        if normalized == self.theme_name and self._widget_registry:
            return

        self._set_theme_colors(normalized)

        try:
            self.main_frame.configure(bg=self.BG)
        except tk.TclError:
            return

        self._configure_styles()
        self._apply_widget_colors()
        self.render_calendar()

    def _watch_theme(self):
        """Detect theme changes when the parent controls the theme."""
        if self._destroyed:
            return

        try:
            latest = self._get_parent_theme()

            if latest != self.theme_name:
                self.apply_theme(latest)

            self._theme_poll_job = self.main_frame.after(
                400, self._watch_theme
            )

        except tk.TclError:
            self._theme_poll_job = None

    def _register(
        self,
        widget,
        kind,
        base_bg=None,
        base_fg=None,
        hover_bg=None,
        primary=False,
    ):
        self._widget_registry.append({
            "widget": widget,
            "kind": kind,
            "base_bg": base_bg,
            "base_fg": base_fg,
            "hover_bg": hover_bg,
            "primary": primary,
        })

        return widget

    def _apply_widget_colors(self):
        # Update existing widgets without rebuilding the editor.
        for item in self._widget_registry:
            widget = item["widget"]

            try:
                if not widget.winfo_exists():
                    continue

                kind = item["kind"]

                if kind == "frame":
                    widget.configure(
                        bg=self._color(item["base_bg"])
                    )

                elif kind == "label":
                    widget.configure(
                        bg=self._color(item["base_bg"]),
                        fg=self._color(item["base_fg"]),
                    )

                elif kind == "button":
                    primary = item["primary"]
                    base = self.ACCENT if primary else self.CARD
                    hover = (
                        self.ACCENT_HOVER if primary else self.BORDER
                    )

                    widget.configure(
                        bg=base,
                        fg=self.WHITE if primary else self.TEXT,
                        activebackground=hover,
                        activeforeground=(
                            self.WHITE if primary else self.TEXT
                        ),
                    )

                elif kind == "text":
                    widget.configure(
                        bg=self.INPUT,
                        fg=self.TEXT,
                        insertbackground=self.ACCENT,
                        selectbackground=self.ACCENT_HOVER,
                        selectforeground=self.WHITE,
                    )

                elif kind == "separator":
                    widget.configure(bg=self.BORDER)

            except tk.TclError:
                pass

        self._configure_styles()

    def _color(self, name):
        if not name:
            return self.CARD

        return getattr(self, name, name)

    # ========================================================
    # STYLES
    # ========================================================

    def _configure_styles(self):
        style = ttk.Style(self.main_frame)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Journal.TCombobox",
            fieldbackground=self.INPUT,
            background=self.CARD,
            foreground=self.TEXT,
            arrowcolor=self.ACCENT,
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
            padding=8,
        )

        style.map(
            "Journal.TCombobox",
            fieldbackground=[("readonly", self.INPUT)],
            foreground=[("readonly", self.TEXT)],
            selectbackground=[("readonly", self.INPUT)],
            selectforeground=[("readonly", self.TEXT)],
        )

        style.configure(
            "Journal.Vertical.TScrollbar",
            background=self.CARD,
            troughcolor=self.INPUT,
            bordercolor=self.BORDER,
            arrowcolor=self.MUTED,
        )

    # ========================================================
    # UI HELPERS
    # ========================================================

    def label(
        self,
        parent,
        text,
        size=10,
        color=None,
        bold=False,
        bg=None,
        **kwargs,
    ):
        bg_name = bg or "CARD"
        fg_value = color or self.TEXT

        widget = tk.Label(
            parent,
            text=text,
            font=(
                self.FONT,
                size,
                "bold" if bold else "normal",
            ),
            fg=fg_value,
            bg=self._color(bg_name),
            **kwargs,
        )

        fg_name = next(
            (
                key
                for key, value in self.THEMES[self.theme_name].items()
                if value == fg_value
            ),
            fg_value,
        )

        self._register(widget, "label", bg_name, fg_name)

        return widget

    def button(self, parent, text, command, primary=False, width=None):
        background = self.ACCENT if primary else self.CARD
        foreground = self.WHITE if primary else self.TEXT
        hover = self.ACCENT_HOVER if primary else self.BORDER

        widget = tk.Button(
            parent,
            text=text,
            command=command,
            font=(self.FONT, 9, "bold"),
            fg=foreground,
            bg=background,
            activeforeground=foreground,
            activebackground=hover,
            relief="flat",
            bd=0,
            padx=12,
            pady=9,
            cursor="hand2",
            width=width,
            highlightthickness=0,
        )

        self._register(widget, "button", primary=primary)

        # Read current colors dynamically so hover remains correct
        # after changing between dark and light themes.
        widget.bind(
            "<Enter>",
            lambda event, b=widget, p=primary: b.config(
                bg=self.ACCENT_HOVER if p else self.BORDER
            ),
        )

        widget.bind(
            "<Leave>",
            lambda event, b=widget, p=primary: b.config(
                bg=self.ACCENT if p else self.CARD
            ),
        )

        return widget

    def make_card(self, parent):
        widget = tk.Frame(
            parent,
            bg=self.CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )

        self._register(widget, "frame", "CARD")

        return widget

    def separator(self, parent):
        widget = tk.Frame(
            parent,
            bg=self.BORDER,
            height=1,
        )

        widget.pack(fill="x")
        self._register(widget, "separator")

        return widget

    def _frame(self, parent, color="CARD", **kwargs):
        widget = tk.Frame(
            parent,
            bg=self._color(color),
            **kwargs,
        )

        self._register(widget, "frame", color)

        return widget

    # ========================================================
    # MAIN LAYOUT
    # ========================================================

    def _build_layout(self):
        header = self._frame(self.main_frame, "BG")
        header.pack(fill="x", padx=28, pady=(24, 20))

        title_area = self._frame(header, "BG")
        title_area.pack(side="left", fill="x", expand=True)

        self.label(
            title_area, "YOUR PERSONAL SPACE", 9,
            self.ACCENT, True, bg="BG"
        ).pack(anchor="w")

        self.label(
            title_area, "Daily Notes", 25,
            self.TEXT, True, bg="BG"
        ).pack(anchor="w", pady=(5, 3))

        self.label(
            title_area,
            "Clear your mind. Reflect on your day. Keep growing.",
            10,
            self.MUTED,
            bg="BG",
        ).pack(anchor="w")

        self.button(
            header, "↩ Today", self.go_to_today
        ).pack(side="right", anchor="center")

        content = self._frame(self.main_frame, "BG")
        content.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=(0, 20),
        )

        content.grid_columnconfigure(0, minsize=280, weight=0)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self.calendar_panel = self.make_card(content)
        self.calendar_panel.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 14),
        )
        self._build_calendar_panel()

        self.editor_panel = self.make_card(content)
        self.editor_panel.grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        self._build_editor_panel()

    # ========================================================
    # CALENDAR PANEL
    # ========================================================

    def _build_calendar_panel(self):
        panel = self.calendar_panel

        heading = self._frame(panel)
        heading.pack(fill="x", padx=18, pady=(20, 8))

        self.label(
            heading, "Calendar", 15, self.TEXT, True
        ).pack(anchor="w")

        self.label(
            heading, "Choose a day to open your notes", 9, self.MUTED
        ).pack(anchor="w", pady=(5, 0))

        self.separator(panel)

        month_bar = self._frame(panel)
        month_bar.pack(fill="x", padx=12, pady=(16, 12))

        self.button(
            month_bar, "‹", self.previous_month, width=2
        ).pack(side="left")

        self.month_label = self.label(
            month_bar, "", 11, self.TEXT, True
        )
        self.month_label.pack(
            side="left", fill="x", expand=True, padx=5
        )

        self.button(
            month_bar, "›", self.next_month, width=2
        ).pack(side="right")

        self.calendar_grid = self._frame(panel)
        self.calendar_grid.pack(fill="x", padx=10)

        for column in range(7):
            self.calendar_grid.grid_columnconfigure(
                column, weight=1, uniform="calendar"
            )

        self.separator(panel)

        legend = self._frame(panel)
        legend.pack(fill="x", padx=16, pady=16)

        self.label(legend, "●", 10, self.ACCENT).pack(side="left")
        self.label(legend, "Selected", 9, self.MUTED).pack(
            side="left", padx=(5, 12)
        )
        self.label(legend, "●", 10, self.GREEN).pack(side="left")
        self.label(legend, "Today", 9, self.MUTED).pack(
            side="left", padx=5
        )

        self.separator(panel)

        summary = self._frame(panel)
        summary.pack(fill="x", padx=18, pady=18)

        self.label(
            summary, "SELECTED DATE", 8, self.MUTED, True
        ).pack(anchor="w")

        self.selected_date_label = self.label(
            summary, "", 12, self.TEXT, True
        )
        self.selected_date_label.pack(anchor="w", pady=(7, 5))

        self.selected_date_status = self.label(
            summary, "", 9, self.MUTED
        )
        self.selected_date_status.pack(anchor="w")

        self.button(
            summary, "Open today's notes", self.go_to_today
        ).pack(fill="x", pady=(16, 0))

    def render_calendar(self):
        for widget in self.calendar_grid.winfo_children():
            widget.destroy()

        month_name = date(
            self.calendar_year, self.calendar_month, 1
        ).strftime("%B %Y")

        self.month_label.config(text=month_name)

        weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

        for column, day_name in enumerate(weekdays):
            self.label(
                self.calendar_grid, day_name, 8, self.MUTED, True
            ).grid(
                row=0,
                column=column,
                sticky="nsew",
                pady=(0, 10),
            )

        cal = calendar.Calendar(firstweekday=calendar.MONDAY)
        weeks = cal.monthdayscalendar(
            self.calendar_year, self.calendar_month
        )

        for row, week in enumerate(weeks, start=1):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    tk.Frame(
                        self.calendar_grid,
                        bg=self.CARD,
                        height=35,
                    ).grid(
                        row=row,
                        column=column,
                        sticky="nsew",
                        padx=1,
                        pady=2,
                    )
                    continue

                current_date = date(
                    self.calendar_year,
                    self.calendar_month,
                    day_number,
                )

                is_selected = current_date == self.selected_date
                is_today = current_date == date.today()

                if is_selected:
                    background, foreground = self.ACCENT, self.WHITE
                elif is_today:
                    background = self.TODAY_BG
                    foreground = self.TODAY_FG
                else:
                    background = self.CARD
                    foreground = self.TEXT

                day_button = tk.Button(
                    self.calendar_grid,
                    text=str(day_number),
                    command=lambda d=current_date: self.select_date(d),
                    font=(
                        self.FONT,
                        9,
                        "bold" if is_selected or is_today else "normal",
                    ),
                    fg=foreground,
                    bg=background,
                    activeforeground=self.WHITE,
                    activebackground=self.ACCENT_HOVER,
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    height=1,
                    padx=0,
                    pady=8,
                    highlightthickness=0,
                )

                day_button.grid(
                    row=row,
                    column=column,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                )

                if not is_selected and not is_today:
                    day_button.bind(
                        "<Enter>",
                        lambda event, b=day_button: b.config(
                            bg=self.BORDER
                        ),
                    )
                    day_button.bind(
                        "<Leave>",
                        lambda event, b=day_button: b.config(
                            bg=self.CARD
                        ),
                    )

        self.selected_date_label.config(
            text=self.selected_date.strftime("%d %B %Y")
        )

    # ========================================================
    # CALENDAR NAVIGATION
    # ========================================================

    def previous_month(self):
        if self.calendar_month == 1:
            self.calendar_month = 12
            self.calendar_year -= 1
        else:
            self.calendar_month -= 1

        self.render_calendar()

    def next_month(self):
        if self.calendar_month == 12:
            self.calendar_month = 1
            self.calendar_year += 1
        else:
            self.calendar_month += 1

        self.render_calendar()

    def select_date(self, chosen_date):
        if chosen_date == self.selected_date:
            return

        self._cancel_pending_save()

        if self._dirty and not self._write_current_note():
            return

        self.selected_date = chosen_date
        self.calendar_year = chosen_date.year
        self.calendar_month = chosen_date.month

        self.render_calendar()
        self.load_note()

    def go_to_today(self):
        self.select_date(date.today())

    # ========================================================
    # EDITOR PANEL
    # ========================================================

    def _build_editor_panel(self):
        panel = self.editor_panel

        heading = self._frame(panel)
        heading.pack(fill="x", padx=22, pady=(20, 15))

        title_area = self._frame(heading)
        title_area.pack(side="left", fill="x", expand=True)

        self.note_title = self.label(
            title_area, "Daily reflection", 16, self.TEXT, True
        )
        self.note_title.pack(anchor="w")

        self.note_subtitle = self.label(
            title_area, "", 9, self.MUTED
        )
        self.note_subtitle.pack(anchor="w", pady=(5, 0))

        status_area = self._frame(heading)
        status_area.pack(side="right")

        self.status_dot = self.label(
            status_area, "●", 9, self.GREEN
        )
        self.status_dot.pack(side="left")

        self.status_label = self.label(
            status_area, "Saved", 9, self.MUTED
        )
        self.status_label.pack(side="left", padx=(5, 0))

        self.separator(panel)

        mood_row = self._frame(panel)
        mood_row.pack(fill="x", padx=22, pady=(16, 10))

        self.label(
            mood_row, "MOOD", 9, self.MUTED, True
        ).pack(side="left", padx=(0, 14))

        self.mood_var = tk.StringVar(value="")

        self.mood_box = ttk.Combobox(
            mood_row,
            textvariable=self.mood_var,
            values=self.MOODS,
            state="readonly",
            width=17,
            style="Journal.TCombobox",
            font=(self.FONT, 9),
        )
        self.mood_box.pack(side="left")
        self.mood_box.bind(
            "<<ComboboxSelected>>", self._on_mood_changed
        )

        editor_container = tk.Frame(
            panel,
            bg=self.INPUT,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        self._register(editor_container, "frame", "INPUT")

        editor_container.pack(
            fill="both",
            expand=True,
            padx=22,
            pady=(8, 14),
        )

        self.note_text = tk.Text(
            editor_container,
            font=(self.FONT, 11),
            fg=self.TEXT,
            bg=self.INPUT,
            insertbackground=self.ACCENT,
            selectbackground=self.ACCENT_HOVER,
            selectforeground=self.WHITE,
            wrap="word",
            undo=True,
            relief="flat",
            bd=0,
            padx=18,
            pady=18,
            spacing1=3,
            spacing3=6,
            highlightthickness=0,
        )
        self.note_text.pack(
            side="left", fill="both", expand=True
        )
        self._register(self.note_text, "text")

        scrollbar = ttk.Scrollbar(
            editor_container,
            orient="vertical",
            command=self.note_text.yview,
            style="Journal.Vertical.TScrollbar",
        )
        scrollbar.pack(side="right", fill="y")

        self.note_text.configure(
            yscrollcommand=scrollbar.set
        )

        self.note_text.bind(
            "<KeyRelease>", self._on_text_changed
        )
        self.note_text.bind(
            "<<Paste>>", self._on_text_changed
        )
        self.note_text.bind(
            "<Control-s>", self._save_shortcut
        )

        self.label(
            panel,
            "What mattered today? What did you learn? What comes next?",
            9,
            self.MUTED,
        ).pack(anchor="w", padx=23, pady=(0, 12))

        footer = self._frame(panel)
        footer.pack(fill="x", padx=22, pady=(0, 18))

        counts = self._frame(footer)
        counts.pack(side="left", fill="x", expand=True)

        self.word_count_label = self.label(
            counts, "0 words", 9, self.MUTED
        )
        self.word_count_label.pack(side="left")

        self.label(
            counts, "  ·  ", 9, self.BORDER
        ).pack(side="left")

        self.char_count_label = self.label(
            counts, "0 characters", 9, self.MUTED
        )
        self.char_count_label.pack(side="left")

        actions = self._frame(footer)
        actions.pack(side="right")

        self.button(
            actions, "Clear", self.clear_note
        ).pack(side="left", padx=(0, 8))

        self.button(
            actions,
            "Save note  ✓",
            self.save_current_note,
            primary=True,
        ).pack(side="left")

    # ========================================================
    # LOAD NOTE
    # ========================================================

    def load_note(self):
        self._cancel_pending_save()
        self._loading = True

        try:
            entry = get_note(self.selected_date)
            self.note_text.delete("1.0", "end")

            if entry:
                self.note_text.insert(
                    "1.0", entry.get("note", "") or ""
                )

                mood = entry.get("mood", "") or ""
                self.mood_var.set(
                    mood if mood in self.MOODS else ""
                )
            else:
                self.mood_var.set("")

            self._dirty = False

            if self.selected_date == date.today():
                title = "Today's reflection"
            elif self.selected_date == date.today() - timedelta(days=1):
                title = "Yesterday's reflection"
            else:
                title = "Daily reflection"

            self.note_title.config(text=title)
            self.note_subtitle.config(
                text=self.selected_date.strftime("%A, %d %B %Y")
            )

            self._set_status("All changes saved", self.GREEN)
            self.update_word_count()

            if entry and (entry.get("note", "") or "").strip():
                self.selected_date_status.config(
                    text="Journal entry available",
                    fg=self.GREEN,
                )
            else:
                self.selected_date_status.config(
                    text="No written entry yet",
                    fg=self.MUTED,
                )

        except Exception as error:
            self._set_status("Unable to load", self.RED)

            messagebox.showerror(
                "Notes Error",
                f"Could not load this day's note.\n\n{error}",
                parent=self.parent,
            )

        finally:
            self._loading = False

    # ========================================================
    # EDIT TRACKING
    # ========================================================

    def _on_text_changed(self, event=None):
        if self._loading or self._destroyed:
            return

        self._dirty = True
        self.update_word_count()
        self._set_status("Unsaved changes", self.YELLOW)
        self._schedule_autosave()

    def _on_mood_changed(self, event=None):
        if self._loading or self._destroyed:
            return

        self._dirty = True
        self._set_status("Unsaved changes", self.YELLOW)
        self._schedule_autosave()

    def update_word_count(self):
        content = self.note_text.get("1.0", "end-1c")
        words = len(content.split())
        characters = len(content)

        self.word_count_label.config(
            text=f"{words} {'word' if words == 1 else 'words'}"
        )

        self.char_count_label.config(
            text=(
                f"{characters} "
                f"{'character' if characters == 1 else 'characters'}"
            )
        )

    # ========================================================
    # AUTOSAVE
    # ========================================================

    def _schedule_autosave(self):
        self._cancel_pending_save()
        self._save_job = self.main_frame.after(
            1000, self._autosave
        )

    def _cancel_pending_save(self):
        if self._save_job is not None:
            try:
                self.main_frame.after_cancel(self._save_job)
            except tk.TclError:
                pass

            self._save_job = None

    def _autosave(self):
        self._save_job = None

        if self._destroyed or not self._dirty:
            return

        self._write_current_note()

    # ========================================================
    # SAVE NOTE
    # ========================================================

    def _write_current_note(self):
        content = self.note_text.get("1.0", "end-1c")
        mood = self.mood_var.get()

        try:
            save_note(self.selected_date, content, mood)
            self._dirty = False

            self._set_status("All changes saved", self.GREEN)

            if content.strip():
                self.selected_date_status.config(
                    text="Journal entry available",
                    fg=self.GREEN,
                )
            else:
                self.selected_date_status.config(
                    text="No written entry yet",
                    fg=self.MUTED,
                )

            return True

        except Exception as error:
            self._set_status("Save failed — retry", self.RED)
            print(f"[Notes] Failed to save entry: {error}")
            return False

    def save_current_note(self):
        self._cancel_pending_save()
        success = self._write_current_note()

        if success:
            messagebox.showinfo(
                "Saved",
                "Your journal entry has been saved.",
                parent=self.parent,
            )
        else:
            messagebox.showerror(
                "Save Failed",
                "Your entry could not be saved. "
                "Your current text remains on screen.",
                parent=self.parent,
            )

    def save_without_message(self):
        self._cancel_pending_save()

        if not self._dirty:
            return True

        return self._write_current_note()

    def _save_shortcut(self, event=None):
        self.save_current_note()
        return "break"

    # ========================================================
    # CLEAR NOTE
    # ========================================================

    def clear_note(self):
        confirm = messagebox.askyesno(
            "Clear Journal",
            "Clear the note and mood for this date?",
            parent=self.parent,
        )

        if not confirm:
            return

        self._cancel_pending_save()
        self._loading = True

        try:
            self.note_text.delete("1.0", "end")
            self.mood_var.set("")
        finally:
            self._loading = False

        self._dirty = True
        self.update_word_count()
        self._set_status("Unsaved changes", self.YELLOW)
        self._cancel_pending_save()

        if not self._write_current_note():
            messagebox.showerror(
                "Clear Failed",
                "The entry could not be cleared in the database.",
                parent=self.parent,
            )

    # ========================================================
    # STATUS
    # ========================================================

    def _set_status(self, message, color):
        self.status_label.config(text=message)
        self.status_dot.config(fg=color)

    # ========================================================
    # CLEANUP
    # ========================================================

    def destroy(self):
        if self._destroyed:
            return True

        self._cancel_pending_save()

        if getattr(self, "_theme_poll_job", None) is not None:
            try:
                self.main_frame.after_cancel(
                    self._theme_poll_job
                )
            except tk.TclError:
                pass

            self._theme_poll_job = None

        if self._dirty and not self._write_current_note():
            return False

        self._destroyed = True
        self.main_frame.destroy()

        return True


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Social Lock — Daily Notes")
    root.geometry("1180x800")
    root.minsize(900, 650)
    root.configure(bg=NotesView.BG)

    view = NotesView(root)

    def close_app():
        if view.destroy():
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_app)
    root.mainloop()
