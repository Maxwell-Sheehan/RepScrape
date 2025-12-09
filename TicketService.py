import json

class TicketService:

    """Simple ticket service: fetch tickets, filter by owner."""

    def __init__(self, api_client):
        self.api = api_client

    # Normalize strings
    @staticmethod
    def normalize(s):
        if not s:
            return ""
        return s.strip().lower()

    # Fetch the first page of tickets (no filtering, no expand, no fields)
    def get_all_tickets(self):
        return self.api.get_tickets()

    def filter_by_owner(self, tickets, username):
        username = self.normalize(username)
        filtered = []

        for t in tickets:
            # POSSIBLE OWNER FIELDS
            owner1 = t.get("owner", {}).get("identifier", "")
            owner2 = t.get("assignedMember", {}).get("identifier", "")
            owner3 = t.get("member", {}).get("identifier", "")
            owner4 = ""
            if "resources" in t and isinstance(t["resources"], list) and t["resources"]:
                owner4 = t["resources"][0].get("member", {}).get("identifier", "")

            owners = [
                self.normalize(owner1),
                self.normalize(owner2),
                self.normalize(owner3),
                self.normalize(owner4),
            ]

            if username in owners:
                filtered.append(t)

        return filtered

    # Main function the UI calls
    def search_tickets(self, owner=None):
        tickets = self.get_all_tickets()
        if owner:
            tickets = self.filter_by_owner(tickets, owner)
        return tickets
