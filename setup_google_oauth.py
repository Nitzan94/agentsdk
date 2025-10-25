# ABOUTME: Google OAuth setup script
# ABOUTME: Authenticate with Google and save credentials for Drive/Calendar access

from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
import json

SCOPES = [
    'https://www.googleapis.com/auth/drive',  # Full Drive access (read/write/delete)
    'https://www.googleapis.com/auth/calendar',  # Full Calendar access (read/write/delete)
    'https://www.googleapis.com/auth/gmail.modify'  # Gmail read/send/modify (not delete)
]

def setup_oauth():
    """
    Run OAuth flow to get Google credentials

    Requirements:
    1. Go to https://console.cloud.google.com
    2. Create a project
    3. Enable Google Drive API and Google Calendar API
    4. Create OAuth 2.0 credentials (Desktop app)
    5. Download credentials as 'credentials.json' and place in project root
    """

    credentials_file = Path('credentials.json')

    if not credentials_file.exists():
        print("[ERROR] credentials.json not found!")
        print()
        print("Setup steps:")
        print("1. Go to: https://console.cloud.google.com")
        print("2. Create a new project (or select existing)")
        print("3. Enable APIs:")
        print("   - Google Drive API")
        print("   - Google Calendar API")
        print("   - Gmail API")
        print("4. Create OAuth 2.0 credentials:")
        print("   - Credentials > Create Credentials > OAuth client ID")
        print("   - Application type: Desktop app")
        print("   - Download JSON")
        print("5. Save downloaded file as 'credentials.json' in this directory")
        print()
        return False

    print("[INFO] Starting OAuth flow...")
    print("[INFO] A browser window will open for authorization")

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file),
            SCOPES
        )

        # Run local server to receive OAuth callback
        creds = flow.run_local_server(port=0)

        # Save token for future use
        token_dir = Path('storage')
        token_dir.mkdir(exist_ok=True)
        token_path = token_dir / 'google_token.json'

        token_path.write_text(creds.to_json())

        print()
        print("[OK] Authentication successful!")
        print(f"[OK] Token saved to: {token_path}")
        print()
        print("You can now use Google Drive and Calendar tools in your agent.")
        print()
        print("Available tools:")
        print("  Drive: list_drive_files, upload_to_drive, download_from_drive")
        print("  Calendar: list_calendar_events, create_calendar_event")
        print("  Gmail: list_gmail_messages, read_gmail, send_gmail")
        print()

        return True

    except Exception as e:
        print(f"[ERROR] OAuth flow failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  Google OAuth Setup for Personal Assistant")
    print("=" * 60)
    print()

    success = setup_oauth()

    if not success:
        print()
        print("[INFO] Setup incomplete. Follow the steps above and try again.")
        exit(1)

    print("[INFO] Setup complete! Run: python main.py")
