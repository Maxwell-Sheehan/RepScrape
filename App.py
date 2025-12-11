import tkinter as tk
from tkinter import ttk
from threading import Thread

from TicketService import TicketService
from TicketStatusService import TicketStatusService
from ProgressIndicator import ProgressIndicator


class App:
    def __init__(self, root, api_client):
        self.root = root
        self.api_client = api_client

        self.ticket_service = TicketService(api_client)
        self.status_service = TicketStatusService(api_client)

        self.root.title("ConnectWise Ticket Viewer")

        # ---------------------------------
        # Notebook (Tabs)
        # ---------------------------------
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_user = tk.Frame(self.notebook)
        self.tab_status = tk.Frame(self.notebook)

        self.notebook.add(self.tab_user, text="Search by Username")
        self.notebook.add(self.tab_status, text="Search by Status/Board")

        # ============================================================
        # TAB 1: USERNAME SEARCH
        # ============================================================
        tk.Label(self.tab_user, text="Enter Username:").pack(anchor="w")
        self.user_entry = tk.Entry(self.tab_user)
        self.user_entry.pack(fill="x")

        # Ticket Limit Selector
        tk.Label(self.tab_user, text="Number of Tickets:").pack(anchor="w")
        self.limit_var_user = tk.StringVar(value="10")
        self.limit_combo_user = ttk.Combobox(
            self.tab_user,
            textvariable=self.limit_var_user,
            values=["10", "25", "50", "100"],
            state="readonly",
            width=10
        )
        self.limit_combo_user.pack()

        tk.Button(self.tab_user, text="Search", command=self.start_user_search).pack(pady=5)

        # ============================================================
        # TAB 2: STATUS + BOARD SEARCH
        # ============================================================
        tk.Label(self.tab_status, text="Board Name:").pack(anchor="w")
        self.board_entry = tk.Entry(self.tab_status)
        self.board_entry.pack(fill="x")

        tk.Label(self.tab_status, text="Status Name:").pack(anchor="w")
        self.status_entry = tk.Entry(self.tab_status)
        self.status_entry.pack(fill="x")

        # Ticket Limit Selector for status search
        tk.Label(self.tab_status, text="Number of Tickets:").pack(anchor="w")
        self.limit_var_status = tk.StringVar(value="25")
        self.limit_combo_status = ttk.Combobox(
            self.tab_status,
            textvariable=self.limit_var_status,
            values=["10", "25", "50", "100"],
            state="readonly",
            width=10
        )
        self.limit_combo_status.pack()

        tk.Button(self.tab_status, text="Search", command=self.start_status_search).pack(pady=5)

        # ---------------------------------
        # Shared UI components
        # ---------------------------------
        self.duration_label = tk.Label(root, text="", fg="gray")
        self.duration_label.pack()

        self.progress = ProgressIndicator(root)

        self.output_box = tk.Text(root, width=120, height=25)
        self.output_box.pack(expand=True, fill="both")

    # ===================================================================
    # USERNAME SEARCH
    # ===================================================================
    def start_user_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self.search_by_user, daemon=True).start()

    def search_by_user(self):
        username = self.user_entry.get().strip()
        limit = int(self.limit_var_user.get())

        try:
            tickets, duration = self.ticket_service.get_tickets_for_user(
                username, limit=limit
            )
            self.root.after(0, lambda: self.duration_label.config(
                text=f"Query time: {duration} ms"
            ))
        except Exception as e:
            self.root.after(0, lambda err=e: self.output_box.insert(
                tk.END, f"Error: {err}\n"
            ))
            self.root.after(0, self.progress.stop)
            return

        self.root.after(0, lambda: self.render_results(tickets, f"Tickets for '{username}'"))

    # ===================================================================
    # STATUS + BOARD SEARCH
    # ===================================================================
    def start_status_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self.search_by_status, daemon=True).start()

    def search_by_status(self):
        board = self.board_entry.get().strip() or None
        status = self.status_entry.get().strip() or None
        limit = int(self.limit_var_status.get())

        try:
            tickets, duration = self.status_service.get_tickets_by_status(
                board_name=board,
                status_name=status,
                limit=limit
            )
            self.root.after(0, lambda: self.duration_label.config(
                text=f"Query time: {duration} ms"
            ))
        except Exception as e:
            self.root.after(0, lambda err=e: self.output_box.insert(
                tk.END, f"Error: {err}\n"
            ))
            self.root.after(0, self.progress.stop)
            return

        label = f"Tickets (Board={board}, Status={status})"
        self.root.after(0, lambda: self.render_results(tickets, label))

    # ===================================================================
    # SHARED RESULT RENDERING
    # ===================================================================
    def render_results(self, tickets, label):
        self.progress.stop()

        self.output_box.insert(tk.END, f"{label}:\n\n")

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

            # Replace YOUR_URL with your ConnectWise site
            ticket_link = f"https://<YOUR_URL>/ConnectWise.aspx?routeTo=Ticket/{tid}"

            self.output_box.insert(
                tk.END,
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Ticket #{tid}\n"
                f"Summary      : {summary}\n"
                f"Owner        : {owner}\n"
                f"Status       : {status}\n"
                f"Board        : {board}\n"
                f"Team         : {team}\n"
                f"Last Updated : {updated}\n"
                f"Link         : {ticket_link}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )