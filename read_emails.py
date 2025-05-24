import os
import requests
from msal import PublicClientApplication
from dotenv import load_dotenv

# === Load .env file ===
# load_dotenv()
# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")  # This can stay, even if not used

CLIENT_ID="ef5577dd-b581-43a1-bbb8-7e7a16a10895"
TENANT_ID="5419060b-50b8-486c-bc99-03492d268a6a"

AUTHORITY = "https://login.microsoftonline.com/consumers"
SCOPES = ["Mail.Read", "User.Read"]

# === Setup public app ===
app = PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)

# === Start device flow login ===
flow = app.initiate_device_flow(scopes=SCOPES)
if "user_code" not in flow:
    raise ValueError("❌ Device flow failed to initiate", flow)

print("🔑 Please authenticate now:")
print(flow["message"])  # Shows login URL and user code

# === Wait for user login ===
result = app.acquire_token_by_device_flow(flow)

# === Use token to access emails ===
if "access_token" in result:
    print("✅ Authenticated successfully")
    headers = {
        "Authorization": f"Bearer {result['access_token']}"
    }

    url ="https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$top=5&$select=subject,bodyPreview,from,receivedDateTime"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # emails = response.json().get("value", [])
        # print("\n📧 Recent Emails:\n" + "=" * 40)
        # for email in emails:
        #     print("Subject:", email.get("subject", "(No subject)"))
        #     print("From:", email["from"]["emailAddress"]["address"])
        #     print("Preview:", email.get("bodyPreview", "")[:100])
        #     print("-" * 40)

        print("📨 Raw email JSON from Microsoft Graph:\n")
        print(response.json())

    else:
        print(f"❌ Failed to fetch emails: {response.status_code} - {response.text}")
else:
    print("❌ Authentication failed:", result.get("error_description"))
