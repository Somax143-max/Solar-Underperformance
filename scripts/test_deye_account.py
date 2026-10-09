import os
import hashlib
import requests


def load_env(path=".env"):
    if not os.path.exists(path):
        raise FileNotFoundError(".env file not found in project root")

    with open(path, "r", encoding="utf-8-sig") as file:
        for raw_line in file:
            line = raw_line.strip()
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

    required = {
        "DEYE_APP_ID": app_id,
        "DEYE_APP_SECRET": app_secret,
        "DEYE_EMAIL": email,
        "DEYE_PASSWORD": password,
        "DEYE_TOKEN_URL": token_url,
    }
    missing = [key for key, value in required.items() if not value]
    if missing:
        print("Missing .env settings:", ", ".join(missing))
        return

    encrypted_password = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    print("Requesting DeyeCloud authentication...")
    auth_response = requests.post(
        token_url,
        params={"appId": app_id},
        json={
            "appSecret": app_secret,
            "email": email,
            "password": encrypted_password,
        },
        headers={"Content-Type": "application/json"},
        timeout=20,
    )
    print("Authentication HTTP status:", auth_response.status_code)
    auth_response.raise_for_status()

    auth_data = auth_response.json()
    token = auth_data.get("accessToken")

    if not auth_data.get("success") or not token:
        print("Authentication was not successful.")
        print("API code:", auth_data.get("code"))
        print("API message:", auth_data.get("msg"))
        return

    print("Authentication: SUCCESS (token hidden)")

    response = requests.post(
        "https://india-developer.deyecloud.com/v1.0/account/info",
        headers={
            "authorization": (token if token.strip().lower().startswith("bearer ") else f"Bearer {token}"),
            "Content-Type": "application/json",
        },
        timeout=20,
    )

    print("Account-info HTTP status:", response.status_code)
    response.raise_for_status()
    data = response.json()

    print("Account-info API success:", data.get("success"))
    print("API code:", data.get("code"))
    print("API message:", data.get("msg"))

    # Print only organization-related fields, not the full account response.
    allowed_names = {
        "companyId",
        "companyName",
        "organization",
        "orgName",
        "role",
        "memberType",
    }

    def inspect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in allowed_names:
                    print(f"{key}: {child}")
                elif isinstance(child, (dict, list)):
                    inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)

    inspect(data)

    print("Account-info check finished.")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        print("Request failed:", type(exc).__name__)
        print("Check the endpoint, network, and HTTP status.")
    except Exception as exc:
        print("Script error:", type(exc).__name__, str(exc))

