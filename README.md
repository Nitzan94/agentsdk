# Personal Assistant Agent

CLI agent for web research, note-taking, and document creation with persistent memory across sessions.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` env var.

## Usage

**Rich terminal UI** (recommended):
```bash
python main_rich.py
```

**Simple CLI**:
```bash
python main.py
```

**Resume previous session**:
```bash
python main_rich.py --resume
```

See [CLI_GUIDE.md](CLI_GUIDE.md) for full CLI documentation.

## Features

### Memory & Sessions
- **Custom memory** - Agent remembers facts about your business, preferences, personal details across ALL sessions
- **Session history** - List, view, and search all past conversations
- **Session context** - Agent maintains conversation within same session
- **Cost tracking** - Track API costs per session

### Research
- **Web search** - DuckDuckGo integration (no API key needed)
- **HTML parsing** - Clean content extraction from web pages
- **Source tracking** - Research findings saved to database with citations

### Google Services
- **Google Drive** - List, upload, download files
- **Google Calendar** - View and create events
- **Gmail** - List, read, send emails

See [GOOGLE_SETUP.md](GOOGLE_SETUP.md) for Google OAuth setup.

### Document Creation
- **Excel** - Spreadsheets via xlsx skill
- **Word** - Documents via docx skill
- **PowerPoint** - Presentations via pptx skill
- **PDF** - PDF files via pdf skill
- **Markdown conversion** - Convert files to markdown via markitdown-skill

### File Management
- **Read/Write/Edit** - File operations
- **Bash** - Run commands with permission prompts
- **Project organization** - Automatic file organization by project
