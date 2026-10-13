

# #!/usr/bin/env python3
# """
# Social Lock — Focus Dashboard

# Features:
# - Side-by-side Social Media Lock and Pomodoro cards
# - Large digital countdowns and circular progress indicators
# - Customizable lock, focus, and break durations
# - Social lock has no stop button
# - Dark/light theme support
# - Accurate countdowns based on timestamps

# Expected FocusLock interface:
#     FocusLock(selected_sites, duration_minutes)
#     focus_lock.start()
#     focus_lock.stop()
# """

# import time
# import tkinter as tk
# from tkinter import messagebox


# try:
#     from focus_lock import FocusLock
# except ImportError:
#     from focus_lock import FocusLock


# class FocusView:

#     DEFAULT_THEME = {
#         "BG": "#0F1117",
#         "SIDEBAR": "#151821",
#         "CARD": "#1B1F2A",
#         "CARD_HOVER": "#252A38",
#         "INPUT": "#151821",
#         "BORDER": "#303747",
#         "TEXT": "#F3F5FA",
#         "SECONDARY": "#9AA4B5",
#         "MUTED": "#9AA4B5",
#         "ACCENT": "#8B7CFF",
#         "ACCENT_HOVER": "#7667EE",
#         "GREEN": "#37C991",
#         "RED": "#FF6376",
#         "ORANGE": "#F5A65B",
#         "RING_BG": "#343A49",
#     }

#     MAX_MINUTES = 525600

#     SOCIAL_SITES = [
#         ("Facebook", "facebook.com"),
#         ("Instagram", "instagram.com"),
#         ("TikTok", "tiktok.com"),
#         ("Reddit", "reddit.com"),
#         ("YouTube", "youtube.com"),
#     ]

#     def __init__(self, parent, theme=None):
#         self.parent = parent
#         self.theme = {**self.DEFAULT_THEME, **(theme or {})}

#         # Social lock state
#         self.social_lock = None
#         self.social_running = False
#         self.social_end_time = None
#         self.social_total_seconds = 0
#         self.social_after_id = None

#         # Pomodoro state
#         self.pomo_running = False
#         self.pomo_paused = False
#         self.pomo_phase = "Focus"
#         self.pomo_end_time = None
#         self.pomo_remaining = 25 * 60
#         self.pomo_total_seconds = 25 * 60
#         self.pomo_after_id = None
#         self.pomo_sessions = 0

#         self.destroyed = False

#         # Main container. This view packs itself into the parent.
#         self.main_frame = tk.Frame(
#             parent,
#             bg=self.color("BG"),
#         )
#         self.main_frame.pack(fill="both", expand=True)

#         self.build_interface()

#         self.main_frame.bind(
#             "<Destroy>",
#             self._on_destroy_event,
#             add="+",
#         )

#     # =========================================================
#     # THEME
#     # =========================================================

#     def color(self, name):
#         return self.theme.get(name, self.DEFAULT_THEME.get(name, "#FFFFFF"))

#     def themed_frame(self, parent, **kwargs):
#         return tk.Frame(
#             parent,
#             bg=self.color("CARD"),
#             **kwargs,
#         )

#     def make_label(
#         self,
#         parent,
#         text,
#         size=11,
#         color="TEXT",
#         bold=False,
#         **kwargs,
#     ):
#         return tk.Label(
#             parent,
#             text=text,
#             font=(
#                 "Ubuntu",
#                 size,
#                 "bold" if bold else "normal",
#             ),
#             bg=self.color("CARD"),
#             fg=self.color(color),
#             **kwargs,
#         )

#     def make_button(
#         self,
#         parent,
#         text,
#         command,
#         primary=False,
#         danger=False,
#         **kwargs,
#     ):
#         if primary:
#             bg = self.color("ACCENT")
#             fg = "#FFFFFF"
#             active_bg = self.color("ACCENT_HOVER")
#         elif danger:
#             bg = self.color("RED")
#             fg = "#FFFFFF"
#             active_bg = self.color("RED")
#         else:
#             bg = self.color("CARD_HOVER")
#             fg = self.color("TEXT")
#             active_bg = self.color("BORDER")

#         return tk.Button(
#             parent,
#             text=text,
#             command=command,
#             font=("Ubuntu", 10, "bold"),
#             bg=bg,
#             fg=fg,
#             activebackground=active_bg,
#             activeforeground=fg,
#             relief="flat",
#             bd=0,
#             cursor="hand2",
#             padx=15,
#             pady=10,
#             highlightthickness=0,
#             **kwargs,
#         )

#     def make_entry(self, parent, variable, width=8):
#         return tk.Entry(
#             parent,
#             textvariable=variable,
#             font=("Ubuntu", 12, "bold"),
#             width=width,
#             justify="center",
#             bg=self.color("INPUT"),
#             fg=self.color("TEXT"),
#             insertbackground=self.color("TEXT"),
#             relief="flat",
#             bd=0,
#             highlightthickness=1,
#             highlightbackground=self.color("BORDER"),
#             highlightcolor=self.color("ACCENT"),
#         )

#     # =========================================================
#     # MAIN INTERFACE
#     # =========================================================

#     def build_interface(self):
#         header = tk.Frame(
#             self.main_frame,
#             bg=self.color("BG"),
#         )
#         header.pack(fill="x", padx=26, pady=(22, 18))

#         title_area = tk.Frame(
#             header,
#             bg=self.color("BG"),
#         )
#         title_area.pack(side="left", fill="x", expand=True)

#         tk.Label(
#             title_area,
#             text="Focus Dashboard",
#             font=("Ubuntu", 24, "bold"),
#             bg=self.color("BG"),
#             fg=self.color("TEXT"),
#         ).pack(anchor="w")

#         tk.Label(
#             title_area,
#             text="Protect your attention. Make every minute count.",
#             font=("Ubuntu", 10),
#             bg=self.color("BG"),
#             fg=self.color("SECONDARY"),
#         ).pack(anchor="w", pady=(5, 0))

#         self.clock_label = tk.Label(
#             header,
#             text="",
#             font=("Ubuntu", 12, "bold"),
#             bg=self.color("BG"),
#             fg=self.color("ACCENT"),
#         )
#         self.clock_label.pack(side="right", padx=(10, 0))
#         self.update_clock()

#         # Two cards side by side.
#         self.columns = tk.Frame(
#             self.main_frame,
#             bg=self.color("BG"),
#         )
#         self.columns.pack(
#             fill="both",
#             expand=True,
#             padx=22,
#             pady=(0, 22),
#         )

#         self.columns.grid_columnconfigure(0, weight=1, uniform="cards")
#         self.columns.grid_columnconfigure(1, weight=1, uniform="cards")
#         self.columns.grid_rowconfigure(0, weight=1)

#         self.build_social_card()
#         self.build_pomodoro_card()

#     # =========================================================
#     # CARD HELPERS
#     # =========================================================

#     def create_card(self, column):
#         outer = tk.Frame(
#             self.columns,
#             bg=self.color("BORDER"),
#             bd=0,
#             highlightthickness=0,
#         )
#         outer.grid(
#             row=0,
#             column=column,
#             sticky="nsew",
#             padx=7,
#         )

#         card = tk.Frame(
#             outer,
#             bg=self.color("CARD"),
#             bd=0,
#             highlightthickness=0,
#         )
#         card.pack(fill="both", expand=True, padx=1, pady=1)

#         return card

#     def create_timer_canvas(self, parent, diameter=210):
#         canvas = tk.Canvas(
#             parent,
#             width=diameter,
#             height=diameter,
#             bg=self.color("CARD"),
#             highlightthickness=0,
#             bd=0,
#         )
#         canvas.pack(pady=(10, 8))
#         return canvas

#     def draw_timer(
#         self,
#         canvas,
#         seconds,
#         total_seconds,
#         progress_color,
#         subtitle,
#     ):
#         canvas.delete("all")

#         width = int(canvas["width"])
#         height = int(canvas["height"])

#         padding = 15
#         x1 = padding
#         y1 = padding
#         x2 = width - padding
#         y2 = height - padding

#         canvas.create_oval(
#             x1,
#             y1,
#             x2,
#             y2,
#             outline=self.color("RING_BG"),
#             width=12,
#         )

#         total_seconds = max(1, total_seconds)
#         progress = max(0, min(1, seconds / total_seconds))

#         # Arc begins at the top and moves clockwise.
#         canvas.create_arc(
#             x1,
#             y1,
#             x2,
#             y2,
#             start=90,
#             extent=-359.99 * progress,
#             style="arc",
#             outline=progress_color,
#             width=12,
#         )

#         canvas.create_text(
#             width // 2,
#             height // 2 - 12,
#             text=self.format_time(seconds),
#             fill=self.color("TEXT"),
#             font=("Ubuntu", 28, "bold"),
#         )

#         canvas.create_text(
#             width // 2,
#             height // 2 + 24,
#             text=subtitle,
#             fill=self.color("SECONDARY"),
#             font=("Ubuntu", 10),
#         )

#     # =========================================================
#     # SOCIAL MEDIA LOCK
#     # =========================================================

#     def build_social_card(self):
#         card = self.create_card(0)

#         header = tk.Frame(card, bg=self.color("CARD"))
#         header.pack(fill="x", padx=22, pady=(20, 0))

#         tk.Label(
#             header,
#             text="◉",
#             font=("Ubuntu", 22, "bold"),
#             bg=self.color("CARD"),
#             fg=self.color("ACCENT"),
#         ).pack(side="left", padx=(0, 10))

#         title_area = tk.Frame(header, bg=self.color("CARD"))
#         title_area.pack(side="left", fill="x", expand=True)

#         self.make_label(
#             title_area,
#             "Social Media Lock",
#             size=15,
#             bold=True,
#         ).pack(anchor="w")

#         self.make_label(
#             title_area,
#             "Stay away from distractions",
#             color="SECONDARY",
#             size=9,
#         ).pack(anchor="w", pady=(3, 0))

#         self.social_status = self.make_label(
#             card,
#             "●  READY TO FOCUS",
#             color="GREEN",
#             size=9,
#             bold=True,
#         )
#         self.social_status.pack(pady=(15, 0))

#         self.social_canvas = self.create_timer_canvas(card, 190)
#         self.draw_timer(
#             self.social_canvas,
#             0,
#             1,
#             self.color("GREEN"),
#             "LOCK DURATION",
#         )

#         # Duration controls
#         duration_area = tk.Frame(card, bg=self.color("CARD"))
#         duration_area.pack(pady=(0, 14))

#         self.make_label(
#             duration_area,
#             "Lock duration",
#             color="SECONDARY",
#         ).grid(row=0, column=0, columnspan=2, pady=(0, 8))

#         self.social_hours_var = tk.StringVar(value="1")
#         self.social_minutes_var = tk.StringVar(value="0")

#         self.make_entry(
#             duration_area,
#             self.social_hours_var,
#             width=5,
#         ).grid(row=1, column=0, padx=(0, 5), ipady=7)

#         self.make_label(
#             duration_area,
#             "hours",
#             color="SECONDARY",
#         ).grid(row=1, column=1, padx=(0, 12))

#         self.make_entry(
#             duration_area,
#             self.social_minutes_var,
#             width=5,
#         ).grid(row=1, column=2, padx=(0, 5), ipady=7)

#         self.make_label(
#             duration_area,
#             "minutes",
#             color="SECONDARY",
#         ).grid(row=1, column=3)

#         # Common duration shortcuts
#         shortcuts = tk.Frame(card, bg=self.color("CARD"))
#         shortcuts.pack(pady=(0, 14))

#         for label, hours, minutes in [
#             ("30 min", 0, 30),
#             ("1 hour", 1, 0),
#             ("3 hours", 3, 0),
#             ("8 hours", 8, 0),
#         ]:
#             tk.Button(
#                 shortcuts,
#                 text=label,
#                 command=lambda h=hours, m=minutes:
#                     self.set_social_duration(h, m),
#                 font=("Ubuntu", 8),
#                 bg=self.color("CARD_HOVER"),
#                 fg=self.color("TEXT"),
#                 activebackground=self.color("BORDER"),
#                 activeforeground=self.color("TEXT"),
#                 relief="flat",
#                 bd=0,
#                 padx=8,
#                 pady=6,
#                 cursor="hand2",
#             ).pack(side="left", padx=3)

#         # Website selection
#         site_area = tk.Frame(card, bg=self.color("CARD"))
#         site_area.pack(fill="x", padx=24, pady=(0, 12))

#         self.make_label(
#             site_area,
#             "Choose websites to block",
#             color="SECONDARY",
#             size=9,
#         ).pack(anchor="w", pady=(0, 8))

#         self.site_vars = {}

#         site_grid = tk.Frame(site_area, bg=self.color("CARD"))
#         site_grid.pack(fill="x")

#         for index, (name, domain) in enumerate(self.SOCIAL_SITES):
#             var = tk.BooleanVar(value=True)
#             self.site_vars[domain] = var

#             check = tk.Checkbutton(
#                 site_grid,
#                 text=name,
#                 variable=var,
#                 bg=self.color("CARD"),
#                 fg=self.color("TEXT"),
#                 activebackground=self.color("CARD"),
#                 activeforeground=self.color("TEXT"),
#                 selectcolor=self.color("INPUT"),
#                 font=("Ubuntu", 9),
#                 bd=0,
#                 highlightthickness=0,
#                 cursor="hand2",
#             )
#             check.grid(
#                 row=index // 3,
#                 column=index % 3,
#                 sticky="w",
#                 padx=(0, 8),
#                 pady=4,
#             )

#         self.social_start_button = self.make_button(
#             card,
#             "Start Social Lock",
#             self.start_social_lock,
#             primary=True,
#         )
#         self.social_start_button.pack(
#             fill="x",
#             padx=24,
#             pady=(2, 8),
#         )

#         self.make_label(
#             card,
#             "The lock runs until the timer expires.",
#             color="SECONDARY",
#             size=8,
#         ).pack(pady=(0, 15))

#     def set_social_duration(self, hours, minutes):
#         if self.social_running:
#             return

#         self.social_hours_var.set(str(hours))
#         self.social_minutes_var.set(str(minutes))

#     def get_social_duration(self):
#         try:
#             hours_text = self.social_hours_var.get().strip()
#             minutes_text = self.social_minutes_var.get().strip()

#             hours = int(hours_text)
#             minutes = int(minutes_text)

#             if hours < 0 or minutes < 0:
#                 raise ValueError

#             if hours == 0 and minutes == 0:
#                 raise ValueError

#             total_minutes = hours * 60 + minutes

#             if total_minutes > self.MAX_MINUTES:
#                 raise ValueError

#             return total_minutes

#         except (ValueError, TypeError):
#             messagebox.showerror(
#                 "Invalid duration",
#                 "Enter a valid duration up to 525,600 minutes.",
#                 parent=self.main_frame,
#             )
#             return None

#     def start_social_lock(self):
#         if self.social_running:
#             return

#         duration_minutes = self.get_social_duration()
#         if duration_minutes is None:
#             return

#         selected_sites = [
#             domain
#             for domain, var in self.site_vars.items()
#             if var.get()
#         ]

#         if not selected_sites:
#             messagebox.showwarning(
#                 "No websites selected",
#                 "Select at least one website to block.",
#                 parent=self.main_frame,
#             )
#             return

#         confirmed = messagebox.askyesno(
#             "Start Social Lock",
#             (
#                 f"Block {len(selected_sites)} website(s) for "
#                 f"{self.format_duration(duration_minutes)}?\n\n"
#                 "You won't have a stop button once the lock starts."
#             ),
#             parent=self.main_frame,
#         )

#         if not confirmed:
#             return

#         try:
#             # lock = FocusLock(selected_sites, duration_minutes)
#             # lock.start()

#             # self.social_lock = lock
#             # self.social_running = True

#             lock = FocusLock(selected_sites, duration_minutes)
#             success, message = lock.start()

#             if not success:
#                 messagebox.showerror(
#                     "Could not start lock",
#                     message,
#                     parent=self.main_frame,
#                 )
#                 return

#             self.social_lock = lock
#             self.social_running = True
#             self.social_total_seconds = duration_minutes * 60
#             self.social_end_time = time.time() + self.social_total_seconds

#             self.social_total_seconds = duration_minutes * 60
#             self.social_end_time = time.time() + self.social_total_seconds

#             self.social_hours_var.set(
#                 str(duration_minutes // 60)
#             )
#             self.social_minutes_var.set(
#                 str(duration_minutes % 60)
#             )

#             self.social_start_button.configure(
#                 text="Social Lock Active",
#                 state="disabled",
#                 bg=self.color("CARD_HOVER"),
#             )

#             self.social_hours_entry_state("disabled")

#             self.social_status.configure(
#                 text="●  WEBSITES BLOCKED",
#                 fg=self.color("GREEN"),
#             )

#             self.update_social_timer()

#         except Exception as exc:
#             messagebox.showerror(
#                 "Could not start lock",
#                 f"The social media lock could not be started.\n\n{exc}",
#                 parent=self.main_frame,
#             )

#     def social_hours_entry_state(self, state):
#         # Prevent changing duration while a lock is running.
#         for widget in self.main_frame.winfo_children():
#             self._set_entries_state(widget, state)

#     def _set_entries_state(self, widget, state):
#         try:
#             if isinstance(widget, tk.Entry):
#                 widget.configure(state=state)
#         except tk.TclError:
#             pass

#         for child in widget.winfo_children():
#             self._set_entries_state(child, state)

#     def update_social_timer(self):
#         if self.destroyed or not self.social_running:
#             return

#         remaining = max(
#             0,
#             int(self.social_end_time - time.time() + 0.999),
#         )

#         self.draw_timer(
#             self.social_canvas,
#             remaining,
#             self.social_total_seconds,
#             self.color("GREEN"),
#             "TIME REMAINING",
#         )

#         if remaining <= 0:
#             self.finish_social_lock()
#             return

#         self.social_after_id = self.main_frame.after(
#             250,
#             self.update_social_timer,
#         )

#     def finish_social_lock(self):
#         if not self.social_running:
#             return

#         self.social_running = False

#         try:
#             if self.social_lock is not None:
#                 self.social_lock.stop()
#         except Exception as exc:
#             messagebox.showerror(
#                 "Unlock error",
#                 f"The timer expired, but the websites could not be unblocked:\n{exc}",
#                 parent=self.main_frame,
#             )

#         self.social_lock = None
#         self.social_end_time = None

#         self.social_start_button.configure(
#             text="Start Social Lock",
#             state="normal",
#             bg=self.color("ACCENT"),
#         )

#         self.social_hours_entry_state("normal")

#         self.social_status.configure(
#             text="●  LOCK FINISHED",
#             fg=self.color("ORANGE"),
#         )

#         self.draw_timer(
#             self.social_canvas,
#             0,
#             1,
#             self.color("GREEN"),
#             "COMPLETED",
#         )

#         if not self.destroyed:
#             messagebox.showinfo(
#                 "Social Lock Complete",
#                 "Your social media lock has finished.",
#                 parent=self.main_frame,
#             )

#     # =========================================================
#     # POMODORO
#     # =========================================================

#     def build_pomodoro_card(self):
#         card = self.create_card(1)

#         header = tk.Frame(card, bg=self.color("CARD"))
#         header.pack(fill="x", padx=22, pady=(20, 0))

#         tk.Label(
#             header,
#             text="◷",
#             font=("Ubuntu", 24, "bold"),
#             bg=self.color("CARD"),
#             fg=self.color("ACCENT"),
#         ).pack(side="left", padx=(0, 10))

#         title_area = tk.Frame(header, bg=self.color("CARD"))
#         title_area.pack(side="left", fill="x", expand=True)

#         self.make_label(
#             title_area,
#             "Pomodoro Timer",
#             size=15,
#             bold=True,
#         ).pack(anchor="w")

#         self.make_label(
#             title_area,
#             "Work in focused intervals",
#             color="SECONDARY",
#             size=9,
#         ).pack(anchor="w", pady=(3, 0))

#         self.pomo_status = self.make_label(
#             card,
#             "●  READY",
#             color="ACCENT",
#             size=9,
#             bold=True,
#         )
#         self.pomo_status.pack(pady=(15, 0))

#         self.pomo_canvas = self.create_timer_canvas(card, 210)
#         self.draw_timer(
#             self.pomo_canvas,
#             self.pomo_remaining,
#             self.pomo_total_seconds,
#             self.color("ACCENT"),
#             "FOCUS SESSION",
#         )

#         self.pomo_phase_label = self.make_label(
#             card,
#             "Focus session",
#             color="TEXT",
#             size=12,
#             bold=True,
#         )
#         self.pomo_phase_label.pack(pady=(0, 12))

#         # Custom focus and break durations
#         settings = tk.Frame(card, bg=self.color("CARD"))
#         settings.pack(pady=(0, 14))

#         self.make_label(
#             settings,
#             "Focus (min)",
#             color="SECONDARY",
#             size=9,
#         ).grid(row=0, column=0, padx=7, pady=(0, 6))

#         self.make_label(
#             settings,
#             "Break (min)",
#             color="SECONDARY",
#             size=9,
#         ).grid(row=0, column=1, padx=7, pady=(0, 6))

#         self.focus_minutes_var = tk.StringVar(value="25")
#         self.break_minutes_var = tk.StringVar(value="5")

#         self.make_entry(
#             settings,
#             self.focus_minutes_var,
#             width=8,
#         ).grid(row=1, column=0, padx=7, ipady=7)

#         self.make_entry(
#             settings,
#             self.break_minutes_var,
#             width=8,
#         ).grid(row=1, column=1, padx=7, ipady=7)

#         # Controls
#         controls = tk.Frame(card, bg=self.color("CARD"))
#         controls.pack(fill="x", padx=24, pady=(0, 10))

#         self.pomo_start_button = self.make_button(
#             controls,
#             "Start Focus",
#             self.start_pomodoro,
#             primary=True,
#         )
#         self.pomo_start_button.pack(
#             side="left",
#             fill="x",
#             expand=True,
#             padx=(0, 5),
#         )

#         self.pomo_pause_button = self.make_button(
#             controls,
#             "Pause",
#             self.pause_pomodoro,
#         )
#         self.pomo_pause_button.pack(
#             side="left",
#             fill="x",
#             expand=True,
#             padx=5,
#         )

#         self.pomo_reset_button = self.make_button(
#             controls,
#             "Reset",
#             self.reset_pomodoro,
#         )
#         self.pomo_reset_button.pack(
#             side="left",
#             fill="x",
#             expand=True,
#             padx=(5, 0),
#         )

#         self.pomo_sessions_label = self.make_label(
#             card,
#             "Completed focus sessions: 0",
#             color="SECONDARY",
#             size=9,
#         )
#         self.pomo_sessions_label.pack(pady=(0, 17))

#         self.pomo_pause_button.configure(state="disabled")

#     def get_pomodoro_durations(self):
#         try:
#             focus = int(self.focus_minutes_var.get().strip())
#             rest = int(self.break_minutes_var.get().strip())

#             if not (1 <= focus <= self.MAX_MINUTES):
#                 raise ValueError

#             if not (1 <= rest <= self.MAX_MINUTES):
#                 raise ValueError

#             return focus, rest

#         except (ValueError, TypeError):
#             messagebox.showerror(
#                 "Invalid duration",
#                 "Focus and break durations must be whole numbers from "
#                 f"1 to {self.MAX_MINUTES} minutes.",
#                 parent=self.main_frame,
#             )
#             return None

#     def start_pomodoro(self):
#         if self.pomo_running:
#             return

#         durations = self.get_pomodoro_durations()
#         if durations is None:
#             return

#         focus_minutes, _ = durations

#         self.pomo_phase = "Focus"
#         self.pomo_remaining = focus_minutes * 60
#         self.pomo_total_seconds = self.pomo_remaining
#         self.pomo_running = True
#         self.pomo_paused = False
#         self.pomo_end_time = time.time() + self.pomo_remaining

#         self.focus_minutes_var.set(str(focus_minutes))

#         self.pomo_start_button.configure(state="disabled")
#         self.pomo_pause_button.configure(
#             text="Pause",
#             state="normal",
#         )
#         self.set_pomodoro_inputs_state("disabled")

#         self.update_pomodoro_display()
#         self.update_pomodoro_timer()

#     def pause_pomodoro(self):
#         if not self.pomo_running:
#             return

#         if not self.pomo_paused:
#             self.pomo_remaining = max(
#                 0,
#                 int(self.pomo_end_time - time.time() + 0.999),
#             )

#             self.pomo_running = False
#             self.pomo_paused = True
#             self.pomo_end_time = None

#             self.cancel_pomo_callback()

#             self.pomo_pause_button.configure(text="Resume")
#             self.pomo_status.configure(
#                 text="●  PAUSED",
#                 fg=self.color("ORANGE"),
#             )
#             self.update_pomodoro_display()

#         else:
#             self.pomo_running = True
#             self.pomo_paused = False
#             self.pomo_end_time = time.time() + self.pomo_remaining

#             self.pomo_pause_button.configure(text="Pause")
#             self.update_pomodoro_display()
#             self.update_pomodoro_timer()

#     def reset_pomodoro(self):
#         self.cancel_pomo_callback()

#         self.pomo_running = False
#         self.pomo_paused = False
#         self.pomo_end_time = None
#         self.pomo_phase = "Focus"

#         durations = self.get_pomodoro_durations()
#         if durations is None:
#             focus_minutes = 25
#             self.focus_minutes_var.set("25")
#         else:
#             focus_minutes, _ = durations

#         self.pomo_remaining = focus_minutes * 60
#         self.pomo_total_seconds = self.pomo_remaining

#         self.pomo_start_button.configure(
#             text="Start Focus",
#             state="normal",
#         )
#         self.pomo_pause_button.configure(
#             text="Pause",
#             state="disabled",
#         )
#         self.set_pomodoro_inputs_state("normal")

#         self.pomo_status.configure(
#             text="●  READY",
#             fg=self.color("ACCENT"),
#         )
#         self.pomo_phase_label.configure(text="Focus session")

#         self.update_pomodoro_display()

#     def update_pomodoro_timer(self):
#         if self.destroyed or not self.pomo_running:
#             return

#         self.pomo_remaining = max(
#             0,
#             int(self.pomo_end_time - time.time() + 0.999),
#         )

#         self.update_pomodoro_display()

#         if self.pomo_remaining <= 0:
#             self.complete_pomodoro_phase()
#             return

#         self.pomo_after_id = self.main_frame.after(
#             250,
#             self.update_pomodoro_timer,
#         )

#     def complete_pomodoro_phase(self):
#         self.cancel_pomo_callback()

#         finished_phase = self.pomo_phase

#         if finished_phase == "Focus":
#             self.pomo_sessions += 1
#             self.pomo_sessions_label.configure(
#                 text=f"Completed focus sessions: {self.pomo_sessions}"
#             )

#             next_phase = "Break"
#             _, break_minutes = self.get_safe_durations()
#             next_seconds = break_minutes * 60

#         else:
#             next_phase = "Focus"
#             focus_minutes, _ = self.get_safe_durations()
#             next_seconds = focus_minutes * 60

#         self.pomo_phase = next_phase
#         self.pomo_remaining = next_seconds
#         self.pomo_total_seconds = next_seconds

#         self.pomo_running = False
#         self.pomo_paused = False
#         self.pomo_end_time = None

#         self.pomo_start_button.configure(
#             text=f"Start {next_phase}",
#             state="normal",
#         )
#         self.pomo_pause_button.configure(state="disabled")
#         self.set_pomodoro_inputs_state("normal")

#         self.pomo_status.configure(
#             text="●  PHASE COMPLETE",
#             fg=self.color("GREEN"),
#         )
#         self.pomo_phase_label.configure(
#             text=f"{next_phase} session ready"
#         )

#         self.update_pomodoro_display()

#         if not self.destroyed:
#             messagebox.showinfo(
#                 "Pomodoro Complete",
#                 (
#                     "Focus session completed! Take a break."
#                     if finished_phase == "Focus"
#                     else "Break completed! Ready for another focus session?"
#                 ),
#                 parent=self.main_frame,
#             )

#     def get_safe_durations(self):
#         try:
#             focus = int(self.focus_minutes_var.get().strip())
#             rest = int(self.break_minutes_var.get().strip())

#             if not (1 <= focus <= self.MAX_MINUTES):
#                 focus = 25

#             if not (1 <= rest <= self.MAX_MINUTES):
#                 rest = 5

#             return focus, rest

#         except (ValueError, TypeError):
#             return 25, 5

#     def update_pomodoro_display(self):
#         if self.pomo_phase == "Focus":
#             progress_color = self.color("ACCENT")
#             subtitle = "FOCUS SESSION"
#         else:
#             progress_color = self.color("GREEN")
#             subtitle = "BREAK TIME"

#         self.draw_timer(
#             self.pomo_canvas,
#             self.pomo_remaining,
#             self.pomo_total_seconds,
#             progress_color,
#             subtitle,
#         )

#         self.pomo_phase_label.configure(
#             text=(
#                 "Focus session"
#                 if self.pomo_phase == "Focus"
#                 else "Break session"
#             )
#         )

#     def set_pomodoro_inputs_state(self, state):
#         self._set_entries_state(
#             self.main_frame,
#             state,
#         )

#         # Restore duration entries when the timer is idle.
#         # The social entries are controlled separately.
#         if state == "normal" and self.social_running:
#             self.social_hours_entry_state("disabled")

#     # =========================================================
#     # CLOCK AND HELPERS
#     # =========================================================

#     @staticmethod
#     def format_time(seconds):
#         seconds = max(0, int(seconds))
#         hours, remainder = divmod(seconds, 3600)
#         minutes, seconds = divmod(remainder, 60)

#         if hours:
#             return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

#         return f"{minutes:02d}:{seconds:02d}"

#     @staticmethod
#     def format_duration(minutes):
#         hours, remainder = divmod(minutes, 60)

#         parts = []
#         if hours:
#             parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
#         if remainder:
#             parts.append(
#                 f"{remainder} minute{'s' if remainder != 1 else ''}"
#             )

#         return " ".join(parts) or "0 minutes"

#     def update_clock(self):
#         if self.destroyed:
#             return

#         self.clock_label.configure(
#             text=time.strftime("%H:%M:%S")
#         )

#         self.main_frame.after(1000, self.update_clock)

#     def cancel_pomo_callback(self):
#         if self.pomo_after_id is not None:
#             try:
#                 self.main_frame.after_cancel(self.pomo_after_id)
#             except tk.TclError:
#                 pass

#             self.pomo_after_id = None

#     def _on_destroy_event(self, event):
#         if event.widget is not self.main_frame:
#             return

#         if self.destroyed:
#             return

#         self.destroyed = True

#         for after_id in (
#             self.social_after_id,
#             self.pomo_after_id,
#         ):
#             if after_id is not None:
#                 try:
#                     self.main_frame.after_cancel(after_id)
#                 except tk.TclError:
#                     pass

#         self.social_after_id = None
#         self.pomo_after_id = None

#         # Do not automatically stop an active social lock here.
#         # The lock should not be accidentally removed just because
#         # the user switches pages or closes this view.

#     def destroy(self):
#         if self.main_frame.winfo_exists():
#             self.main_frame.destroy()


#!/usr/bin/env python3
"""Social Lock — Focus Dashboard with in-app Ubuntu password prompt."""

import time
import tkinter as tk
from tkinter import messagebox
from focus_lock import FocusLock


class FocusView:
    DEFAULT_THEME = {
        "BG": "#0F1117", "SIDEBAR": "#151821", "CARD": "#1B1F2A",
        "CARD_HOVER": "#252A38", "INPUT": "#151821", "BORDER": "#303747",
        "TEXT": "#F3F5FA", "SECONDARY": "#9AA4B5", "MUTED": "#9AA4B5",
        "ACCENT": "#8B7CFF", "ACCENT_HOVER": "#7667EE",
        "GREEN": "#37C991", "RED": "#FF6376", "ORANGE": "#F5A65B",
        "RING_BG": "#343A49",
    }
    MAX_MINUTES = 525600
    SOCIAL_SITES = ["Facebook", "Instagram", "TikTok", "Reddit", "YouTube"]

    def __init__(self, parent, theme=None):
        self.parent = parent
        self.theme = {**self.DEFAULT_THEME, **(theme or {})}
        self.social_lock = None
        self.social_running = False
        self.social_end_time = None
        self.social_total_seconds = 0
        self.social_after_id = None
        self.pomo_running = False
        self.pomo_paused = False
        self.pomo_phase = "Focus"
        self.pomo_end_time = None
        self.pomo_remaining = 25 * 60
        self.pomo_total_seconds = 25 * 60
        self.pomo_after_id = None
        self.pomo_sessions = 0
        self.destroyed = False

        self.main_frame = tk.Frame(parent, bg=self.color("BG"))
        self.main_frame.pack(fill="both", expand=True)
        self.build_interface()
        self.main_frame.bind("<Destroy>", self._on_destroy_event, add="+")

    def color(self, name):
        return self.theme.get(name, self.DEFAULT_THEME.get(name, "#FFFFFF"))

    def make_label(self, parent, text, size=11, color="TEXT", bold=False, **kwargs):
        return tk.Label(
            parent, text=text,
            font=("Ubuntu", size, "bold" if bold else "normal"),
            bg=self.color("CARD"), fg=self.color(color), **kwargs
        )

    def make_button(self, parent, text, command, primary=False, danger=False, **kwargs):
        if primary:
            bg, fg, active_bg = self.color("ACCENT"), "#FFFFFF", self.color("ACCENT_HOVER")
        elif danger:
            bg, fg, active_bg = self.color("RED"), "#FFFFFF", self.color("RED")
        else:
            bg, fg, active_bg = self.color("CARD_HOVER"), self.color("TEXT"), self.color("BORDER")
        return tk.Button(
            parent, text=text, command=command, font=("Ubuntu", 10, "bold"),
            bg=bg, fg=fg, activebackground=active_bg, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2", padx=15, pady=10,
            highlightthickness=0, **kwargs
        )

    def make_entry(self, parent, variable, width=8):
        return tk.Entry(
            parent, textvariable=variable, font=("Ubuntu", 12, "bold"),
            width=width, justify="center", bg=self.color("INPUT"),
            fg=self.color("TEXT"), insertbackground=self.color("TEXT"),
            relief="flat", bd=0, highlightthickness=1,
            highlightbackground=self.color("BORDER"),
            highlightcolor=self.color("ACCENT"),
        )

    def build_interface(self):
        header = tk.Frame(self.main_frame, bg=self.color("BG"))
        header.pack(fill="x", padx=26, pady=(22, 18))
        title_area = tk.Frame(header, bg=self.color("BG"))
        title_area.pack(side="left", fill="x", expand=True)
        tk.Label(
            title_area, text="Focus Dashboard", font=("Ubuntu", 24, "bold"),
            bg=self.color("BG"), fg=self.color("TEXT"),
        ).pack(anchor="w")
        tk.Label(
            title_area, text="Protect your attention. Make every minute count.",
            font=("Ubuntu", 10), bg=self.color("BG"), fg=self.color("SECONDARY"),
        ).pack(anchor="w", pady=(5, 0))
        self.clock_label = tk.Label(
            header, text="", font=("Ubuntu", 12, "bold"),
            bg=self.color("BG"), fg=self.color("ACCENT"),
        )
        self.clock_label.pack(side="right", padx=(10, 0))
        self.update_clock()

        self.columns = tk.Frame(self.main_frame, bg=self.color("BG"))
        self.columns.pack(fill="both", expand=True, padx=22, pady=(0, 22))
        self.columns.grid_columnconfigure(0, weight=1, uniform="cards")
        self.columns.grid_columnconfigure(1, weight=1, uniform="cards")
        self.columns.grid_rowconfigure(0, weight=1)
        self.build_social_card()
        self.build_pomodoro_card()

    def create_card(self, column):
        outer = tk.Frame(self.columns, bg=self.color("BORDER"), bd=0, highlightthickness=0)
        outer.grid(row=0, column=column, sticky="nsew", padx=7)
        card = tk.Frame(outer, bg=self.color("CARD"), bd=0, highlightthickness=0)
        card.pack(fill="both", expand=True, padx=1, pady=1)
        return card

    def create_timer_canvas(self, parent, diameter=210):
        canvas = tk.Canvas(parent, width=diameter, height=diameter,
                           bg=self.color("CARD"), highlightthickness=0, bd=0)
        canvas.pack(pady=(10, 8))
        return canvas

    @staticmethod
    def format_time(seconds):
        seconds = max(0, int(seconds))
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def format_duration(minutes):
        hours, remainder = divmod(minutes, 60)
        parts = []
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if remainder:
            parts.append(f"{remainder} minute{'s' if remainder != 1 else ''}")
        return " ".join(parts) or "0 minutes"

    def draw_timer(self, canvas, seconds, total_seconds, progress_color, subtitle):
        canvas.delete("all")
        width, height = int(canvas["width"]), int(canvas["height"])
        padding = 15
        x1, y1, x2, y2 = padding, padding, width - padding, height - padding
        canvas.create_oval(x1, y1, x2, y2, outline=self.color("RING_BG"), width=12)
        progress = max(0, min(1, seconds / max(1, total_seconds)))
        canvas.create_arc(x1, y1, x2, y2, start=90, extent=-359.99 * progress,
                          style="arc", outline=progress_color, width=12)
        canvas.create_text(width // 2, height // 2 - 12, text=self.format_time(seconds),
                           fill=self.color("TEXT"), font=("Ubuntu", 28, "bold"))
        canvas.create_text(width // 2, height // 2 + 24, text=subtitle,
                           fill=self.color("SECONDARY"), font=("Ubuntu", 10))

    # In-app password dialog. Password is not written to a file.
    def ask_for_password(self):
        dialog = tk.Toplevel(self.main_frame)
        dialog.title("Ubuntu Authentication")
        dialog.transient(self.main_frame.winfo_toplevel())
        dialog.resizable(False, False)
        dialog.configure(bg=self.color("CARD"))
        dialog.grab_set()

        tk.Label(dialog, text="Ubuntu Authentication", font=("Ubuntu", 14, "bold"),
                 bg=self.color("CARD"), fg=self.color("TEXT")).pack(padx=28, pady=(22, 8))
        tk.Label(dialog, text="Enter your Ubuntu account password to start the lock.",
                 font=("Ubuntu", 9), bg=self.color("CARD"), fg=self.color("SECONDARY"),
                 wraplength=310).pack(padx=28, pady=(0, 14))
        password_var = tk.StringVar()
        entry = tk.Entry(dialog, textvariable=password_var, show="*", font=("Ubuntu", 12),
                         bg=self.color("INPUT"), fg=self.color("TEXT"),
                         insertbackground=self.color("TEXT"), relief="flat", width=30)
        entry.pack(padx=28, ipady=8, fill="x")
        entry.focus_set()
        result = {"password": None}

        def submit(event=None):
            value = password_var.get()
            if not value:
                messagebox.showwarning("Password required", "Enter your Ubuntu password.", parent=dialog)
                return
            result["password"] = value
            password_var.set("")
            dialog.destroy()

        buttons = tk.Frame(dialog, bg=self.color("CARD"))
        buttons.pack(fill="x", padx=28, pady=20)
        tk.Button(buttons, text="Cancel", command=dialog.destroy,
                  bg=self.color("CARD_HOVER"), fg=self.color("TEXT"),
                  relief="flat", padx=14, pady=8).pack(side="right", padx=(8, 0))
        tk.Button(buttons, text="Continue", command=submit,
                  bg=self.color("ACCENT"), fg="white",
                  activebackground=self.color("ACCENT_HOVER"),
                  relief="flat", padx=14, pady=8).pack(side="right")
        dialog.bind("<Return>", submit)
        dialog.bind("<Escape>", lambda event: dialog.destroy())
        self.main_frame.wait_window(dialog)
        return result["password"]

    def build_social_card(self):
        card = self.create_card(0)
        header = tk.Frame(card, bg=self.color("CARD"))
        header.pack(fill="x", padx=22, pady=(20, 0))
        tk.Label(header, text="◉", font=("Ubuntu", 22, "bold"),
                 bg=self.color("CARD"), fg=self.color("ACCENT")).pack(side="left", padx=(0, 10))
        title_area = tk.Frame(header, bg=self.color("CARD"))
        title_area.pack(side="left", fill="x", expand=True)
        self.make_label(title_area, "Social Media Lock", size=15, bold=True).pack(anchor="w")
        self.make_label(title_area, "Stay away from distractions", color="SECONDARY", size=9).pack(anchor="w", pady=(3, 0))
        self.social_status = self.make_label(card, "●  READY TO FOCUS", color="GREEN", size=9, bold=True)
        self.social_status.pack(pady=(15, 0))
        self.social_canvas = self.create_timer_canvas(card, 190)
        self.draw_timer(self.social_canvas, 0, 1, self.color("GREEN"), "LOCK DURATION")

        duration_area = tk.Frame(card, bg=self.color("CARD"))
        duration_area.pack(pady=(0, 14))
        self.make_label(duration_area, "Lock duration", color="SECONDARY").grid(row=0, column=0, columnspan=4, pady=(0, 8))
        self.social_hours_var = tk.StringVar(value="1")
        self.social_minutes_var = tk.StringVar(value="0")
        self.social_hours_entry = self.make_entry(duration_area, self.social_hours_var, width=5)
        self.social_hours_entry.grid(row=1, column=0, padx=(0, 5), ipady=7)
        self.make_label(duration_area, "hours", color="SECONDARY").grid(row=1, column=1, padx=(0, 12))
        self.social_minutes_entry = self.make_entry(duration_area, self.social_minutes_var, width=5)
        self.social_minutes_entry.grid(row=1, column=2, padx=(0, 5), ipady=7)
        self.make_label(duration_area, "minutes", color="SECONDARY").grid(row=1, column=3)

        shortcuts = tk.Frame(card, bg=self.color("CARD"))
        shortcuts.pack(pady=(0, 14))
        for label, hours, minutes in [("30 min", 0, 30), ("1 hour", 1, 0), ("3 hours", 3, 0), ("8 hours", 8, 0)]:
            tk.Button(shortcuts, text=label,
                      command=lambda h=hours, m=minutes: self.set_social_duration(h, m),
                      font=("Ubuntu", 8), bg=self.color("CARD_HOVER"), fg=self.color("TEXT"),
                      activebackground=self.color("BORDER"), activeforeground=self.color("TEXT"),
                      relief="flat", bd=0, padx=8, pady=6, cursor="hand2").pack(side="left", padx=3)

        site_area = tk.Frame(card, bg=self.color("CARD"))
        site_area.pack(fill="x", padx=24, pady=(0, 12))
        self.make_label(site_area, "Choose websites to block", color="SECONDARY", size=9).pack(anchor="w", pady=(0, 8))
        self.site_vars = {}
        site_grid = tk.Frame(site_area, bg=self.color("CARD"))
        site_grid.pack(fill="x")
        for index, name in enumerate(self.SOCIAL_SITES):
            var = tk.BooleanVar(value=True)
            self.site_vars[name] = var
            tk.Checkbutton(site_grid, text=name, variable=var, bg=self.color("CARD"),
                           fg=self.color("TEXT"), activebackground=self.color("CARD"),
                           activeforeground=self.color("TEXT"), selectcolor=self.color("INPUT"),
                           font=("Ubuntu", 9), bd=0, highlightthickness=0, cursor="hand2").grid(
                               row=index // 3, column=index % 3, sticky="w", padx=(0, 8), pady=4)
        self.social_start_button = self.make_button(card, "Start Social Lock", self.start_social_lock, primary=True)
        self.social_start_button.pack(fill="x", padx=24, pady=(2, 8))
        self.make_label(card, "The lock runs until the timer expires.", color="SECONDARY", size=8).pack(pady=(0, 15))

    def set_social_duration(self, hours, minutes):
        if not self.social_running:
            self.social_hours_var.set(str(hours))
            self.social_minutes_var.set(str(minutes))

    def get_social_duration(self):
        try:
            hours = int(self.social_hours_var.get().strip())
            minutes = int(self.social_minutes_var.get().strip())
            if hours < 0 or minutes < 0 or (hours == 0 and minutes == 0):
                raise ValueError
            total = hours * 60 + minutes
            if total > self.MAX_MINUTES:
                raise ValueError
            return total
        except (ValueError, TypeError):
            messagebox.showerror("Invalid duration", "Enter a valid duration up to 525,600 minutes.", parent=self.main_frame)
            return None

    def start_social_lock(self):
        if self.social_running:
            return
        duration = self.get_social_duration()
        if duration is None:
            return
        selected_sites = [name for name, var in self.site_vars.items() if var.get()]
        if not selected_sites:
            messagebox.showwarning("No websites selected", "Select at least one website to block.", parent=self.main_frame)
            return
        if not messagebox.askyesno("Start Social Lock",
                                   f"Block {len(selected_sites)} website(s) for {self.format_duration(duration)}?\n\nYou won't have a stop button once the lock starts.",
                                   parent=self.main_frame):
            return
        password = self.ask_for_password()
        if password is None:
            return
        try:
            lock = FocusLock(selected_sites, duration, password)
            success, message = lock.start()
        except Exception as exc:
            success, message = False, str(exc)
        finally:
            password = None
        if not success:
            messagebox.showerror("Could not start lock", message, parent=self.main_frame)
            return
        self.social_lock = lock
        self.social_running = True
        self.social_total_seconds = duration * 60
        self.social_end_time = time.time() + self.social_total_seconds
        self.social_hours_var.set(str(duration // 60))
        self.social_minutes_var.set(str(duration % 60))
        self.social_start_button.configure(text="Social Lock Active", state="disabled", bg=self.color("CARD_HOVER"))
        self.set_social_inputs_state("disabled")
        self.social_status.configure(text="●  WEBSITES BLOCKED", fg=self.color("GREEN"))
        self.update_social_timer()

    def set_social_inputs_state(self, state):
        for widget in (self.social_hours_entry, self.social_minutes_entry):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass

    def update_social_timer(self):
        if self.destroyed or not self.social_running:
            return
        remaining = max(0, int(self.social_end_time - time.time() + 0.999))
        self.draw_timer(self.social_canvas, remaining, self.social_total_seconds, self.color("GREEN"), "TIME REMAINING")
        if remaining <= 0:
            self.finish_social_lock()
            return
        self.social_after_id = self.main_frame.after(250, self.update_social_timer)

    def finish_social_lock(self):
        if not self.social_running:
            return
        try:
            success, message = self.social_lock.stop() if self.social_lock else (True, "")
        except Exception as exc:
            success, message = False, str(exc)
        if not success:
            self.social_running = False
            self.social_status.configure(text="●  UNLOCK FAILED", fg=self.color("RED"))
            messagebox.showerror("Unlock error", f"The timer expired, but websites could not be unblocked:\n{message}", parent=self.main_frame)
            return
        self.social_running = False
        self.social_lock = None
        self.social_end_time = None
        self.social_start_button.configure(text="Start Social Lock", state="normal", bg=self.color("ACCENT"))
        self.set_social_inputs_state("normal")
        self.social_status.configure(text="●  LOCK FINISHED", fg=self.color("ORANGE"))
        self.draw_timer(self.social_canvas, 0, 1, self.color("GREEN"), "COMPLETED")
        if not self.destroyed:
            messagebox.showinfo("Social Lock Complete", "Your social media lock has finished.", parent=self.main_frame)

    # ---------------- Pomodoro ----------------

    def build_pomodoro_card(self):
        card = self.create_card(1)
        header = tk.Frame(card, bg=self.color("CARD"))
        header.pack(fill="x", padx=22, pady=(20, 0))
        tk.Label(header, text="◷", font=("Ubuntu", 24, "bold"), bg=self.color("CARD"), fg=self.color("ACCENT")).pack(side="left", padx=(0, 10))
        title_area = tk.Frame(header, bg=self.color("CARD"))
        title_area.pack(side="left", fill="x", expand=True)
        self.make_label(title_area, "Pomodoro Timer", size=15, bold=True).pack(anchor="w")
        self.make_label(title_area, "Work in focused intervals", color="SECONDARY", size=9).pack(anchor="w", pady=(3, 0))
        self.pomo_status = self.make_label(card, "●  READY", color="ACCENT", size=9, bold=True)
        self.pomo_status.pack(pady=(15, 0))
        self.pomo_canvas = self.create_timer_canvas(card, 210)
        self.draw_timer(self.pomo_canvas, self.pomo_remaining, self.pomo_total_seconds, self.color("ACCENT"), "FOCUS SESSION")
        self.pomo_phase_label = self.make_label(card, "Focus session", color="TEXT", size=12, bold=True)
        self.pomo_phase_label.pack(pady=(0, 12))
        settings = tk.Frame(card, bg=self.color("CARD"))
        settings.pack(pady=(0, 14))
        self.make_label(settings, "Focus (min)", color="SECONDARY", size=9).grid(row=0, column=0, padx=7, pady=(0, 6))
        self.make_label(settings, "Break (min)", color="SECONDARY", size=9).grid(row=0, column=1, padx=7, pady=(0, 6))
        self.focus_minutes_var = tk.StringVar(value="25")
        self.break_minutes_var = tk.StringVar(value="5")
        self.focus_entry = self.make_entry(settings, self.focus_minutes_var, width=8)
        self.focus_entry.grid(row=1, column=0, padx=7, ipady=7)
        self.break_entry = self.make_entry(settings, self.break_minutes_var, width=8)
        self.break_entry.grid(row=1, column=1, padx=7, ipady=7)
        controls = tk.Frame(card, bg=self.color("CARD"))
        controls.pack(fill="x", padx=24, pady=(0, 10))
        self.pomo_start_button = self.make_button(controls, "Start Focus", self.start_pomodoro, primary=True)
        self.pomo_start_button.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.pomo_pause_button = self.make_button(controls, "Pause", self.pause_pomodoro)
        self.pomo_pause_button.pack(side="left", fill="x", expand=True, padx=5)
        self.pomo_reset_button = self.make_button(controls, "Reset", self.reset_pomodoro)
        self.pomo_reset_button.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.pomo_sessions_label = self.make_label(card, "Completed focus sessions: 0", color="SECONDARY", size=9)
        self.pomo_sessions_label.pack(pady=(0, 17))
        self.pomo_pause_button.configure(state="disabled")

    def get_pomodoro_durations(self):
        try:
            focus = int(self.focus_minutes_var.get().strip())
            rest = int(self.break_minutes_var.get().strip())
            if not (1 <= focus <= self.MAX_MINUTES and 1 <= rest <= self.MAX_MINUTES):
                raise ValueError
            return focus, rest
        except (ValueError, TypeError):
            messagebox.showerror("Invalid duration", f"Focus and break durations must be whole numbers from 1 to {self.MAX_MINUTES} minutes.", parent=self.main_frame)
            return None

    def start_pomodoro(self):
        if self.pomo_running:
            return
        durations = self.get_pomodoro_durations()
        if durations is None:
            return
        focus, _ = durations
        self.pomo_phase = "Focus"
        self.pomo_remaining = focus * 60
        self.pomo_total_seconds = self.pomo_remaining
        self.pomo_running = True
        self.pomo_paused = False
        self.pomo_end_time = time.time() + self.pomo_remaining
        self.pomo_start_button.configure(state="disabled")
        self.pomo_pause_button.configure(text="Pause", state="normal")
        self.set_pomodoro_inputs_state("disabled")
        self.update_pomodoro_display()
        self.update_pomodoro_timer()

    def pause_pomodoro(self):
        if not self.pomo_running and not self.pomo_paused:
            return
        if self.pomo_running:
            self.pomo_remaining = max(0, int(self.pomo_end_time - time.time() + 0.999))
            self.pomo_running = False
            self.pomo_paused = True
            self.pomo_end_time = None
            self.cancel_pomo_callback()
            self.pomo_pause_button.configure(text="Resume")
            self.pomo_status.configure(text="●  PAUSED", fg=self.color("ORANGE"))
            self.update_pomodoro_display()
        else:
            self.pomo_running = True
            self.pomo_paused = False
            self.pomo_end_time = time.time() + self.pomo_remaining
            self.pomo_pause_button.configure(text="Pause")
            self.update_pomodoro_display()
            self.update_pomodoro_timer()

    def reset_pomodoro(self):
        self.cancel_pomo_callback()
        self.pomo_running = False
        self.pomo_paused = False
        self.pomo_end_time = None
        self.pomo_phase = "Focus"
        try:
            focus = int(self.focus_minutes_var.get().strip())
            if not 1 <= focus <= self.MAX_MINUTES:
                raise ValueError
        except (ValueError, TypeError):
            focus = 25
            self.focus_minutes_var.set("25")
        self.pomo_remaining = focus * 60
        self.pomo_total_seconds = self.pomo_remaining
        self.pomo_start_button.configure(text="Start Focus", state="normal")
        self.pomo_pause_button.configure(text="Pause", state="disabled")
        self.set_pomodoro_inputs_state("normal")
        self.pomo_status.configure(text="●  READY", fg=self.color("ACCENT"))
        self.pomo_phase_label.configure(text="Focus session")
        self.update_pomodoro_display()

    def update_pomodoro_timer(self):
        if self.destroyed or not self.pomo_running:
            return
        self.pomo_remaining = max(0, int(self.pomo_end_time - time.time() + 0.999))
        self.update_pomodoro_display()
        if self.pomo_remaining <= 0:
            self.complete_pomodoro_phase()
            return
        self.pomo_after_id = self.main_frame.after(250, self.update_pomodoro_timer)

    def complete_pomodoro_phase(self):
        self.cancel_pomo_callback()
        finished = self.pomo_phase
        if finished == "Focus":
            self.pomo_sessions += 1
            self.pomo_sessions_label.configure(text=f"Completed focus sessions: {self.pomo_sessions}")
            next_phase = "Break"
            _, rest = self.get_safe_durations()
            seconds = rest * 60
        else:
            next_phase = "Focus"
            focus, _ = self.get_safe_durations()
            seconds = focus * 60
        self.pomo_phase = next_phase
        self.pomo_remaining = seconds
        self.pomo_total_seconds = seconds
        self.pomo_running = False
        self.pomo_paused = False
        self.pomo_end_time = None
        self.pomo_start_button.configure(text=f"Start {next_phase}", state="normal")
        self.pomo_pause_button.configure(state="disabled")
        self.set_pomodoro_inputs_state("normal")
        self.pomo_status.configure(text="●  PHASE COMPLETE", fg=self.color("GREEN"))
        self.pomo_phase_label.configure(text=f"{next_phase} session ready")
        self.update_pomodoro_display()
        if not self.destroyed:
            msg = "Focus session completed! Take a break." if finished == "Focus" else "Break completed! Ready for another focus session?"
            messagebox.showinfo("Pomodoro Complete", msg, parent=self.main_frame)

    def get_safe_durations(self):
        try:
            focus = int(self.focus_minutes_var.get().strip())
            rest = int(self.break_minutes_var.get().strip())
            if not 1 <= focus <= self.MAX_MINUTES:
                focus = 25
            if not 1 <= rest <= self.MAX_MINUTES:
                rest = 5
            return focus, rest
        except (ValueError, TypeError):
            return 25, 5

    def update_pomodoro_display(self):
        if self.pomo_phase == "Focus":
            color, subtitle = self.color("ACCENT"), "FOCUS SESSION"
        else:
            color, subtitle = self.color("GREEN"), "BREAK TIME"
        self.draw_timer(self.pomo_canvas, self.pomo_remaining, self.pomo_total_seconds, color, subtitle)
        self.pomo_phase_label.configure(text="Focus session" if self.pomo_phase == "Focus" else "Break session")

    def set_pomodoro_inputs_state(self, state):
        for widget in (self.focus_entry, self.break_entry):
            try:
                widget.configure(state=state)
            except tk.TclError:
                pass

    def update_clock(self):
        if self.destroyed:
            return
        self.clock_label.configure(text=time.strftime("%H:%M:%S"))
        self.main_frame.after(1000, self.update_clock)

    def cancel_pomo_callback(self):
        if self.pomo_after_id is not None:
            try:
                self.main_frame.after_cancel(self.pomo_after_id)
            except tk.TclError:
                pass
            self.pomo_after_id = None

    def _on_destroy_event(self, event):
        if event.widget is not self.main_frame or self.destroyed:
            return
        self.destroyed = True
        for after_id in (self.social_after_id, self.pomo_after_id):
            if after_id is not None:
                try:
                    self.main_frame.after_cancel(after_id)
                except tk.TclError:
                    pass
        self.social_after_id = None
        self.pomo_after_id = None
        # Do not automatically remove a running hosts block when changing pages.

    def destroy(self):
        if self.main_frame.winfo_exists():
            self.main_frame.destroy()
