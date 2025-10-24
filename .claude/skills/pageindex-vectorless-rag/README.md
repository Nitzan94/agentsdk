# PageIndex Vectorless RAG Skill

A comprehensive Claude Code skill for building vectorless RAG (Retrieval Augmented Generation) systems using PageIndex's reasoning-based tree search approach.

## Overview

This skill enables Claude to help users build and work with PageIndex, a vectorless RAG system that uses hierarchical tree structures and multi-step reasoning instead of traditional vector databases.

## What's Inside

- **SKILL.md** - Main skill guide with setup, workflows, and best practices
- **references/pageindex-api.md** - Complete API reference for PageIndex MCP tools
- **references/vectorless-rag-concepts.md** - Deep dive into tree-based reasoning vs vector-based RAG
- **assets/config-examples.md** - Configuration examples for various environments

## When to Use

This skill is ideal for:
- Working with structured documents (financial reports, legal contracts, technical manuals)
- Building RAG systems that need exact page references
- Scenarios requiring transparent, traceable retrieval
- Applications without vector database infrastructure
- Complex documents where hierarchical structure matters

## Installation

### For Claude Desktop

1. Extract this skill to your Claude skills directory
2. Or install via Claude Code's skill management

### For Development

This skill follows the standard Claude Code skill format:
- Main instructions in SKILL.md
- Reference documentation in references/
- Configuration examples in assets/

## Quick Start

Once installed, Claude will automatically use this skill when you:
- Ask about building RAG systems
- Work with PageIndex
- Need help with vectorless retrieval approaches
- Query complex documents that need structure preservation

## Key Features

### Vectorless Architecture
- No vector database required
- Lightweight JSON tree structures
- Preserves natural document hierarchy

### Reasoning-Based Retrieval
- Multi-step tree search (inspired by AlphaGo)
- Transparent reasoning paths
- Automatic node selection

### Exact Provenance
- Page references for every retrieval
- Full tree search trajectories
- Verifiable results

## Requirements

To use PageIndex:
- PageIndex API key (free during beta)
- Node.js ≥18.0.0 (for local PDF processing)
- Or just HTTP connection for API-only mode

## Documentation Structure

### SKILL.md
Main workflow guide covering:
- Setup instructions (npx and HTTP modes)
- Document processing workflow
- Querying strategies
- Best practices
- Troubleshooting

### references/pageindex-api.md
Complete API documentation:
- All MCP tools (process_document, get_page_content, search, add_document)
- Request/response formats
- Error codes and handling
- Rate limits and pagination
- Tree structure format

### references/vectorless-rag-concepts.md
Conceptual deep dive:
- Why vector RAG has limitations
- How tree-based reasoning works
- Algorithm details (LLM-based vs value-based search)
- Use case analysis
- When to choose trees vs vectors

### assets/config-examples.md
Configuration examples for:
- Claude Desktop
- Cursor IDE
- Other MCP clients
- Environment variables
- Advanced configurations
- Multi-tenant setups

## Comparison: Vector vs Tree RAG

| Aspect | Vector RAG | Tree RAG (PageIndex) |
|--------|-----------|---------------------|
| Infrastructure | Vector DB required | JSON files |
| Retrieval | Cosine similarity | Tree search |
| Context | Lost via chunking | Preserved |
| Transparency | Black box | Visible paths |
| Page refs | No | Yes |

## Example Use Cases

### Financial Analysis
Process 10-K filings and query with exact section references:
```
"What was Q3 revenue growth?" → "23% (Page 15, Revenue Analysis section)"
```

### Legal Research
Navigate contracts with hierarchical structure preserved:
```
"Summarize termination clause" → Returns section 5.3 with full context
```

### Technical Documentation
Query manuals with precise page citations:
```
"How to configure feature X?" → Step-by-step with page numbers
```

## Contributing

This is a user-created skill. Contributions and improvements welcome:
1. Suggest enhancements via issues
2. Share additional use cases
3. Provide feedback on documentation

## Resources

- **PageIndex Website**: https://pageindex.ai
- **PageIndex Docs**: https://docs.pageindex.ai
- **MCP Server**: https://github.com/VectifyAI/pageindex-mcp
- **PageIndex GitHub**: https://github.com/VectifyAI/PageIndex

## License

MIT License - see LICENSE.txt for details

This skill integrates with PageIndex, which is a separate service with its own terms of service.

## Support

For issues with:
- **This skill**: Create an issue or contact the maintainer
- **PageIndex service**: Visit https://docs.pageindex.ai or GitHub
- **MCP protocol**: See https://modelcontextprotocol.io

## Version

v1.0.0 - Initial release

Built for Claude Code with ❤️
