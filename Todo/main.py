

#!/usr/bin/env python3

import tkinter as tk
import json
import os
from tkinter import ttk, messagebox

from calendar_view import CalendarView
from habits_view import HabitsView
from todo_view import TodoView
from notes_view import NotesView
from focus_view import FocusView


class SocialLockApp:
    THEME_FILE = os.path.expanduser("~/.social_lock_theme.json")

    THEMES = {
        "dark": {
            "BG": "#0F1117",
            "SIDEBAR": "#151821",
            "CARD": "#1B1F2A",
            "CARD_HOVER": "#242936",
            "TEXT": "#F1F5F9",
            "MUTED": "#8B93A7",
            "ACCENT": "#6366F1",
            "BORDER": "#292E3A",
        },
        "light": {
            "BG": "#F5F7FB",
            "SIDEBAR": "#FFFFFF",
            "CARD": "#FFFFFF",
            "CARD_HOVER": "#EDF0F7",
            "TEXT": "#202538",
            "MUTED": "#687086",
            "ACCENT": "#6366F1",
            "BORDER": "#DFE3EC",
        },
    }

    def __init__(self, root):
        self.root = root
        self.theme_name = self.load_saved_theme()
        self.current_view = None
        self.current_page_name = "Dashboard"
        self.nav_buttons = {}

        self.apply_colors()

        self.root.title("Social Lock")
        self.root.geometry("1250x800")
        self.root.minsize(950, 650)
        self.root.configure(bg=self.BG)

        self.setup_styles()
        self.create_layout()
        self.show_dashboard()

    # ========================================================
    # THEME
    # ========================================================

    def load_saved_theme(self):
        try:
            with open(self.THEME_FILE, "r", encoding="utf-8") as file:
                theme = json.load(file).get("theme", "dark")
                return theme if theme in self.THEMES else "dark"
        except (OSError, json.JSONDecodeError, AttributeError):
            return "dark"

    def save_theme(self):
        try:
            with open(self.THEME_FILE, "w", encoding="utf-8") as file:
                json.dump({"theme": self.theme_name}, file)
        except OSError as error:
            print("Could not save theme:", error)

    def apply_colors(self):
        for key, value in self.THEMES[self.theme_name].items():
            setattr(self, key, value)

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "TProgressbar",
            troughcolor=self.BORDER,
            background=self.ACCENT,
            borderwidth=0,
        )

    def change_theme(self, theme_name):
        if theme_name not in self.THEMES:
            return

        self.theme_name = theme_name
        self.apply_colors()
        self.save_theme()
        self.root.configure(bg=self.BG)

        self.sidebar.configure(bg=self.SIDEBAR)
        self.content.configure(bg=self.BG)

        self.setup_styles()

        # Recreate the active page using the new theme.
        self.open_page(self.current_page_name)

    # ========================================================
    # MAIN LAYOUT
    # ========================================================

    def create_layout(self):
        self.sidebar = tk.Frame(
            self.root,
            bg=self.SIDEBAR,
            width=300,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(self.root, bg=self.BG)
        self.content.pack(side="right", fill="both", expand=True)

        self.create_sidebar()

    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):
        logo = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        logo.pack(fill="x", padx=18, pady=(25, 30))

        tk.Label(
            logo,
            text="◉",
            font=("Arial", 25, "bold"),
            fg=self.ACCENT,
            bg=self.SIDEBAR,
        ).pack(side="left")

        tk.Label(
            logo,
            text="Focus Lock",
            font=("Arial", 10, "bold"),
            fg=self.TEXT,
            bg=self.SIDEBAR,
        ).pack(side="left", padx=8)

        tk.Label(
            self.sidebar,
            text="MENU",
            font=("Arial", 9, "bold"),
            fg=self.MUTED,
            bg=self.SIDEBAR,
        ).pack(anchor="w", padx=22, pady=(0, 10))

        pages = [
            ("Dashboard", "⌂"),
            ("Habits", "✓"),
            ("Calendar", "▦"),
            ("Daily Notes", "✎"),
            ("To_doList", "✎"),
            ("Focus Lock", "◉"),
            ("Settings", "⚙"),
        ]

        actions = {
            "Dashboard": self.show_dashboard,
            "Habits": self.show_habits,
            "Calendar": self.show_calendar,
            "Daily Notes": self.show_notes,
            "Focus Lock": self.show_focus,
            "To_doList": self.show_todo,
            
            "Settings": self.show_settings,
        }

        for name, icon in pages:
            button = tk.Button(
                self.sidebar,
                text=f"  {icon}    {name}",
                command=actions[name],
                anchor="w",
                font=("Arial", 11),
                fg=self.TEXT,
                bg=self.SIDEBAR,
                activeforeground=self.TEXT,
                activebackground=self.CARD_HOVER,
                relief="flat",
                bd=0,
                padx=16,
                pady=13,
                cursor="hand2",
            )
            button.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[name] = button

        bottom = tk.Frame(self.sidebar, bg=self.SIDEBAR)
        bottom.pack(side="bottom", fill="x", padx=20, pady=20)

        tk.Label(
            bottom,
            text="Build your discipline.",
            font=("Arial", 10),
            fg=self.MUTED,
            bg=self.SIDEBAR,
        ).pack(anchor="w")

        tk.Label(
            bottom,
            text="Social Lock v1.0",
            font=("Arial", 9),
            fg=self.MUTED,
            bg=self.SIDEBAR,
        ).pack(anchor="w", pady=(5, 0))

    def set_active_nav(self, name):
        for page_name, button in self.nav_buttons.items():
            if page_name == name:
                button.configure(bg=self.ACCENT, fg="white")
            else:
                button.configure(bg=self.SIDEBAR, fg=self.TEXT)

    # ========================================================
    # PAGE MANAGEMENT
    # ========================================================

    def clear_content(self):
        # Destroy the old view before creating another one.
        if self.current_view is not None:
            try:
                if hasattr(self.current_view, "destroy"):
                    self.current_view.destroy()
            except (tk.TclError, Exception):
                pass

            self.current_view = None

        for widget in self.content.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

    def open_page(self, name):
        pages = {
            "Dashboard": self.show_dashboard,
            "Habits": self.show_habits,
            "Calendar": self.show_calendar,
            "Daily Notes": self.show_notes,
            "Focus Lock": self.show_focus,
            "To_doList": self.show_todo,
            
            "Settings": self.show_settings,
        }

        page = pages.get(name)
        if page is not None:
            page()

    def create_page_header(self, title, subtitle=""):
        header = tk.Frame(self.content, bg=self.BG)
        header.pack(fill="x", padx=30, pady=(25, 20))

        tk.Label(
            header,
            text=title,
            font=("Arial", 25, "bold"),
            fg=self.TEXT,
            bg=self.BG,
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                header,
                text=subtitle,
                font=("Arial", 10),
                fg=self.MUTED,
                bg=self.BG,
            ).pack(anchor="w", pady=(5, 0))

    # ========================================================
    # DASHBOARD
    # ========================================================

    def show_dashboard(self):
        self.current_page_name = "Dashboard"
        self.clear_content()
        self.set_active_nav("Dashboard")

        self.create_page_header(
            "Dashboard",
            "Stay consistent. Build your day.",
        )

        stats = tk.Frame(self.content, bg=self.BG)
        stats.pack(fill="x", padx=25, pady=(0, 20))

        for title, value, icon in [
            ("Today's Habits", "0 / 0", "✓"),
            ("Habit Progress", "0%", "%"),
            ("Current Streak", "0 days", "🔥"),
            ("Focus Sessions", "0", "◉"),
        ]:
            card = tk.Frame(stats, bg=self.CARD, height=110)
            card.pack(side="left", fill="both", expand=True, padx=5)
            card.pack_propagate(False)

            tk.Label(
                card,
                text=icon,
                font=("Arial", 17),
                fg=self.ACCENT,
                bg=self.CARD,
            ).pack(anchor="w", padx=15, pady=(12, 0))

            tk.Label(
                card,
                text=value,
                font=("Arial", 19, "bold"),
                fg=self.TEXT,
                bg=self.CARD,
            ).pack(anchor="w", padx=15)

            tk.Label(
                card,
                text=title,
                font=("Arial", 9),
                fg=self.MUTED,
                bg=self.CARD,
            ).pack(anchor="w", padx=15)

        tk.Label(
            self.content,
            text="Quick Actions",
            font=("Arial", 16, "bold"),
            fg=self.TEXT,
            bg=self.BG,
        ).pack(anchor="w", padx=30, pady=(5, 12))

        actions = tk.Frame(self.content, bg=self.BG)
        actions.pack(fill="x", padx=25)

        for title, command in [
            ("✓  Manage Habits", self.show_habits),
            ("▦  Open Calendar", self.show_calendar),
            ("✎  Daily Notes", self.show_notes),
            ("◉  Focus Lock", self.show_focus),
        ]:
            tk.Button(
                actions,
                text=title,
                command=command,
                font=("Arial", 10, "bold"),
                bg=self.CARD,
                fg=self.TEXT,
                activebackground=self.CARD_HOVER,
                activeforeground=self.TEXT,
                relief="flat",
                padx=12,
                pady=16,
                cursor="hand2",
            ).pack(side="left", fill="x", expand=True, padx=4)

        welcome = tk.Frame(self.content, bg=self.CARD)
        welcome.pack(fill="both", expand=True, padx=30, pady=25)

        tk.Label(
            welcome,
            text="Your personal discipline system",
            font=("Arial", 19, "bold"),
            fg=self.TEXT,
            bg=self.CARD,
        ).pack(anchor="w", padx=22, pady=(25, 8))

        tk.Label(
            welcome,
            text=(
                "Track your habits, schedule your day, write your thoughts, "
                "and protect your focus from distracting websites."
            ),
            font=("Arial", 11),
            fg=self.MUTED,
            bg=self.CARD,
            wraplength=650,
            justify="left",
        ).pack(anchor="w", padx=22)

    # ========================================================
    # HABITS
    # ========================================================

    def show_habits(self):
        self.current_page_name = "Habits"
        self.clear_content()
        self.set_active_nav("Habits")

        # HabitsView manages and packs its own main_frame.
        self.current_view = HabitsView(
            self.content,
            theme=self.theme_name,
        )
    def show_todo(self):
        self.current_page_name = "To-Do List"
        self.clear_content()
        self.set_active_nav("To-Do List")

        self.current_view = TodoView(
            self.content,
            theme=self.theme_name,
        )

        self.current_view.pack(
            fill="both",
            expand=True,
        )
    # ========================================================
    # CALENDAR
    # ========================================================

    def show_calendar(self):
        self.current_page_name = "Calendar"
        self.clear_content()
        self.set_active_nav("Calendar")

        # CalendarView is a Tkinter Frame, so pack it explicitly.
        self.current_view = CalendarView(
            self.content,
            theme=self.theme_name,
        )
        self.current_view.pack(fill="both", expand=True)

    # ========================================================
    # DAILY NOTES
    # ========================================================

    def show_notes(self):
        self.current_page_name = "Daily Notes"
        self.clear_content()
        self.set_active_nav("Daily Notes")

        self.current_view = NotesView(
            self.content,
            theme=self.theme_name,
        )

        # Support views that don't pack themselves.
        if isinstance(self.current_view, tk.Widget):
            if not self.current_view.winfo_manager():
                self.current_view.pack(fill="both", expand=True)

    # ========================================================
    # FOCUS LOCK
    # ========================================================

    def show_focus(self):
        self.current_page_name = "Focus Lock"
        self.clear_content()
        self.set_active_nav("Focus Lock")

        focus_theme = {
            "BG": self.BG,
            "CARD": self.CARD,
            "BORDER": self.BORDER,
            "TEXT": self.TEXT,
            "SECONDARY": self.MUTED,
            "ACCENT": self.ACCENT,
            "ACCENT_HOVER": self.ACCENT,
            "GREEN": "#35D07F" if self.theme_name == "dark" else "#168B50",
            "RED": "#FF5C68" if self.theme_name == "dark" else "#D93649",
            "INPUT": self.CARD_HOVER,
        }

        self.current_view = FocusView(
            self.content,
            theme=focus_theme,
        )

        if isinstance(self.current_view, tk.Widget):
            if not self.current_view.winfo_manager():
                self.current_view.pack(fill="both", expand=True)

    # ========================================================
    # SETTINGS
    # ========================================================

    def show_settings(self):
        self.current_page_name = "Settings"
        self.clear_content()
        self.set_active_nav("Settings")

        self.create_page_header(
            "Settings",
            "Configure your Social Lock application.",
        )

        card = tk.Frame(self.content, bg=self.CARD)
        card.pack(fill="x", padx=30, pady=10)

        tk.Label(
            card,
            text="Appearance",
            font=("Arial", 17, "bold"),
            fg=self.TEXT,
            bg=self.CARD,
        ).pack(anchor="w", padx=22, pady=(22, 8))

        tk.Label(
            card,
            text="Choose your preferred application theme.",
            font=("Arial", 10),
            fg=self.MUTED,
            bg=self.CARD,
        ).pack(anchor="w", padx=22, pady=(0, 15))

        buttons = tk.Frame(card, bg=self.CARD)
        buttons.pack(anchor="w", padx=22, pady=(0, 22))

        for theme, label in [
            ("dark", "☾  Dark Mode"),
            ("light", "☀  Light Mode"),
        ]:
            tk.Button(
                buttons,
                text=label,
                command=lambda t=theme: self.change_theme(t),
                font=("Arial", 10, "bold"),
                bg=self.ACCENT if self.theme_name == theme else self.CARD_HOVER,
                fg="white" if self.theme_name == theme else self.TEXT,
                activebackground=self.ACCENT,
                activeforeground="white",
                relief="flat",
                padx=18,
                pady=12,
                cursor="hand2",
            ).pack(side="left", padx=(0, 10))

        info = tk.Frame(self.content, bg=self.CARD)
        info.pack(fill="x", padx=30, pady=10)

        tk.Label(
            info,
            text="Application Information",
            font=("Arial", 15, "bold"),
            fg=self.TEXT,
            bg=self.CARD,
        ).pack(anchor="w", padx=22, pady=(18, 10))

        for label, value in [
            ("Application", "Social Lock"),
            ("Version", "1.0.0"),
            ("Platform", "Ubuntu / Linux"),
        ]:
            row = tk.Frame(info, bg=self.CARD)
            row.pack(fill="x", padx=22, pady=6)

            tk.Label(
                row, text=label, fg=self.MUTED, bg=self.CARD
            ).pack(side="left")

            tk.Label(
                row, text=value, fg=self.TEXT, bg=self.CARD
            ).pack(side="right")

        tk.Frame(info, bg=self.CARD, height=15).pack()

    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(self):
        if self.current_view is not None:
            try:
                self.current_view.destroy()
            except Exception:
                pass

        self.root.destroy()


def main():
    root = tk.Tk()
    app = SocialLockApp(root)

    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
