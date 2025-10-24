#!/usr/bin/env python3
"""
Batch convert multiple files to Markdown using MarkItDown.

This script processes all supported files in a directory and converts them
to Markdown, with comprehensive error handling and progress reporting.

Usage:
    python batch_convert.py /path/to/input /path/to/output
    python batch_convert.py /mnt/user-data/uploads /mnt/user-data/outputs
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from datetime import datetime

try:
    from markitdown import MarkItDown
    from markitdown._exceptions import FileConversionException
except ImportError:
    print("Error: MarkItDown not installed.")
    print("Install with: pip install 'markitdown[all]' --break-system-packages")
    sys.exit(1)


@dataclass
class ConversionResult:
    """Result of a single file conversion"""
    filepath: str
    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
    char_count: int = 0
    word_count: int = 0


class BatchConverter:
    """Batch file converter using MarkItDown"""
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.pdf', '.docx', '.pptx', '.xlsx', '.xls',
        '.jpg', '.jpeg', '.png', '.gif', '.webp',
        '.html', '.htm', '.csv', '.json', '.xml',
        '.zip', '.epub', '.wav', '.mp3', '.msg'
    }
    
    def __init__(self, output_dir: str, use_llm: bool = False):
        """
        Initialize batch converter.
        
        Args:
            output_dir: Directory for output files
            use_llm: Whether to use LLM for image descriptions
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize MarkItDown
        if use_llm:
            try:
                from openai import OpenAI
                self.md = MarkItDown(
                    llm_client=OpenAI(),
                    llm_model="gpt-4o"
                )
                print("✓ LLM support enabled for images")
            except ImportError:
                print("Warning: OpenAI not available, LLM disabled")
                self.md = MarkItDown()
        else:
            self.md = MarkItDown()
        
        self.results: List[ConversionResult] = []
    
    def is_supported(self, filepath: Path) -> bool:
        """Check if file extension is supported"""
        return filepath.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def convert_file(self, filepath: Path) -> ConversionResult:
        """
        Convert a single file to Markdown.
        
        Args:
            filepath: Path to input file
            
        Returns:
            ConversionResult object
        """
        try:
            # Convert file
            result = self.md.convert(str(filepath))
            
            # Generate output filename
            output_filename = filepath.stem + '.md'
            output_path = self.output_dir / output_filename
            
            # Save markdown
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            # Calculate statistics
            char_count = len(result.text_content)
            word_count = len(result.text_content.split())
            
            return ConversionResult(
                filepath=str(filepath),
                success=True,
                output_path=str(output_path),
                char_count=char_count,
                word_count=word_count
            )
            
        except FileConversionException as e:
            return ConversionResult(
                filepath=str(filepath),
                success=False,
                error=f"Conversion failed: {str(e)}"
            )
        except PermissionError as e:
            return ConversionResult(
                filepath=str(filepath),
                success=False,
                error=f"Permission denied: {str(e)}"
            )
        except Exception as e:
            return ConversionResult(
                filepath=str(filepath),
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    def convert_directory(self, input_dir: str, recursive: bool = False) -> Dict:
        """
        Convert all supported files in a directory.
        
        Args:
            input_dir: Input directory path
            recursive: Whether to process subdirectories
            
        Returns:
            Summary dictionary
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            print(f"Error: Directory not found: {input_dir}")
            return {}
        
        # Find all supported files
        if recursive:
            files = [
                f for f in input_path.rglob('*')
                if f.is_file() and self.is_supported(f)
            ]
        else:
            files = [
                f for f in input_path.glob('*')
                if f.is_file() and self.is_supported(f)
            ]
        
        if not files:
            print(f"No supported files found in {input_dir}")
            return {}
        
        print(f"\nFound {len(files)} files to convert")
        print(f"Output directory: {self.output_dir}\n")
        
        # Convert each file
        for i, filepath in enumerate(files, 1):
            print(f"[{i}/{len(files)}] Converting: {filepath.name}...", end=' ')
            
            result = self.convert_file(filepath)
            self.results.append(result)
            
            if result.success:
                print(f"✓ ({result.word_count} words)")
            else:
                print(f"✗ {result.error}")
        
        # Generate summary
        return self._generate_summary()
    
    def _generate_summary(self) -> Dict:
        """Generate conversion summary"""
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'total_words': sum(r.word_count for r in successful),
            'total_chars': sum(r.char_count for r in successful),
            'success_rate': len(successful) / len(self.results) * 100 if self.results else 0,
            'failed_files': [
                {'file': r.filepath, 'error': r.error}
                for r in failed
            ]
        }
        
        return summary
    
    def save_summary(self, filename: str = 'conversion_summary.json'):
        """Save conversion summary to JSON file"""
        summary = self._generate_summary()
        summary_path = self.output_dir / filename
        
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary_path
    
    def print_summary(self):
        """Print conversion summary to console"""
        summary = self._generate_summary()
        
        print("\n" + "="*50)
        print("CONVERSION SUMMARY")
        print("="*50)
        print(f"Total files:     {summary['total_files']}")
        print(f"Successful:      {summary['successful']} ({summary['success_rate']:.1f}%)")
        print(f"Failed:          {summary['failed']}")
        print(f"Total words:     {summary['total_words']:,}")
        print(f"Total chars:     {summary['total_chars']:,}")
        
        if summary['failed_files']:
            print("\nFailed files:")
            for item in summary['failed_files']:
                print(f"  ✗ {Path(item['file']).name}")
                print(f"    {item['error']}")
        
        print("="*50)


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python batch_convert.py <input_dir> <output_dir> [--recursive] [--llm]")
        print("\nOptions:")
        print("  --recursive  Process subdirectories")
        print("  --llm        Enable LLM for image descriptions")
        print("\nExample:")
        print("  python batch_convert.py /mnt/user-data/uploads /mnt/user-data/outputs")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    recursive = '--recursive' in sys.argv
    use_llm = '--llm' in sys.argv
    
    # Create converter and run
    converter = BatchConverter(output_dir, use_llm=use_llm)
    converter.convert_directory(input_dir, recursive=recursive)
    
    # Print and save summary
    converter.print_summary()
    summary_path = converter.save_summary()
    print(f"\nSummary saved to: {summary_path}")


if __name__ == '__main__':
    main()
