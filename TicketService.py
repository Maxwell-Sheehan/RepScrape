import json
from timer import Timer

class TicketService:
    """Business logic for filtering and working with tickets."""

    def __init__(self, api_client):
        self.api = api_client

    def get_tickets_for_user(self, username, limit=10):
        """
        Returns tickets where owner.identifier matches the username.
        """
        username = username.strip()

        # ConnectWise 'contains' handles partial matches & case insensitivity
        conditions = f'owner/identifier contains "{username}"'

        with Timer() as t:
           #increase page limit for dropdown
            tickets = self.api.get_tickets(
                conditions=conditions,
                page_size=limit,
                page=1
            )

        # Return only requested amount + timing
        return tickets[:limit], t.ms()
