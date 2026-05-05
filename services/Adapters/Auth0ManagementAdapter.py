import requests
import json
import os
from dotenv import load_dotenv
import http.client
from typing import Any

load_dotenv()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_ROLE_USER = os.environ.get("AUTH0_ROLE_USER")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")
AUTH0_MANAGEMENT_API_AUDIENCE = os.environ.get("AUTH0_MANAGEMENT_API_AUDIENCE")


def updateUserPermissions(auth0Id: str, role: str = [AUTH0_ROLE_USER]):
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0Id}/roles"

    payload = json.dumps({"roles": [*role]})
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


def getUser(auth0Id: str) -> None:
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0Id}"
    accessToken = getManagementAPIAccessToken()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {accessToken}",
    }

    response = requests.request("GET", url, headers=headers)

    return response.payload


def getManagementAPIAccessToken() -> dict[str, Any]:
    conn = http.client.HTTPSConnection(AUTH0_DOMAIN)

    payload = json.dumps(
        {
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "audience": AUTH0_MANAGEMENT_API_AUDIENCE,
            "grant_type": "client_credentials",
        }
    )

    headers = {"content-type": "application/json"}

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()
    decoded_data = data.decode("utf-8")

    try:
        parsed_body = json.loads(decoded_data)
    except json.JSONDecodeError:
        parsed_body = {"raw_response": decoded_data}

    return parsed_body["access_token"]
