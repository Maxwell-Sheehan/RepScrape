# styles.py
import tkinter as tk
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

def create_page_size_dropdown(parent):
    """
    Creates a standardized 'Page Size' label + combobox using global styles.
    Returns (label_widget, combobox_widget, variable_reference).
    """
    label = ttk.Label(parent, text="Page Size")

    var = tk.IntVar(value=50)

    box = ttk.Combobox(
        parent,
        textvariable=var,
        values=[50, 150, 250],
        state="readonly",
        font=("Segoe UI", 11)
    )

    return label, box, var
