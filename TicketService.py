import json

#remember import json

class TicketService:
    """Business logic for filtering and working with tickets."""

    def __init__(self, api_client):
        self.api = api_client

    def get_tickets_for_user(self, username):
        """
        Returns tickets where owner.identifier matches the username
        (case-insensitive, whitespace trimmed).
        """
        username = username.strip()  # remove extra whitespace

        # ConnectWise 'contains' handles partial matches & case insensitivity
        conditions = f"owner/identifier contains \"{username}\""

        # Pull tickets with server-side filtering (fast)
        tickets = self.api.get_tickets(conditions=conditions)

        # Return the newest 10
        return tickets[:10]
