# Personal Assistant Agent - Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install claude-agent-sdk httpx aiosqlite python-dateutil
```

Or use requirements file:
```bash
pip install -r requirements.txt
```

### 2. Set API Key

**Windows:**
```cmd
set ANTHROPIC_API_KEY=your_key_here
```

**Linux/Mac:**
```bash
export ANTHROPIC_API_KEY=your_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Run Assistant

**New session:**
```bash
python main.py
```

**Resume last session:**
```bash
python main.py --resume
```

## CLI Commands

While chatting with the assistant:

- `/help` - Show available commands
- `/stats` - Display session statistics (messages, cost)
- `/clear` - Clear screen
- `/exit` - Exit assistant
- `Ctrl+C` - Interrupt current response

## Agent Capabilities

### Note-Taking

**Create notes:**
```
You: Create a note about Python async best practices
```

Assistant will:
- Create markdown file in `storage/notes/`
- Save to database with searchable metadata
- Support tags for organization

**Search notes:**
```
You: Search notes about asyncio
You: Find notes tagged with "python"
```

**List recent notes:**
```
You: Show me my recent notes
```

### Web Research

**Fetch web content:**
```
You: Fetch content from https://docs.python.org/3/library/asyncio.html
```

**Analyze findings:**
```
You: Analyze my research on async programming and save it with sources
```

### Reports & Suggestions

**Generate reports:**
```
You: Create a report summarizing what we learned about async patterns
```

Report saved to `storage/reports/` with:
- Executive summary
- Sections with findings
- Recommendations

**Track suggestions:**
```
You: Add suggestion: Consider using async context managers
```

**Review suggestions:**
```
You: List my recent suggestions
```

## Memory & Sessions

### Session Persistence

All conversations stored in SQLite (`storage/agent.db`):
- Full message history
- Notes and research
- Suggestions and reports
- Cost tracking

### Resume Conversations

```bash
python main.py --resume
```

Agent remembers:
- Previous discussions
- Notes created
- Research completed
- Context from past sessions

### Session Statistics

Check costs and usage:
```
You: /stats
```

Shows:
- Session ID
- Start/end times
- Message count
- Total cost (USD)

## File Structure

```
personal-assistant/
├── storage/
│   ├── agent.db              # SQLite database
│   ├── notes/                # Markdown notes
│   │   └── 20250423_120000_topic.md
│   └── reports/              # Generated reports
│       └── report_20250423_topic.md
├── agent/
│   ├── client.py             # SDK wrapper
│   ├── memory.py             # Database manager
│   └── prompts.py            # System prompts
├── tools/
│   ├── notes.py              # Note tools
│   ├── research.py           # Research tools
│   └── reports.py            # Report tools
├── main.py                   # CLI entry point
└── test_setup.py             # Setup validation
```

## Example Workflows

### Research Workflow

```
You: Research best practices for Python async programming

[Assistant fetches sources, analyzes content]

You: Create a note summarizing the key points

[Assistant creates note with findings]

You: Generate a report with recommendations

[Assistant creates structured report]
```

### Note Organization

```
You: Create a note about meeting with team
    Title: Sprint Planning Meeting
    Tags: work, meetings, planning

[Note created]

You: Search notes tagged with "work"

[Assistant shows all work-related notes]
```

### Multi-Session Project

**Day 1:**
```bash
python main.py

You: Research machine learning frameworks for production
[Assistant researches and creates notes]

You: /exit
```

**Day 2:**
```bash
python main.py --resume

You: What did we find about ML frameworks yesterday?
[Assistant recalls previous research]

You: Let's dive deeper into deployment patterns
[Continues research]
```

## Troubleshooting

### Import Errors

```
[ERROR] Import failed: No module named 'claude_agent_sdk'
```

**Fix:** Install dependencies
```bash
pip install claude-agent-sdk httpx aiosqlite python-dateutil
```

### API Key Missing

```
[ERROR] ANTHROPIC_API_KEY not set
```

**Fix:** Set environment variable
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### Session Resume Fails

```
[INFO] No previous session found
```

**Fix:** This is normal for first run. Create new session first, then resume works.

### Database Locked

```
[ERROR] database is locked
```

**Fix:** Close other instances of the agent or delete `storage/agent.db` (loses history)

## Advanced Usage

### Custom Storage Location

Edit `agent/memory.py`:
```python
memory = MemoryManager(db_path="/path/to/custom/agent.db")
```

### Custom System Prompt

Edit `agent/prompts.py` to modify agent personality and behavior.

### Add New Tools

Create new tool in `tools/` directory:

```python
from claude_agent_sdk import tool

@tool("my_tool", "Description", {"param": str})
async def my_tool(args):
    return {"content": [{"type": "text", "text": "result"}]}
```

Register in `agent/client.py`:
```python
all_tools.append(my_tool)
```

Add to `allowed_tools` list.

## Cost Management

Track spending per session with `/stats` command.

Typical costs (approximate):
- Simple note: $0.001-0.005
- Web research: $0.01-0.05
- Report generation: $0.02-0.10

Use Haiku model for lower costs (requires SDK config change).

## Tips

1. **Be specific** - "Create note about X with tags Y, Z"
2. **Use tags** - Organize notes with consistent tags
3. **Resume sessions** - Build on previous work
4. **Check stats** - Monitor costs regularly
5. **Review notes** - Search before creating duplicates
6. **Interrupt freely** - Ctrl+C stops long responses
7. **Ask for reports** - Consolidate findings periodically

## Next Steps

- Configure additional MCP servers
- Integrate real search APIs (Google, Bing)
- Add custom tools for your workflow
- Set up automated backups of `storage/`
- Create templates for common reports
