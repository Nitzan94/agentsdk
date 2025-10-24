---
name: markitdown
description: Convert various file formats (PDF, DOCX, PPTX, XLSX, images, audio, HTML, ZIP, EPub, and more) to clean, structured Markdown optimized for LLM consumption and text analysis. Use when processing uploaded documents, extracting content from office files, converting media to text, or preparing files for analysis. Handles multimodal content with OCR for images and speech transcription for audio.
license: MIT (Microsoft MarkItDown)
---

# MarkItDown - Universal Document to Markdown Converter

MarkItDown is Microsoft's lightweight Python utility for converting various file formats into clean, structured Markdown optimized for LLM consumption and text analysis. It preserves document structure (headings, lists, tables, links) while maintaining high token efficiency.

## Supported File Formats

- **Office Documents**: DOCX, PPTX, XLSX, XLS
- **PDFs**: Text-based PDFs (OCR preprocessing required for image-based PDFs)
- **Images**: JPG, JPEG, PNG, GIF, WEBP (with EXIF metadata and optional LLM-powered descriptions)
- **Audio**: WAV, MP3 (with EXIF metadata and speech transcription)
- **Web**: HTML, URLs
- **Structured Data**: CSV, JSON, XML
- **Archives**: ZIP files (processes contents recursively)
- **E-books**: EPub
- **Email**: Outlook messages (with [outlook] dependency)
- **YouTube**: Video URLs (with [youtube-transcription] dependency)

## Installation

**Critical**: Always install with the `--break-system-packages` flag in this environment:

```bash
pip install 'markitdown[all]' --break-system-packages
```

### Optional Dependencies

For targeted installations, use specific feature groups:

```bash
# Minimal installation (only specific formats)
pip install 'markitdown[pdf,docx,pptx]' --break-system-packages

# Individual features
pip install 'markitdown[pptx]' --break-system-packages    # PowerPoint
pip install 'markitdown[docx]' --break-system-packages    # Word
pip install 'markitdown[xlsx]' --break-system-packages    # Excel (modern)
pip install 'markitdown[xls]' --break-system-packages     # Excel (legacy)
pip install 'markitdown[pdf]' --break-system-packages     # PDF
pip install 'markitdown[outlook]' --break-system-packages # Email
pip install 'markitdown[az-doc-intel]' --break-system-packages  # Azure Document Intelligence
pip install 'markitdown[audio-transcription]' --break-system-packages  # Audio files
pip install 'markitdown[youtube-transcription]' --break-system-packages  # YouTube
```

## Core Usage Patterns

### Pattern 1: Basic File Conversion (Most Common)

For files in `/mnt/user-data/uploads`:

```python
from markitdown import MarkItDown

# Initialize converter
md = MarkItDown()

# Convert file
result = md.convert("/mnt/user-data/uploads/document.pdf")

# Access markdown content
markdown_text = result.text_content

# Save to outputs for user access
with open("/mnt/user-data/outputs/document.md", "w", encoding="utf-8") as f:
    f.write(markdown_text)
```

### Pattern 2: Stream-Based Conversion (For Binary Data)

When working with file streams or binary data:

```python
from markitdown import MarkItDown
import io

md = MarkItDown()

# From binary file stream (must be binary mode)
with open("/mnt/user-data/uploads/file.xlsx", "rb") as f:
    result = md.convert_stream(f, file_extension=".xlsx")

# From BytesIO object
binary_data = get_file_data()  # Your binary data
stream = io.BytesIO(binary_data)
result = md.convert_stream(stream, file_extension=".pdf")

# Important: convert_stream requires binary streams (rb mode or BytesIO)
# Text streams (StringIO) will fail
```

### Pattern 3: URL Conversion

For web content and YouTube videos:

```python
from markitdown import MarkItDown

md = MarkItDown()

# Convert web page
result = md.convert("https://example.com/article")

# Convert YouTube video (requires [youtube-transcription])
result = md.convert("https://www.youtube.com/watch?v=VIDEO_ID")

markdown_text = result.text_content
```

### Pattern 4: Image Description with LLM

For rich image descriptions using an LLM (images and PPTX files):

```python
from markitdown import MarkItDown
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

# Create MarkItDown with LLM support
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    llm_prompt="Write a detailed caption for this image."  # Optional custom prompt
)

# Convert image with AI-powered descriptions
result = md.convert("/mnt/user-data/uploads/photo.jpg")
```

**Important**: Without an LLM client, image conversions will only extract EXIF metadata, not visual content descriptions.

### Pattern 5: Azure Document Intelligence (Advanced PDF)

For high-fidelity PDF conversion with Azure Document Intelligence:

```python
from markitdown import MarkItDown

md = MarkItDown(
    docintel_endpoint="https://your-endpoint.cognitiveservices.azure.com/"
)

result = md.convert("/mnt/user-data/uploads/complex.pdf")
```

**Note**: Requires Azure setup and [az-doc-intel] dependency.

### Pattern 6: Batch Processing Multiple Files

For processing multiple files efficiently:

```python
from markitdown import MarkItDown
import os

md = MarkItDown()
input_dir = "/mnt/user-data/uploads"
output_dir = "/mnt/user-data/outputs"

for filename in os.listdir(input_dir):
    input_path = os.path.join(input_dir, filename)
    
    # Skip directories
    if os.path.isdir(input_path):
        continue
    
    try:
        result = md.convert(input_path)
        
        # Create output filename
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, f"{base_name}.md")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)
            
        print(f"✓ Converted: {filename}")
    except Exception as e:
        print(f"✗ Failed: {filename} - {e}")
```

### Pattern 7: Plugin System (Advanced)

For custom file format support:

```python
from markitdown import MarkItDown

# Enable plugins (disabled by default)
md = MarkItDown(enable_plugins=True)

result = md.convert("custom_format.ext")
```

To discover available plugins:

```bash
markitdown --list-plugins
```

Search GitHub for `#markitdown-plugin` to find community plugins.

## Result Object Structure

All conversion methods return a `DocumentConverterResult` object:

```python
result = md.convert("file.docx")

# Access content
result.text_content  # The converted Markdown as string
result.title         # Document title (if available)

# Check properties
if result.text_content:
    print("Conversion successful")
```

## Error Handling Best Practices

Always wrap conversions in try-except blocks:

```python
from markitdown import MarkItDown
from markitdown._exceptions import FileConversionException

md = MarkItDown()

try:
    result = md.convert("/mnt/user-data/uploads/file.pdf")
    
    if not result.text_content:
        print("Warning: Conversion produced empty content")
    else:
        # Process successful conversion
        save_to_file(result.text_content)
        
except FileConversionException as e:
    print(f"Conversion failed: {e}")
    # Handle conversion-specific errors
    
except PermissionError as e:
    print(f"Permission denied: {e}")
    # Handle file access issues
    
except UnicodeEncodeError as e:
    print(f"Encoding issue: {e}")
    # Handle encoding problems
    # Fallback: result.text_content.encode('utf-8', errors='replace')
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle other errors
```

## Critical Limitations and Workarounds

### 1. PDF Limitations

**Problem**: PDFs without extractable text (image-based/scanned) return no content.

**Solution**: Preprocess with OCR or use Azure Document Intelligence:

```python
# Option 1: Use Azure Document Intelligence
md = MarkItDown(docintel_endpoint="your-endpoint")

# Option 2: Preprocess with external OCR tool before conversion
```

**Problem**: PDF formatting is lost during extraction.

**Reality**: Headings and body text are not distinguished. This is a library limitation.

### 2. Image Processing Requirements

**Problem**: Images return only EXIF metadata without LLM integration.

**Solution**: Always provide LLM client for image content:

```python
from openai import OpenAI
md = MarkItDown(llm_client=OpenAI(), llm_model="gpt-4o")
```

### 3. Stream Handling (Breaking Change in v0.1.0+)

**Problem**: `convert_stream()` only accepts binary streams, not text streams.

**Critical**: Always use binary mode:

```python
# ✓ CORRECT
with open("file.pdf", "rb") as f:  # Binary mode
    result = md.convert_stream(f, file_extension=".pdf")

# ✗ WRONG
with open("file.pdf", "r") as f:  # Text mode - will fail
    result = md.convert_stream(f, file_extension=".pdf")
```

### 4. File Path vs. Stream Trade-offs

**File paths** (`convert()`):
- Simpler API
- Automatic MIME type detection
- Direct file access

**Streams** (`convert_stream()`):
- More flexible for binary data
- Requires manual file extension specification
- Still creates temporary files internally

### 5. Network File Access

**Problem**: Permission errors on mapped network drives.

**Solution**: Copy to local filesystem first:

```python
import shutil

# Copy network file to local temp
local_temp = "/tmp/temp_file.docx"
shutil.copy(network_path, local_temp)

result = md.convert(local_temp)
os.remove(local_temp)  # Cleanup
```

### 6. Unicode Encoding Issues

**Problem**: Output redirection fails with special characters.

**Solution**: Handle encoding explicitly:

```python
try:
    print(result.text_content)
except UnicodeEncodeError:
    # Fallback with character replacement
    safe_text = result.text_content.encode('utf-8', errors='replace').decode('utf-8')
    print(safe_text)
```

### 7. Large File Processing

**Consideration**: Very large files (>100MB) may take significant time.

**Best Practice**: Inform users about processing time for large files:

```python
import os

file_size = os.path.getsize(filepath)
if file_size > 100_000_000:  # 100MB
    print(f"Processing large file ({file_size / 1_000_000:.1f}MB), this may take a moment...")
```

## Advanced Features

### Custom Prompts for LLM Image Processing

Tailor image descriptions to specific needs:

```python
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    llm_prompt="Describe this image with focus on technical diagrams and charts."
)
```

### ZIP Archive Processing

MarkItDown automatically processes ZIP contents recursively:

```python
# Converts all files inside the ZIP
result = md.convert("archive.zip")

# Result contains concatenated markdown from all files
print(result.text_content)  # All files' content
```

### Azure Document Intelligence Setup

Requires Azure AI Services resource. Get endpoint from Azure Portal:

```python
# Set up endpoint (requires API key in environment)
import os
os.environ["AZURE_DOCUMENT_INTELLIGENCE_KEY"] = "your-key"

md = MarkItDown(docintel_endpoint="https://your-resource.cognitiveservices.azure.com/")
```

More info: [Azure Document Intelligence Setup](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/how-to-guides/create-document-intelligence-resource)

## Typical Workflows

### Workflow 1: Process User Upload and Provide Summary

```python
from markitdown import MarkItDown

def process_user_document(uploaded_file_path):
    """Convert document and provide summary."""
    md = MarkItDown()
    
    try:
        # Convert document
        result = md.convert(uploaded_file_path)
        
        # Save markdown output
        filename = os.path.basename(uploaded_file_path)
        base_name = os.path.splitext(filename)[0]
        output_path = f"/mnt/user-data/outputs/{base_name}.md"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result.text_content)
        
        # Analyze content (you can now process the markdown)
        word_count = len(result.text_content.split())
        
        return {
            "success": True,
            "output_file": output_path,
            "word_count": word_count,
            "content": result.text_content
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Use it
result = process_user_document("/mnt/user-data/uploads/report.pdf")
if result["success"]:
    print(f"Converted successfully. Output: {result['output_file']}")
```

### Workflow 2: Extract Data from Multiple Spreadsheets

```python
from markitdown import MarkItDown
import os

def extract_all_spreadsheets(directory):
    """Extract data from all Excel files in a directory."""
    md = MarkItDown()
    results = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(('.xlsx', '.xls')):
            filepath = os.path.join(directory, filename)
            
            try:
                result = md.convert(filepath)
                results[filename] = result.text_content
            except Exception as e:
                results[filename] = f"Error: {e}"
    
    return results

# Process all spreadsheets
data = extract_all_spreadsheets("/mnt/user-data/uploads")

# Now you can analyze the extracted data
for filename, content in data.items():
    print(f"\n=== {filename} ===")
    print(content[:200])  # First 200 chars
```

### Workflow 3: Create Searchable Archive from Documents

```python
from markitdown import MarkItDown
import os
import json

def create_searchable_archive(input_dir, output_dir):
    """Convert all documents to markdown for text search."""
    md = MarkItDown()
    archive = {}
    
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            try:
                result = md.convert(filepath)
                
                # Store metadata and content
                archive[filepath] = {
                    "title": result.title or filename,
                    "content": result.text_content,
                    "word_count": len(result.text_content.split())
                }
                
            except Exception as e:
                print(f"Skipped {filename}: {e}")
    
    # Save searchable index
    with open(os.path.join(output_dir, "archive_index.json"), "w") as f:
        json.dump(archive, f, indent=2)
    
    return archive

# Build archive
archive = create_searchable_archive(
    "/mnt/user-data/uploads",
    "/mnt/user-data/outputs"
)

print(f"Processed {len(archive)} documents")
```

## Quality Considerations

### Output Quality Expectations

1. **Structure Preservation**: Headings, lists, tables, and links are preserved
2. **Token Efficiency**: Markdown is highly token-efficient for LLM processing
3. **Not for Human Presentation**: Output optimized for text analysis, not visual fidelity
4. **Formatting Trade-offs**: Complex formatting may be simplified

### When to Use MarkItDown

**Ideal Use Cases**:
- Preparing documents for LLM analysis
- Extracting text content from office documents
- Building searchable document archives
- Text mining and content analysis
- Document preprocessing pipelines

**Not Ideal For**:
- High-fidelity document conversion for human reading
- Preserving exact visual layout
- Processing documents requiring perfect formatting retention

## Troubleshooting

### Dependency Errors

**Error**: `No module named 'pdfminer'` or similar

**Solution**: Install missing optional dependency:

```bash
pip install 'markitdown[pdf]' --break-system-packages
```

### Empty Output

**Causes**:
1. Image-based PDF without OCR
2. Image file without LLM client
3. Unsupported file format
4. File corruption

**Debug Steps**:
1. Check file type and size
2. Verify optional dependencies installed
3. Try different conversion method
4. Check error messages in exception

### Performance Issues

**Large Files**: Break into smaller chunks if possible

**Many Files**: Consider parallel processing:

```python
from concurrent.futures import ThreadPoolExecutor

def convert_file(filepath):
    md = MarkItDown()
    return md.convert(filepath)

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(convert_file, file_list))
```

## Version Compatibility Notes

**Current Version**: v0.1.3+ (as of January 2025)

**Breaking Changes from v0.0.1**:
- Dependencies now organized into optional feature groups
- `convert_stream()` requires binary file-like objects only
- DocumentConverter interface changed (affects plugin developers)

**Migration Guide**:
- Update installation: `pip install 'markitdown[all]'`
- Update streams: Use `open(file, "rb")` instead of `open(file, "r")`
- Plugins: Update custom converters to use streams instead of paths

## Quick Reference

```python
# Basic setup
from markitdown import MarkItDown
md = MarkItDown()

# Simple conversion
result = md.convert("/path/to/file.pdf")
markdown = result.text_content

# With LLM for images
from openai import OpenAI
md = MarkItDown(llm_client=OpenAI(), llm_model="gpt-4o")

# Stream conversion
with open("file.xlsx", "rb") as f:
    result = md.convert_stream(f, file_extension=".xlsx")

# Enable plugins
md = MarkItDown(enable_plugins=True)

# Azure Document Intelligence
md = MarkItDown(docintel_endpoint="https://endpoint.com")
```

## Bundled Resources

This skill includes additional resources for complex scenarios and automation:

### Scripts

Located in `scripts/` directory, ready to execute:

- **`batch_convert.py`** - Batch convert multiple files with progress tracking, error handling, and summary reports
  - Usage: `python scripts/batch_convert.py <input_dir> <output_dir> [--recursive] [--llm]`
  - Features: Progress tracking, error handling, JSON summary reports
  
- **`analyze_document.py`** - Convert and analyze documents with structure detection and content metrics
  - Usage: `python scripts/analyze_document.py <filepath> [output_dir] [--detailed]`
  - Features: Word count, heading extraction, reading time estimation, top words analysis

Use these scripts when:
- Processing multiple documents at once
- Need detailed document analysis beyond conversion
- Want automated batch workflows with reporting

### Reference Documents

Located in `references/` directory, read when needed:

- **`advanced-features.md`** - Advanced features for power users
  - Custom document converters and plugin development
  - Performance optimization and parallel processing
  - Azure integration patterns
  - Special case handling (password-protected files, corrupted documents, etc.)
  - Read this for: Plugin development, performance tuning, complex integrations

- **`troubleshooting.md`** - Comprehensive troubleshooting guide
  - Installation issues and dependency errors
  - Conversion failures and output quality problems
  - Performance issues and platform-specific problems
  - Complete error reference with solutions
  - Read this for: Resolving errors, debugging conversion issues

### Examples

Located in `examples/` directory:

- **`usage_examples.md`** - 21 practical, copy-paste code examples
  - Basic conversions, batch processing, error handling
  - Stream processing, analysis and processing patterns
  - Integration patterns, performance optimization
  - Read this for: Quick reference code snippets for common tasks

## Additional Resources

- **GitHub Repository**: https://github.com/microsoft/markitdown
- **PyPI Package**: https://pypi.org/project/markitdown/
- **Plugin Development**: See `packages/markitdown-sample-plugin` in repository
- **Azure Document Intelligence**: https://learn.microsoft.com/azure/ai-services/document-intelligence/
