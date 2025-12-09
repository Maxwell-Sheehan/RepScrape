import tkinter as tk
from tkinter import ttk
from threading import Thread
from TicketService import TicketService
from ProgressIndicator import ProgressIndicator
import json

#don't forget the libraries
class App:
    def __init__(self, root, api_client):
        self.root = root
        self.api_client = api_client
        self.ticket_service = TicketService(api_client)

        self.root.title("ConnectWise Ticket Viewer")

        tk.Label(root, text="Enter Username:").pack()
        self.user_entry = tk.Entry(root)
        self.user_entry.pack()

        tk.Button(root, text="Search", command=self.start_search).pack()

        self.duration_label = tk.Label(root, text="", fg="gray")
        self.duration_label.pack()

        # Use the separate progress indicator class
        self.progress = ProgressIndicator(root)

        self.output_box = tk.Text(root, width=120, height=25)
        self.output_box.pack(expand=True, fill="both")

    def start_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self.search_tickets, daemon=True).start()

    def search_tickets(self):
        username = self.user_entry.get().strip()

        try:
            tickets, duration_ms = self.ticket_service.get_tickets_for_user(username)
            self.duration_label.config(text=f"Query time: {duration_ms} ms")

        except Exception as e:
            # Capture "e" safely inside lambda
            self.root.after(0, lambda err=e: self.output_box.insert(tk.END, f"Error: {err}\n"))
            self.root.after(0, self.progress.stop)
            return

        # ------- INSIDE search_tickets --------
        def update_output():
            self.progress.stop()
            self.output_box.insert(tk.END, f"Tickets for '{username}':\n\n")

            if not tickets:
                self.output_box.insert(tk.END, "No tickets found.\n")
                return

            for t in tickets[:25]:
                tid = t.get("id", "N/A")
                summary = t.get("summary", "")
                owner = t.get("owner", {}).get("identifier", "")
                status = t.get("status", {}).get("name", "")
                board = t.get("board", {}).get("name", "")
                team = t.get("team", {}).get("name", "")
                updated = t.get("lastUpdated", "")

                # Replace YOUR_CONNECTWISE_URL
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

        self.root.after(0, update_output)
