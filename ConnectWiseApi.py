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
            "companyIdentifier": self.company_identifier   # ✔ REQUIRED FIX
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
    # GET TICKETS
    # --------------------------
    def get_tickets(self, conditions=None, page=1, page_size=100,
                    order_by=None, expand=None, fields=None):
        url = f"{self.base_url}/service/tickets"

        params = {
            "page": page,
            "pageSize": page_size,
            "orderBy": "lastUpdated DESC",
            "expand": "owner,board,team,assignedMember,member,resources",
            "fields": (
                "id,"
                "summary,"
                "owner/identifier,"
                "assignedMember/identifier,"
                "member/identifier,"
                "resources/member/identifier,"
                "board/name,"
                "team/name,"
                "status/name"
            )
        }

        if conditions:
            params["conditions"] = conditions
        if order_by:
            params["orderBy"] = order_by
        if expand:
            params["expand"] = expand
        if fields:
            params["fields"] = fields

        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()

        return response.json()
