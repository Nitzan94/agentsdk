#!/usr/bin/env python3
"""
Smart Document Analyzer - Convert and analyze documents using MarkItDown.

This script converts documents to Markdown and provides intelligent analysis
including structure detection, content summary, and metadata extraction.

Usage:
    python analyze_document.py <filepath>
    python analyze_document.py /mnt/user-data/uploads/report.pdf
"""

import sys
import os
from pathlib import Path
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import Counter

try:
    from markitdown import MarkItDown
except ImportError:
    print("Error: MarkItDown not installed.")
    print("Install with: pip install 'markitdown[all]' --break-system-packages")
    sys.exit(1)


@dataclass
class DocumentAnalysis:
    """Analysis results for a document"""
    filepath: str
    success: bool
    error: Optional[str] = None
    
    # Content metrics
    char_count: int = 0
    word_count: int = 0
    line_count: int = 0
    
    # Structure analysis
    heading_count: int = 0
    headings: List[str] = None
    list_count: int = 0
    table_count: int = 0
    link_count: int = 0
    image_count: int = 0
    
    # Content analysis
    top_words: List[tuple] = None
    estimated_reading_time: int = 0  # minutes
    
    # Markdown output
    markdown_path: Optional[str] = None
    
    def __post_init__(self):
        if self.headings is None:
            self.headings = []
        if self.top_words is None:
            self.top_words = []


class DocumentAnalyzer:
    """Analyze documents using MarkItDown"""
    
    # Common stopwords to exclude from word frequency
    STOPWORDS = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
        'is', 'are', 'was', 'were', 'been', 'has', 'had', 'can', 'may'
    }
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize analyzer.
        
        Args:
            output_dir: Directory to save markdown output (optional)
        """
        self.md = MarkItDown()
        self.output_dir = Path(output_dir) if output_dir else None
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze(self, filepath: str) -> DocumentAnalysis:
        """
        Analyze a document.
        
        Args:
            filepath: Path to document
            
        Returns:
            DocumentAnalysis object
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return DocumentAnalysis(
                filepath=str(filepath),
                success=False,
                error="File not found"
            )
        
        try:
            # Convert to markdown
            result = self.md.convert(str(filepath))
            markdown = result.text_content
            
            # Save markdown if output directory specified
            markdown_path = None
            if self.output_dir:
                output_filename = filepath.stem + '.md'
                markdown_path = self.output_dir / output_filename
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown)
            
            # Analyze content
            analysis = self._analyze_markdown(markdown)
            analysis.filepath = str(filepath)
            analysis.success = True
            analysis.markdown_path = str(markdown_path) if markdown_path else None
            
            return analysis
            
        except Exception as e:
            return DocumentAnalysis(
                filepath=str(filepath),
                success=False,
                error=str(e)
            )
    
    def _analyze_markdown(self, markdown: str) -> DocumentAnalysis:
        """Analyze markdown content"""
        lines = markdown.split('\n')
        words = markdown.split()
        
        # Basic metrics
        char_count = len(markdown)
        word_count = len(words)
        line_count = len(lines)
        
        # Structure analysis
        headings = self._extract_headings(markdown)
        heading_count = len(headings)
        list_count = self._count_lists(lines)
        table_count = self._count_tables(markdown)
        link_count = len(re.findall(r'\[.*?\]\(.*?\)', markdown))
        image_count = len(re.findall(r'!\[.*?\]\(.*?\)', markdown))
        
        # Content analysis
        top_words = self._get_top_words(words, n=10)
        
        # Estimated reading time (average 200 words per minute)
        reading_time = max(1, word_count // 200)
        
        return DocumentAnalysis(
            filepath='',  # Will be set by caller
            success=True,
            char_count=char_count,
            word_count=word_count,
            line_count=line_count,
            heading_count=heading_count,
            headings=headings,
            list_count=list_count,
            table_count=table_count,
            link_count=link_count,
            image_count=image_count,
            top_words=top_words,
            estimated_reading_time=reading_time
        )
    
    def _extract_headings(self, markdown: str) -> List[str]:
        """Extract all headings from markdown"""
        headings = []
        for line in markdown.split('\n'):
            if line.strip().startswith('#'):
                # Remove markdown heading syntax
                heading = re.sub(r'^#+\s*', '', line.strip())
                if heading:
                    headings.append(heading)
        return headings
    
    def _count_lists(self, lines: List[str]) -> int:
        """Count list items in markdown"""
        count = 0
        for line in lines:
            stripped = line.strip()
            # Unordered lists
            if stripped.startswith(('- ', '* ', '+ ')):
                count += 1
            # Ordered lists
            elif re.match(r'^\d+\.\s', stripped):
                count += 1
        return count
    
    def _count_tables(self, markdown: str) -> int:
        """Count tables in markdown"""
        # Tables have rows with pipe separators
        table_rows = [
            line for line in markdown.split('\n')
            if '|' in line and line.strip().startswith('|')
        ]
        
        # Approximate number of tables (separator rows start tables)
        separators = [
            row for row in table_rows
            if re.match(r'\|[\s:-]+\|', row)
        ]
        
        return len(separators)
    
    def _get_top_words(self, words: List[str], n: int = 10) -> List[tuple]:
        """Get top N most frequent words"""
        # Clean and filter words
        clean_words = []
        for word in words:
            # Remove punctuation and convert to lowercase
            word = re.sub(r'[^\w\s]', '', word.lower())
            # Filter out stopwords and short words
            if word and len(word) > 3 and word not in self.STOPWORDS:
                clean_words.append(word)
        
        # Count frequencies
        word_freq = Counter(clean_words)
        return word_freq.most_common(n)
    
    def print_analysis(self, analysis: DocumentAnalysis, detailed: bool = False):
        """Print analysis results"""
        print("\n" + "="*60)
        print("DOCUMENT ANALYSIS")
        print("="*60)
        print(f"File: {Path(analysis.filepath).name}")
        
        if not analysis.success:
            print(f"\n✗ Error: {analysis.error}")
            return
        
        print("\n📊 Content Metrics:")
        print(f"  Characters:          {analysis.char_count:,}")
        print(f"  Words:               {analysis.word_count:,}")
        print(f"  Lines:               {analysis.line_count:,}")
        print(f"  Estimated reading:   ~{analysis.estimated_reading_time} min")
        
        print("\n📋 Structure:")
        print(f"  Headings:            {analysis.heading_count}")
        print(f"  Lists:               {analysis.list_count} items")
        print(f"  Tables:              {analysis.table_count}")
        print(f"  Links:               {analysis.link_count}")
        print(f"  Images:              {analysis.image_count}")
        
        if detailed and analysis.headings:
            print("\n📑 Document Structure:")
            for i, heading in enumerate(analysis.headings[:10], 1):
                print(f"  {i}. {heading[:60]}")
            if len(analysis.headings) > 10:
                print(f"  ... and {len(analysis.headings) - 10} more")
        
        if analysis.top_words:
            print("\n🔤 Top Words:")
            for word, count in analysis.top_words:
                print(f"  {word:20} {count:4} times")
        
        if analysis.markdown_path:
            print(f"\n💾 Markdown saved to: {analysis.markdown_path}")
        
        print("="*60)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_document.py <filepath> [output_dir] [--detailed]")
        print("\nOptions:")
        print("  output_dir   Directory to save markdown (optional)")
        print("  --detailed   Show detailed analysis")
        print("\nExample:")
        print("  python analyze_document.py report.pdf")
        print("  python analyze_document.py report.pdf /mnt/user-data/outputs --detailed")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Parse optional arguments
    output_dir = None
    detailed = False
    
    for arg in sys.argv[2:]:
        if arg == '--detailed':
            detailed = True
        elif not arg.startswith('--'):
            output_dir = arg
    
    # Analyze document
    analyzer = DocumentAnalyzer(output_dir=output_dir)
    analysis = analyzer.analyze(filepath)
    analyzer.print_analysis(analysis, detailed=detailed)
    
    # Return exit code based on success
    sys.exit(0 if analysis.success else 1)


if __name__ == '__main__':
    main()
