import requests
import json
import os
from dotenv import load_dotenv
import http.client
from typing import Any, Optional

load_dotenv()

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
AUTH0_ROLE_USER = os.environ.get("AUTH0_ROLE_USER")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE")
AUTH0_MANAGEMENT_API_AUDIENCE = os.environ.get("AUTH0_MANAGEMENT_API_AUDIENCE")


def authorizationHeaders(accessToken: str) -> dict[str, str]:
    return {"Accept": "application/json", "Authorization": f"Bearer {accessToken}"}


def updateUserPermissions(
    auth0Id: str,
    roles: Optional[list[str]] = None,
) -> dict[str, Any]:
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0Id}/roles"
    accessToken = getManagementAPIAccessToken()
    resolved_roles = (
        roles if roles is not None else ([AUTH0_ROLE_USER] if AUTH0_ROLE_USER else [])
    )
    if not resolved_roles:
        return {
            "status_code": 400,
            "error": "No roles provided (expected Auth0 role IDs like `rol_...`).",
        }
    invalid_roles = [
        r for r in resolved_roles if not isinstance(r, str) or not r.startswith("rol_")
    ]
    if invalid_roles:
        return {
            "status_code": 400,
            "error": "Invalid role ids (Auth0 expects role IDs like `rol_...`).",
            "invalid_roles": invalid_roles,
        }

    payload = json.dumps({"roles": resolved_roles})
    headers = {**authorizationHeaders(accessToken), "Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload, timeout=30)

    if response.ok:
        return {
            "status_code": response.status_code,
            "body": (response.json() if response.content else None),
        }
    try:
        error_body: Any = response.json()
    except ValueError:
        error_body = response.text
    return {"status_code": response.status_code, "error": error_body}


def getUser(auth0Id: str) -> Optional[dict[str, Any]]:
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0Id}"
    accessToken = getManagementAPIAccessToken()
    headers = authorizationHeaders(accessToken)

    response = requests.request("GET", url, headers=headers, timeout=30)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def getUserRoles(auth0Id: str) -> Optional[list[dict[str, Any]]]:
    """
    GET /api/v2/users/:id/roles — returns a JSON array of role objects.
    Empty roles => [] (not null). Uses response.json() so you always get a Python list.
    """
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0Id}/roles"
    accessToken = getManagementAPIAccessToken()
    headers = authorizationHeaders(accessToken)

    response = requests.request("GET", url, headers=headers, timeout=30)
    if response.status_code == 404:
        return []
    response.raise_for_status()
    if not response.content or not response.content.strip():
        return []
    body = response.json()
    if body is None:
        return []
    if not isinstance(body, list):
        return [body] if isinstance(body, dict) else []
    return body


def getManagementAPIAccessToken() -> str:
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

    if "access_token" not in parsed_body:
        raise ValueError(f"Auth0 client_credentials failed: {parsed_body}")

    return parsed_body["access_token"]
