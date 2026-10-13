
#!/usr/bin/env python3
"""
Notes Manager
=============

Business logic for the Social Lock daily journaling system.

Responsibilities:
    - Save and retrieve daily notes.
    - Manage moods associated with notes.
    - Normalize and validate dates.
    - Provide convenient helpers for today's note.
    - Keep database operations separate from the UI.

Database functions required:
    save_daily_note(note_date, note, mood)
    get_daily_note(note_date)
"""

from datetime import date, datetime
from typing import Any, Optional

from database import (
    save_daily_note,
    get_daily_note,
)


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_MOOD = ""

NOTE_FIELD = "note"
MOOD_FIELD = "mood"


# ============================================================
# NOTES MANAGER
# ============================================================

class NotesManager:
    """
    Manages daily journal entries.

    Notes are stored using ISO date strings:
        YYYY-MM-DD

    Each entry may contain:
        - note: journal text
        - mood: mood associated with the day
    """

    def __init__(self):
        """Initialize the notes manager."""
        pass

    # ========================================================
    # DATE HANDLING
    # ========================================================

    @staticmethod
    def normalize_date(note_date: Any) -> str:
        """
        Convert a date, datetime, or ISO date string into
        a consistent YYYY-MM-DD string.

        Examples:
            date.today()          -> '2026-10-12'
            '2026-10-12'          -> '2026-10-12'
            datetime.now()        -> '2026-10-12'

        Raises:
            TypeError: If the supplied value has an invalid type.
            ValueError: If the date string is invalid.
        """

        if isinstance(note_date, datetime):
            return note_date.date().isoformat()

        if isinstance(note_date, date):
            return note_date.isoformat()

        if isinstance(note_date, str):
            cleaned_date = note_date.strip()

            if not cleaned_date:
                raise ValueError("Note date cannot be empty.")

            try:
                parsed_date = date.fromisoformat(cleaned_date)
            except ValueError as error:
                raise ValueError(
                    "Invalid note date. Use YYYY-MM-DD."
                ) from error

            return parsed_date.isoformat()

        raise TypeError(
            "note_date must be a date, datetime, or ISO date string."
        )

    # ========================================================
    # SAVE NOTE
    # ========================================================

    def save_note(
        self,
        note_date: Any,
        note: str,
        mood: str = DEFAULT_MOOD,
    ) -> Any:
        """
        Save or update a daily note.

        Args:
            note_date: Date object, datetime object, or ISO date.
            note: Journal text.
            mood: Optional mood label.

        Returns:
            The result returned by the database save function.

        Notes:
            Empty text is allowed so the existing database
            function can handle clearing or updating an entry.
        """

        normalized_date = self.normalize_date(note_date)

        if not isinstance(note, str):
            raise TypeError("Note content must be a string.")

        if not isinstance(mood, str):
            raise TypeError("Mood must be a string.")

        cleaned_note = note.strip()
        cleaned_mood = mood.strip()

        return save_daily_note(
            normalized_date,
            cleaned_note,
            cleaned_mood,
        )

    # ========================================================
    # GET NOTE
    # ========================================================

    def get_note(
        self,
        note_date: Any,
    ) -> Optional[dict]:
        """
        Retrieve a note for a particular date.

        Returns:
            A dictionary containing the stored note, or None
            when no entry exists.

        The dictionary structure depends on database.py.
        """

        normalized_date = self.normalize_date(note_date)

        result = get_daily_note(normalized_date)

        if result is None:
            return None

        if not isinstance(result, dict):
            raise TypeError(
                "get_daily_note() must return a dictionary or None."
            )

        return result

    # ========================================================
    # GET NOTE TEXT
    # ========================================================

    def get_note_text(
        self,
        note_date: Any,
    ) -> str:
        """Return only the journal text for a given date."""

        note = self.get_note(note_date)

        if not note:
            return ""

        value = note.get(NOTE_FIELD, "")

        return value if isinstance(value, str) else ""

    # ========================================================
    # GET MOOD
    # ========================================================

    def get_mood(
        self,
        note_date: Any,
    ) -> str:
        """Return the mood saved for a particular date."""

        note = self.get_note(note_date)

        if not note:
            return ""

        value = note.get(MOOD_FIELD, "")

        return value if isinstance(value, str) else ""

    # ========================================================
    # CHECK WHETHER A NOTE EXISTS
    # ========================================================

    def has_note(
        self,
        note_date: Any,
    ) -> bool:
        """
        Return True if the date has non-empty journal text.

        A mood-only entry does not count as a written note.
        """

        return bool(
            self.get_note_text(note_date).strip()
        )

    # ========================================================
    # GET WORD COUNT
    # ========================================================

    def get_word_count(
        self,
        note_date: Any,
    ) -> int:
        """Return the number of words in a saved journal entry."""

        return len(
            self.get_note_text(note_date).split()
        )

    # ========================================================
    # GET CHARACTER COUNT
    # ========================================================

    def get_character_count(
        self,
        note_date: Any,
    ) -> int:
        """Return the number of characters in a saved note."""

        return len(
            self.get_note_text(note_date)
        )

    # ========================================================
    # TODAY'S NOTE
    # ========================================================

    def save_today_note(
        self,
        note: str,
        mood: str = DEFAULT_MOOD,
    ) -> Any:
        """Save a note for today's date."""

        return self.save_note(
            date.today(),
            note,
            mood,
        )

    def get_today_note(self) -> Optional[dict]:
        """Retrieve today's complete note entry."""

        return self.get_note(date.today())

    def get_today_note_text(self) -> str:
        """Retrieve only today's journal text."""

        return self.get_note_text(date.today())

    def get_today_mood(self) -> str:
        """Retrieve today's saved mood."""

        return self.get_mood(date.today())


# ============================================================
# SHARED MANAGER
# ============================================================

_manager = NotesManager()


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

def save_note(
    note_date: Any,
    note: str,
    mood: str = DEFAULT_MOOD,
) -> Any:
    """Save or update a note for a particular date."""

    return _manager.save_note(
        note_date,
        note,
        mood,
    )


def get_note(
    note_date: Any,
) -> Optional[dict]:
    """Retrieve a complete note entry."""

    return _manager.get_note(note_date)


def get_note_text(
    note_date: Any,
) -> str:
    """Retrieve the journal text for a date."""

    return _manager.get_note_text(note_date)


def get_mood(
    note_date: Any,
) -> str:
    """Retrieve the mood associated with a date."""

    return _manager.get_mood(note_date)


def has_note(
    note_date: Any,
) -> bool:
    """Check whether a date has non-empty journal text."""

    return _manager.has_note(note_date)


def get_word_count(
    note_date: Any,
) -> int:
    """Get the word count of a saved note."""

    return _manager.get_word_count(note_date)


def get_character_count(
    note_date: Any,
) -> int:
    """Get the character count of a saved note."""

    return _manager.get_character_count(note_date)


# ============================================================
# TODAY'S NOTE HELPERS
# ============================================================

def save_today_note(
    note: str,
    mood: str = DEFAULT_MOOD,
) -> Any:
    """Save today's journal entry."""

    return _manager.save_today_note(
        note,
        mood,
    )


def get_today_note() -> Optional[dict]:
    """Retrieve today's complete journal entry."""

    return _manager.get_today_note()


def get_today_note_text() -> str:
    """Retrieve today's journal text."""

    return _manager.get_today_note_text()


def get_today_mood() -> str:
    """Retrieve today's mood."""

    return _manager.get_today_mood()


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 45)
    print("SOCIAL LOCK | NOTES MANAGER")
    print("=" * 45)

    today = date.today()

    try:
        note = get_note(today)

        print(f"Date:       {today.isoformat()}")

        if note:
            print(f"Has note:   {has_note(today)}")
            print(f"Word count: {get_word_count(today)}")
            print(f"Mood:       {get_mood(today) or 'Not recorded'}")
            print()
            print("Journal entry:")
            print(get_note_text(today) or "(Empty)")
        else:
            print("No journal entry exists for today.")

        print()
        print("Notes manager loaded successfully.")

    except Exception as error:
        print(f"Could not load notes: {error}")
        raise
