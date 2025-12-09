import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
import re
import pytz
import time
import json
import os
from dotenv import load_dotenv
from colorama import Fore, Style



load_dotenv()

# configurations
username = os.getenv("CONNECTWISE_USERNAME")
password = os.getenv("CONNECTWISE_PASSWORD")


def get_tickets():

    data = []
    headers = {
        "clientId": "7e24f143-6e6e-4ae8-a26f-ebc90ca077c7"
    }

    url = (
        f"https://api-na.myconnectwise.net/v4_6_release/apis/3.0/service/tickets/{6133471}"
    )

    try:
        response = requests.get(url, headers=headers, auth=HTTPBasicAuth(username, password), timeout=1000)
        if response.status_code == 200:
            items = response.json()
            print(json.dumps(items, indent=4))

    except Exception as e:
        print(f"Failed to fetch MNS activation tickets, Script will restart..")
        return data




get_tickets()