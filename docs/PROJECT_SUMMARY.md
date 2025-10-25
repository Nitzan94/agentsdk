# Personal Assistant Agent - Project Summary

## Overview

Full-featured CLI agent built with Claude Agent SDK for note-taking, web research, and report generation with persistent memory across sessions.

## Architecture

**Technology Stack:**
- Python 3.8+ with async/await
- Claude Agent SDK (official)
- SQLite for persistence
- Custom MCP tools
- Streaming CLI interface

**Core Components:**

1. **Memory System** (`agent/memory.py`)
   - SQLite database for sessions, messages, notes, research, suggestions
   - Session resume capability
   - Cost tracking
   - Full conversation history

2. **Custom Tools** (`tools/`)
   - **Notes**: Create, search, list with markdown export
   - **Research**: Web fetch, analysis with source tracking
   - **Reports**: Structured document generation
   - **Suggestions**: Track recommendations over time

3. **Agent Client** (`agent/client.py`)
   - ClaudeSDKClient wrapper
   - Tool orchestration
   - Session management
   - Streaming message handling

4. **CLI Interface** (`main.py`)
   - Interactive chat like Claude Code CLI
   - Streaming responses
   - Interrupt handling (Ctrl+C)
   - Session commands (/help, /stats, /exit)

5. **System Prompt** (`agent/prompts.py`)
   - Personal assistant personality
   - Tool usage guidelines
   - Windows-compatible (ASCII-only output)
   - Colleague-style communication

## File Structure

```
personal-assistant/
├── agent/
│   ├── __init__.py
│   ├── client.py          (372 lines)
│   ├── memory.py          (219 lines)
│   └── prompts.py         (94 lines)
├── tools/
│   ├── __init__.py
│   ├── notes.py           (154 lines)
│   ├── research.py        (139 lines)
│   └── reports.py         (165 lines)
├── storage/
│   ├── agent.db           (SQLite, created on first run)
│   ├── notes/             (Markdown files)
│   └── reports/           (Generated reports)
├── main.py                (155 lines)
├── test_setup.py          (99 lines)
├── requirements.txt
├── README.md
├── USAGE.md
├── install.sh             (Unix/Linux/Mac)
└── install.bat            (Windows)
```

**Total LOC:** ~1,400 lines Python code

## Key Features

### 1. Persistent Memory
- SQLite stores all conversations
- Resume previous sessions with `--resume`
- Full message history retrieval
- Cross-session context awareness

### 2. Note Management
- Create notes with title, content, tags
- Auto-generates markdown files
- Searchable by text or tags
- Organized by timestamp

### 3. Web Research
- Fetch URL content
- Track sources and citations
- Analyze patterns across sources
- Save research with metadata

### 4. Reports & Suggestions
- Generate structured reports
- Track suggestions over time
- Export as markdown
- Section-based organization

### 5. CLI Interface
- Streaming responses
- Interrupt support (Ctrl+C)
- Session statistics
- Cost tracking per session

### 6. Windows Compatible
- ASCII-only output (no Unicode)
- Tested on Windows 11
- Batch install script
- Path handling for Windows

## Database Schema

**sessions:**
- id (TEXT, PK)
- started_at, last_active_at (TEXT)
- total_cost_usd (REAL)
- message_count (INTEGER)

**messages:**
- id (INTEGER, PK)
- session_id (FK)
- timestamp, role, content (TEXT)

**notes:**
- id (INTEGER, PK)
- title, content, tags (TEXT)
- created_at, file_path (TEXT)
- session_id (FK)

**research:**
- id (INTEGER, PK)
- query, sources, analysis (TEXT)
- created_at (TEXT)
- session_id (FK)

**suggestions:**
- id (INTEGER, PK)
- content, context (TEXT)
- created_at (TEXT)
- session_id (FK)

## Installation

**Quick:**
```bash
pip install claude-agent-sdk httpx aiosqlite python-dateutil
export ANTHROPIC_API_KEY=your_key
python main.py
```

**Full:**
```bash
# Windows
install.bat

# Unix/Linux/Mac
chmod +x install.sh
./install.sh
```

## Usage Examples

### New Session
```bash
python main.py
You: Create a note about Python asyncio patterns
You: Research best practices for async/await
You: Generate a report summarizing our findings
```

### Resume Session
```bash
python main.py --resume
You: What did we discuss about asyncio yesterday?
[Agent recalls previous notes and research]
```

### Commands
- `/stats` - Session statistics and costs
- `/help` - Command reference
- `/exit` - Quit assistant

## Testing

Setup validation script verifies:
- All imports work
- Database initialization
- Tool creation
- Memory operations
- Note search

Run: `python test_setup.py`

## Configuration

**System Prompt:** Edit `agent/prompts.py`
**Storage Path:** Edit `agent/memory.py` db_path
**Tools:** Add new tools in `tools/` directory
**Permissions:** Set in `agent/client.py` (default: acceptEdits)

## Cost Management

Tracked per session in database:
- Total cost in USD
- Message count
- Token usage

View with `/stats` command.

## Extension Points

### Add Custom Tools

1. Create tool function:
```python
@tool("my_tool", "description", {"param": str})
async def my_tool(args):
    return {"content": [{"type": "text", "text": "result"}]}
```

2. Register in `agent/client.py`:
```python
all_tools.append(my_tool)
```

3. Add to `allowed_tools` list

### Integrate Search APIs

Replace placeholder in `tools/research.py` with:
- Google Custom Search API
- Bing Search API
- DuckDuckGo API
- SerpAPI

### Add MCP Servers

Configure external MCP servers in `agent/client.py`:
```python
options = ClaudeAgentOptions(
    mcp_servers={
        "assistant": internal_server,
        "external": external_mcp_config
    }
)
```

## Production Considerations

**Current State:** Development-ready
**For Production:**
- Add authentication/user management
- Implement rate limiting
- Add backup automation for SQLite
- Integrate real search APIs
- Add logging and monitoring
- Implement error recovery
- Add data export features
- Create admin CLI

## Limitations

1. **Web search** - Placeholder (needs API integration)
2. **HTML parsing** - Basic text extraction (needs BeautifulSoup)
3. **Cost limits** - No budget enforcement yet
4. **Multi-user** - Single-user design
5. **Backup** - Manual only

## Next Steps

Immediate:
1. Set ANTHROPIC_API_KEY
2. Run `python test_setup.py`
3. Start chatting: `python main.py`

Future enhancements:
- Real search API integration
- Advanced HTML parsing
- Cost budget controls
- Data export/import
- Web UI option
- Multi-user support
- Cloud sync

## Dependencies

```
claude-agent-sdk >= 0.1.0
httpx >= 0.27.0
aiosqlite >= 0.20.0
python-dateutil >= 2.9.0
```

## License & Credits

Built with Claude Agent SDK by Anthropic.
Agent implementation follows SDK best practices and documentation.

## Support

- Read USAGE.md for detailed guide
- Run test_setup.py for validation
- Check agent/prompts.py for behavior customization
- See tools/ for adding capabilities
