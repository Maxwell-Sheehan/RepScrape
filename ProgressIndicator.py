# progress_indicator.py
import tkinter as tk
from tkinter import ttk

class ProgressIndicator:
    def __init__(self, parent):
        self.progress = ttk.Progressbar(parent, mode='indeterminate', length=300)
        self.progress.pack(pady=5)

    def start(self):
        self.progress.start(10)

    def stop(self):
        self.progress.stop()
