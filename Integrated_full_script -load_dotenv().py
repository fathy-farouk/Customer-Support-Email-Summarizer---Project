import os
import requests
from msal import PublicClientApplication
from openai import AzureOpenAI
from dotenv import load_dotenv

# === Load environment variables from .env file ===
load_dotenv()

# === Azure OpenAI Credentials from .env ===
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")

# === Microsoft Graph Auth Config from .env ===
CLIENT_ID = os.getenv("CLIENT_ID")
AUTHORITY = os.getenv("AUTHORITY") or "https://login.microsoftonline.com/consumers"
SCOPES = ["Mail.Read"]

# === Step 1: Authenticate with Microsoft Graph ===
app = PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)
flow = app.initiate_device_flow(scopes=SCOPES)
if "user_code" not in flow:
    raise ValueError("❌ Device code flow failed", flow)

print("🔐 Go to", flow["verification_uri"])
print("🔑 Enter code:", flow["user_code"])
print("⏳ Waiting for authentication...")
result = app.acquire_token_by_device_flow(flow)

if "access_token" not in result:
    raise Exception("❌ Authentication failed")

# === Step 2: Fetch Emails ===
headers = {
    "Authorization": f"Bearer {result['access_token']}",
    "Content-Type": "application/json"
}
url = "https://graph.microsoft.com/v1.0/me/messages?$top=5"

response = requests.get(url, headers=headers)
emails = response.json().get("value", [])

# === Step 3: Summarize with Azure OpenAI ===
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

print("\n📧 Summarized Emails\n" + "=" * 40)
for email in emails:
    subject = email.get("subject", "(No subject)")
    body = email.get("bodyPreview", "")
    
    prompt = f"Summarize this customer support email:\n\n{body}"
    
    ai_response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes customer emails."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = ai_response.choices[0].message.content.strip()
    print(f"\n🔹 Subject: {subject}\n📝 Summary: {summary}\n" + "-" * 40)
