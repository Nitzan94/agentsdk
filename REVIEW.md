# SDK Best Practices Review

## Overall Assessment: STRONG ✓

Your agent follows SDK best practices well. Few issues found.

---

## What's Good

### Architecture
- **ClaudeSDKClient wrapper pattern** - client.py wraps SDK cleanly
- **Session management** - proper initialize() → setup_client() → connect() flow
- **Memory integration** - SQLite tracking sessions, messages, research
- **Clean separation** - CLI, agent client, memory, tools in separate modules

### Tools Implementation
- **MCP tools** - properly using @tool decorator, correct schema
- **Tool organization** - tools grouped by domain (research, documents, export)
- **Error handling** - graceful fallbacks when dependencies missing
- **Async properly** - all tools async, httpx.AsyncClient for network

### Configuration
- **Skills enabled** - setting_sources=["user", "project"] ✓
- **Custom permission handler** - prompts for Bash, auto-approves MCP ✓
- **Tool allowlist** - explicit allowed_tools list ✓
- **System prompt** - custom prompt via ClaudeAgentOptions ✓

---

## Issues Found

### 1. Session Resume NOT Working (client.py:119)

**Problem:**
```python
resume=self.session_id if self.resume else None  # WRONG
```

SDK expects session_id for resume, not boolean check.

**Fix:**
```python
# If resuming and have session_id, pass it
resume=self.session_id if (self.resume and self.session_id) else None
```

**Why:** Currently passes session_id even when self.resume=False, causing unintended resume.

---

### 2. Message Saving Incomplete (client.py:137-164)

**Problem:**
- Only saves text blocks
- Ignores tool_use and tool_result messages
- Stream yields all message types but only text saved

**Current:**
```python
if hasattr(message, 'content'):
    if isinstance(message.content, str):
        assistant_response.append(message.content)
    # ...
```

**Better:**
```python
# Save all message types to reconstruct full conversation
if hasattr(message, 'type'):
    if message.type == 'text':
        # save text
    elif message.type == 'tool_use':
        # save tool invocation
    elif message.type == 'tool_result':
        # save tool result
```

**Why:** When resuming sessions, missing tool_use/tool_result breaks context.

---

### 3. Cost Tracking Per-Response (client.py:151-156)

**Problem:**
```python
if hasattr(message, 'total_cost_usd'):
    await self.memory.update_session(
        self.session_id,
        cost_usd=message.total_cost_usd,  # This is TOTAL, not delta
        message_count=1
    )
```

**Issue:**
- `total_cost_usd` is cumulative for entire session
- Currently adds it multiple times (once per message with cost)
- Should only track at end of response

**Fix:**
```python
# After receive_response loop ends
async for message in self.client.receive_response():
    yield message
    if hasattr(message, 'content'):
        # collect content...

    # Store last cost
    if hasattr(message, 'total_cost_usd'):
        last_cost = message.total_cost_usd

# After loop
if last_cost:
    await self.memory.update_session(
        self.session_id,
        cost_usd=last_cost - previous_cost,  # Track delta
        message_count=2  # user + assistant
    )
```

---

### 4. Duplicate Tables in Schema (memory.py)

**Problem:**
- export.py references tables: notes, suggestions
- memory.py doesn't create these tables
- export_data will fail when querying non-existent tables

**Fix:** Add to memory.py initialize():
```python
await db.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT,
        created_at TEXT NOT NULL,
        file_path TEXT,
        session_id TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )
""")

await db.execute("""
    CREATE TABLE IF NOT EXISTS suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        context TEXT,
        created_at TEXT NOT NULL,
        session_id TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )
""")
```

---

### 5. Tool Schema Not Fully Typed (tools/*.py)

**Problem:**
```python
@tool(
    "web_search",
    "description",
    {
        "query": str,
        "max_results": int  # No default value indication
    }
)
```

**Better:**
Use proper schema with optional fields:
```python
from claude_agent_sdk import tool_schema

schema = tool_schema({
    "query": {"type": "string", "description": "Search query"},
    "max_results": {"type": "integer", "description": "Max results", "default": 5}
})

@tool("web_search", "description", schema)
```

**Why:** SDK can validate and provide better errors. Current works but less robust.

---

### 6. Interrupt Not Awaited (main.py:78)

**Problem:**
```python
except KeyboardInterrupt:
    print(f"{Colors.RESET}\n{Colors.ERROR}[INTERRUPTED]{Colors.RESET}")
    if client.client:
        await client.client.interrupt()  # In sync context!
```

**Context:** This is inside async function, so await is fine. But client.interrupt() may not complete before function exits.

**Better:**
```python
except KeyboardInterrupt:
    print(f"{Colors.RESET}\n{Colors.ERROR}[INTERRUPTED]{Colors.RESET}")
    if client.client:
        try:
            await asyncio.wait_for(client.client.interrupt(), timeout=1.0)
        except asyncio.TimeoutError:
            pass
```

---

### 7. No Session ID Tracking for Tools

**Problem:**
```python
# research.py:263
await self.memory.save_research(
    query=topic,
    sources=sources,
    analysis=analysis,
    session_id=None  # Always None!
)
```

**Why:** Comment says "Will be set by client" but client never sets it.

**Fix:** Pass session_id to tools:
```python
# client.py
self.research_tools = ResearchTools(self.memory, self.session_id)

# research.py
class ResearchTools:
    def __init__(self, memory_manager, session_id=None):
        self.memory = memory_manager
        self.session_id = session_id

    # In tool:
    await self.memory.save_research(
        query=topic,
        sources=sources,
        analysis=analysis,
        session_id=self.session_id
    )
```

---

## Minor Issues

### 8. No cleanup on tool errors (research.py:283)
```python
async def close(self):
    await self.client.aclose()
```

If exception during send_message, httpx client never closed.

**Fix:** Use context manager or try/finally in AssistantClient.close()

---

### 9. System prompt formatting (prompts.py:39)
```python
# IMPORTANT: Do NOT use markdown formatting (##, **, -, etc.) in responses
```

But then uses markdown in tool outputs:
```python
output += f"**{i}. {r['title']}**\n"  # research.py:84
```

Inconsistent.

---

### 10. Windows Unicode warning (prompts.py:36)
Good! You correctly document no Unicode. But in code:
```python
# main.py:28
print(f"{'=' * 60}")  # OK, ASCII
```

All tool outputs use ASCII markers. Good.

---

## Recommendations

### Priority 1 (Fix Now)
1. Session resume logic - breaks resume feature
2. Missing DB tables - breaks export feature
3. Session ID in tools - data not linked to sessions

### Priority 2 (Soon)
4. Cost tracking - inflates costs in DB
5. Message saving - breaks session resume context

### Priority 3 (Nice to Have)
6. Tool schema typing - better validation
7. Interrupt timeout - cleaner shutdown
8. Resource cleanup - prevent leaks

---

## SDK Best Practices Checklist

- [x] ClaudeSDKClient for multi-turn conversations
- [x] Async/await throughout
- [x] Custom permission handler
- [x] MCP tools with @tool decorator
- [x] Skills enabled via setting_sources
- [x] System prompt customization
- [x] Session management
- [x] Cost tracking (needs fix)
- [x] Error handling
- [x] Resource cleanup (needs improvement)
- [ ] Session resume (broken)
- [ ] Message persistence (incomplete)
- [ ] Tool schema validation (basic)

---

## Overall Grade: B+

Strong foundation. Core patterns correct. Issues are fixable bugs, not architectural problems.
