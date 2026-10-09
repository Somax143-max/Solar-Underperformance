
import hashlib
import os
from pathlib import Path

import requests


def load_env():
    """Load project-root .env without printing any secret values."""
    env_path = Path(__file__).resolve().parent.parent / ".env"

    if not env_path.exists():
        raise RuntimeError(".env file not found in project root")

    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def main():
    load_env()

    app_id = os.getenv("DEYE_APP_ID")
    app_secret = os.getenv("DEYE_APP_SECRET")
    email = os.getenv("DEYE_EMAIL")
    password = os.getenv("DEYE_PASSWORD")
    token_url = os.getenv("DEYE_TOKEN_URL")

    if not all([app_id, app_secret, email, password, token_url]):
        raise RuntimeError("One or more required DeyeCloud settings are missing")

    base_url = "https://india-developer.deyecloud.com"

    # DeyeCloud requires the account password to be SHA-256 encrypted.
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # Authenticate without displaying the token.
    auth_response = requests.post(
        token_url,
        params={"appId": app_id},
        json={
            "appSecret": app_secret,
            "email": email,
            "password": password_hash,
        },
        timeout=20,
    )
    auth_response.raise_for_status()
    auth_data = auth_response.json()

    if not auth_data.get("success"):
        raise RuntimeError(
            f"Authentication rejected: "
            f"code={auth_data.get('code')}, msg={auth_data.get('msg')}"
        )

    token = auth_data.get("accessToken") or auth_data.get("access_token")
    if not token:
        raise RuntimeError("Authentication succeeded but no access token was returned")

    if not token.lower().startswith("bearer "):
        token = f"Bearer {token}"

    print("Authentication: SUCCESS")
    print("Access token: hidden")

    # Read station list; this endpoint does not control plant equipment.
    response = requests.post(
        f"{base_url}/v1.0/station/list",
        headers={
            "authorization": (token if token.strip().lower().startswith("bearer ") else f"Bearer {token}"),
            "Content-Type": "application/json",
        },
        json={"page": 1, "size": 20},
        timeout=20,
    )

    print("Station API HTTP status:", response.status_code)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError:
        raise RuntimeError("Station API returned a non-JSON response")

    if not data.get("success"):
        raise RuntimeError(
            f"Station query failed: "
            f"code={data.get('code')}, msg={data.get('msg')}"
        )

    print("Station API: SUCCESS")
    print("API message:", data.get("msg", "No message supplied"))

   
    # Safely inspect the station-list response structure.
    payload = data.get("stationList")

    print("Total stations reported by API:", data.get("total"))
    print("stationList response type:", type(payload).__name__)

    if isinstance(payload, list):
        print("Stations returned on this page:", len(payload))

        for index, station in enumerate(payload, start=1):
            if not isinstance(station, dict):
                print(f"{index}. Unexpected station record type")
                continue

            print(
                f"{index}. Name: {station.get('name', '(not supplied)')} | "
                f"ID: {station.get('id', station.get('stationId', '(not supplied)'))} | "
                f"Capacity: {station.get('installedCapacity', '(not supplied)')}"
            )

    elif isinstance(payload, dict):
        print("Station-list object fields:", ", ".join(payload.keys()))
        print("The station-list object needs further mapping.")

    elif payload is None:
        print("stationList is null or missing.")
        print("Check the API response structure locally.")

    else:
        print("Unexpected stationList format; no records displayed.")

if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        print("Network/API request failed:", type(exc).__name__)
        print("Check connectivity, API region, and endpoint configuration.")
    except Exception as exc:
        print("Test failed:", str(exc))
