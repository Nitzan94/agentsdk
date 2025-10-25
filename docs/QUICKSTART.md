# Personal Assistant Agent - Quick Start

## 1-Minute Setup

```bash
# Install
pip install claude-agent-sdk httpx aiosqlite python-dateutil

# Set API key
export ANTHROPIC_API_KEY=your_key_here  # Mac/Linux
set ANTHROPIC_API_KEY=your_key_here     # Windows

# Run
python main.py
```

## First Conversation

```
You: Create a note about my project ideas
Assistant: [Creates note and saves as markdown]

You: Search notes about project
Assistant: [Shows matching notes]

You: /stats
[Shows session cost and message count]

You: /exit
```

## Resume Later

```bash
python main.py --resume
```

Picks up exactly where you left off - full memory intact.

## What You Can Do

**Notes:**
- "Create note about X with tags Y, Z"
- "Search notes about topic"
- "List recent notes"

**Research:**
- "Fetch content from URL"
- "Analyze my research on topic"

**Reports:**
- "Generate report summarizing our findings"
- "Add suggestion: try X approach"
- "List my suggestions"

**Commands:**
- `/stats` - Cost and message count
- `/help` - Show commands
- `/exit` - Quit
- `Ctrl+C` - Interrupt response

## File Locations

- **Notes:** `storage/notes/*.md`
- **Reports:** `storage/reports/*.md`
- **Database:** `storage/agent.db`
- **Memory:** All conversations stored

## Troubleshooting

**Missing dependencies:**
```bash
pip install -r requirements.txt
```

**API key error:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**Test setup:**
```bash
python test_setup.py
```

## Tips

1. Tag notes consistently
2. Use `/stats` to track costs
3. Resume sessions to build context
4. Interrupt anytime with Ctrl+C
5. Ask for reports to consolidate

## Full Documentation

- `USAGE.md` - Comprehensive guide
- `PROJECT_SUMMARY.md` - Technical overview
- `README.md` - Project intro

Get your API key: https://console.anthropic.com/
