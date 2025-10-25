# DeepSeek-OCR Summary

**Release:** October 2025
**License:** MIT (open-source)
**Repository:** github.com/deepseek-ai/DeepSeek-OCR
**Paper:** arXiv:2510.18234

## What Makes It Special

DeepSeek-OCR introduces **"contexts optical compression"** - a novel paradigm that treats document pages like zip files. Instead of converting images to text tokens, it compresses pages into compact **vision tokens** that preserve layout, spacing, and structure.

### Key Innovation: Token Efficiency
- Traditional OCR: 2000-5000 text tokens per page
- DeepSeek-OCR: 200-400 vision tokens per page
- **10-20x compression** with controllable quality trade-offs

Vision tokens capture 2D information (layout, word shapes, spacing) far more densely than text tokens, enabling:
- Longer documents in LLM context windows
- Lower processing costs
- Faster throughput (~2500 tokens/s on A100-40G)

## Architecture

```
Input Image → DeepEncoder → Vision Tokens → MoE Decoder → Text/Markdown
```

### DeepEncoder (~380M params)
1. **SAM-base** (80M): Windowed attention for local detail
2. **16x convolution**: Reduces tokens (e.g., 4096 → 256)
3. **CLIP-large** (300M): Global attention for layout

### Decoder: DeepSeek-3B-MoE-A570M
- **3B total params, 570M active** (6 of 64 experts per token)
- Trained on diverse OCR data: text, math, charts, chemical diagrams, multi-language

## Multi-Resolution Modes

| Mode | Resolution | Vision Tokens | Use Case |
|------|-----------|---------------|----------|
| Tiny | 512×512 | ~64 | Quick scans, simple docs |
| Small | 640×640 | ~100 | Balanced (default) |
| Base | 1024×1024 | ~256 | High-quality OCR |
| Large | 1280×1280 | ~400 | Dense layouts |
| Gundam | n×640×640 + 1×1024×1024 | Variable | Dynamic tiling for complex docs |

## Compression vs Quality Trade-offs

| Compression Ratio | OCR Precision | Use Case |
|------------------|---------------|----------|
| <10x | ~97% | High-fidelity extraction |
| ~20x | ~60% | Search/summarization where approximation OK |

**Insight:** Adjustable compression lets you dial cost vs accuracy based on task requirements.

## Benchmarks (Author-Reported)

### OmniDocBench
- Beats GOT-OCR2.0 (256 tokens/page) using **only 100 vision tokens**

### MinerU2.0 Comparison
- MinerU2.0: 6000+ tokens/page
- DeepSeek-OCR: <800 vision tokens/page
- Better accuracy with 87% fewer tokens

### Throughput
- **200,000+ pages/day** on single A100-40G (data generation)
- ~2500 tokens/s concurrency for PDF processing

## Capabilities

### OCR 2.0 with "Deep Parsing"
- Extracts text from documents
- Parses nested images within documents via secondary model calls
- Preserves layout structure (headings, lists, tables)

### Supported Tasks
```python
# Document to markdown
"<image>\n<|grounding|>Convert the document to markdown."

# Free OCR (no layout)
"<image>\nFree OCR."

# Figure parsing
"<image>\nParse the figure."

# General description
"<image>\nDescribe this image in detail."

# Grounded recognition
"<image>\nLocate <|ref|>text<|/ref|> in the image."
```

### Multi-Language & Handwritten
- Supports multiple languages
- Handles handwritten notes

## Technical Requirements

### Environment
- **CUDA 11.8+** (NVIDIA only, no Apple M-series support)
- PyTorch 2.6.0
- FlashAttention 2.x
- vLLM 0.8.5+ or Transformers 4.46.3+

### Hardware
- A100-40G recommended
- Works on consumer GPUs with reduced batch sizes

### Installation
```bash
pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu118
pip install flash-attn==2.7.3 --no-build-isolation
pip install transformers==4.46.3 accelerate safetensors addict
```

## Usage Examples

### vLLM (Recommended)
```python
from vllm import LLM, SamplingParams
from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
from PIL import Image

llm = LLM(
    model="deepseek-ai/DeepSeek-OCR",
    enable_prefix_caching=False,
    mm_processor_cache_gb=0,
    logits_processors=[NGramPerReqLogitsProcessor]
)

image = Image.open("doc.png").convert("RGB")
prompt = "<image>\nFree OCR."

sampling_param = SamplingParams(
    temperature=0.0,
    max_tokens=8192,
    extra_args=dict(
        ngram_size=30,
        window_size=90,
        whitelist_token_ids={128821, 128822}  # <td>, </td>
    )
)

outputs = llm.generate([{"prompt": prompt, "multi_modal_data": {"image": image}}], sampling_param)
print(outputs[0].outputs[0].text)
```

### Transformers
```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained("deepseek-ai/DeepSeek-OCR", trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-OCR", trust_remote_code=True)

model = model.eval().cuda().to(torch.bfloat16)

res = model.infer(
    tokenizer,
    prompt="<image>\n<|grounding|>Convert the document to markdown.",
    image_file="doc.jpg",
    base_size=1024,
    image_size=640,
    crop_mode=True
)
```

## Practical Workflow

1. **Preprocess:** Convert PDF to per-page PNGs (200-300 DPI)
2. **Prompt:** Pass image + instruction (e.g., "Convert to markdown")
3. **Post-process:** Concatenate pages, clean repeated headers/footers
4. **Validate:** Sample pages at different compressions to measure precision/recall

**Note:** Direct PDF input reported unstable (GitHub issue #33) - image-per-page workaround recommended.

## Strengths

1. **Token efficiency:** 10-20x compression enables longer contexts at lower cost
2. **Layout preservation:** Vision tokens maintain 2D structure better than text
3. **Production throughput:** 200k+ pages/day on single GPU
4. **Open-source:** MIT license, weights available, vLLM integration
5. **Flexible compression:** Dial quality vs cost based on use case

## Limitations

1. **Lossy at high compression:** 20x ratio drops to 60% accuracy
2. **Complex layouts:** Heavy tables, math, or idiosyncratic formatting may need lower compression
3. **PDF input instability:** Requires image conversion workaround
4. **Environment friction:** Setup issues reported, CUDA-only (no Apple Silicon)
5. **Not general-purpose VLM:** Optimized for OCR, not reasoning or complex visual understanding

## When to Use DeepSeek-OCR

**Good fit:**
- Long documents where context window is bottleneck
- Cost-sensitive pipelines processing thousands of pages
- Tasks tolerating some approximation (search, summarization)
- Structured documents (reports, invoices, forms)

**Not ideal for:**
- Exact transcription of complex math/chemical notation
- Heavy diagrams requiring visual reasoning
- Real-time interactive applications (setup overhead)
- Non-NVIDIA hardware environments

## Related Systems

- **GOT-OCR2.0:** 256 tokens/page, less compression
- **MinerU2.0:** 6000+ tokens/page, higher fidelity but expensive
- **PaddleOCR:** Traditional OCR without vision-language integration
- **Vary, OneChart, Slow Perception:** Inspiration for architecture

## Citations

```bibtex
@article{wei2025deepseek,
  title={DeepSeek-OCR: Contexts Optical Compression},
  author={Wei, Haoran and Sun, Yaofeng and Li, Yukun},
  journal={arXiv preprint arXiv:2510.18234},
  year={2025}
}
```

## Resources

- **GitHub:** https://github.com/deepseek-ai/DeepSeek-OCR
- **Paper:** https://arxiv.org/abs/2510.18234
- **Model:** https://huggingface.co/deepseek-ai/DeepSeek-OCR
- **vLLM docs:** https://wheels.vllm.ai/nightly

---

**Last Updated:** October 2025
**Status:** Active development, vLLM integration complete
