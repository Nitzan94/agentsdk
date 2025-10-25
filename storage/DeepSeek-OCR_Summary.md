# DeepSeek-OCR Summary

**Released:** October 20, 2025
**Developer:** DeepSeek-AI (China)

## What Makes It Special

DeepSeek-OCR revolutionizes text processing by **compressing text 10x while retaining 97% accuracy** through converting text to images - counterintuitively more efficient than processing digital text.

## Key Innovations

### Compression Efficiency
- 10x text compression maintaining 97% fidelity
- Processes text as images using less compute than digital text
- Drastically reduces token count for LLMs

### Resolution Modes
- **Tiny:** 512×512, 64 tokens - quick previews, low-resource
- **Small:** 640×640, 100 tokens - books, reports
- **Base:** 1024×1024, 256 tokens - standard documents
- **Large:** 1280×1280, 400 tokens - detailed extraction
- **Gundam (dynamic):** Combines segments for ultra-high-resolution docs (up to 800 tokens)

### Grounding Capabilities
- Spatial location referencing with tags: `<|ref|>xxxx<|/ref|>`
- Precise element location for AR/interactive documents

## Architecture

**DeepEncoder** (380M parameters)
- SAM-ViTDet (80M) for image segmentation
- CLIP ViT-300M for image-text linking
- 16x token compressor: 4,096 → 256 tokens

**Text Generator**
- DeepSeek3B-MoE (570M active parameters)

## Performance Benchmarks

### vs Competitors
- Beats GOT-OCR 2.0: 100 tokens vs 256
- Beats MinerU 2.0: <800 tokens vs 6,000+ per page

### Throughput
- 2,500 tokens/sec on A100-40G GPU
- 200,000+ pages/day on single A100
- **33M pages/day** with 20 servers (8× A100 each)

## Capabilities

### Document Processing
- Image → text conversion
- Markdown output (preserves tables, lists, structure)
- Chart/figure parsing with data extraction
- Chemical formulas, geometric figures
- Handwritten text, distorted images
- ~100 languages

### Advanced Features
- General image description and captioning
- Preserves original formatting
- Location-based queries

## Training Data

- 30M PDF pages in ~100 languages
- 25M in Chinese/English
- 10M synthetic diagrams
- 5M chemical formulas
- 1M geometric figures

## Use Cases

1. **Document automation** - bulk conversion, extraction
2. **Chatbot memory compression** - store old conversations at lower resolution (mimics human memory fade)
3. **Training dataset generation** - extract text from massive document collections
4. **Accessibility tools** - image captioning, descriptions
5. **Interactive documents** - AR, spatial referencing
6. **Complex content** - financial charts → structured data/Markdown tables

## Availability

- **Open source**: Code and model weights on GitHub/HuggingFace
- Integrates with vLLM, Transformers
- Lightweight, minimal dependencies

## Why It Matters

1. **Paradigm shift**: Images can be more efficient than digital text for LLMs
2. **Context length breakthrough**: 10x compression enables much longer documents without memory limits
3. **Production-ready**: Industrial throughput (33M pages/day)
4. **Benchmark leader**: Best accuracy with fraction of tokens
5. **Flexible scaling**: Adapts from low-resource to high-detail tasks

---

**Sources:**
- https://apidog.com/blog/deepseek-ocr/
- https://the-decoder.com/deepseeks-ocr-system-compresses-image-based-text-so-ai-can-handle-much-longer-documents/
