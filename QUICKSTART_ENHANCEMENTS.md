# Quick Start - New Enhancements

## Install New Dependencies (2 minutes)

```bash
cd personal-assistant
pip install beautifulsoup4 lxml duckduckgo-search
```

## Test Everything

```bash
python main.py

You: Search for Python asyncio tutorial
[Agent searches DuckDuckGo, returns URLs]

You: Fetch the first URL
[Agent extracts clean text from webpage]

You: Create a note about async patterns
[Note saved]

You: Export my data
[Backup created in storage/exports/]

You: /exit
```

## What's New

### 1. Web Search (DuckDuckGo)
```
You: Search for [topic]
→ Returns titles, URLs, snippets
```

### 2. Clean HTML Parsing
```
You: Fetch [URL]
→ Returns clean text (no HTML, scripts, ads)
```

### 3. Data Backup
```
You: Export my data
→ Creates JSON backup in storage/exports/

You: Import data from backup_YYYYMMDD.json
→ Restores from backup
```

## That's It!

All three enhancements work automatically. No configuration needed.

See **ENHANCEMENTS.md** for full documentation.
