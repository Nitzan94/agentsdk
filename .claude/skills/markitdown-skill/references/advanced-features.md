# Advanced MarkItDown Features

This document covers advanced features and edge cases not needed for typical usage.

## Table of Contents

- [Custom Document Converters](#custom-document-converters)
- [Plugin Development](#plugin-development)
- [Performance Optimization](#performance-optimization)
- [Azure Integration Patterns](#azure-integration-patterns)
- [Handling Special Cases](#handling-special-cases)

## Custom Document Converters

For specialized file formats not supported by default, implement custom converters.

### Creating a Custom Converter

```python
from markitdown import MarkItDown
from markitdown.converter import DocumentConverter
from markitdown._markitdown import DocumentConverterResult

class CustomConverter(DocumentConverter):
    """Custom converter for .xyz files"""
    
    def convert(self, source_stream, **kwargs):
        """
        Convert file stream to markdown.
        
        Args:
            source_stream: Binary file stream
            **kwargs: Additional parameters
            
        Returns:
            DocumentConverterResult with text_content
        """
        # Read binary content
        content = source_stream.read()
        
        # Process content (your custom logic here)
        text = self._process_xyz_format(content)
        
        # Convert to markdown
        markdown = self._format_as_markdown(text)
        
        return DocumentConverterResult(
            text_content=markdown,
            title=kwargs.get('title', 'Custom Document')
        )
    
    def _process_xyz_format(self, content):
        """Process .xyz specific format"""
        # Your processing logic
        return content.decode('utf-8')
    
    def _format_as_markdown(self, text):
        """Format processed text as markdown"""
        return f"# Custom Document\n\n{text}"

# Register custom converter
md = MarkItDown()
md.register_converter(CustomConverter())

# Use it
result = md.convert("file.xyz")
```

## Plugin Development

Plugins extend MarkItDown via Python's entry point system.

### Plugin Structure

```
markitdown-xyz-plugin/
├── pyproject.toml
├── src/
│   └── markitdown_xyz_plugin/
│       ├── __init__.py
│       ├── __about__.py
│       └── _plugin.py
└── tests/
    └── test_xyz_plugin.py
```

### Plugin Implementation

**File: src/markitdown_xyz_plugin/_plugin.py**

```python
from markitdown.converter import DocumentConverter
from markitdown._markitdown import DocumentConverterResult

__plugin_interface_version__ = "0.1.0"

ACCEPTED_MIMETYPES = ["application/xyz", "application/x-xyz"]
ACCEPTED_FILE_EXTENSIONS = [".xyz"]

class XyzConverter(DocumentConverter):
    def accepts(self, file_stream, stream_info, **kwargs):
        """Determine if this converter can handle the file"""
        return (
            stream_info.mimetype in ACCEPTED_MIMETYPES
            or stream_info.extension in ACCEPTED_FILE_EXTENSIONS
        )
    
    def convert(self, file_stream, stream_info, **kwargs):
        """Convert XYZ file to markdown"""
        content = file_stream.read()
        # Process content
        markdown = self._convert_to_markdown(content)
        
        return DocumentConverterResult(text_content=markdown)
    
    def _convert_to_markdown(self, content):
        """Custom conversion logic"""
        # Implementation here
        pass

def register_converters(markitdown_instance):
    """Called by MarkItDown to register converters"""
    markitdown_instance.register_converter(XyzConverter())
```

### Plugin Registration

**File: pyproject.toml**

```toml
[project.entry-points."markitdown.plugin"]
xyz = "markitdown_xyz_plugin._plugin"
```

### Using Plugins

```python
from markitdown import MarkItDown

# Enable plugins
md = MarkItDown(enable_plugins=True)

# List installed plugins
# (From CLI: markitdown --list-plugins)

# Convert with plugin
result = md.convert("file.xyz")
```

## Performance Optimization

### Parallel Processing

For batch processing, use parallel execution:

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from markitdown import MarkItDown
import os

def convert_single_file(filepath):
    """Convert single file (runs in separate process)"""
    md = MarkItDown()
    try:
        result = md.convert(filepath)
        return (filepath, result.text_content, None)
    except Exception as e:
        return (filepath, None, str(e))

def batch_convert_parallel(file_list, max_workers=4):
    """Convert multiple files in parallel"""
    results = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(convert_single_file, fp): fp 
            for fp in file_list
        }
        
        # Process completed tasks
        for future in as_completed(futures):
            filepath, content, error = future.result()
            results.append({
                'file': filepath,
                'content': content,
                'error': error,
                'success': error is None
            })
    
    return results

# Use it
files = [f"/path/to/file{i}.pdf" for i in range(10)]
results = batch_convert_parallel(files, max_workers=4)

for r in results:
    if r['success']:
        print(f"✓ {r['file']}")
    else:
        print(f"✗ {r['file']}: {r['error']}")
```

### Memory Management for Large Files

```python
import os
from markitdown import MarkItDown

def convert_with_memory_check(filepath, max_size_mb=500):
    """Convert with file size check"""
    file_size = os.path.getsize(filepath)
    size_mb = file_size / (1024 * 1024)
    
    if size_mb > max_size_mb:
        raise ValueError(
            f"File too large ({size_mb:.1f}MB). "
            f"Maximum: {max_size_mb}MB"
        )
    
    md = MarkItDown()
    return md.convert(filepath)
```

### Caching Converted Documents

```python
import hashlib
import json
import os
from markitdown import MarkItDown

class CachedMarkItDown:
    def __init__(self, cache_dir="/tmp/markitdown_cache"):
        self.md = MarkItDown()
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_file_hash(self, filepath):
        """Generate hash of file for cache key"""
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def convert(self, filepath):
        """Convert with caching"""
        file_hash = self._get_file_hash(filepath)
        cache_file = os.path.join(self.cache_dir, f"{file_hash}.json")
        
        # Check cache
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                print(f"Cache hit: {filepath}")
                return type('Result', (), cached)
        
        # Convert and cache
        result = self.md.convert(filepath)
        with open(cache_file, 'w') as f:
            json.dump({
                'text_content': result.text_content,
                'title': result.title
            }, f)
        
        return result

# Use cached converter
cached_md = CachedMarkItDown()
result = cached_md.convert("large_document.pdf")  # First call: converts
result = cached_md.convert("large_document.pdf")  # Second call: cached
```

## Azure Integration Patterns

### Using Document Intelligence with Fallback

```python
from markitdown import MarkItDown
import os

def convert_with_azure_fallback(filepath):
    """Try Azure Document Intelligence, fallback to standard"""
    azure_endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    
    if azure_endpoint:
        try:
            # Try Azure first
            md = MarkItDown(docintel_endpoint=azure_endpoint)
            result = md.convert(filepath)
            print("Used Azure Document Intelligence")
            return result
        except Exception as e:
            print(f"Azure failed: {e}, falling back to standard")
    
    # Fallback to standard conversion
    md = MarkItDown()
    return md.convert(filepath)
```

### Batch Processing with Azure

```python
from markitdown import MarkItDown
import os
import time

def batch_convert_azure(file_list, delay=0.5):
    """
    Batch convert using Azure Document Intelligence.
    Includes delay to respect rate limits.
    """
    md = MarkItDown(docintel_endpoint=os.getenv("AZURE_DOC_INTEL_ENDPOINT"))
    results = []
    
    for i, filepath in enumerate(file_list):
        try:
            result = md.convert(filepath)
            results.append({
                'file': filepath,
                'content': result.text_content,
                'success': True
            })
            
            # Rate limiting
            if i < len(file_list) - 1:
                time.sleep(delay)
                
        except Exception as e:
            results.append({
                'file': filepath,
                'error': str(e),
                'success': False
            })
    
    return results
```

## Handling Special Cases

### Processing Password-Protected Files

```python
from markitdown import MarkItDown
import subprocess
import os

def convert_protected_pdf(filepath, password):
    """Convert password-protected PDF"""
    # Use qpdf to remove password first
    unlocked_path = filepath.replace('.pdf', '_unlocked.pdf')
    
    try:
        # Remove password using qpdf
        subprocess.run([
            'qpdf',
            '--password=' + password,
            '--decrypt',
            filepath,
            unlocked_path
        ], check=True)
        
        # Convert unlocked file
        md = MarkItDown()
        result = md.convert(unlocked_path)
        
        return result
        
    finally:
        # Clean up unlocked file
        if os.path.exists(unlocked_path):
            os.remove(unlocked_path)
```

### Handling Mixed-Encoding Files

```python
from markitdown import MarkItDown
import chardet

def convert_with_encoding_detection(filepath):
    """Handle files with unknown encoding"""
    # Detect encoding
    with open(filepath, 'rb') as f:
        raw_data = f.read()
        detected = chardet.detect(raw_data)
        encoding = detected['encoding']
    
    print(f"Detected encoding: {encoding}")
    
    # Convert
    md = MarkItDown()
    result = md.convert(filepath)
    
    return result
```

### Processing Corrupted Files

```python
from markitdown import MarkItDown
from markitdown._exceptions import FileConversionException

def convert_with_repair_attempt(filepath):
    """Attempt conversion with repair for corrupted files"""
    md = MarkItDown()
    
    try:
        # Try normal conversion
        return md.convert(filepath)
        
    except FileConversionException:
        # For corrupted PDFs, try pypdf with error recovery
        if filepath.endswith('.pdf'):
            from pypdf import PdfReader
            
            try:
                reader = PdfReader(filepath, strict=False)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
                
                # Return as markdown
                return type('Result', (), {
                    'text_content': text,
                    'title': 'Recovered Document'
                })
            except Exception as e:
                raise FileConversionException(
                    f"Failed to recover: {e}"
                ) from e
```

### URL Conversion with Timeout

```python
from markitdown import MarkItDown
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    """Context manager for timeout"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds}s")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def convert_url_with_timeout(url, timeout_seconds=30):
    """Convert URL with timeout protection"""
    md = MarkItDown()
    
    try:
        with timeout(timeout_seconds):
            result = md.convert(url)
            return result
    except TimeoutError as e:
        raise Exception(f"URL conversion timed out: {url}") from e
```

## Advanced CLI Usage

### Processing with Shell Scripts

```bash
#!/bin/bash
# Process all PDFs in a directory

INPUT_DIR="/mnt/user-data/uploads"
OUTPUT_DIR="/mnt/user-data/outputs"

for file in "$INPUT_DIR"/*.pdf; do
    filename=$(basename "$file" .pdf)
    echo "Converting: $filename"
    
    markitdown "$file" -o "$OUTPUT_DIR/$filename.md"
    
    if [ $? -eq 0 ]; then
        echo "✓ Success: $filename"
    else
        echo "✗ Failed: $filename"
    fi
done
```

### Using Plugins from CLI

```bash
# Enable plugins
markitdown --use-plugins file.xyz -o output.md

# List available plugins
markitdown --list-plugins
```

## Troubleshooting Advanced Issues

### Debug Mode

```python
import logging
from markitdown import MarkItDown

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

md = MarkItDown()
result = md.convert("problematic_file.pdf")
```

### Inspecting Conversion Attempts

```python
from markitdown import MarkItDown
from markitdown._exceptions import FileConversionException

md = MarkItDown()

try:
    result = md.convert("file.pdf")
except FileConversionException as e:
    # Inspect failed attempts
    print(f"Failed after {len(e.attempts)} attempts:")
    for attempt in e.attempts:
        print(f"  - {attempt}")
```
