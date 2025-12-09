import tkinter as tk
from tkinter import ttk
from threading import Thread
from TicketService import TicketService
from ProgressIndicator import ProgressIndicator
import json

# Main App
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

        # Use the separate progress indicator class
        self.progress = ProgressIndicator(root)

        self.output_box = tk.Text(root, width=80, height=20)
        self.output_box.pack()

    def start_search(self):
        self.output_box.delete("1.0", tk.END)
        self.progress.start()
        Thread(target=self.search_tickets, daemon=True).start()

    def search_tickets(self):
        username = self.user_entry.get().strip()

        try:
            tickets = self.ticket_service.search_tickets(owner=username)
        except Exception as e:
            self.root.after(0, lambda: self.output_box.insert(tk.END, f"Error: {e}\n"))
            self.root.after(0, self.progress.stop)
            return

        def update_output():
            self.progress.stop()
            self.output_box.insert(tk.END, f"Tickets for '{username}':\n\n")

            if not tickets:
                self.output_box.insert(tk.END, "No tickets found.\n")
                return

            for t in tickets[:10]:
                tid = t.get("id", "N/A")
                summary = t.get("summary", "")
                owner = t.get("owner", {}).get("identifier", "")
                self.output_box.insert(tk.END, f"#{tid} - {summary} (Owner: {owner})\n")

        self.root.after(0, update_output)
