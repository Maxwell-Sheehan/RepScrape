import json
from timer import Timer

class TicketService:
    """Business logic for filtering and working with tickets."""

    def __init__(self, api_client):
        self.api = api_client

    def get_tickets_for_user(self, username):
        """
        Returns tickets where owner.identifier matches the username
        (case-insensitive, whitespace trimmed).
        """
        username = username.strip()

        # ConnectWise 'contains' handles partial matches & case insensitivity
        conditions = f"owner/identifier contains \"{username}\""

        # ---- ADDED TIMER (minimal change) ----
        with Timer() as t:
            tickets = self.api.get_tickets(conditions=conditions)
        # --------------------------------------

        # Return newest 10 + timing
        return tickets[:10], t.ms()
