# Container & Document Skills - How It Actually Works

## The Confusion (And The Fix)

### What I Initially Thought ❌

I tried to configure `betas` and `container` directly in the Agent SDK:

```python
# THIS DOESN'T WORK - Agent SDK doesn't support these params
options = ClaudeAgentOptions(
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={"skills": [...]}  # ERROR!
)
```

**Result:** `TypeError: unexpected keyword argument 'betas'`

### How It Actually Works ✅

**The Agent SDK wraps Claude Code CLI**, which already has document skills built-in!

```
You write:                   Agent SDK does:                Claude Code CLI has:
┌──────────────┐            ┌──────────────┐               ┌─────────────────┐
│              │            │              │               │                 │
│ ClaudeAgent  │───calls───>│  Agent SDK   │────spawns────>│ Claude Code CLI │
│ Options()    │            │              │               │                 │
│              │            │              │               │ - xlsx skill    │
│              │            │              │               │ - docx skill    │
│              │            │              │               │ - pptx skill    │
│              │            │              │               │ - pdf skill     │
│              │            │              │               │ - container     │
│              │            │              │               │ - beta API      │
│              │            │              │               │                 │
└──────────────┘            └──────────────┘               └─────────────────┘
```

**The fix:**
```python
# CORRECT - Just use basic options
options = ClaudeAgentOptions(
    allowed_tools=["Bash", "Read", "Write", "Edit"],
    can_use_tool=self._permission_handler,
    cwd="."
)
# Document skills work automatically via Claude Code CLI!
```

## How Document Skills Are Available

### Architecture Layers

**Layer 1: Your Agent (Python)**
```python
# personal-assistant/agent/client.py
client = ClaudeSDKClient(options=options)
```

**Layer 2: Agent SDK (Python wrapper)**
```python
# Installed via: pip install claude-agent-sdk
# Spawns and controls Claude Code CLI process
```

**Layer 3: Claude Code CLI (Node.js)**
```bash
# Installed globally: npm install -g @anthropic-ai/claude-code
# Has document skills plugin installed by default
```

**Layer 4: Anthropic API (Cloud)**
```
# Claude Code CLI sends requests with:
# - Beta headers (code-execution, skills)
# - Container config (automatic)
# - Your prompts and tool calls
```

**Layer 5: Container (Anthropic's Cloud Sandbox)**
```
# Anthropic spins up isolated environment with:
# - Python runtime
# - Document libraries (openpyxl, python-docx, etc.)
# - Skills loaded dynamically
# - Executes code
# - Returns results
```

## What You Actually Configured

### 1. Permission Handler ✅

```python
async def _permission_handler(self, tool_name, input_data, context):
    if tool_name == "Bash":
        # Show prompt and wait for approval
        command = input_data.get("command", "")
        print(f"[PERMISSION] Bash: {command}")
        response = input("Approve? (y/n): ")
        return allow or deny
```

**This controls:** Whether agent can run bash/python commands
**Location:** Your agent code
**Purpose:** User approval for potentially dangerous operations

### 2. Allowed Tools ✅

```python
allowed_tools=[
    "Bash",           # Execute bash commands
    "Read",           # Read files
    "Write",          # Write files
    "Edit",           # Edit files
    "mcp__assistant__*"  # Your custom tools
]
```

**This controls:** Which tools agent can use
**Location:** Your agent code
**Purpose:** Whitelist of available capabilities

### 3. Custom MCP Tools ✅

```python
# Your tools: notes, research, reports, documents
all_tools = [...]
mcp_server = create_sdk_mcp_server(name="assistant", tools=all_tools)
```

**This controls:** Your custom functionality
**Location:** tools/*.py
**Purpose:** Domain-specific operations

## Document Skills Flow

### When You Ask: "Create an Excel spreadsheet"

**Step 1: Your Agent**
```
User input: "Create Excel spreadsheet"
↓
Agent client receives prompt
↓
Sends to Agent SDK
```

**Step 2: Agent SDK**
```
Receives prompt
↓
Spawns Claude Code CLI process
↓
Sends API request
```

**Step 3: Claude Code CLI**
```
Receives request from SDK
↓
Adds beta headers automatically
↓
Adds container config automatically
↓
Sends to Anthropic API
```

**Step 4: Claude AI (via API)**
```
Analyzes prompt
↓
Decides: "Need to create Excel file"
↓
Generates Python code:
  import openpyxl
  wb = openpyxl.Workbook()
  # ... creates spreadsheet
  wb.save('output.xlsx')
↓
Requests Bash tool execution
```

**Step 5: Your Permission Handler**
```
============================================================
[PERMISSION] Bash command requested:
  python /tmp/create_excel_abc123.py
============================================================
Approve? (y/n):
```

**Step 6: User Approves**
```
User types: y
↓
Permission granted
↓
Request continues to API
```

**Step 7: Anthropic Container (Cloud)**
```
Receives approved code execution request
↓
Spins up isolated container
↓
Loads xlsx skill (openpyxl library)
↓
Executes Python code
↓
Creates output.xlsx IN CONTAINER
↓
Returns: Success + file metadata
```

**Step 8: Response Back to You**
```
Container → API → CLI → SDK → Your Agent → Terminal
↓
[OK] Created spreadsheet: output.xlsx
```

## What's Automatically Handled

### By Claude Code CLI

✅ Beta API headers
✅ Container configuration
✅ Skills loading
✅ Code execution sandbox
✅ Error handling

### By Agent SDK

✅ CLI process management
✅ Message streaming
✅ Session management
✅ Tool call routing

### By You (Your Code)

✅ Permission prompts
✅ Custom tools (notes, research, etc.)
✅ Database persistence
✅ User interface (CLI)

## Where Files Live

### Created Files

**Initial location:** Anthropic's container (cloud)
**Lifespan:** Temporary, deleted after session
**Access:** Via file_id from API response

**To save locally:** Would need to:
1. Get file_id from response
2. Use Anthropic Files API to download
3. Save to `storage/documents/`

**Current behavior:**
- Agent creates file in container
- Shows success message
- File not automatically downloaded

## Configuration Summary

| Component | Configured By | Location |
|-----------|---------------|----------|
| Beta API | Claude Code CLI | Automatic |
| Container | Claude Code CLI | Automatic |
| Skills | Claude Code CLI | Pre-installed |
| Permission Handler | You | agent/client.py |
| Allowed Tools | You | agent/client.py |
| Custom Tools | You | tools/*.py |
| Database | You | agent/memory.py |

## Key Takeaway

**You don't configure the container** - it's handled automatically by the Claude Code CLI that the Agent SDK spawns!

Your configuration focuses on:
- **Permissions** - What to approve
- **Tools** - What's available
- **Business logic** - Your custom features

The document skills work "out of the box" because:
1. Claude Code CLI has them installed
2. Agent SDK uses Claude Code CLI
3. Your agent uses Agent SDK

It's turtles all the way down, but each layer handles its own responsibility!

## Testing Document Skills

Try these commands:

```bash
python main.py

You: Create a simple Excel file with test data

[Permission prompt appears]
Approve? (y/n): y

[Agent creates file in container]
[Shows success message]
```

**Note:** Files created in container but not auto-downloaded. That's expected behavior with current setup!

To download files automatically, would need to integrate Anthropic Files API (future enhancement).
