import tkinter as tk
from tkinter import ttk
from threading import Thread
from TicketService import TicketService
from TicketStatusService import TicketStatusService
from ProgressIndicator import ProgressIndicator

# ---------- Simple dark palette ----------
DARK_BG = "#22252a"
DARK_PANEL = "#2b2f35"
DARK_TEXT = "#e6eef6"
ACCENT = "#4aa3df"
SEPARATOR = "#374047"

class AppSidebarDark:
    def __init__(self, root, api_client):
        self.root = root
        self.api_client = api_client

        self.ticket_service = TicketService(api_client)
        self.status_service = TicketStatusService(api_client)

        # root config
        self.root.title("ConnectWise Ticket Viewer")
        self.root.configure(bg=DARK_BG)

        # style tweaks for ttk
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background=ACCENT, foreground=DARK_TEXT)
        style.configure("TLabel", background=DARK_BG, foreground=DARK_TEXT)
        style.configure("TFrame", background=DARK_PANEL)
        style.configure(
            "TCombobox",
            fieldbackground=DARK_PANEL,
            background=DARK_PANEL,
            foreground=DARK_TEXT,
            relief="flat"
        )

        # --- Custom style for the LIMIT combobox (the blue textbox look) ---
        style.configure(
            "LimitCombo.TCombobox",
            fieldbackground="#2b4d6e",  # bluish background
            background="#2b4d6e",
            foreground="white",
            arrowcolor="white",
            selectbackground="#1e3a56",
            selectforeground="white",
        )

        # ---------- layout frames ----------
        self.sidebar = tk.Frame(root, bg=DARK_PANEL, width=320, padx=12, pady=12)
        self.sidebar.pack(side="left", fill="y")

        self.main = tk.Frame(root, bg=DARK_BG, padx=8, pady=8)
        self.main.pack(side="right", fill="both", expand=True)

        # ---------------------------------------------------------
        #                   SIDEBAR CONTENT
        # ---------------------------------------------------------

        # --- Max Tickets (Global) ---
        ttk.Label(self.sidebar, text="Max Tickets (Global)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,4))

        self.limit_var = tk.IntVar(value=25)
        self.limit_combo = ttk.Combobox(
            self.sidebar,
            textvariable=self.limit_var,
            values=[10, 25, 50, 100],
            state="readonly",
            width=14,
            font=("Segoe UI", 11),
            style="LimitCombo.TCombobox"
        )

        self.limit_combo.pack(fill="x", pady=(0, 14))

        # --- Search by Username ---
        ttk.Label(self.sidebar, text="Search by Username", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,4))

        self.user_entry = tk.Entry(
            self.sidebar,
            bg="#33373b",
            fg=DARK_TEXT,
            insertbackground=DARK_TEXT,
            font=("Segoe UI", 11)
        )
        self.user_entry.pack(fill="x", pady=(0, 8))

        ttk.Button(self.sidebar, text="Search Username", command=self.start_user_search).pack(fill="x", pady=(0,12))

        # separator
        ttk.Separator(self.sidebar, orient="horizontal").pack(fill="x", pady=8)

        # --- Search by Board/Status ---
        ttk.Label(self.sidebar, text="Search by Board/Status", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,4))

        ttk.Label(self.sidebar, text="Board").pack(anchor="w")
        self.board_entry = tk.Entry(
            self.sidebar,
            bg="#33373b",
            fg=DARK_TEXT,
            insertbackground=DARK_TEXT,
            font=("Segoe UI", 11)
        )
        self.board_entry.pack(fill="x", pady=(0,8))

        ttk.Label(self.sidebar, text="Status").pack(anchor="w")
        self.status_entry = tk.Entry(
            self.sidebar,
            bg="#33373b",
            fg=DARK_TEXT,
            insertbackground=DARK_TEXT,
            font=("Segoe UI", 11)
        )
        self.status_entry.pack(fill="x", pady=(0,8))

        ttk.Button(self.sidebar, text="Search Board/Status", command=self.start_status_search).pack(fill="x", pady=(4,10))

        # small footer info
        self.duration_label = ttk.Label(self.sidebar, text="")
        self.duration_label.pack(anchor="w", pady=(6,0))

        # ---------- Main content ----------
        self.progress = ProgressIndicator(self.main)
        self.output_box = tk.Text(
            self.main,
            bg="#111316",
            fg=DARK_TEXT,
            insertbackground=DARK_TEXT,
            wrap="word"
        )
        self.output_box.pack(fill="both", expand=True)
        self.output_box.config(padx=8, pady=8)

    # ---------- Username search ----------
    def start_user_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self._search_user, daemon=True).start()

    def _search_user(self):
        username = self.user_entry.get().strip()
        limit = int(self.limit_var.get() or 25)
        try:
            tickets, duration = self.ticket_service.get_tickets_for_user(username, limit=limit)
            self.root.after(0, lambda: self.duration_label.config(text=f"Query time: {duration} ms"))
            label = f"Tickets for '{username}'"
            self.root.after(0, lambda: self.display_tickets(tickets, label))
        except Exception as e:
            self.root.after(0, lambda: self.output_box.insert(tk.END, f"Error: {e}\n"))
            self.root.after(0, self.progress.stop)

    # ---------- Board/status search ----------
    def start_status_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self._search_status, daemon=True).start()

    def _search_status(self):
        board = self.board_entry.get().strip() or None
        status = self.status_entry.get().strip() or None
        limit = int(self.limit_var.get() or 25)
        try:
            tickets, duration = self.status_service.get_tickets_by_status(
                board_name=board,
                status_name=status,
                limit=limit
            )
            self.root.after(0, lambda: self.duration_label.config(text=f"Query time: {duration} ms"))
            label = f"Board='{board}', Status='{status}'"
            self.root.after(0, lambda: self.display_tickets(tickets, label))
        except Exception as e:
            self.root.after(0, lambda: self.output_box.insert(tk.END, f"Error: {e}\n"))
            self.root.after(0, self.progress.stop)

    # ---------- Render tickets ----------
    def display_tickets(self, tickets, header_label):
        self.progress.stop()
        self.output_box.insert(tk.END, f"Results for {header_label}:\n\n")

        if not tickets:
            self.output_box.insert(tk.END, "No tickets found.\n")
            return

        for t in tickets:
            tid = t.get("id", "N/A")
            summary = t.get("summary", "")
            owner = t.get("owner", {}).get("identifier", "")
            status = t.get("status", {}).get("name", "")
            board = t.get("board", {}).get("name", "")
            team = t.get("team", {}).get("name", "")
            updated = t.get("lastUpdated", "")

            ticket_link = f"https://<YOUR_URL>/ConnectWise.aspx?routeTo=Ticket/{tid}"

            self.output_box.insert(
                tk.END,
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Ticket # {tid}\n"
                f"Summary      : {summary}\n"
                f"Owner        : {owner}\n"
                f"Status       : {status}\n"
                f"Board        : {board}\n"
                f"Team         : {team}\n"
                f"Last Updated : {updated}\n"
                f"Link         : {ticket_link}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )
