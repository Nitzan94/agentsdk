---
name: pageindex-vectorless-rag
description: Build vectorless RAG (Retrieval Augmented Generation) systems using PageIndex's reasoning-based tree search approach. This skill should be used when working with complex documents (financial reports, legal documents, technical manuals, academic papers) that require deep understanding without vector databases or artificial chunking. Use when implementing RAG systems that need transparent, traceable retrieval with exact page references.
---

# PageIndex Vectorless RAG

Build reasoning-based RAG systems that navigate documents like human experts using hierarchical tree structures and multi-step reasoning instead of vector similarity search.

## Overview

PageIndex transforms documents into hierarchical tree structures and uses reasoning-based tree search to retrieve information, eliminating the need for vector databases and preserving natural document structure.

### Core Differences from Traditional RAG

**Traditional Vector-Based RAG:**
- Requires vector database infrastructure
- Relies on semantic similarity matching
- Requires artificial text chunking
- Black-box retrieval process
- No page references

**PageIndex Vectorless RAG:**
- Lightweight JSON tree structures
- Multi-step reasoning and tree search
- Preserves natural document structure
- Transparent, traceable reasoning paths
- Exact page references for every node

## When to Use This Skill

Use PageIndex for:
- Complex, structured documents (financial reports, regulatory filings, legal contracts)
- Academic textbooks and research papers
- Technical manuals and documentation
- Scenarios requiring traceable retrieval paths
- Applications where exact page references are critical
- RAG systems without vector database infrastructure

## PageIndex Architecture

### Three Core Components

**1. PageIndex OCR**
Converts PDFs to markdown while preserving global document structure, preparing documents for tree generation.

**2. PageIndex Tree Generation**
Transforms documents into semantic tree structures optimized for LLM navigation. Creates hierarchical "table of contents" representation enabling reasoning-based traversal.

**3. PageIndex Retrieval**
Extracts relevant context using LLM-based tree search and value-based tree search algorithms. Given a query and tree, performs tree search to identify most relevant nodes, returning:
- Relevant tree nodes
- Associated paragraphs
- Tree search trajectories
- Exact page references

### Key Features

- **No Vector Database**: Trees stored as lightweight JSON objects
- **No Chunking**: Preserves natural document structure
- **Transparent Retrieval**: Visible tree search reasoning process
- **Automatic Node Selection**: No manual parameter tuning
- **Page References**: Every retrieved node includes exact page number

## Setup

### Installation

Install the PageIndex Python SDK:

```bash
pip install pageindex
```

Or using uv:

```bash
uv add pageindex
```

### Authentication

Initialize the client with API key:

```python
from pageindex import PageIndexClient

pi_client = PageIndexClient(api_key="YOUR_API_KEY")
```

### Getting API Key

1. Visit https://dash.pageindex.ai
2. Sign up for free beta access
3. Generate API key from dashboard
4. Store in environment variable or pass directly to client

## Workflow

### 1. Submit Document

Submit PDF for processing using `submit_document()`:

```python
result = pi_client.submit_document("./financial_report_q3.pdf")
doc_id = result["doc_id"]
```

Processing pipeline:
- Extracts text via OCR
- Generates hierarchical tree structure
- Creates semantic node representations
- Indexes for reasoning-based retrieval

### 2. Check OCR Status

Monitor OCR processing and retrieve results:

```python
ocr_result = pi_client.get_ocr(doc_id, format="node")
if ocr_result.get("status") == "completed":
    # OCR complete, proceed to tree generation
    print("OCR completed successfully")
```

**Format options:**
- `"page"` - Results organized by page with markdown and images
- `"node"` - Hierarchical structure preserving document layout
- `"raw"` - Concatenated markdown as single string

### 3. Generate Tree Structure

Check tree generation status:

```python
tree_result = pi_client.get_tree(doc_id, node_summary=True)
if tree_result.get("status") == "completed":
    tree = tree_result.get("result")
    # Tree ready for retrieval
```

Setting `node_summary=True` includes summary for each node in response.

### 4. Query Documents

Check retrieval readiness and submit queries:

```python
if pi_client.is_retrieval_ready(doc_id):
    retrieval = pi_client.submit_retrieval_query(
        doc_id=doc_id,
        query="What are the main risk factors?",
        thinking=False  # Set True for deeper retrieval
    )
    retrieval_id = retrieval["retrieval_id"]
```

**Query Strategy:**
- Frame queries as specific questions
- Leverage tree structure for multi-step reasoning
- Use `thinking=True` for comprehensive results
- Verify using page references

**Example queries:**
- "What is the total revenue reported in Q3?"
- "Summarize the risk factors section"
- "Find all mentions of regulatory compliance requirements"

### 5. Retrieve Results

Get retrieval results:

```python
retrieval_result = pi_client.get_retrieval_result(retrieval_id)
if retrieval_result.get("status") == "completed":
    nodes = retrieval_result.get("retrieved_nodes")
    for node in nodes:
        print(f"Title: {node['title']}")
        print(f"Node ID: {node['node_id']}")
        for content in node['relevant_contents']:
            print(f"Page: {content['page_index']}")
            print(f"Content: {content['relevant_content']}")
```

Results include:
- **Retrieved nodes**: Tree nodes matching the query
- **Page references**: Exact page numbers for verification
- **Relevant contents**: Actual text from matched sections

### 6. Iterate and Refine

For complex information needs:
- Start with broad queries to understand document structure
- Use tree node hierarchy to identify promising sections
- Drill down with specific follow-up queries
- Combine information from multiple nodes
- Use `thinking=True` for complex multi-step reasoning

## SDK Methods Reference

### submit_document(file_path)
Submit PDF for OCR and tree processing.

**Parameters:**
- `file_path` (string, required) - Local path to PDF file

**Returns:** `{"doc_id": "..."}`

### get_ocr(doc_id, format="page")
Check OCR status and retrieve results.

**Parameters:**
- `doc_id` (string, required) - Document identifier
- `format` (string, optional) - Output format: "page", "node", or "raw"

**Returns:** Status dict with OCR result when completed

### get_tree(doc_id, node_summary=False)
Check tree generation status and retrieve tree structure.

**Parameters:**
- `doc_id` (string, required) - Document identifier
- `node_summary` (boolean, optional) - Include node summaries

**Returns:** Status dict with tree structure when completed

### is_retrieval_ready(doc_id)
Check if document is ready for retrieval.

**Parameters:**
- `doc_id` (string, required) - Document identifier

**Returns:** Boolean indicating readiness

### submit_retrieval_query(doc_id, query, thinking=False)
Submit query for retrieval.

**Parameters:**
- `doc_id` (string, required) - Document identifier
- `query` (string, required) - Natural language query
- `thinking` (boolean, optional) - Enable deeper retrieval

**Returns:** `{"retrieval_id": "..."}`

### get_retrieval_result(retrieval_id)
Get retrieval results.

**Parameters:**
- `retrieval_id` (string, required) - Retrieval task identifier

**Returns:** Status dict with retrieved nodes when completed

### delete_document(doc_id)
Permanently delete document and all associated data.

**Parameters:**
- `doc_id` (string, required) - Document identifier

**Returns:** None

## Best Practices

### Document Processing

- **Process once, query many**: Tree generation is one-time per document
- **Structure matters**: Well-structured documents (headings, sections) produce better trees
- **Version control**: Track document IDs for reproducibility

### Querying

- **Be specific**: Precise queries enable targeted tree search
- **Multi-step reasoning**: Complex questions benefit from PageIndex's reasoning approach
- **Use page references**: Always verify critical information via page numbers
- **Iterative refinement**: Start broad, then narrow based on initial results

### Error Handling

- **Invalid documents**: Ensure PDFs are text-based (not scanned images without OCR)
- **API limits**: Respect rate limits during beta (check dashboard)
- **Missing content**: If retrieval fails, try broader queries or check document quality

### Performance Optimization

- **Batch processing**: Process multiple documents upfront
- **Cache document IDs**: Store IDs for frequently accessed documents
- **Query efficiency**: Specific queries reduce unnecessary tree traversal

## Comparison: When to Choose PageIndex

**Choose PageIndex when:**
- Document structure is important (hierarchical, well-organized)
- Exact page references are required
- Transparency in retrieval is needed
- Infrastructure should be minimal (no vector DB)
- Working with regulatory/legal documents requiring citations

**Choose Traditional Vector RAG when:**
- Documents lack clear structure
- Semantic similarity is primary concern
- Working with unstructured text (social media, chat logs)
- Need to search across very large, homogeneous corpora

## Troubleshooting

### Common Issues

**"Document processing failed"**
- Verify PDF is not corrupted
- Check file size limits
- Ensure PDF contains extractable text

**"No results found"**
- Try broader query terms
- Check document was fully processed
- Verify document ID is correct

**"API key invalid"**
- Regenerate key from dashboard
- Check environment variable is set correctly
- Verify no extra spaces in key

### Getting Help

- Documentation: https://docs.pageindex.ai
- Python SDK: https://pypi.org/project/pageindex/
- GitHub: https://github.com/VectifyAI/PageIndex
- Discord: https://discord.gg/VuXuf29EUj

## Advanced Usage

For detailed API documentation, tree structure internals, and advanced retrieval strategies, see:
- `references/pageindex-api.md` - Complete API reference
- `references/vectorless-rag-concepts.md` - Deep dive into tree-based reasoning
- `assets/config-examples.md` - Additional configuration patterns

## Example Workflow

Complete example processing and querying a financial report:

```python
from pageindex import PageIndexClient

# Initialize client
pi_client = PageIndexClient(api_key="YOUR_API_KEY")

# 1. Submit document
result = pi_client.submit_document("./financial_report_q3.pdf")
doc_id = result["doc_id"]

# 2. Wait for OCR completion
ocr_result = pi_client.get_ocr(doc_id)
while ocr_result.get("status") == "processing":
    time.sleep(5)
    ocr_result = pi_client.get_ocr(doc_id)

# 3. Wait for tree generation
tree_result = pi_client.get_tree(doc_id, node_summary=True)
while tree_result.get("status") == "processing":
    time.sleep(5)
    tree_result = pi_client.get_tree(doc_id)

# 4. Query the document
if pi_client.is_retrieval_ready(doc_id):
    # Submit query
    retrieval = pi_client.submit_retrieval_query(
        doc_id=doc_id,
        query="What was the net income for Q3?",
        thinking=False
    )

    # Get results
    retrieval_result = pi_client.get_retrieval_result(retrieval["retrieval_id"])
    while retrieval_result.get("status") == "processing":
        time.sleep(2)
        retrieval_result = pi_client.get_retrieval_result(retrieval["retrieval_id"])

    # Display results
    for node in retrieval_result.get("retrieved_nodes", []):
        print(f"Section: {node['title']}")
        for content in node['relevant_contents']:
            print(f"Page {content['page_index']}: {content['relevant_content']}")
```

## Integration Patterns

### Standalone Python Application
Use SDK directly in Python scripts, notebooks, or applications.

### FastAPI/Flask Backend
Integrate PageIndex as document processing service in web applications.

### Batch Processing Pipeline
Process multiple documents in batch jobs with result caching.

### Interactive Analysis
Use in Jupyter notebooks for document exploration and analysis.
