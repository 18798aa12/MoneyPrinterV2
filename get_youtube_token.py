"""
Get YouTube OAuth2 refresh token for YouTube Data API uploads.

Usage:
  1. Create OAuth2 Desktop App credentials at https://console.cloud.google.com/apis/credentials
  2. Download the client_secret JSON file
  3. Run: python get_youtube_token.py /path/to/client_secret.json
  4. Copy the refresh_token to config.json
"""
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if len(sys.argv) < 2:
    print("Usage: python get_youtube_token.py <path_to_client_secret.json>")
    sys.exit(1)

CLIENT_SECRET_FILE = sys.argv[1]

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
credentials = flow.run_local_server(port=8080)

print("\n=== Copy these to config.json ===")
print(f"refresh_token: {credentials.refresh_token}")
print("=================================")
