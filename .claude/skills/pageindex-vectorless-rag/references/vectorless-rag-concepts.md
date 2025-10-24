# Vectorless RAG Concepts: Deep Dive

Comprehensive guide to understanding reasoning-based retrieval using tree structures.

## Table of Contents

1. [The Problem with Vector-Based RAG](#the-problem-with-vector-based-rag)
2. [Tree-Based Reasoning Approach](#tree-based-reasoning-approach)
3. [How Tree Search Works](#how-tree-search-works)
4. [Comparison: Vectors vs Trees](#comparison-vectors-vs-trees)
5. [Architecture Details](#architecture-details)
6. [Use Case Analysis](#use-case-analysis)

---

## The Problem with Vector-Based RAG

### Traditional RAG Pipeline

```
Document → Chunk → Embed → Store in Vector DB → Query → Similarity Search → Retrieve
```

### Key Limitations

#### 1. Chunking Destroys Context

**The Problem:**
Documents are artificially split into fixed-size chunks (e.g., 512 tokens), breaking natural document structure.

**Example:**
```
Original document:
  Chapter 3: Revenue Analysis
    3.1 Q3 Revenue: $45M (up 23% YoY)
    3.2 Cost Structure: ...

After chunking:
  Chunk 47: "...Revenue Analysis\n  3.1 Q3 Revenue: $45M (up 23%..."
  Chunk 48: "...YoY)\n  3.2 Cost Structure: Operating expenses..."
```

**Result:**
- Context split across chunks
- Section headings separated from content
- Relationships lost

#### 2. Semantic Similarity ≠ Relevance

**The Problem:**
Vector similarity matches semantically similar text, not necessarily relevant information.

**Example Query:** "What were Q3 earnings?"

**Vector RAG might retrieve:**
- "Q2 earnings were strong" (semantically similar, wrong quarter)
- "Q3 predictions suggest..." (similar words, not actual data)
- "Historical Q3 performance..." (similar, but not current)

**Correct answer location:**
Section 3.1 under "Revenue Analysis" chapter - but may not rank highest by cosine similarity.

#### 3. No Reasoning Path

**The Problem:**
Vector search is black-box - no visibility into why chunks were retrieved.

**User asks:** "Why did you retrieve this information?"
**Vector RAG:** 🤷 "Cosine similarity score: 0.87"

**No ability to:**
- Trace retrieval logic
- Understand document navigation
- Verify reasoning process
- Debug incorrect retrievals

#### 4. Lost Document Structure

**The Problem:**
Hierarchical organization (chapters, sections, subsections) is flattened into independent chunks.

**Example:**
A legal contract:
```
Agreement
  ├─ Definitions
  ├─ Terms and Conditions
  │   ├─ Payment Terms
  │   ├─ Termination Clauses
  │   └─ Liability Limits
  └─ Signatures
```

**Vector RAG sees:**
- 47 independent chunks with no structural relationships
- No understanding that "Payment Terms" is under "Terms and Conditions"
- No ability to navigate hierarchically

#### 5. No Provenance

**The Problem:**
Retrieved chunks lack precise source attribution.

**Vector RAG result:**
"Revenue was $45M..."

**Questions:**
- What page is this from?
- What section?
- What's the broader context?

**Answer:** Unknown or requires additional processing.

---

## Tree-Based Reasoning Approach

### Core Philosophy

**Humans don't read documents by computing embeddings.**

They navigate hierarchically:
1. Check table of contents
2. Navigate to relevant chapter
3. Scan section headings
4. Read specific paragraphs
5. Verify page references

**PageIndex replicates this process algorithmically.**

### Tree Structure Representation

```
Financial Report Q3 2024 (Page 1)
│
├─ Executive Summary (Page 2)
│   ├─ Key Highlights (Page 2)
│   └─ Financial Overview (Page 3)
│
├─ Revenue Analysis (Page 5)
│   ├─ Q3 Revenue Breakdown (Page 5)
│   │   ├─ Product Revenue: $30M (Page 5)
│   │   └─ Service Revenue: $15M (Page 6)
│   │
│   └─ Year-over-Year Comparison (Page 7)
│       ├─ Revenue Growth: +23% (Page 7)
│       └─ Market Share Analysis (Page 8)
│
└─ Risk Factors (Page 15)
    ├─ Market Risks (Page 15)
    └─ Operational Risks (Page 17)
```

### Advantages

1. **Preserved Structure:** Natural document hierarchy maintained
2. **Page References:** Every node linked to exact page
3. **Contextual Relationships:** Parent-child relationships explicit
4. **Navigable:** Can traverse like table of contents

---

## How Tree Search Works

### Algorithm Overview

PageIndex uses **reasoning-based tree search** inspired by AlphaGo's Monte Carlo Tree Search (MCTS).

### Search Process

Given query: "What was Q3 revenue?"

**Step 1: Start at Root**
```
Current: Financial Report Q3 2024
Reasoning: Root node, check children for revenue-related sections
```

**Step 2: Evaluate Children**
```
Options:
- Executive Summary (may contain summary, check)
- Revenue Analysis (highly relevant, priority)
- Risk Factors (unlikely, deprioritize)

Decision: Navigate to "Revenue Analysis"
```

**Step 3: Descend Tree**
```
Current: Revenue Analysis
Children:
- Q3 Revenue Breakdown (directly relevant!)
- Year-over-Year Comparison (secondary)

Decision: Navigate to "Q3 Revenue Breakdown"
```

**Step 4: Extract Information**
```
Current: Q3 Revenue Breakdown (Page 5)
Content: "Total Q3 revenue: $45M
  - Product Revenue: $30M
  - Service Revenue: $15M"

Found answer! Page reference: 5
```

### Search Strategy Types

#### 1. LLM-Based Tree Search

**Approach:** Use LLM to reason about which branches to explore.

**Prompt Template:**
```
You are navigating a document tree to answer: "{query}"

Current node: "{current_heading}"
Children:
1. {child_1_heading}
2. {child_2_heading}
...

Which child node(s) are most likely to contain the answer?
Provide reasoning for your decision.
```

**Advantages:**
- Understands semantic relationships
- Can make complex inferences
- Adapts to query nuance

**Disadvantages:**
- Requires LLM calls (slower, more expensive)
- Non-deterministic

#### 2. Value-Based Tree Search

**Approach:** Compute relevance scores for each node and use value function to guide search.

**Scoring Function:**
```python
def relevance_score(node, query):
    heading_match = semantic_similarity(node.heading, query)
    content_match = semantic_similarity(node.content, query)
    depth_penalty = 0.1 * node.depth  # Prefer shallower nodes

    return (0.6 * heading_match +
            0.4 * content_match -
            depth_penalty)
```

**Advantages:**
- Faster than LLM-based
- Deterministic results
- Efficient for simple queries

**Disadvantages:**
- Less sophisticated reasoning
- May miss nuanced relationships

### Hybrid Approach (PageIndex Default)

Combines both strategies:
1. **Value-based** for initial pruning (eliminate obviously irrelevant branches)
2. **LLM-based** for complex decisions at promising nodes
3. **Backtracking** if chosen path yields no results

### Tree Search vs. Graph Search

**Why trees, not graphs?**

Documents have natural hierarchical structure:
- Chapters contain sections
- Sections contain subsections
- Subsections contain paragraphs

**Tree properties:**
- Single root (document title)
- Clear parent-child relationships
- No cycles
- Efficient traversal algorithms

**When graphs are better:**
- Cross-references between sections
- Non-hierarchical knowledge (Wikipedia)
- Entity relationships

PageIndex focuses on structured documents where trees excel.

---

## Comparison: Vectors vs Trees

### Side-by-Side Comparison

| Aspect | Vector-Based RAG | Tree-Based RAG (PageIndex) |
|--------|------------------|---------------------------|
| **Infrastructure** | Vector database required (Pinecone, Weaviate, Chroma) | Lightweight JSON files |
| **Storage** | High-dimensional vectors (~1536 dims) | Hierarchical text structures |
| **Retrieval Method** | Cosine similarity search | Multi-step reasoning + tree search |
| **Chunking** | Required (destroys structure) | Not required (preserves structure) |
| **Context Preservation** | Lost through chunking | Fully preserved in tree |
| **Provenance** | Chunk IDs, no page refs | Exact page numbers |
| **Reasoning Transparency** | Black box (similarity scores) | Explicit search path |
| **Query Complexity** | Simple semantic matching | Multi-step reasoning |
| **Setup Complexity** | High (vector DB, embedding model) | Low (JSON + tree search) |
| **Best For** | Unstructured text, large corpora | Structured documents, complex retrieval |

### Performance Comparison

**Query:** "What were the Q3 revenue growth drivers?"

**Vector RAG:**
1. Embed query → [0.123, -0.456, ...]
2. Similarity search → 10 chunks
3. Chunks may contain:
   - Q2 revenue (wrong quarter)
   - Revenue predictions (not actuals)
   - Partial context (split across chunks)
4. LLM synthesizes answer from noisy chunks
5. **Time:** ~2-3 seconds
6. **Accuracy:** Moderate (depends on chunk quality)

**Tree RAG (PageIndex):**
1. Start at root
2. Navigate: Revenue Analysis → Q3 Analysis → Growth Drivers
3. Retrieve entire "Growth Drivers" section with context
4. Page reference: Page 7
5. **Time:** ~1-2 seconds
6. **Accuracy:** High (structured navigation)

### Cost Comparison

**Vector RAG Costs:**
- Vector database hosting: $50-200/month
- Embedding API calls: $0.0001/1K tokens
- Storage: $0.25/GB/month (vectors are large)
- Compute: Similarity search at scale

**Tree RAG Costs:**
- Storage: Negligible (JSON files ~10% of vector size)
- API calls: PageIndex API (free during beta)
- Compute: Tree traversal (minimal)

**Example:** 1000 documents, 100K queries/month
- Vector RAG: ~$150-300/month
- Tree RAG: ~$0-50/month (beta pricing TBD)

---

## Architecture Details

### Component Breakdown

#### 1. PageIndex OCR

**Purpose:** Convert PDFs to structured markdown

**Process:**
```
PDF → Extract text → Parse structure → Generate markdown
```

**Output:**
```markdown
# Financial Report Q3 2024

## Executive Summary
Key highlights from Q3...

### Key Highlights
- Revenue: $45M
- Growth: +23% YoY

## Revenue Analysis
...
```

**Challenges Addressed:**
- Scanned PDFs → OCR extraction
- Complex layouts → Structure parsing
- Tables/images → Markdown conversion
- Page boundaries → Page reference tracking

#### 2. PageIndex Tree Generation

**Purpose:** Transform markdown into navigable tree structure

**Algorithm:**
```
1. Parse markdown headings (H1, H2, H3, etc.)
2. Build hierarchy based on heading levels
3. Assign content to appropriate nodes
4. Generate node IDs and metadata
5. Link page numbers to nodes
6. Create JSON tree representation
```

**Example Transformation:**

**Input (Markdown):**
```markdown
# Report
## Chapter 1
### Section 1.1
Content here...
### Section 1.2
More content...
## Chapter 2
...
```

**Output (Tree):**
```json
{
  "root": {
    "heading": "Report",
    "children": [
      {
        "heading": "Chapter 1",
        "children": [
          {"heading": "Section 1.1", "content": "Content here..."},
          {"heading": "Section 1.2", "content": "More content..."}
        ]
      },
      {
        "heading": "Chapter 2",
        "children": [...]
      }
    ]
  }
}
```

#### 3. PageIndex Retrieval

**Purpose:** Execute reasoning-based tree search to find relevant content

**Retrieval Algorithm:**

```python
def retrieve(tree, query):
    # Initialize search
    current_node = tree.root
    search_path = []
    retrieved_nodes = []

    # Tree search loop
    while True:
        search_path.append(current_node.heading)

        # Check if current node is relevant
        if is_relevant(current_node, query):
            retrieved_nodes.append(current_node)

        # Evaluate children
        if current_node.children:
            # Score children by relevance
            child_scores = [
                (child, relevance_score(child, query))
                for child in current_node.children
            ]

            # Sort by score
            child_scores.sort(key=lambda x: x[1], reverse=True)

            # Navigate to most promising child
            if child_scores[0][1] > threshold:
                current_node = child_scores[0][0]
            else:
                break  # No promising children
        else:
            break  # Leaf node reached

    return {
        "nodes": retrieved_nodes,
        "search_path": search_path
    }
```

**Key Features:**
- **Greedy search:** Follow most promising branch
- **Backtracking:** Return if dead end
- **Multi-node retrieval:** Collect all relevant nodes
- **Path tracking:** Record navigation for transparency

### Tree Search Optimizations

#### 1. Pruning

**Problem:** Large trees are slow to traverse

**Solution:** Prune obviously irrelevant branches early

```python
def should_prune(node, query):
    # Quick relevance check
    heading_contains_keywords = any(
        keyword in node.heading.lower()
        for keyword in extract_keywords(query)
    )

    if not heading_contains_keywords:
        # Skip entire subtree
        return True

    return False
```

#### 2. Caching

**Problem:** Repeated queries traverse same paths

**Solution:** Cache node relevance scores

```python
relevance_cache = {}

def cached_relevance_score(node, query):
    key = (node.id, query)
    if key not in relevance_cache:
        relevance_cache[key] = compute_relevance(node, query)
    return relevance_cache[key]
```

#### 3. Parallel Search

**Problem:** Deep trees require many sequential steps

**Solution:** Explore multiple branches in parallel

```python
def parallel_tree_search(root, query, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Search top-level branches in parallel
        futures = [
            executor.submit(search_subtree, child, query)
            for child in root.children
        ]

        results = [f.result() for f in futures]

    return merge_results(results)
```

---

## Use Case Analysis

### When to Use PageIndex (Tree-Based RAG)

#### ✅ Ideal Use Cases

**1. Structured Documents**
- Financial reports (10-K, 10-Q filings)
- Legal contracts and agreements
- Technical manuals and specifications
- Academic textbooks and papers
- Regulatory documents
- Medical literature

**Why:** These documents have clear hierarchical structure that trees preserve.

**2. High-Accuracy Requirements**
- Legal research (need exact citations)
- Medical diagnosis support (precision critical)
- Financial analysis (numbers must be accurate)
- Compliance checking (no room for error)

**Why:** Tree search provides exact page references and preserves context.

**3. Transparency Requirements**
- Auditable retrieval (must explain decisions)
- Research applications (need to cite sources)
- Regulated industries (must justify answers)

**Why:** Tree search path shows exactly how information was found.

**4. Complex Multi-Step Queries**
- "Compare Q3 revenue across all product lines and identify the largest growth driver"
- "What are the tax implications of the termination clause in section 5.3?"
- "Summarize all risk factors related to regulatory compliance"

**Why:** Tree search enables multi-step reasoning through document structure.

### When to Use Traditional Vector RAG

#### ✅ Vector RAG Strengths

**1. Unstructured Text**
- Social media posts
- Customer support tickets
- Chat logs and transcripts
- Blog articles without clear structure
- Email archives

**Why:** No hierarchical structure to preserve; semantic similarity is primary signal.

**2. Large Homogeneous Corpora**
- Wikipedia articles (millions of documents)
- News archives
- Research paper databases
- Web scraping results

**Why:** Vector databases excel at scaling to millions of documents.

**3. Fuzzy Semantic Matching**
- "Find discussions similar to this complaint"
- "What products are related to X?"
- "Show me analogous case studies"

**Why:** Vector similarity captures semantic relationships well.

**4. Cross-Document Concept Search**
- "All mentions of machine learning across 10,000 documents"
- "Find patterns in customer feedback over 5 years"

**Why:** Vector search efficiently finds concept matches across massive corpora.

### Hybrid Approach: Best of Both Worlds

**Use Case:** Enterprise document search across diverse document types

**Architecture:**
```
User Query
    ↓
Query Classifier
    ↓
┌────────────────┬────────────────┐
│ Structured?    │ Unstructured?  │
│ (Tree Search)  │ (Vector Search)│
└────────────────┴────────────────┘
    ↓                    ↓
PageIndex            Vector DB
    ↓                    ↓
    └─────→ Merge Results ←──────┘
```

**Decision Logic:**
```python
def route_query(query, document):
    if document.has_structure() and query.needs_precision():
        return tree_search(document, query)
    elif document.is_unstructured() or query.is_exploratory():
        return vector_search(document, query)
    else:
        # Use both, merge results
        tree_results = tree_search(document, query)
        vector_results = vector_search(document, query)
        return merge_and_rank(tree_results, vector_results)
```

### Decision Matrix

| Document Type | Query Type | Recommended Approach |
|--------------|------------|---------------------|
| Financial report | "What was Q3 revenue?" | Tree (PageIndex) |
| Financial report | "What are revenue-related risks?" | Tree (PageIndex) |
| Legal contract | "Summarize termination clause" | Tree (PageIndex) |
| Technical manual | "How to configure feature X?" | Tree (PageIndex) |
| Social media | "Find posts about product X" | Vector |
| News archive | "Articles similar to this one" | Vector |
| Research papers | "Papers about transformer architectures" | Vector |
| Mixed corpus | "Find compliance mentions" | Hybrid |
| Wiki + manuals | "How does X work?" | Hybrid |

---

## Future Directions

### Tree RAG Innovations

**1. Dynamic Tree Refinement**
- Update trees as documents change
- Incremental re-processing
- Version control for tree structures

**2. Cross-Document Tree Linking**
- Link related sections across documents
- Build meta-trees spanning multiple documents
- Graph-based connections within tree structure

**3. Learned Tree Search**
- Train models to optimize search strategy
- Learn document-specific navigation patterns
- Adaptive search based on query types

**4. Multimodal Trees**
- Incorporate images, tables, charts as tree nodes
- Visual reasoning through tree search
- Cross-modal retrieval (text query → image result)

### Convergence: Trees + Vectors

**Complementary Strengths:**
- Trees for structured navigation
- Vectors for semantic similarity
- Combine for comprehensive retrieval

**Research Questions:**
- How to optimally blend tree and vector search?
- When to use which approach?
- Can we learn to route queries automatically?

The future of RAG is not "vectors OR trees" but "vectors AND trees" - using the right tool for each retrieval challenge.
