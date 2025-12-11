import requests
import json
import inspect

class ConnectWiseAPIClient:

    def __init__(self, username, password, client_id, company="company", site="na"):
        import  inspect
        print(">>> USING ConnectWiseApi FROM:", inspect.getfile(self.__class__))
        self.base_url = f"https://api-{site}.myconnectwise.net/v4_6_release/apis/3.0"
        self.auth = (username, password)
        self.client_id = client_id
        self.company_identifier = company

        self.headers = {
            "clientId": self.client_id,
            "Content-Type": "application/json",
            "companyIdentifier": self.company_identifier
        }

    # --------------------------
    # GET COMPANY BY IDENTIFIER
    # --------------------------
    def get_company(self, identifier):
        url = f"{self.base_url}/company/companies"
        params = {"conditions": f"identifier='{identifier}'"}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        results = response.json()
        if not results:
            raise ValueError(f"No company found for identifier {identifier}")
        company_obj = results[0]
        return {
            "id": company_obj["id"],
            "identifier": company_obj["identifier"],
            "name": company_obj["name"]
        }

    # --------------------------
    # GET SITE BY NAME
    # --------------------------
    def get_company_site(self, company_id, site_name):
        url = f"{self.base_url}/company/companies/{company_id}/sites"
        params = {"conditions": f"name='{site_name}'"}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        results = response.json()
        if not results:
            raise ValueError(f"No site '{site_name}' found for company {company_id}")
        site_obj = results[0]
        return {
            "id": site_obj["id"],
            "name": site_obj["name"]
        }

    # --------------------------
    # CREATE TICKET
    # --------------------------
    def create_ticket(self, payload):
        url = f"{self.base_url}/service/tickets"
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # --------------------------
    # GET BOARDS
    # --------------------------
    def get_boards(self):
        """
        Returns a list of boards. Each entry is the raw JSON object returned by CW.
        """
        url = f"{self.base_url}/service/boards"
        # You can add ordering or filtering as needed, e.g. params={"orderBy": "name"}
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    # --------------------------
    # GET TICKETS BY COMPANY
    # --------------------------
    def get_tickets_by_company(self, company_identifier, extra_conditions=None,
                               page=1, page_size=25, order_by=None):
        """
        Search tickets that belong to a specific company.
        extra_conditions can be something like:
            "status/name='New'" OR "owner/identifier='max'"
        """

        # 1) Look up company → get ID
        company = self.get_company(company_identifier)
        company_id = company["id"]

        # 2) Build the CW condition string
        base_condition = f"company/id={company_id}"

        if extra_conditions:
            # Combine using AND
            condition_string = f"{base_condition} AND ({extra_conditions})"
        else:
            condition_string = base_condition

        # 3) Reuse your existing ticket call
        return self.get_tickets(
            conditions=condition_string,
            page=page,
            page_size=page_size,
            order_by=order_by
        )


    # --------------------------
    # GET STATUSES FOR A BOARD
    # --------------------------
    def get_statuses(self, board_id):
        """
        Given a board id, return its statuses.
        """
        url = f"{self.base_url}/service/boards/{board_id}/statuses"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    # --------------------------
    # GET TICKETS
    # --------------------------
    def get_tickets(self, conditions=None, page=1, page_size=25,
                    order_by=None, expand=None, fields=None):

        url = f"{self.base_url}/service/tickets"

        # Everything except conditions can be safely encoded
        params = {
            "page": page,
            "pageSize": page_size,
            "orderBy": "lastUpdated DESC" if not order_by else order_by,
            "expand": (
                "owner,board,team,assignedMember,member,resources,company"
            ) if not expand else expand,  # ← ★ minimal required change
            "fields": (
                "id,"
                "summary,"
                "owner/identifier,"
                "status/name,"
                "board/name,"
                "team/name,"
                "company/name,"
                "company/identifier,"
                "lastUpdated"
            ) if not fields else fields
        }

        # Use explicit overrides if provided above
        if order_by:
            params["orderBy"] = order_by
        if expand:
            params["expand"] = expand
        if fields:
            params["fields"] = fields

        # Build the URL manually to avoid encoding conditions
        if conditions:
            query = requests.models.RequestEncodingMixin._encode_params(params)
            url = f"{url}?{query}&conditions={conditions}"
            response = requests.get(url, headers=self.headers, auth=self.auth)
        else:
            response = requests.get(url, headers=self.headers, auth=self.auth, params=params)

        response.raise_for_status()
        return response.json()
