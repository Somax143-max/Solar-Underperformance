import hashlib
import os
import sys
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

app_id = os.getenv("DEYE_APP_ID", "").strip()
app_secret = os.getenv("DEYE_APP_SECRET", "").strip()
email = os.getenv("DEYE_EMAIL", "").strip()
password = os.getenv("DEYE_PASSWORD", "")
token_url = os.getenv("DEYE_TOKEN_URL", "").strip()

required = {
    "DEYE_APP_ID": app_id,
    "DEYE_APP_SECRET": app_secret,
    "DEYE_EMAIL": email,
    "DEYE_PASSWORD": password,
    "DEYE_TOKEN_URL": token_url,
}

missing = [name for name, value in required.items() if not value]
if missing:
    print("Missing .env settings:", ", ".join(missing))
    sys.exit(1)

parsed = urlparse(token_url)
if parsed.scheme != "https" or not parsed.netloc:
    print("DEYE_TOKEN_URL must be a valid HTTPS URL from DeyeCloud docs.")
    sys.exit(1)

# Never print credentials, request bodies, or the returned token.
hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

payload = {
    "appSecret": app_secret,
    "email": email,
    "password": hashed_password,
}

try:
    response = requests.post(
        token_url,
        params={"appId": app_id},
        json=payload,
        timeout=20,
    )

    print("HTTP status:", response.status_code)

    try:
        result = response.json()
    except ValueError:
        print("Response was not JSON. Check the endpoint and API region.")
        sys.exit(1)

    if response.ok and result.get("success") is True:
        token_present = bool(
            result.get("accessToken") or result.get("access_token")
        )
        print("DeyeCloud authentication: SUCCESS")
        print("Access token returned:", "yes" if token_present else "not detected")
        print("Token value: deliberately hidden")
    else:
        print("DeyeCloud authentication: NOT CONFIRMED")
        print("API code:", result.get("code", "not provided"))
        print("API message:", result.get("msg", "not provided"))
        print("Check the documented endpoint, region, and credential format.")

except requests.Timeout:
    print("Request timed out. Check your connection and API endpoint.")
    sys.exit(1)
except requests.RequestException:
    print("Request failed. Check connectivity and the documented HTTPS endpoint.")
    sys.exit(1)