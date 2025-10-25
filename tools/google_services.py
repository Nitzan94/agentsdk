# ABOUTME: Google Drive and Calendar integration tools
# ABOUTME: List files, upload/download from Drive, manage Calendar events

from claude_agent_sdk import tool
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime, timedelta, UTC
import os

try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GoogleTools:
    def __init__(self, token_path: str = "storage/google_token.json"):
        self.token_path = token_path
        self.scopes = [
            'https://www.googleapis.com/auth/drive',  # Full Drive access (read/write/delete)
            'https://www.googleapis.com/auth/calendar',  # Full Calendar access
            'https://www.googleapis.com/auth/gmail.modify'  # Read/send/modify Gmail
        ]
        self.creds = None

    def _get_credentials(self) -> Optional[Credentials]:
        """Load and refresh credentials if needed"""
        if not GOOGLE_AVAILABLE:
            return None

        token_file = Path(self.token_path)
        if not token_file.exists():
            return None

        try:
            self.creds = Credentials.from_authorized_user_file(str(token_file), self.scopes)

            # Refresh if expired
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                # Save refreshed token
                token_file.write_text(self.creds.to_json())

            return self.creds
        except Exception as e:
            print(f"[WARN] Failed to load Google credentials: {e}")
            return None

    def get_tools(self):
        """Return list of Google service tools"""
        return [
            # Drive tools
            self._list_drive_files_tool(),
            self._upload_to_drive_tool(),
            self._download_from_drive_tool(),
            # Calendar tools
            self._list_calendar_events_tool(),
            self._create_calendar_event_tool(),
            # Gmail tools
            self._list_gmail_messages_tool(),
            self._send_gmail_tool(),
            self._read_gmail_tool()
        ]

    def _list_drive_files_tool(self):
        @tool(
            "list_drive_files",
            "List files from Google Drive. Can filter by name, type, or folder.",
            {
                "query": str,  # Search query (e.g., "name contains 'report'")
                "max_results": int  # Max files to return (default 10)
            }
        )
        async def list_drive_files(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available\nRun: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google\nRun: python setup_google_oauth.py"
                    }]
                }

            try:
                service = build('drive', 'v3', credentials=creds)
                query = args.get("query", "")
                max_results = args.get("max_results", 10)

                results = service.files().list(
                    q=query,
                    pageSize=max_results,
                    fields="files(id, name, mimeType, createdTime, size, webViewLink)"
                ).execute()

                files = results.get('files', [])

                if not files:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[INFO] No files found matching: {query or 'all files'}"
                        }]
                    }

                output = f"[OK] Found {len(files)} file(s):\n\n"
                for f in files:
                    size = int(f.get('size', 0)) if f.get('size') else 0
                    size_mb = size / (1024 * 1024) if size > 0 else 0
                    output += f"**{f['name']}**\n"
                    output += f"  Type: {f['mimeType']}\n"
                    output += f"  ID: {f['id']}\n"
                    if size_mb > 0:
                        output += f"  Size: {size_mb:.2f} MB\n"
                    output += f"  Created: {f.get('createdTime', 'Unknown')}\n"
                    output += f"  Link: {f.get('webViewLink', 'N/A')}\n\n"

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Drive API failed: {str(e)}"
                    }],
                    "isError": True
                }

        return list_drive_files

    def _upload_to_drive_tool(self):
        @tool(
            "upload_to_drive",
            "Upload a local file to Google Drive.",
            {
                "file_path": str,  # Local file path
                "drive_folder_id": str  # Optional Drive folder ID
            }
        )
        async def upload_to_drive(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google\nRun: python setup_google_oauth.py"
                    }]
                }

            file_path = Path(args["file_path"])
            if not file_path.exists():
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] File not found: {file_path}"
                    }]
                }

            try:
                service = build('drive', 'v3', credentials=creds)

                file_metadata = {'name': file_path.name}
                folder_id = args.get("drive_folder_id")
                if folder_id:
                    file_metadata['parents'] = [folder_id]

                media = MediaFileUpload(str(file_path), resumable=True)
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name, webViewLink'
                ).execute()

                return {
                    "content": [{
                        "type": "text",
                        "text": f"[OK] Uploaded to Google Drive\n"
                               f"File: {file['name']}\n"
                               f"ID: {file['id']}\n"
                               f"Link: {file.get('webViewLink', 'N/A')}"
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Upload failed: {str(e)}"
                    }],
                    "isError": True
                }

        return upload_to_drive

    def _download_from_drive_tool(self):
        @tool(
            "download_from_drive",
            "Download a file from Google Drive by file ID.",
            {
                "file_id": str,  # Google Drive file ID
                "save_path": str  # Local path to save file
            }
        )
        async def download_from_drive(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google"
                    }]
                }

            try:
                service = build('drive', 'v3', credentials=creds)
                file_id = args["file_id"]
                save_path = Path(args["save_path"])

                # Get file metadata
                file_metadata = service.files().get(fileId=file_id, fields='name').execute()

                # Download file
                request = service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while not done:
                    status, done = downloader.next_chunk()

                # Save to disk
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(fh.getvalue())

                file_size = save_path.stat().st_size / (1024 * 1024)

                return {
                    "content": [{
                        "type": "text",
                        "text": f"[OK] Downloaded from Google Drive\n"
                               f"File: {file_metadata['name']}\n"
                               f"Saved to: {save_path}\n"
                               f"Size: {file_size:.2f} MB"
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Download failed: {str(e)}"
                    }],
                    "isError": True
                }

        return download_from_drive

    def _list_calendar_events_tool(self):
        @tool(
            "list_calendar_events",
            "List upcoming events from Google Calendar.",
            {
                "max_results": int,  # Max events to return (default 10)
                "days_ahead": int    # Days to look ahead (default 7)
            }
        )
        async def list_calendar_events(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google"
                    }]
                }

            try:
                service = build('calendar', 'v3', credentials=creds)

                now = datetime.now(UTC).isoformat()
                days_ahead = args.get("days_ahead", 7)
                end_time = (datetime.now(UTC) + timedelta(days=days_ahead)).isoformat()
                max_results = args.get("max_results", 10)

                events_result = service.events().list(
                    calendarId='primary',
                    timeMin=now,
                    timeMax=end_time,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()

                events = events_result.get('items', [])

                if not events:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[INFO] No events in next {days_ahead} days"
                        }]
                    }

                output = f"[OK] Found {len(events)} upcoming event(s):\n\n"
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary = event.get('summary', 'No title')
                    location = event.get('location', 'No location')

                    output += f"**{summary}**\n"
                    output += f"  When: {start}\n"
                    output += f"  Where: {location}\n"
                    if event.get('description'):
                        desc = event['description'][:100]
                        output += f"  Description: {desc}...\n"
                    output += f"  Link: {event.get('htmlLink', 'N/A')}\n\n"

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Calendar API failed: {str(e)}"
                    }],
                    "isError": True
                }

        return list_calendar_events

    def _create_calendar_event_tool(self):
        @tool(
            "create_calendar_event",
            "Create a new event in Google Calendar.",
            {
                "summary": str,      # Event title
                "start_time": str,   # ISO format or human readable
                "end_time": str,     # ISO format or human readable
                "description": str,  # Optional description
                "location": str      # Optional location
            }
        )
        async def create_calendar_event(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google"
                    }]
                }

            try:
                service = build('calendar', 'v3', credentials=creds)

                event = {
                    'summary': args["summary"],
                    'start': {'dateTime': args["start_time"], 'timeZone': 'UTC'},
                    'end': {'dateTime': args["end_time"], 'timeZone': 'UTC'},
                }

                if args.get("description"):
                    event['description'] = args["description"]
                if args.get("location"):
                    event['location'] = args["location"]

                created_event = service.events().insert(
                    calendarId='primary',
                    body=event
                ).execute()

                return {
                    "content": [{
                        "type": "text",
                        "text": f"[OK] Calendar event created\n"
                               f"Title: {created_event['summary']}\n"
                               f"Start: {created_event['start']['dateTime']}\n"
                               f"Link: {created_event.get('htmlLink', 'N/A')}"
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Event creation failed: {str(e)}\n\n"
                               f"[TIP] Use ISO format for times: 2025-10-26T15:00:00Z"
                    }],
                    "isError": True
                }

        return create_calendar_event

    def _list_gmail_messages_tool(self):
        @tool(
            "list_gmail_messages",
            "List recent emails from Gmail. Can filter by sender, subject, or labels.",
            {
                "query": str,  # Search query (e.g., "from:someone@example.com", "subject:urgent")
                "max_results": int  # Max emails to return (default 10)
            }
        )
        async def list_gmail_messages(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google"
                    }]
                }

            try:
                service = build('gmail', 'v1', credentials=creds)
                query = args.get("query", "")
                max_results = args.get("max_results", 10)

                results = service.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=max_results
                ).execute()

                messages = results.get('messages', [])

                if not messages:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"[INFO] No emails found matching: {query or 'recent emails'}"
                        }]
                    }

                output = f"[OK] Found {len(messages)} email(s):\n\n"

                for msg in messages:
                    # Get message details
                    msg_data = service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']
                    ).execute()

                    headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}

                    output += f"**{headers.get('Subject', 'No Subject')}**\n"
                    output += f"  From: {headers.get('From', 'Unknown')}\n"
                    output += f"  Date: {headers.get('Date', 'Unknown')}\n"
                    output += f"  ID: {msg['id']}\n\n"

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Gmail API failed: {str(e)}"
                    }],
                    "isError": True
                }

        return list_gmail_messages

    def _read_gmail_tool(self):
        @tool(
            "read_gmail",
            "Read the full content of a Gmail message by ID.",
            {
                "message_id": str  # Gmail message ID (from list_gmail_messages)
            }
        )
        async def read_gmail(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google"
                    }]
                }

            try:
                service = build('gmail', 'v1', credentials=creds)
                message_id = args["message_id"]

                msg = service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()

                # Extract headers
                headers = {h['name']: h['value'] for h in msg['payload']['headers']}

                # Extract body
                body = ""
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            import base64
                            body = base64.urlsafe_b64decode(
                                part['body'].get('data', '')
                            ).decode('utf-8')
                            break
                elif 'body' in msg['payload']:
                    import base64
                    body = base64.urlsafe_b64decode(
                        msg['payload']['body'].get('data', '')
                    ).decode('utf-8')

                output = f"**{headers.get('Subject', 'No Subject')}**\n\n"
                output += f"From: {headers.get('From', 'Unknown')}\n"
                output += f"To: {headers.get('To', 'Unknown')}\n"
                output += f"Date: {headers.get('Date', 'Unknown')}\n\n"
                output += "---\n\n"
                output += body if body else "[No text content found]"

                return {
                    "content": [{
                        "type": "text",
                        "text": output
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to read email: {str(e)}"
                    }],
                    "isError": True
                }

        return read_gmail

    def _send_gmail_tool(self):
        @tool(
            "send_gmail",
            "Send an email via Gmail.",
            {
                "to": str,       # Recipient email
                "subject": str,  # Email subject
                "body": str,     # Email body (plain text)
                "cc": str        # Optional CC recipients
            }
        )
        async def send_gmail(args: Dict[str, Any]) -> Dict[str, Any]:
            if not GOOGLE_AVAILABLE:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Google API not available"
                    }]
                }

            creds = self._get_credentials()
            if not creds:
                return {
                    "content": [{
                        "type": "text",
                        "text": "[ERROR] Not authenticated with Google"
                    }]
                }

            try:
                from email.mime.text import MIMEText
                import base64

                service = build('gmail', 'v1', credentials=creds)

                # Create message
                message = MIMEText(args["body"])
                message['to'] = args["to"]
                message['subject'] = args["subject"]

                if args.get("cc"):
                    message['cc'] = args["cc"]

                # Encode message
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
                body = {'raw': raw}

                # Send
                sent = service.users().messages().send(
                    userId='me',
                    body=body
                ).execute()

                return {
                    "content": [{
                        "type": "text",
                        "text": f"[OK] Email sent successfully\n"
                               f"To: {args['to']}\n"
                               f"Subject: {args['subject']}\n"
                               f"Message ID: {sent['id']}"
                    }]
                }

            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"[ERROR] Failed to send email: {str(e)}"
                    }],
                    "isError": True
                }

        return send_gmail
