import tkinter as tk
from tkinter import ttk
from threading import Thread
import json

from Styles import DARK_BG, DARK_PANEL, DARK_TEXT, ACCENT, apply_styles, create_page_size_dropdown
from TicketService import TicketService
from TicketStatusService import TicketStatusService
from ProgressIndicator import ProgressIndicator
from log import log
from orderby import OrderBy



class AppSidebarDark:
    def __init__(self, root, api_client):
        self.root = root
        self.api_client = api_client

        # Theme
        apply_styles()
        self.root.title("ConnectWise Ticket Viewer")
        self.root.configure(bg=DARK_BG)

        # Services
        self.ticket_service = TicketService(api_client)
        self.status_service = TicketStatusService(api_client)

        # Board → Status mapping
        self.board_status_map = {
            "MNS Config": [
                "Pending Allocation", "Rejected", "Reject Resolved", "Assigned",
                "Unassigned", "New", "Ready to Configure", "Equipment configure",
                "Closed", "Cancelled"
            ],
            "MNS Activations": [
                "Cancelled", "Fail", "Open", "Partial Success", "Pending Coverage",
                "Rejected", "Scheduled", "Success"
            ]
        }

        # Layout
        self.sidebar = tk.Frame(root, bg=DARK_PANEL, width=320, padx=12, pady=12)
        self.sidebar.pack(side="left", fill="y")

        self.main = tk.Frame(root, bg=DARK_BG, padx=8, pady=8)
        self.main.pack(side="right", fill="both", expand=True)

        # Page Size
        label, box, var = create_page_size_dropdown(self.sidebar)
        label.pack(anchor="w")
        box.pack(fill="x", pady=(0, 10))
        self.page_size_var = var

        # UI — Unified Search
        ttk.Label(self.sidebar, text="Unified Search", font=("Segoe UI", 12, "bold"))\
            .pack(anchor="w", pady=(0, 10))

        # Company
        ttk.Label(self.sidebar, text="Company").pack(anchor="w")
        self.company_entry = tk.Entry(
            self.sidebar, bg="#33373b", fg=DARK_TEXT,
            insertbackground=DARK_TEXT, font=("Segoe UI", 11)
        )
        self.company_entry.pack(fill="x", pady=(0, 6))

        # Username
        ttk.Label(self.sidebar, text="Username").pack(anchor="w")
        self.user_entry = tk.Entry(
            self.sidebar, bg="#33373b", fg=DARK_TEXT,
            insertbackground=DARK_TEXT, font=("Segoe UI", 11)
        )
        self.user_entry.pack(fill="x", pady=(0, 6))

        # Board
        ttk.Label(self.sidebar, text="Board").pack(anchor="w")
        self.board_var = tk.StringVar()
        self.board_entry = ttk.Combobox(
            self.sidebar, textvariable=self.board_var,
            values=list(self.board_status_map.keys()),
            state="readonly", font=("Segoe UI", 11)
        )
        self.board_entry.pack(fill="x", pady=(0, 6))
        self.board_entry.bind("<<ComboboxSelected>>", self._update_status_dropdown)

        # Status
        ttk.Label(self.sidebar, text="Status").pack(anchor="w")
        self.status_var = tk.StringVar()
        self.status_entry = ttk.Combobox(
            self.sidebar, textvariable=self.status_var,
            values=[], state="readonly", font=("Segoe UI", 11)
        )
        self.status_entry.pack(fill="x", pady=(0, 10))

        # Order By
        ttk.Label(self.sidebar, text="Order").pack(anchor="w")

        self.order_var = tk.StringVar(value="Newest First")

        self.order_entry = ttk.Combobox(
            self.sidebar,
            textvariable=self.order_var,
            values=["Newest First", "Oldest First"],
            state="readonly",
            font=("Segoe UI", 11)
        )
        self.order_entry.pack(fill="x", pady=(0, 10))

        # Search button
        self.search_button = ttk.Button(self.sidebar, text="Search", command=self.start_unified_search)
        self.search_button.pack(fill="x", pady=(10, 10))

        # Progress bar (just instantiate)
        self.progress = ProgressIndicator(self.sidebar)

        # Duration label
        self.duration_label = ttk.Label(self.sidebar, text="")
        self.duration_label.pack(anchor="w", pady=(6, 0))

        # --- Scrollable Text Output ---
        output_frame = tk.Frame(self.main, bg=DARK_BG)
        output_frame.pack(fill="both", expand=True)

        # Scrollbar (thicker)
        scrollbar = tk.Scrollbar(output_frame, width=18)  # try 12,16,18,20,24
        scrollbar.pack(side="right", fill="y")

        self.output_box = tk.Text(
            output_frame,
            bg="#111316",
            fg=DARK_TEXT,
            insertbackground=DARK_TEXT,
            wrap="word",
            padx=8,
            pady=8,
            yscrollcommand=scrollbar.set
        )
        self.output_box.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.output_box.yview)

    # ----------------------------------------------------
    # Status dropdown updater
    # ----------------------------------------------------
    def _update_status_dropdown(self, event=None):
        board = self.board_var.get()
        statuses = self.board_status_map.get(board, [])
        self.status_entry["values"] = statuses
        self.status_var.set("")

    # ----------------------------------------------------
    # Unified Search
    # ----------------------------------------------------
    def start_unified_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self._unified_search, daemon=True).start()

    def _unified_search(self):
        full_conditions = self.build_conditions()

        log(f"Unified search conditions = {full_conditions}")

        try:
            tickets = self.api_client.get_tickets(
                conditions=full_conditions,
                page=1,
                page_size=50,
                order_by=self.get_order_by(),
                full_response=True
            )

            log(f"Received {len(tickets)} tickets")

            # TEMP DEBUG
            if tickets:
                first_id = tickets[0]["id"]
                self.api_client.debug_get_full_ticket(first_id)

            self.root.after(0, lambda: self.display_tickets(tickets, "Unified Search"))
            self.root.after(
                0,
                lambda: self.duration_label.config(text=f"Results: {len(tickets)} tickets")
            )

        except Exception as e:
            self.root.after(
                0,
                lambda e=e: self.output_box.insert(tk.END, f"Error: {e}\n")
            )

        finally:
            self.root.after(0, self.progress.stop)

    def build_conditions(self):
        conditions = []

        if company := self.company_entry.get().strip():
            conditions.append(
                f'(company/name contains "{company}" '
                f'OR company/identifier contains "{company}")'
            )

        if username := self.user_entry.get().strip():
            conditions.append(f'owner/identifier contains "{username}"')

        if board := self.board_entry.get().strip():
            conditions.append(f'board/name="{board}"')

        if status := self.status_entry.get().strip():
            conditions.append(f'status/name="{status}"')

        return " AND ".join(conditions) if conditions else None

    def extract_identifiers(self, text):
        identifiers = {}

        patterns = {
            "Equipment Ticket": r"EQUIPMENTTICKET:\s*(\d+)",
            "Mobility Ticket": r"MOBILITY TICKET:\s*(\d+)",
            "SIM ID": r"SIM\s*1\s*ID:\s*([0-9]+)",
            "TN": r"TN:\s*([0-9]+)",
            "IP Address": r"IP Address:\s*([\d\.]+)",
            "Subnet Mask": r"Subnet Mask:\s*([\d\.]+)",
            "Default Gateway": r"Default Gateway:\s*([\d\.]+)",
            "MAC Address": r"Mac:\s*([0-9A-Fa-f]+)",
        }

        import re
        for label, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                identifiers[label] = match.group(1)

        return identifiers

    def get_order_by(self):
        return (
            OrderBy.newest_first()
            if self.order_var.get() == "Newest First"
            else OrderBy.oldest_first()
        )

    # ----------------------------------------------------
    # Ticket Renderer
    # ----------------------------------------------------
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

            # ------------------------------------------------
            # Initial Description (fetched from notes)
            # ------------------------------------------------
            description = ""

            try:
                notes = self.api_client.get_ticket_notes(
                    tid,
                    detail=True,
                    internal=False,
                    resolution=False
                )

                for note in notes:
                    if note.get("detailDescriptionFlag"):
                        description = note.get("text", "").strip()
                        break

            except Exception as e:
                log(f"Failed to fetch notes for ticket {tid}: {e}")

            identifiers = self.extract_identifiers(description)

            self.output_box.insert(
                tk.END,
                "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Ticket # {tid}\n"
                f"Summary      : {summary}\n"
                f"Owner        : {owner}\n"
                f"Company      : {company} ({company_id})\n"
                f"Status       : {status}\n"
                f"Board        : {board}\n\n"
            )

            # ---- Identifiers (if present) ----
            if identifiers:
                self.output_box.insert(tk.END, "Identifiers:\n")
                for k, v in identifiers.items():
                    self.output_box.insert(tk.END, f"  {k}: {v}\n")
                self.output_box.insert(tk.END, "\n")

            # ---- Full description ----
            self.output_box.insert(tk.END, f"{description}\n\n")
