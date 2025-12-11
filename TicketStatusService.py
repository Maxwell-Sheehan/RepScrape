# TicketStatusService.py

from timer import Timer

class TicketStatusService:
    """Business logic for filtering tickets by board + status."""

    def __init__(self, api_client):
        self.api = api_client

    def get_tickets_by_status(self, board_name=None, status_name=None, limit=20):
        """
        Returns tickets filtered by board and/or status.

        Args:
            board_name (str): e.g. "Service Desk"
            status_name (str): e.g. "New", "In Progress"
            limit (int): number of tickets to return (default 20)

        Returns:
            (tickets, elapsed_ms)
        """

        # Build CW conditions string
        conditions_list = []

        if board_name:
            conditions_list.append(f'board/name="{board_name}"')

        if status_name:
            conditions_list.append(f'status/name="{status_name}"')

        # Combine conditions with AND
        conditions = " AND ".join(conditions_list) if conditions_list else None

        with Timer() as t:
            tickets = self.api.get_tickets(conditions=conditions)

        return tickets[:limit], t.ms()
