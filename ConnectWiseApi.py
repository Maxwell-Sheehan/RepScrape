import requests
import json
from log import log


class ConnectWiseAPIClient:

    def __init__(self, username, password, client_id, company="company", site="na"):
        self.base_url = f"https://api-{site}.myconnectwise.net/v4_6_release/apis/3.0"
        self.auth = (username, password)
        self.client_id = client_id
        self.company_identifier = company

        self.headers = {
            "clientId": self.client_id,
            "Content-Type": "application/json",
            "companyIdentifier": self.company_identifier
        }

    # ---------------------------------------
    # COMPANY LOOKUPS
    # ---------------------------------------
    def get_company(self, identifier):
        url = f"{self.base_url}/company/companies"
        params = {"conditions": f"identifier='{identifier}'"}

        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()

        results = response.json()
        if not results:
            raise ValueError(f"No company found for identifier {identifier}")

        obj = results[0]
        return {"id": obj["id"], "identifier": obj["identifier"], "name": obj["name"]}

    def get_company_site(self, company_id, site_name):
        url = f"{self.base_url}/company/companies/{company_id}/sites"
        params = {"conditions": f"name='{site_name}'"}

        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()

        results = response.json()
        if not results:
            raise ValueError(f"No site '{site_name}' found for company {company_id}")

        obj = results[0]
        return {"id": obj["id"], "name": obj["name"]}

    # ---------------------------------------
    # CREATE TICKET
    # ---------------------------------------
    def create_ticket(self, payload):
        url = f"{self.base_url}/service/tickets"
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # ---------------------------------------
    # GET BOARDS & STATUSES
    # ---------------------------------------
    def get_boards(self):
        url = f"{self.base_url}/service/boards"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_statuses(self, board_id):
        url = f"{self.base_url}/service/boards/{board_id}/statuses"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    # ---------------------------------------
    # DEBUG: FULL TICKET FETCH
    # ---------------------------------------
    def debug_get_full_ticket(self, ticket_id):
        url = f"{self.base_url}/service/tickets/{ticket_id}"
        params = {
            "expand": "owner,company,board,notes,contact,team,documents",
            "fields": (
                "id,summary,description,initialDescription,internalAnalysis,"
                "resolution,notes,status,board,company,owner,contact,team,documents"
            )
        }

        log("===== DEBUG FULL TICKET REQUEST =====")
        log(f"URL: {url}")
        log(f"PARAMS: {params}")

        r = requests.get(url, headers=self.headers, auth=self.auth, params=params)

        log(f"STATUS: {r.status_code}")

        try:
            log(json.dumps(r.json(), indent=2))
        except Exception:
            log(f"RAW RESPONSE: {r.text}")

        log("===== END DEBUG =====\n")

    # ---------------------------------------
    # TICKET SEARCH HELPERS
    # ---------------------------------------
    def get_tickets_by_company(self, company_identifier, extra_conditions=None,
                               page=1, page_size=25, order_by=None):

        company = self.get_company(company_identifier)
        company_id = company["id"]

        base_condition = f"company/id={company_id}"
        if extra_conditions:
            full_cond = f"{base_condition} AND ({extra_conditions})"
        else:
            full_cond = base_condition

        return self.get_tickets(
            conditions=full_cond,
            page=page,
            page_size=page_size,
            order_by=order_by
        )

    # ---------------------------------------
    # MAIN TICKET FETCHER
    # ---------------------------------------
    def get_tickets(self, conditions=None, page=1, page_size=25,
                    order_by=None, expand=None, fields=None,
                    full_response=False):

        url = f"{self.base_url}/service/tickets"

        params = {
            "page": page,
            "pageSize": page_size,
            "orderBy": order_by or "lastUpdated DESC",
            "expand": expand or "owner,company,board,notes",
            "fields": fields or (
                "id,summary,description,initialDescription,internalAnalysis,resolution,"
                "notes,owner/identifier,status/name,board/name,company/name,company/identifier"
            )
        }

        # If conditions is present, we must manually append it
        if conditions:
            query = requests.models.RequestEncodingMixin._encode_params(params)
            url = f"{url}?{query}&conditions={conditions}"
            response = requests.get(url, headers=self.headers, auth=self.auth)
        else:
            response = requests.get(url, headers=self.headers, auth=self.auth, params=params)

        response.raise_for_status()
        return response.json()
