# MarkItDown Troubleshooting Guide

Comprehensive troubleshooting for common issues and errors.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Conversion Failures](#conversion-failures)
- [Output Quality Issues](#output-quality-issues)
- [Performance Problems](#performance-problems)
- [Platform-Specific Issues](#platform-specific-issues)
- [Error Reference](#error-reference)

## Installation Issues

### Issue: `pip install` fails with dependency errors

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:

1. Update pip and setuptools:
```bash
pip install --upgrade pip setuptools --break-system-packages
```

2. Install with specific Python version:
```bash
python3.10 -m pip install 'markitdown[all]' --break-system-packages
```

3. Check Python version (requires 3.10+):
```bash
python --version
```

### Issue: Missing optional dependencies

**Symptoms**:
```
ModuleNotFoundError: No module named 'pdfminer'
ModuleNotFoundError: No module named 'mammoth'
```

**Solution**: Install specific feature groups:
```bash
pip install 'markitdown[pdf]' --break-system-packages  # For PDFs
pip install 'markitdown[docx]' --break-system-packages  # For Word
pip install 'markitdown[all]' --break-system-packages  # For everything
```

### Issue: `--break-system-packages` flag issues

**Symptoms**: Error about system packages

**Solution**: This environment requires this flag. Always use it:
```bash
pip install markitdown --break-system-packages
```

## Conversion Failures

### Issue: FileConversionException

**Symptoms**:
```python
markitdown._exceptions.FileConversionException: File conversion failed
```

**Common Causes**:

1. **Unsupported file format**
   - Check if format is supported
   - Verify file extension matches content
   
2. **Missing dependencies**
   ```bash
   pip install 'markitdown[pdf,docx,pptx,xlsx]' --break-system-packages
   ```

3. **Corrupted file**
   - Try opening file in native application
   - Re-download or re-save file
   
4. **File permissions**
   ```python
   # Check file permissions
   import os
   print(os.access(filepath, os.R_OK))
   ```

**Diagnostic Script**:
```python
from markitdown import MarkItDown
from markitdown._exceptions import FileConversionException
import os

def diagnose_conversion(filepath):
    print(f"Diagnosing: {filepath}")
    
    # Check file exists
    if not os.path.exists(filepath):
        print("✗ File does not exist")
        return
    print("✓ File exists")
    
    # Check file size
    size = os.path.getsize(filepath)
    print(f"✓ File size: {size} bytes")
    
    # Check file permissions
    if not os.access(filepath, os.R_OK):
        print("✗ No read permission")
        return
    print("✓ Read permission OK")
    
    # Try conversion
    md = MarkItDown()
    try:
        result = md.convert(filepath)
        print("✓ Conversion successful")
        print(f"  Content length: {len(result.text_content)} chars")
    except FileConversionException as e:
        print(f"✗ Conversion failed: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

# Use it
diagnose_conversion("/path/to/file.pdf")
```

### Issue: Empty or minimal output

**Symptoms**: Conversion succeeds but produces little/no text

**Causes & Solutions**:

1. **Image-based PDF without OCR**
   ```python
   # Solution: Use Azure Document Intelligence
   from markitdown import MarkItDown
   md = MarkItDown(docintel_endpoint="your-endpoint")
   ```

2. **Image file without LLM**
   ```python
   # Solution: Provide LLM client
   from openai import OpenAI
   md = MarkItDown(llm_client=OpenAI(), llm_model="gpt-4o")
   ```

3. **File is actually empty or encrypted**
   - Check file in native application
   - Remove password protection first

### Issue: Permission denied errors

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied
```

**Solutions**:

1. **For network drives**:
   ```python
   import shutil
   import tempfile
   
   # Copy to local temp
   temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
   shutil.copy(network_path, temp_file.name)
   
   md = MarkItDown()
   result = md.convert(temp_file.name)
   
   os.unlink(temp_file.name)
   ```

2. **For locked files**:
   ```python
   import time
   
   # Wait and retry
   for attempt in range(3):
       try:
           result = md.convert(filepath)
           break
       except PermissionError:
           time.sleep(1)
   ```

## Output Quality Issues

### Issue: Lost formatting in PDFs

**Symptoms**: No distinction between headings and body text

**Reality**: This is a library limitation. PDFs lose formatting during extraction.

**Workaround**: Use Azure Document Intelligence for better structure:
```python
md = MarkItDown(docintel_endpoint="your-endpoint")
```

### Issue: Poor image descriptions

**Symptoms**: Generic or inaccurate image descriptions

**Solution**: Provide custom prompts:
```python
from markitdown import MarkItDown
from openai import OpenAI

md = MarkItDown(
    llm_client=OpenAI(),
    llm_model="gpt-4o",
    llm_prompt="Describe this image in detail, focusing on [specific aspects]"
)
```

### Issue: Garbled text or encoding issues

**Symptoms**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Solutions**:

1. **For output encoding**:
   ```python
   try:
       print(result.text_content)
   except UnicodeEncodeError:
       safe_text = result.text_content.encode('utf-8', errors='replace').decode('utf-8')
       print(safe_text)
   ```

2. **For input files**:
   ```python
   # Try with explicit encoding
   with open(filepath, 'rb') as f:
       content = f.read()
       text = content.decode('utf-8', errors='ignore')
   ```

### Issue: Tables rendered poorly

**Symptoms**: Table structure lost or unclear

**Reality**: Markdown table conversion is best-effort

**Improvement Options**:
- For Excel: Tables are usually well-preserved
- For PDFs: Consider Azure Document Intelligence
- For Word: Use native DOCX support (usually good)

## Performance Problems

### Issue: Slow conversion for large files

**Symptoms**: Conversion takes minutes for large files

**Solutions**:

1. **Show progress for large files**:
   ```python
   import os
   
   file_size = os.path.getsize(filepath)
   if file_size > 50_000_000:  # 50MB
       print(f"Processing large file ({file_size/1_000_000:.1f}MB)...")
   
   result = md.convert(filepath)
   ```

2. **Split large files**:
   ```python
   # For PDFs, split into smaller chunks
   from pypdf import PdfReader, PdfWriter
   
   def split_pdf(input_path, pages_per_chunk=50):
       reader = PdfReader(input_path)
       total_pages = len(reader.pages)
       
       chunks = []
       for start in range(0, total_pages, pages_per_chunk):
           end = min(start + pages_per_chunk, total_pages)
           
           writer = PdfWriter()
           for page_num in range(start, end):
               writer.add_page(reader.pages[page_num])
           
           chunk_path = f"temp_chunk_{start}_{end}.pdf"
           with open(chunk_path, 'wb') as f:
               writer.write(f)
           
           chunks.append(chunk_path)
       
       return chunks
   ```

3. **Use parallel processing** (see advanced-features.md)

### Issue: High memory usage

**Symptoms**: Process uses excessive RAM

**Solutions**:

1. **Process files in batches**:
   ```python
   def process_in_batches(files, batch_size=10):
       for i in range(0, len(files), batch_size):
           batch = files[i:i+batch_size]
           for file in batch:
               result = md.convert(file)
               # Process result immediately
               save_result(result)
   ```

2. **Stream processing for text output**:
   ```python
   # Write directly to file instead of keeping in memory
   result = md.convert(large_file)
   with open(output_file, 'w') as f:
       f.write(result.text_content)
   # Clear reference
   del result
   ```

### Issue: Timeout on URL conversions

**Symptoms**: Hangs when converting web pages

**Solution**: Implement timeout (see advanced-features.md)

## Platform-Specific Issues

### Windows Issues

**Issue**: Path separators in file paths

**Solution**:
```python
import os

# Use os.path.join for cross-platform paths
filepath = os.path.join('folder', 'file.pdf')

# Or use raw strings
filepath = r'C:\Users\Name\Documents\file.pdf'
```

**Issue**: Unicode in console output

**Solution**:
```python
import sys
import io

# Set console encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### Linux/Unix Issues

**Issue**: Permission errors on shared filesystems

**Solution**:
```bash
# Check and fix permissions
chmod 644 file.pdf
# Or copy to local temp directory first
```

**Issue**: Missing system libraries for audio

**Solution**:
```bash
# Install system dependencies
apt-get install ffmpeg portaudio19-dev
# Or
yum install ffmpeg portaudio-devel
```

### macOS Issues

**Issue**: Permission errors on app-restricted folders

**Solution**: Move files to non-restricted location like `/tmp`

**Issue**: SSL certificate errors

**Solution**:
```bash
# Install certificates
/Applications/Python\ 3.10/Install\ Certificates.command
```

## Error Reference

### Common Error Types

| Error | Cause | Solution |
|-------|-------|----------|
| `FileConversionException` | Conversion failed after all attempts | Check file format, dependencies, corruption |
| `PermissionError` | No file access | Check permissions, copy to local |
| `UnicodeEncodeError` | Character encoding issue | Use encoding='utf-8', errors='replace' |
| `ModuleNotFoundError` | Missing dependency | Install optional dependencies |
| `TimeoutError` | Operation too slow | Implement timeout or break into chunks |
| `ValueError` | Invalid parameter | Check file extension, parameters |

### Debugging Workflow

```python
from markitdown import MarkItDown
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create detailed error handler
def safe_convert(filepath):
    """Convert with comprehensive error handling"""
    md = MarkItDown()
    
    try:
        print(f"Converting: {filepath}")
        result = md.convert(filepath)
        
        if not result.text_content:
            print("Warning: Empty result")
            return None
            
        print(f"Success: {len(result.text_content)} characters")
        return result
        
    except FileConversionException as e:
        print(f"Conversion failed: {e}")
        # Log details
        logging.error(f"File: {filepath}")
        logging.error(f"Error: {e}")
        return None
        
    except PermissionError as e:
        print(f"Permission denied: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        logging.exception("Full traceback:")
        return None

# Use it
result = safe_convert("/path/to/file.pdf")
```

### Getting Help

If issues persist after trying these solutions:

1. Check the GitHub Issues: https://github.com/microsoft/markitdown/issues
2. Search for similar problems
3. Create new issue with:
   - MarkItDown version (`pip show markitdown`)
   - Python version
   - Operating system
   - Full error traceback
   - Minimal reproducible example
   - Example file (if possible)

### Version-Specific Issues

**v0.0.1 → v0.1.0 Breaking Changes**:

Issue: `convert_stream()` fails with StringIO
```python
# Old (v0.0.1) - no longer works
with open('file.pdf', 'r') as f:  # Text mode
    result = md.convert_stream(f)

# New (v0.1.0+) - use binary mode
with open('file.pdf', 'rb') as f:  # Binary mode
    result = md.convert_stream(f, file_extension='.pdf')
```

Issue: Dependencies not found
```bash
# Old
pip install markitdown

# New
pip install 'markitdown[all]'  # Install all features
```
