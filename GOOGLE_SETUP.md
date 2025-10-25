# Google Drive & Calendar Setup

Your agent now has Google Drive and Calendar tools! Follow these steps to enable them.

## Quick Setup (5 minutes)

### 1. Get Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. **Enable APIs:**
   - Click "Enable APIs and Services"
   - Search and enable: **Google Drive API**
   - Search and enable: **Google Calendar API**
   - Search and enable: **Gmail API**

4. **Create OAuth Credentials:**
   - Go to: Credentials > Create Credentials > OAuth client ID
   - Application type: **Desktop app**
   - Name it: "Personal Assistant"
   - Click Create
   - Download the JSON file

5. **Save credentials:**
   - Rename downloaded file to `credentials.json`
   - Place in project root: `personal-assistant/credentials.json`

### 2. Authenticate

Run the OAuth setup script:

```bash
python setup_google_oauth.py
```

This will:
- Open your browser for Google authorization
- Ask you to grant Drive and Calendar permissions
- Save token to `storage/google_token.json`

### 3. Done!

Your agent can now:
- List, upload, download files from Google Drive
- View and create calendar events
- Read, send, and search Gmail

## Available Tools

Ask your agent things like:

**Google Drive:**
- "List my recent files from Google Drive"
- "Upload the budget spreadsheet to my Drive"
- "Download the Q4 report from Drive (file ID: xyz)"
- "Show me all PDFs in my Drive"

**Google Calendar:**
- "What's on my calendar this week?"
- "Create a meeting for tomorrow at 2pm titled 'Team Sync'"
- "List my events for the next 3 days"

**Gmail:**
- "Show me my recent emails"
- "List emails from john@example.com"
- "Read the email with ID abc123"
- "Send an email to sarah@example.com about the project update"

## Troubleshooting

**"Not authenticated with Google"**
- Run: `python setup_google_oauth.py`

**"credentials.json not found"**
- Download from Google Cloud Console (see step 1)

**Token expired:**
- Tokens auto-refresh, but if issues persist, delete `storage/google_token.json` and re-run setup

## Security Notes

- `credentials.json` - OAuth client config (not secret, but keep private)
- `storage/google_token.json` - Your access token (KEEP SECRET!)
- Add to `.gitignore`:
  ```
  credentials.json
  storage/google_token.json
  ```

## Tool Details

### list_drive_files
```
query: Search filter (e.g., "name contains 'report'")
max_results: Number of files to return (default 10)
```

### upload_to_drive
```
file_path: Local file to upload
drive_folder_id: Optional Drive folder ID
```

### download_from_drive
```
file_id: Google Drive file ID
save_path: Where to save locally
```

### list_calendar_events
```
max_results: Number of events (default 10)
days_ahead: Days to look ahead (default 7)
```

### create_calendar_event
```
summary: Event title
start_time: ISO format (2025-10-26T15:00:00Z)
end_time: ISO format
description: Optional
location: Optional
```

### list_gmail_messages
```
query: Gmail search (e.g., "from:someone@example.com", "subject:urgent")
max_results: Number of emails (default 10)
```

### read_gmail
```
message_id: Gmail message ID (from list_gmail_messages)
```

### send_gmail
```
to: Recipient email
subject: Email subject
body: Email body (plain text)
cc: Optional CC recipients
```

## Permissions Granted

When you authenticate, you'll grant these permissions:
- **Drive**: Full read/write/delete access to your Google Drive
- **Calendar**: Full read/write/delete access to your Calendar
- **Gmail**: Read, send, and modify emails (cannot delete permanently)

Enjoy your Google-powered assistant!
