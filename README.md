# Personal Assistant Agent

CLI agent for note-taking, web research, reports with persistent memory.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set `ANTHROPIC_API_KEY` env var.

## Usage

```bash
python main.py
```

Resume previous session:
```bash
python main.py --resume
```

## Features

- **Persistent memory** across sessions
- **Note-taking** with tags and search
- **Web search** with DuckDuckGo (real search results!)
- **HTML parsing** with BeautifulSoup (clean content extraction)
- **Web research** with source tracking
- **Report generation** with citations
- **Data export/import** for backups
- **Suggestion tracking**
- **Document creation** (Excel, Word, PowerPoint, PDF)
- **Permission system** with terminal prompts for bash/python
- **Cost tracking** per session
