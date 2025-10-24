# PageIndex API Reference

Complete API documentation for PageIndex MCP server tools and capabilities.

## MCP Server Information

### Server Name
`pageindex`

### Transport Modes
- **stdio**: Via npx command (supports local PDFs)
- **HTTP**: Direct API connection (requires dashboard uploads)

### Authentication
API key required via:
- Environment variable: `PAGEINDEX_API_KEY` (stdio mode)
- Authorization header: `Bearer <API_KEY>` (HTTP mode)

## Available Tools

### process_document

Process PDF documents into PageIndex tree structures for reasoning-based retrieval.

**Tool Signature:**
```
process_document(
  source: string | file_path,
  options?: ProcessingOptions
) -> DocumentProcessingResult
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | string | Yes | Local file path (stdio mode) or public URL (both modes) |
| `options` | object | No | Processing configuration options |

**ProcessingOptions:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ocr_mode` | enum | "auto" | OCR processing mode: "auto", "force", "skip" |
| `language` | string | "en" | Document language code (ISO 639-1) |
| `preserve_formatting` | boolean | true | Preserve markdown formatting in tree nodes |

**Returns: DocumentProcessingResult**

```typescript
{
  document_id: string          // Unique identifier for queries
  status: "processing" | "completed" | "failed"
  tree_metadata: {
    total_nodes: number        // Number of nodes in tree
    max_depth: number          // Maximum tree depth
    total_pages: number        // Total document pages
    structure_quality: number  // 0-1 quality score
  }
  processing_time_ms: number
  error?: string              // Present if status="failed"
}
```

**Example Usage:**

Local PDF (stdio mode):
```
process_document(
  source: "/Users/username/documents/report.pdf"
)
```

URL-based:
```
process_document(
  source: "https://example.com/public/report.pdf",
  options: {
    ocr_mode: "force",
    language: "en"
  }
)
```

**Error Codes:**

| Code | Meaning | Solution |
|------|---------|----------|
| `INVALID_PDF` | PDF is corrupted or unreadable | Check file integrity |
| `OCR_FAILED` | OCR processing failed | Try different ocr_mode |
| `SIZE_LIMIT_EXCEEDED` | File too large | Check current beta limits |
| `URL_INACCESSIBLE` | Cannot fetch URL | Verify URL is publicly accessible |
| `AUTH_FAILED` | Invalid API key | Check PAGEINDEX_API_KEY |

### get_page_content

Retrieve content from processed documents using reasoning-based tree search.

**Tool Signature:**
```
get_page_content(
  document_id: string,
  query: string,
  options?: RetrievalOptions
) -> RetrievalResult
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | string | Yes | ID from process_document result |
| `query` | string | Yes | Natural language query |
| `options` | object | No | Retrieval configuration options |

**RetrievalOptions:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_nodes` | number | 10 | Maximum tree nodes to return |
| `include_reasoning_path` | boolean | true | Include tree search trajectory |
| `detail_level` | enum | "standard" | "minimal", "standard", "detailed" |
| `context_window` | number | 500 | Characters of context around matches |

**Returns: RetrievalResult**

```typescript
{
  query: string               // Original query
  retrieved_nodes: TreeNode[] // Matched tree nodes
  reasoning_path: string[]    // Tree search trajectory
  total_matches: number       // Total relevant nodes found
  retrieval_time_ms: number
}

interface TreeNode {
  node_id: string            // Unique node identifier
  content: string            // Node text content
  page_number: number        // Exact page reference
  heading: string            // Section/subsection title
  depth: number              // Tree depth level
  relevance_score: number    // 0-1 relevance to query
  parent_path: string[]      // Hierarchical path to node
  children_summary?: string  // Summary of child nodes
}
```

**Example Usage:**

Basic query:
```
get_page_content(
  document_id: "doc_abc123",
  query: "What was the total revenue in Q3?"
)
```

Detailed retrieval:
```
get_page_content(
  document_id: "doc_abc123",
  query: "Summarize risk factors",
  options: {
    max_nodes: 20,
    detail_level: "detailed",
    include_reasoning_path: true
  }
)
```

**Error Codes:**

| Code | Meaning | Solution |
|------|---------|----------|
| `DOCUMENT_NOT_FOUND` | Invalid document_id | Verify document was processed |
| `PROCESSING_INCOMPLETE` | Document still processing | Wait for processing to complete |
| `QUERY_TOO_SHORT` | Query insufficient | Provide more specific query |
| `NO_RESULTS` | No matching nodes | Try broader query terms |

### add_document (Advanced)

Manually add pre-processed tree structures to PageIndex.

**Tool Signature:**
```
add_document(
  tree: TreeStructure,
  metadata?: DocumentMetadata
) -> AddDocumentResult
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tree` | object | Yes | Pre-built tree structure following PageIndex schema |
| `metadata` | object | No | Document metadata |

**TreeStructure Format:**

```typescript
{
  root: {
    id: string
    heading: string
    content: string
    page_number: number
    children: TreeNode[]
  }
}
```

**DocumentMetadata:**

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Document title |
| `author` | string | Document author |
| `date` | string | Publication date (ISO 8601) |
| `source` | string | Original source URL or path |
| `tags` | string[] | Classification tags |

**Returns: AddDocumentResult**

```typescript
{
  document_id: string
  nodes_added: number
  validation_warnings: string[]
}
```

**Example Usage:**

```
add_document(
  tree: {
    root: {
      id: "root",
      heading: "Financial Report Q3 2024",
      content: "...",
      page_number: 1,
      children: [...]
    }
  },
  metadata: {
    title: "Q3 2024 Report",
    author: "Finance Dept",
    date: "2024-10-15",
    tags: ["financial", "quarterly"]
  }
)
```

**Use Cases:**
- Custom tree generation pipelines
- Migrating existing document indices
- Integrating with specialized OCR systems

### search (Multi-Document Search)

Search across multiple processed documents simultaneously.

**Tool Signature:**
```
search(
  query: string,
  document_ids?: string[],
  options?: SearchOptions
) -> SearchResult
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `document_ids` | string[] | No | Specific docs to search (omit for all) |
| `options` | object | No | Search configuration |

**SearchOptions:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `max_results_per_doc` | number | 5 | Results per document |
| `aggregate_results` | boolean | true | Combine results across documents |
| `min_relevance` | number | 0.5 | Minimum relevance threshold (0-1) |

**Returns: SearchResult**

```typescript
{
  query: string
  results: DocumentResult[]
  total_documents_searched: number
  total_matches: number
}

interface DocumentResult {
  document_id: string
  document_title: string
  matches: TreeNode[]
  top_relevance_score: number
}
```

**Example Usage:**

Search all documents:
```
search(
  query: "What are the compliance requirements?"
)
```

Search specific documents:
```
search(
  query: "regulatory changes",
  document_ids: ["doc_123", "doc_456", "doc_789"],
  options: {
    max_results_per_doc: 10,
    min_relevance: 0.7
  }
)
```

## Rate Limits (Beta)

Current beta limits:
- **Document processing**: 50 documents/day
- **Queries**: 1000 queries/day
- **Max document size**: 50MB
- **Concurrent requests**: 5

Limits are subject to change. Check dashboard for current quotas.

## Response Formats

All responses follow standard JSON format:

**Success Response:**
```json
{
  "status": "success",
  "data": { ... },
  "metadata": {
    "request_id": "req_xyz789",
    "timestamp": "2024-01-15T10:30:00Z",
    "processing_time_ms": 234
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  },
  "metadata": {
    "request_id": "req_xyz789",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Tree Structure Format

PageIndex trees follow hierarchical JSON structure:

```json
{
  "root": {
    "id": "node_0",
    "heading": "Document Title",
    "content": "Introduction paragraph...",
    "page_number": 1,
    "depth": 0,
    "children": [
      {
        "id": "node_1",
        "heading": "Chapter 1: Overview",
        "content": "Chapter content...",
        "page_number": 2,
        "depth": 1,
        "children": [
          {
            "id": "node_1_1",
            "heading": "1.1 Background",
            "content": "Section content...",
            "page_number": 3,
            "depth": 2,
            "children": []
          }
        ]
      }
    ]
  }
}
```

### Tree Node Properties

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique node identifier |
| `heading` | string | Section heading/title |
| `content` | string | Node text content |
| `page_number` | number | Exact page reference |
| `depth` | number | Tree depth (0=root) |
| `children` | array | Child nodes |
| `metadata` | object | Optional node metadata |

## Pagination

For large result sets, use pagination:

```
get_page_content(
  document_id: "doc_123",
  query: "...",
  options: {
    max_nodes: 20,
    offset: 0  // Start from first result
  }
)

// Next page:
get_page_content(
  document_id: "doc_123",
  query: "...",
  options: {
    max_nodes: 20,
    offset: 20  // Skip first 20 results
  }
)
```

## Caching

PageIndex caches:
- **Processed trees**: Indefinite (until deleted)
- **Query results**: 1 hour (repeated queries served from cache)

To clear cache for a document, delete and re-process.

## Best Practices

### API Usage

1. **Process once**: Document trees persist after processing
2. **Reuse document_ids**: Store IDs for frequently accessed documents
3. **Batch queries**: Group related queries to reduce API calls
4. **Handle errors gracefully**: Implement retry logic with exponential backoff
5. **Monitor rate limits**: Check response headers for quota status

### Query Optimization

1. **Be specific**: "Q3 revenue growth rate" better than "revenue"
2. **Use context**: "According to the risk factors section, what are..."
3. **Iterative refinement**: Start broad, narrow based on results
4. **Leverage tree paths**: Use parent_path to understand context

### Error Handling

```python
try:
    result = get_page_content(
        document_id="doc_123",
        query="What is the revenue?"
    )
except DocumentNotFoundError:
    # Re-process document
    pass
except ProcessingIncompleteError:
    # Wait and retry
    time.sleep(5)
    retry()
except NoResultsError:
    # Broaden query
    result = get_page_content(
        document_id="doc_123",
        query="revenue"  # Broader
    )
```

## Webhooks (Coming Soon)

Future webhook support for:
- Document processing completion
- Batch processing status
- Quota warnings

## Versioning

Current API version: `v1`

Version specified in API base URL:
- stdio mode: Automatic (latest)
- HTTP mode: `https://dash.pageindex.ai/api/v1/mcp/...`

Breaking changes will increment version number with backwards compatibility period.
