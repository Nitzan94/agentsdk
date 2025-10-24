# PageIndex Configuration Examples

Complete configuration examples for various environments and use cases.

## Table of Contents

1. [Claude Desktop](#claude-desktop)
2. [Cursor IDE](#cursor-ide)
3. [Other MCP Clients](#other-mcp-clients)
4. [Environment Variables](#environment-variables)
5. [Advanced Configurations](#advanced-configurations)

---

## Claude Desktop

### Basic Configuration (NPX - Local PDFs)

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Features:**
- Local PDF processing
- Full MCP tool access
- Automatic updates via npx

### HTTP Configuration (API-Only)

```json
{
  "mcpServers": {
    "pageindex": {
      "type": "http",
      "url": "https://dash.pageindex.ai/api/mcp/mcp",
      "headers": {
        "Authorization": "Bearer your_api_key_here"
      }
    }
  }
}
```

**Features:**
- Direct API connection
- No local dependencies
- Requires manual PDF uploads via dashboard

### Multiple MCP Servers Configuration

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_pageindex_key"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "/Users/username/documents"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_github_token"
      }
    }
  }
}
```

**Use Case:** Combine PageIndex with filesystem access and GitHub integration for comprehensive document workflows.

---

## Cursor IDE

### Cursor Configuration

**Location:** `.cursor/mcp.json` in your project root

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Project-Specific Setup

For project documentation access:

```json
{
  "mcpServers": {
    "pageindex-docs": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_api_key_here",
        "PROJECT_DOCS_PATH": "./docs"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "."
      }
    }
  }
}
```

**Workflow:**
1. Process project documentation with PageIndex
2. Query docs while coding
3. Reference exact sections in code comments

---

## Other MCP Clients

### Continue.dev

**Location:** `~/.continue/config.json`

```json
{
  "mcpServers": [
    {
      "name": "pageindex",
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_api_key_here"
      }
    }
  ]
}
```

### Custom MCP Client

**Generic MCP Client Configuration:**

```python
from mcp_client import MCPClient

client = MCPClient()

# Connect to PageIndex MCP server
client.connect(
    server_type="stdio",
    command="npx",
    args=["-y", "pageindex-mcp"],
    env={
        "PAGEINDEX_API_KEY": "your_api_key_here"
    }
)

# Use tools
result = client.call_tool(
    "process_document",
    source="/path/to/document.pdf"
)

document_id = result["document_id"]

answer = client.call_tool(
    "get_page_content",
    document_id=document_id,
    query="What is the main conclusion?"
)
```

---

## Environment Variables

### Available Variables

#### PAGEINDEX_API_KEY (Required)

Your PageIndex API key.

```bash
export PAGEINDEX_API_KEY="pi_1234567890abcdef"
```

**Get your key:**
1. Visit https://dash.pageindex.ai
2. Sign up for beta access
3. Generate API key from dashboard

#### PAGEINDEX_DEBUG (Optional)

Enable debug logging.

```bash
export PAGEINDEX_DEBUG="true"
```

**Output:**
- Tool call details
- Tree search paths
- API request/response logs

#### PAGEINDEX_CACHE_DIR (Optional)

Custom cache directory for processed trees.

```bash
export PAGEINDEX_CACHE_DIR="/custom/cache/path"
```

**Default:**
- macOS/Linux: `~/.pageindex/cache`
- Windows: `%LOCALAPPDATA%\PageIndex\cache`

#### PAGEINDEX_TIMEOUT (Optional)

API request timeout in seconds.

```bash
export PAGEINDEX_TIMEOUT="60"
```

**Default:** 30 seconds

### Loading from .env File

**Create `.env` file:**

```bash
# PageIndex Configuration
PAGEINDEX_API_KEY=pi_1234567890abcdef
PAGEINDEX_DEBUG=false
PAGEINDEX_CACHE_DIR=/custom/cache
PAGEINDEX_TIMEOUT=45
```

**Load in configuration:**

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "${PAGEINDEX_API_KEY}",
        "PAGEINDEX_DEBUG": "${PAGEINDEX_DEBUG}",
        "PAGEINDEX_CACHE_DIR": "${PAGEINDEX_CACHE_DIR}",
        "PAGEINDEX_TIMEOUT": "${PAGEINDEX_TIMEOUT}"
      }
    }
  }
}
```

---

## Advanced Configurations

### High-Volume Processing

For bulk document processing:

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_api_key_here",
        "PAGEINDEX_TIMEOUT": "120",
        "PAGEINDEX_MAX_CONCURRENT": "10",
        "PAGEINDEX_RETRY_ATTEMPTS": "3"
      }
    }
  }
}
```

**Settings:**
- `PAGEINDEX_TIMEOUT`: Longer timeout for large documents
- `PAGEINDEX_MAX_CONCURRENT`: Parallel processing limit
- `PAGEINDEX_RETRY_ATTEMPTS`: Automatic retries on failure

### Development vs Production

**Development:**

```json
{
  "mcpServers": {
    "pageindex-dev": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "dev_api_key",
        "PAGEINDEX_DEBUG": "true",
        "PAGEINDEX_ENV": "development"
      }
    }
  }
}
```

**Production:**

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "prod_api_key",
        "PAGEINDEX_DEBUG": "false",
        "PAGEINDEX_ENV": "production",
        "PAGEINDEX_LOG_FILE": "/var/log/pageindex.log"
      }
    }
  }
}
```

### Multi-Tenant Setup

For organizations with multiple teams:

```json
{
  "mcpServers": {
    "pageindex-finance": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "finance_team_key",
        "PAGEINDEX_CACHE_DIR": "/data/pageindex/finance"
      }
    },
    "pageindex-legal": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "legal_team_key",
        "PAGEINDEX_CACHE_DIR": "/data/pageindex/legal"
      }
    },
    "pageindex-engineering": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "engineering_team_key",
        "PAGEINDEX_CACHE_DIR": "/data/pageindex/engineering"
      }
    }
  }
}
```

**Benefits:**
- Separate API keys per team
- Isolated caches
- Team-specific rate limits

### Custom OCR Configuration

For documents requiring specific OCR settings:

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_api_key_here",
        "PAGEINDEX_OCR_MODE": "force",
        "PAGEINDEX_OCR_LANGUAGE": "eng+fra",
        "PAGEINDEX_OCR_DPI": "300"
      }
    }
  }
}
```

**OCR Settings:**
- `PAGEINDEX_OCR_MODE`: "auto", "force", "skip"
- `PAGEINDEX_OCR_LANGUAGE`: Tesseract language codes
- `PAGEINDEX_OCR_DPI`: OCR resolution (default: 200)

---

## Configuration Validation

### Test Your Configuration

**Script to validate MCP setup:**

```bash
#!/bin/bash

# Test PageIndex MCP connection
echo "Testing PageIndex MCP configuration..."

# Check if config file exists
CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "✓ Config file exists"

# Validate JSON
if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
    echo "❌ Invalid JSON in config file"
    exit 1
fi

echo "✓ Valid JSON"

# Check for PageIndex server
if ! jq -e '.mcpServers.pageindex' "$CONFIG_FILE" >/dev/null; then
    echo "❌ PageIndex server not configured"
    exit 1
fi

echo "✓ PageIndex server configured"

# Check API key
if ! jq -e '.mcpServers.pageindex.env.PAGEINDEX_API_KEY' "$CONFIG_FILE" >/dev/null; then
    echo "❌ PAGEINDEX_API_KEY not set"
    exit 1
fi

echo "✓ API key configured"

echo ""
echo "Configuration validated successfully!"
```

### Troubleshooting Common Issues

#### Issue: "Command not found: npx"

**Solution:** Install Node.js ≥18.0.0

```bash
# macOS (using Homebrew)
brew install node

# Windows (using Chocolatey)
choco install nodejs

# Linux (using nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
```

#### Issue: "Invalid API key"

**Solution:** Regenerate key from dashboard

1. Visit https://dash.pageindex.ai
2. Go to Settings → API Keys
3. Revoke old key
4. Generate new key
5. Update configuration

#### Issue: "Connection timeout"

**Solution:** Increase timeout or check network

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_key",
        "PAGEINDEX_TIMEOUT": "120"
      }
    }
  }
}
```

#### Issue: "Cannot process local PDFs"

**Solution:** Ensure using stdio mode (npx), not HTTP

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",  // ✓ Correct for local PDFs
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "your_key"
      }
    }
  }
}
```

NOT:

```json
{
  "mcpServers": {
    "pageindex": {
      "type": "http",  // ✗ HTTP mode doesn't support local files
      "url": "https://dash.pageindex.ai/api/mcp/mcp"
    }
  }
}
```

---

## Security Best Practices

### API Key Management

**❌ DON'T:**
- Commit API keys to version control
- Share keys across teams/projects
- Use production keys in development
- Hardcode keys in configuration

**✓ DO:**
- Use environment variables
- Rotate keys regularly
- Use separate keys per environment
- Store keys in secure credential managers

### Secure Configuration Pattern

```bash
# .env (gitignored)
PAGEINDEX_API_KEY_PROD=pi_prod_key
PAGEINDEX_API_KEY_DEV=pi_dev_key
```

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "${PAGEINDEX_API_KEY_PROD}"
      }
    }
  }
}
```

### Credential Manager Integration

**macOS Keychain:**

```bash
# Store key in keychain
security add-generic-password \
  -a $USER \
  -s pageindex_api_key \
  -w "your_api_key_here"

# Retrieve in script
PAGEINDEX_API_KEY=$(security find-generic-password \
  -a $USER \
  -s pageindex_api_key \
  -w)
```

**Windows Credential Manager:**

```powershell
# Store key
cmdkey /generic:PageIndexAPIKey /user:$env:USERNAME /pass:your_api_key_here

# Retrieve in script
$credential = Get-StoredCredential -Target PageIndexAPIKey
$env:PAGEINDEX_API_KEY = $credential.GetNetworkCredential().Password
```

---

## Complete Example: Enterprise Setup

```json
{
  "mcpServers": {
    "pageindex": {
      "command": "npx",
      "args": ["-y", "pageindex-mcp"],
      "env": {
        "PAGEINDEX_API_KEY": "${PAGEINDEX_API_KEY}",
        "PAGEINDEX_DEBUG": "${PAGEINDEX_DEBUG:-false}",
        "PAGEINDEX_CACHE_DIR": "${PAGEINDEX_CACHE_DIR:-~/.pageindex/cache}",
        "PAGEINDEX_TIMEOUT": "${PAGEINDEX_TIMEOUT:-60}",
        "PAGEINDEX_MAX_CONCURRENT": "${PAGEINDEX_MAX_CONCURRENT:-5}",
        "PAGEINDEX_RETRY_ATTEMPTS": "${PAGEINDEX_RETRY_ATTEMPTS:-3}",
        "PAGEINDEX_LOG_FILE": "${PAGEINDEX_LOG_FILE:-/var/log/pageindex.log}",
        "PAGEINDEX_OCR_MODE": "${PAGEINDEX_OCR_MODE:-auto}",
        "PAGEINDEX_ENV": "${PAGEINDEX_ENV:-production}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "env": {
        "ALLOWED_DIRECTORIES": "${ALLOWED_DIRECTORIES}"
      }
    }
  }
}
```

**Corresponding .env:**

```bash
# PageIndex Configuration
PAGEINDEX_API_KEY=pi_1234567890abcdef
PAGEINDEX_DEBUG=false
PAGEINDEX_CACHE_DIR=/data/pageindex/cache
PAGEINDEX_TIMEOUT=90
PAGEINDEX_MAX_CONCURRENT=10
PAGEINDEX_RETRY_ATTEMPTS=5
PAGEINDEX_LOG_FILE=/var/log/pageindex/app.log
PAGEINDEX_OCR_MODE=force
PAGEINDEX_ENV=production

# Filesystem Configuration
ALLOWED_DIRECTORIES=/data/documents:/data/reports
```

This enterprise setup provides:
- Environment-based configuration
- Sensible defaults with fallbacks
- Comprehensive logging
- High concurrency for bulk processing
- Integrated filesystem access
- Secure credential management
