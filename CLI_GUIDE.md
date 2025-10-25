# Rich CLI Guide

Your personal assistant now has a beautiful rich terminal interface!

## Quick Start

**Use the rich CLI (recommended):**
```bash
python main_rich.py
```

**Fall back to simple CLI:**
```bash
python main.py
# or
python main_rich.py --simple
```

## Features

### 🎨 Beautiful Visuals
- **Markdown rendering** - Code blocks, lists, bold/italic display correctly
- **Syntax highlighting** - Code snippets colorized
- **Message panels** - User and assistant messages in colored boxes
- **Emoji indicators** - 👤 You, 🤖 Assistant, ⚙️ Tools
- **Timestamps** - See when each message was sent

### ⌨️ Enhanced Input
- **Command autocomplete** - Start typing `/` and press Tab
- **History navigation** - Use Up/Down arrows for previous messages
- **Multi-line input** - Press Alt+Enter for newlines (future feature)
- **Command history** - All your inputs saved and searchable

### 📜 Conversation Management
- **/history [N]** - View last N messages (default 10)
- **/search \<query>** - Search past messages
- **/export** - Save conversation to markdown file

### ⚙️ Tool Progress
- See which tools are running (⚙️ Using tool: web_search)
- Clean, non-intrusive tool notifications
- Tool results formatted nicely

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help panel |
| `/stats` | Session statistics (messages, cost, time) |
| `/history [N]` | View last N messages |
| `/search <query>` | Search conversation |
| `/export` | Export conversation to .md file |
| `/clear` | Clear screen |
| `/exit` | Quit assistant |
| `Ctrl+C` | Interrupt current response |

## Examples

**View recent conversation:**
```
You: /history 5
```

**Search for specific topic:**
```
You: /search budget spreadsheet
```

**Export conversation:**
```
You: /export
✓ Conversation exported to: storage/exports/conversation_20251025_143022.md
```

**Session stats:**
```
You: /stats

┌─ Session Statistics ─────────────────┐
│ Session ID      abc123def456...      │
│ Started         2025-10-25 14:00:00  │
│ Last Active     2025-10-25 14:30:22  │
│ Messages        24                   │
│ Total Cost      $0.0456              │
└──────────────────────────────────────┘
```

## Tips

1. **Markdown works!** The assistant's responses render with formatting:
   - **Bold** and *italic*
   - `code blocks`
   - Lists and tables

2. **Use autocomplete:** Type `/` and hit Tab to see all commands

3. **Search is powerful:** Use `/search` to find past topics

4. **Export regularly:** Use `/export` to save important conversations

5. **Keyboard shortcuts:**
   - `Up/Down` - Navigate history
   - `Ctrl+C` - Stop current response
   - Tab - Autocomplete commands

## Comparison: Simple vs Rich CLI

| Feature | Simple (`main.py`) | Rich (`main_rich.py`) |
|---------|-------------------|----------------------|
| Speed | Very fast | Fast |
| Markdown | No | Yes ✓ |
| History | No | Yes ✓ |
| Search | No | Yes ✓ |
| Export | No | Yes ✓ |
| Panels | No | Yes ✓ |
| Autocomplete | No | Yes ✓ |
| Tool progress | Basic | Enhanced ✓ |

## Troubleshooting

**Colors not showing?**
```bash
# Your terminal may not support colors
python main_rich.py --simple
```

**Weird characters?**
```bash
# Terminal encoding issue - use simple mode
python main.py
```

**Want old interface?**
```bash
# Old CLI still available
python main.py
```

Enjoy your beautiful CLI! 🎨
