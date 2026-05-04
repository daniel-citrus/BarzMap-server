import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_ROLE_USER = os.environ.get("AUTH0_ROLE_USER")


def updateUserPermissions(auth0Id: str, role: str = [AUTH0_ROLE_USER]):
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0Id}/roles"

    payload = json.dumps({"roles": [*role]})
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def getUser(auth0Id: str) -> None:
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0Id}"

    headers = {
        "Accept": "application/json",
        # TODO: Authorization: Bearer <management_api_access_token>
    }

    response = requests.request("GET", url, headers=headers)

    print(response.text)


def getManagementAPIAccessToken():
    pass
