# MarkItDown Usage Examples

Practical, copy-paste examples for common MarkItDown tasks.

## Quick Start Examples

### Example 1: Convert a Single PDF

```python
from markitdown import MarkItDown

# Initialize converter
md = MarkItDown()

# Convert PDF
result = md.convert("/mnt/user-data/uploads/document.pdf")

# Save to output
with open("/mnt/user-data/outputs/document.md", "w") as f:
    f.write(result.text_content)

print(f"Converted {len(result.text_content)} characters")
```

### Example 2: Convert Word Document

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("/mnt/user-data/uploads/report.docx")

# Access content
print(result.text_content[:500])  # First 500 characters
```

### Example 3: Convert Excel Spreadsheet

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("/mnt/user-data/uploads/data.xlsx")

# Excel tables are preserved in markdown
with open("/mnt/user-data/outputs/data.md", "w") as f:
    f.write(result.text_content)
```

## Working with Images

### Example 4: Image with LLM Descriptions

```python
from markitdown import MarkItDown
from openai import OpenAI

# Create converter with LLM support
client = OpenAI()  # Requires OPENAI_API_KEY env variable
md = MarkItDown(llm_client=client, llm_model="gpt-4o")

# Convert image
result = md.convert("/mnt/user-data/uploads/photo.jpg")

# Image will include AI-generated description
print(result.text_content)
```

### Example 5: Custom Image Description Prompt

```python
from markitdown import MarkItDown
from openai import OpenAI

md = MarkItDown(
    llm_client=OpenAI(),
    llm_model="gpt-4o",
    llm_prompt="Describe this image in technical detail, focusing on diagrams and charts."
)

result = md.convert("/mnt/user-data/uploads/diagram.png")
```

## Batch Processing

### Example 6: Convert All PDFs in Directory

```python
from markitdown import MarkItDown
import os
from pathlib import Path

md = MarkItDown()
input_dir = "/mnt/user-data/uploads"
output_dir = "/mnt/user-data/outputs"

# Find all PDFs
pdf_files = list(Path(input_dir).glob("*.pdf"))

print(f"Found {len(pdf_files)} PDFs")

for pdf_path in pdf_files:
    try:
        # Convert
        result = md.convert(str(pdf_path))
        
        # Save with same name but .md extension
        output_path = Path(output_dir) / f"{pdf_path.stem}.md"
        with open(output_path, "w") as f:
            f.write(result.text_content)
        
        print(f"✓ {pdf_path.name}")
    except Exception as e:
        print(f"✗ {pdf_path.name}: {e}")
```

### Example 7: Convert Multiple File Types

```python
from markitdown import MarkItDown
from pathlib import Path

md = MarkItDown()

# Supported extensions
EXTENSIONS = ['.pdf', '.docx', '.pptx', '.xlsx', '.html']

input_dir = Path("/mnt/user-data/uploads")
output_dir = Path("/mnt/user-data/outputs")
output_dir.mkdir(exist_ok=True)

# Find all supported files
files = [
    f for f in input_dir.iterdir()
    if f.suffix.lower() in EXTENSIONS
]

print(f"Converting {len(files)} files...")

for filepath in files:
    output_path = output_dir / f"{filepath.stem}.md"
    
    try:
        result = md.convert(str(filepath))
        with open(output_path, "w") as f:
            f.write(result.text_content)
        print(f"✓ {filepath.name}")
    except Exception as e:
        print(f"✗ {filepath.name}: {e}")
```

## Advanced Conversions

### Example 8: URL to Markdown

```python
from markitdown import MarkItDown

md = MarkItDown()

# Convert web page
result = md.convert("https://example.com/article")

# Save
with open("/mnt/user-data/outputs/article.md", "w") as f:
    f.write(result.text_content)
```

### Example 9: YouTube Video Transcript

```python
from markitdown import MarkItDown

# Requires youtube-transcription dependency
md = MarkItDown()

# Convert YouTube video
result = md.convert("https://www.youtube.com/watch?v=VIDEO_ID")

print(result.text_content)
```

### Example 10: Process ZIP Archive

```python
from markitdown import MarkItDown

md = MarkItDown()

# Automatically processes all files in ZIP
result = md.convert("/mnt/user-data/uploads/documents.zip")

# Result contains concatenated markdown from all files
with open("/mnt/user-data/outputs/archive_contents.md", "w") as f:
    f.write(result.text_content)
```

## Error Handling

### Example 11: Robust Conversion with Error Handling

```python
from markitdown import MarkItDown
from markitdown._exceptions import FileConversionException

md = MarkItDown()

def safe_convert(filepath):
    """Convert with comprehensive error handling"""
    try:
        result = md.convert(filepath)
        
        if not result.text_content:
            print(f"Warning: {filepath} produced empty output")
            return None
        
        return result
        
    except FileConversionException as e:
        print(f"Conversion failed: {e}")
        return None
    except PermissionError:
        print(f"Permission denied: {filepath}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Use it
result = safe_convert("/mnt/user-data/uploads/document.pdf")
if result:
    print(f"Success: {len(result.text_content)} characters")
```

### Example 12: Retry Logic for Network Issues

```python
from markitdown import MarkItDown
import time

md = MarkItDown()

def convert_with_retry(filepath, max_retries=3):
    """Convert with retry on failure"""
    for attempt in range(max_retries):
        try:
            result = md.convert(filepath)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"All attempts failed: {e}")
                raise

# Use it
result = convert_with_retry("/path/to/file.pdf")
```

## Stream Processing

### Example 13: Convert from Binary Stream

```python
from markitdown import MarkItDown
import io

md = MarkItDown()

# From binary file
with open("/mnt/user-data/uploads/file.pdf", "rb") as f:
    result = md.convert_stream(f, file_extension=".pdf")

# From BytesIO
binary_data = get_binary_data()  # Your binary data source
stream = io.BytesIO(binary_data)
result = md.convert_stream(stream, file_extension=".docx")

print(result.text_content)
```

### Example 14: Process Uploaded File (API Context)

```python
from markitdown import MarkItDown
import tempfile
import os

md = MarkItDown()

def process_upload(file_content, filename):
    """Process uploaded file content"""
    # Get file extension
    _, ext = os.path.splitext(filename)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name
    
    try:
        # Convert
        result = md.convert(tmp_path)
        return result.text_content
    finally:
        # Cleanup
        os.unlink(tmp_path)

# Use it
markdown = process_upload(uploaded_bytes, "document.pdf")
```

## Analysis and Processing

### Example 15: Extract and Count Headings

```python
from markitdown import MarkItDown
import re

md = MarkItDown()
result = md.convert("/mnt/user-data/uploads/report.pdf")

# Extract headings
headings = []
for line in result.text_content.split('\n'):
    if line.strip().startswith('#'):
        heading = re.sub(r'^#+\s*', '', line.strip())
        headings.append(heading)

print(f"Found {len(headings)} headings:")
for h in headings[:5]:  # First 5
    print(f"  - {h}")
```

### Example 16: Extract Tables

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("/mnt/user-data/uploads/data.xlsx")

# Tables in markdown are delimited by pipes
lines = result.text_content.split('\n')
table_lines = [line for line in lines if '|' in line]

print(f"Found {len(table_lines)} table rows")
print("\nFirst few rows:")
for line in table_lines[:5]:
    print(line)
```

### Example 17: Word Frequency Analysis

```python
from markitdown import MarkItDown
from collections import Counter
import re

md = MarkItDown()
result = md.convert("/mnt/user-data/uploads/document.pdf")

# Extract words
words = re.findall(r'\b\w+\b', result.text_content.lower())

# Filter out short words and count
long_words = [w for w in words if len(w) > 4]
word_freq = Counter(long_words)

print("Top 10 words:")
for word, count in word_freq.most_common(10):
    print(f"  {word:15} {count:4} times")
```

## Integration Patterns

### Example 18: Build Searchable Document Database

```python
from markitdown import MarkItDown
from pathlib import Path
import json

md = MarkItDown()

def build_search_index(input_dir):
    """Build searchable index of documents"""
    index = {}
    
    for filepath in Path(input_dir).rglob('*'):
        if not filepath.is_file():
            continue
        
        try:
            result = md.convert(str(filepath))
            
            index[str(filepath)] = {
                'content': result.text_content,
                'word_count': len(result.text_content.split()),
                'char_count': len(result.text_content)
            }
            
        except Exception as e:
            print(f"Skipped {filepath.name}: {e}")
    
    return index

# Build index
index = build_search_index("/mnt/user-data/uploads")

# Save to JSON
with open("/mnt/user-data/outputs/search_index.json", "w") as f:
    json.dump(index, f, indent=2)

print(f"Indexed {len(index)} documents")
```

### Example 19: Document Comparison

```python
from markitdown import MarkItDown
from difflib import unified_diff

md = MarkItDown()

# Convert two versions
result1 = md.convert("/mnt/user-data/uploads/version1.pdf")
result2 = md.convert("/mnt/user-data/uploads/version2.pdf")

# Compare
diff = unified_diff(
    result1.text_content.splitlines(),
    result2.text_content.splitlines(),
    lineterm='',
    fromfile='version1',
    tofile='version2'
)

# Save diff
with open("/mnt/user-data/outputs/changes.diff", "w") as f:
    f.write('\n'.join(diff))
```

### Example 20: Extract Metadata and Content

```python
from markitdown import MarkItDown
import os
from datetime import datetime

md = MarkItDown()

def extract_document_info(filepath):
    """Extract full document information"""
    result = md.convert(filepath)
    
    file_stat = os.stat(filepath)
    
    return {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'file_size': file_stat.st_size,
        'modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
        'content': result.text_content,
        'word_count': len(result.text_content.split()),
        'char_count': len(result.text_content),
        'title': result.title or os.path.basename(filepath)
    }

# Use it
info = extract_document_info("/mnt/user-data/uploads/report.pdf")

# Save as JSON
import json
with open("/mnt/user-data/outputs/document_info.json", "w") as f:
    json.dump(info, f, indent=2)
```

## Performance Optimization

### Example 21: Parallel Batch Conversion

```python
from markitdown import MarkItDown
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def convert_single(filepath):
    """Convert single file (runs in separate process)"""
    md = MarkItDown()
    try:
        result = md.convert(str(filepath))
        return (str(filepath), result.text_content, None)
    except Exception as e:
        return (str(filepath), None, str(e))

def parallel_convert(input_dir, output_dir, max_workers=4):
    """Convert files in parallel"""
    files = list(Path(input_dir).glob('*.pdf'))
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(convert_single, files))
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for filepath, content, error in results:
        if content:
            filename = Path(filepath).stem + '.md'
            with open(output_path / filename, 'w') as f:
                f.write(content)
            print(f"✓ {Path(filepath).name}")
        else:
            print(f"✗ {Path(filepath).name}: {error}")

# Use it
parallel_convert(
    "/mnt/user-data/uploads",
    "/mnt/user-data/outputs",
    max_workers=4
)
```

## Tips and Tricks

### Tip 1: Check if Conversion Produced Content

```python
result = md.convert("file.pdf")

if result.text_content and len(result.text_content.strip()) > 0:
    print("Conversion successful")
else:
    print("Warning: No content extracted")
```

### Tip 2: Handle Large Files

```python
import os

filepath = "/mnt/user-data/uploads/large.pdf"
file_size = os.path.getsize(filepath)

if file_size > 100_000_000:  # 100MB
    print(f"Warning: Large file ({file_size / 1_000_000:.1f}MB)")
    print("This may take several minutes...")

result = md.convert(filepath)
```

### Tip 3: Preserve Original Filenames

```python
from pathlib import Path

input_file = Path("/mnt/user-data/uploads/My Report (Final v2).pdf")
output_file = Path("/mnt/user-data/outputs") / f"{input_file.stem}.md"

result = md.convert(str(input_file))
with open(output_file, "w") as f:
    f.write(result.text_content)

print(f"Saved to: {output_file}")
```
