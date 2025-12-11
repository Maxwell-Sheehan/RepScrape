import json
from timer import Timer

class TicketService:
    """Business logic for filtering and working with tickets."""

    def __init__(self, api_client):
        self.api = api_client

    def unified_search(self, company=None, username=None, board=None, status=None, limit=25):
        """
        Flexible unified search combining any filter selection.
        """

        conditions = []

        # Company → Convert to ID
        if company:
            try:
                comp = self.api.get_company(company)
                cid = comp["id"]
                conditions.append(f"company/id={cid}")
            except:
                raise ValueError(f"Company '{company}' not found")

        if username:
            conditions.append(f'owner/identifier contains "{username}"')

        if board:
            conditions.append(f'board/name="{board}"')

        if status:
            conditions.append(f'status/name="{status}"')

        condition_str = " AND ".join(conditions) if conditions else None

        with Timer() as t:
            tickets = self.api.get_tickets(
                conditions=condition_str,
                page=1,
                page_size=limit
            )

        return tickets[:limit], t.ms()


    def get_tickets_for_user(self, username, limit=10):
        """
        Returns tickets where owner.identifier matches the username
        and returns only the number specified by `limit`.
        """
        username = username.strip()

        # ConnectWise 'contains' handles partial matches & case insensitivity
        conditions = f'owner/identifier contains "{username}"'

        with Timer() as t:
            # pass page_size so API returns up to `limit`
            tickets = self.api.get_tickets(
                conditions=conditions,
                page_size=limit,
                page=1
            )

        return tickets[:limit], t.ms()
