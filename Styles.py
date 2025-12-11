# styles.py
from tkinter import ttk

# ---------- Simple dark palette ----------
DARK_BG = "#22252a"
DARK_PANEL = "#2b2f35"
DARK_TEXT = "#e6eef6"
ACCENT = "#4aa3df"
SEPARATOR = "#374047"


def apply_styles():
    """Apply global ttk styles for the dark UI theme."""
    style = ttk.Style()
    style.theme_use('clam')

    style.configure("TButton",
                    background=ACCENT,
                    foreground=DARK_TEXT)

    style.configure("TLabel",
                    background=DARK_BG,
                    foreground=DARK_TEXT)

    style.configure("TFrame",
                    background=DARK_PANEL)

    style.configure("TCombobox",
                    fieldbackground=DARK_PANEL,
                    background=DARK_PANEL,
                    foreground=DARK_TEXT,
                    relief="flat")
