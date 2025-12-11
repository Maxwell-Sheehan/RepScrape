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

        self.root.title("ConnectWise Ticket Viewer")
        self.root.configure(bg=DARK_BG)

        # Board → Status Mapping
        self.board_status_map = {
            "MNS Config":[
                "Pending Allocation",
                "Rejected",
                "Reject Resolved",
                "Assigned",
                "Unassigned",
                "New",
                "Ready to Configure",
                "Equipment configure",
                "Closed",
                "Cancelled"
            ],
                "MNS Activations":[
                "Cancelled",
                "Fail",
                "Open",
                "Partial Success",
                "Pending Coverage",
                "Rejected",
                "Scheduled",
                "Success"
                ]

            }



        # ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", background=ACCENT, foreground=DARK_TEXT)
        style.configure("TLabel", background=DARK_BG, foreground=DARK_TEXT)
        style.configure("TFrame", background=DARK_PANEL)
        style.configure("TCombobox", fieldbackground=DARK_PANEL, background=DARK_PANEL,
                        foreground=DARK_TEXT, relief="flat")

        # Layout
        self.sidebar = tk.Frame(root, bg=DARK_PANEL, width=320, padx=12, pady=12)
        self.sidebar.pack(side="left", fill="y")

        self.main = tk.Frame(root, bg=DARK_BG, padx=8, pady=8)
        self.main.pack(side="right", fill="both", expand=True)

        # --------------------------------------
        # Sidebar Widgets
        # --------------------------------------
        ttk.Label(self.sidebar, text="Unified Search", font=("Segoe UI", 12, "bold"))\
            .pack(anchor="w", pady=(0, 10))

        # Company
        ttk.Label(self.sidebar, text="Company").pack(anchor="w")
        self.company_entry = tk.Entry(self.sidebar, bg="#33373b", fg=DARK_TEXT, insertbackground=DARK_TEXT,
                                      font=("Segoe UI", 11))
        self.company_entry.pack(fill="x", pady=(0, 6))

        # Username
        ttk.Label(self.sidebar, text="Username").pack(anchor="w")
        self.user_entry = tk.Entry(self.sidebar, bg="#33373b", fg=DARK_TEXT, insertbackground=DARK_TEXT,
                                   font=("Segoe UI", 11))
        self.user_entry.pack(fill="x", pady=(0, 6))

        # Board
        ttk.Label(self.sidebar, text="Board").pack(anchor="w")
        self.board_var = tk.StringVar()
        self.board_entry = ttk.Combobox(self.sidebar, textvariable=self.board_var,
                                        values=["MNS Config", "MNS Activations"], state="readonly",
                                        font=("Segoe UI", 11))
        self.board_entry.pack(fill="x", pady=(0, 6))
        self.board_entry.bind("<<ComboboxSelected>>", self._update_status_dropdown)

        # Status
        ttk.Label(self.sidebar, text="Status").pack(anchor="w")
        self.status_var = tk.StringVar()
        self.status_entry = ttk.Combobox(self.sidebar, textvariable=self.status_var,
                                         values=[], state="readonly", font=("Segoe UI", 11))
        self.status_entry.pack(fill="x", pady=(0, 10))

        # Search button (NEW)
        self.search_button = ttk.Button(self.sidebar, text="Search", command=self.start_unified_search)
        self.search_button.pack(fill="x", pady=(10, 10))

        # Duration
        self.duration_label = ttk.Label(self.sidebar, text="")
        self.duration_label.pack(anchor="w", pady=(6, 0))

        # Main output
        self.progress = ProgressIndicator(self.main)
        self.output_box = tk.Text(self.main, bg="#111316", fg=DARK_TEXT,
                                  insertbackground=DARK_TEXT, wrap="word", padx=8, pady=8)
        self.output_box.pack(fill="both", expand=True)

    # -------- Update dropdown --------
    def _update_status_dropdown(self, event=None):
        board = self.board_var.get()
        statuses = self.board_status_map.get(board, [])
        self.status_entry["values"] = statuses
        self.status_var.set("")

    # -------- Unified Search --------
    def start_unified_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self._unified_search, daemon=True).start()

    def _unified_search(self):
        company = self.company_entry.get().strip()
        username = self.user_entry.get().strip()
        board = self.board_entry.get().strip()
        status = self.status_entry.get().strip()

        conditions = []
        if company:
            conditions.append(f'(company/name contains "{company}" OR company/identifier contains "{company}")')
        if username:
            conditions.append(f'owner/identifier contains "{username}"')
        if board:
            conditions.append(f'board/name="{board}"')
        if status:
            conditions.append(f'status/name="{status}"')

        full_conditions = " AND ".join(conditions) if conditions else None

        try:
            tickets = self.api_client.get_tickets(conditions=full_conditions, page=1, page_size=50)

            self.root.after(0, lambda: self.display_tickets(tickets, "Unified Search"))
            self.root.after(0, lambda: self.duration_label.config(text=f"Results: {len(tickets)} tickets"))
        except Exception as e:
            self.root.after(0, lambda: self.output_box.insert(tk.END, f"Error: {e}\n"))
        finally:
            self.root.after(0, self.progress.stop)

    # -------- Ticket Renderer --------
    def display_tickets(self, tickets, header_label):
        self.output_box.insert(tk.END, f"Results for {header_label}:\n\n")

        if not tickets:
            self.output_box.insert(tk.END, "No tickets found.\n")
            return

        for t in tickets:
            tid = t.get("id", "N/A")
            summary = t.get("summary", "")
            owner = t.get("owner", {}).get("identifier", "")
            company = t.get("company", {}).get("name", "")
            company_id = t.get("company", {}).get("identifier", "")
            status = t.get("status", {}).get("name", "")
            board = t.get("board", {}).get("name", "")
            team = t.get("team", {}).get("name", "")
            updated = t.get("lastUpdated", "")

            link = f"https://<YOUR_URL>/ConnectWise.aspx?routeTo=Ticket/{tid}"

            self.output_box.insert(
                tk.END,
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Ticket # {tid}\n"
                f"Summary      : {summary}\n"
                f"Owner        : {owner}\n"
                f"Company      : {company} ({company_id})\n"
                f"Status       : {status}\n"
                f"Board        : {board}\n"
                f"Team         : {team}\n"
                f"Last Updated : {updated}\n"
                f"Link         : {link}\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            )