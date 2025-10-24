# PageIndex Python SDK Reference

Complete API reference for PageIndex Python client library.

## Installation

```bash
pip install pageindex
```

## Client Initialization

```python
from pageindex import PageIndex

# Basic initialization
client = PageIndex(api_key="your-api-key")

# Custom endpoint
client = PageIndex(
    api_key="your-api-key",
    base_url="https://custom.endpoint.com"
)
```

## Document Management

### add_document()

Index document for retrieval.

```python
client.add_document(
    document_id: str,          # Unique document identifier
    content: str,              # Document text content
    metadata: dict = None      # Optional metadata
) -> dict
```

**Parameters:**
- `document_id`: Unique identifier for the document
- `content`: Full text content to index
- `metadata`: Optional dict with custom fields

**Returns:** Dict with indexing status

**Example:**
```python
result = client.add_document(
    document_id="report-2024",
    content="Annual financial report...",
    metadata={"year": 2024, "type": "financial"}
)
```

### delete_document()

Remove document from index.

```python
client.delete_document(document_id: str) -> dict
```

**Parameters:**
- `document_id`: ID of document to delete

**Returns:** Dict with deletion status

### list_documents()

Get all indexed documents.

```python
client.list_documents(
    limit: int = 100,
    offset: int = 0
) -> list[dict]
```

**Parameters:**
- `limit`: Max number of results (default: 100)
- `offset`: Pagination offset (default: 0)

**Returns:** List of document metadata dicts

## Query and Retrieval

### search()

Semantic search across indexed documents.

```python
client.search(
    query: str,                      # Search query
    top_k: int = 5,                  # Number of results
    filter_metadata: dict = None,    # Metadata filters
    include_content: bool = True     # Include full content
) -> list[dict]
```

**Parameters:**
- `query`: Natural language search query
- `top_k`: Number of top results to return (default: 5)
- `filter_metadata`: Dict of metadata filters to apply
- `include_content`: Whether to include full document content

**Returns:** List of matching documents with scores

**Example:**
```python
results = client.search(
    query="What were the revenue figures?",
    top_k=3,
    filter_metadata={"year": 2024}
)

for result in results:
    print(f"Score: {result['score']}")
    print(f"Content: {result['content']}")
```

### get_page_content()

Retrieve specific page from indexed document.

```python
client.get_page_content(
    document_id: str,
    page_number: int
) -> dict
```

**Parameters:**
- `document_id`: Document identifier
- `page_number`: Page number to retrieve (1-indexed)

**Returns:** Dict with page content and metadata

**Example:**
```python
page = client.get_page_content(
    document_id="report-2024",
    page_number=5
)
print(page['content'])
```

## RAG Operations

### ask()

Ask question against indexed documents (RAG query).

```python
client.ask(
    question: str,                   # User question
    document_ids: list[str] = None,  # Specific docs to search
    context_pages: int = 3,          # Pages of context
    filter_metadata: dict = None     # Metadata filters
) -> dict
```

**Parameters:**
- `question`: Natural language question
- `document_ids`: Optional list of specific documents to query
- `context_pages`: Number of relevant pages to retrieve (default: 3)
- `filter_metadata`: Optional metadata filters

**Returns:** Dict with answer, sources, and reasoning

**Example:**
```python
response = client.ask(
    question="What was the total revenue in Q4?",
    document_ids=["report-2024"],
    context_pages=5
)

print(f"Answer: {response['answer']}")
print(f"Sources: {response['sources']}")
```

## Response Objects

### Search Result

```python
{
    "document_id": str,
    "score": float,          # Relevance score (0-1)
    "content": str,          # Document content
    "metadata": dict,        # Document metadata
    "page_number": int       # Source page number
}
```

### Ask Response

```python
{
    "answer": str,           # Generated answer
    "sources": list[dict],   # Source documents/pages
    "reasoning": str,        # Explanation of reasoning
    "confidence": float      # Confidence score (0-1)
}
```

### Page Content

```python
{
    "document_id": str,
    "page_number": int,
    "content": str,
    "metadata": dict
}
```

## Error Handling

```python
from pageindex import PageIndexError, AuthenticationError, NotFoundError

try:
    result = client.search(query="example")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
except NotFoundError as e:
    print(f"Document not found: {e}")
except PageIndexError as e:
    print(f"General error: {e}")
```

### Exception Types

- `PageIndexError`: Base exception class
- `AuthenticationError`: Invalid API key
- `NotFoundError`: Document not found
- `RateLimitError`: Rate limit exceeded
- `ValidationError`: Invalid parameters

## Best Practices

### Document Chunking

For large documents, split into logical chunks:

```python
# Split by sections/chapters
sections = extract_sections(document)
for i, section in enumerate(sections):
    client.add_document(
        document_id=f"doc_{doc_id}_section_{i}",
        content=section,
        metadata={"parent_doc": doc_id, "section": i}
    )
```

### Metadata Indexing

Use metadata for efficient filtering:

```python
client.add_document(
    document_id="report",
    content=content,
    metadata={
        "year": 2024,
        "department": "finance",
        "confidential": False,
        "tags": ["quarterly", "revenue"]
    }
)

# Filter queries
results = client.search(
    query="revenue growth",
    filter_metadata={"year": 2024, "confidential": False}
)
```

### Pagination

Handle large result sets:

```python
def get_all_documents(client):
    offset = 0
    limit = 100
    all_docs = []

    while True:
        batch = client.list_documents(limit=limit, offset=offset)
        if not batch:
            break
        all_docs.extend(batch)
        offset += limit

    return all_docs
```

### Retry Logic

Implement retries for transient failures:

```python
from time import sleep

def search_with_retry(client, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.search(query)
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            sleep(2 ** attempt)  # Exponential backoff
```

## Configuration

### Environment Variables

```bash
export PAGEINDEX_API_KEY="your-api-key"
export PAGEINDEX_BASE_URL="https://api.pageindex.ai"
export PAGEINDEX_TIMEOUT=30
```

Load in code:

```python
import os
from pageindex import PageIndex

client = PageIndex(
    api_key=os.getenv("PAGEINDEX_API_KEY"),
    base_url=os.getenv("PAGEINDEX_BASE_URL"),
    timeout=int(os.getenv("PAGEINDEX_TIMEOUT", 30))
)
```

## Rate Limits

Default limits:
- 100 requests/minute for search/ask
- 50 requests/minute for document operations
- 10 MB max document size
- 1000 documents per index (free tier)

Handle rate limits:

```python
from pageindex import RateLimitError

try:
    results = client.search(query)
except RateLimitError as e:
    retry_after = e.retry_after  # Seconds to wait
    print(f"Rate limited. Retry after {retry_after}s")
```

## Async Support

```python
from pageindex import AsyncPageIndex

async def async_search():
    client = AsyncPageIndex(api_key="your-api-key")

    results = await client.search(query="example")

    # Concurrent searches
    queries = ["query1", "query2", "query3"]
    results = await asyncio.gather(*[
        client.search(q) for q in queries
    ])

    return results
```

## Logging

Enable debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pageindex")

client = PageIndex(
    api_key="your-api-key",
    logger=logger
)
```

## Testing

Mock client for testing:

```python
from unittest.mock import Mock
from pageindex import PageIndex

def test_search():
    mock_client = Mock(spec=PageIndex)
    mock_client.search.return_value = [
        {"document_id": "test", "score": 0.9, "content": "..."}
    ]

    results = mock_client.search("test query")
    assert len(results) == 1
    assert results[0]["score"] == 0.9
```

## Migration Guide

### From vector databases

Replace Pinecone/Weaviate:

```python
# Before (Pinecone)
index = pinecone.Index("my-index")
index.upsert(vectors=[(id, embedding, metadata)])
results = index.query(vector=query_embedding, top_k=5)

# After (PageIndex)
client = PageIndex(api_key=key)
client.add_document(document_id=id, content=content, metadata=metadata)
results = client.search(query=query_text, top_k=5)
```

No embedding generation needed - PageIndex handles it internally.

## Support

- Documentation: https://docs.pageindex.ai
- GitHub: https://github.com/PageIndexAI/pageindex-python
- Email: support@pageindex.ai
