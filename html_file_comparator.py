#!/usr/bin/env python3
"""
HTML File Comparator Tool

This script compares two HTML files to determine if they are "the same thing"
using multiple analysis methods including exact matching, content similarity,
structural relationships, and detailed reporting.

Usage:
    python html_file_comparator.py file1.html file2.html
    
Example:
    python html_file_comparator.py HTML_Parser/output/52.203/52.203-1.html HTML_Parser/output/52.203/52.203.html
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup, NavigableString
import difflib


@dataclass
class ComparisonResult:
    """Data class to hold comparison results"""
    are_identical: bool
    are_same_thing: bool
    relationship: str
    similarity_score: float
    file1_stats: Dict
    file2_stats: Dict
    differences: List[str]
    summary: str


class HTMLComparator:
    """Main class for comparing HTML files"""
    
    def __init__(self, file1_path: str, file2_path: str):
        self.file1_path = Path(file1_path)
        self.file2_path = Path(file2_path)
        self.file1_content = None
        self.file2_content = None
        self.soup1 = None
        self.soup2 = None
        
    def load_files(self) -> bool:
        """Load and parse both HTML files"""
        try:
            # Read file contents
            with open(self.file1_path, 'r', encoding='utf-8') as f:
                self.file1_content = f.read()
            with open(self.file2_path, 'r', encoding='utf-8') as f:
                self.file2_content = f.read()
            
            # Parse HTML
            self.soup1 = BeautifulSoup(self.file1_content, 'html.parser')
            self.soup2 = BeautifulSoup(self.file2_content, 'html.parser')
            
            return True
        except Exception as e:
            print(f"Error loading files: {e}")
            return False
    
    def get_file_stats(self, content: str, soup: BeautifulSoup) -> Dict:
        """Get statistics about an HTML file"""
        return {
            'file_size_bytes': len(content.encode('utf-8')),
            'character_count': len(content),
            'line_count': len(content.splitlines()),
            'total_elements': len(soup.find_all()),
            'article_count': len(soup.find_all('article')),
            'heading_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
            'paragraph_count': len(soup.find_all('p')),
            'list_item_count': len(soup.find_all('li')),
        }
    
    def check_exact_match(self) -> bool:
        """Check if files are byte-for-byte identical"""
        hash1 = hashlib.md5(self.file1_content.encode('utf-8')).hexdigest()
        hash2 = hashlib.md5(self.file2_content.encode('utf-8')).hexdigest()
        return hash1 == hash2
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        return text
    
    def calculate_content_similarity(self) -> float:
        """Calculate similarity between text content of files"""
        text1 = self.extract_text_content(self.soup1)
        text2 = self.extract_text_content(self.soup2)
        
        # Use difflib to calculate similarity
        similarity = difflib.SequenceMatcher(None, text1, text2).ratio()
        return similarity
    
    def check_subset_relationship(self) -> Tuple[str, List[str]]:
        """Check if one file is a subset/superset of another"""
        # Extract all article IDs and titles
        articles1 = self.extract_articles(self.soup1)
        articles2 = self.extract_articles(self.soup2)
        
        differences = []
        
        if not articles1 and not articles2:
            return "no_articles", ["Neither file contains article elements"]
        
        if len(articles1) == len(articles2) == 0:
            return "equal_empty", []
        
        # Check if all articles from file1 are in file2
        articles1_ids = set(articles1.keys())
        articles2_ids = set(articles2.keys())
        
        if articles1_ids == articles2_ids:
            # Same articles, check content
            content_differences = []
            for article_id in articles1_ids:
                if articles1[article_id] != articles2[article_id]:
                    content_differences.append(f"Article {article_id} has different content")
            
            if content_differences:
                return "same_structure_different_content", content_differences
            else:
                return "identical_articles", []
        
        elif articles1_ids.issubset(articles2_ids):
            missing_in_file1 = articles2_ids - articles1_ids
            differences.append(f"File 1 is a subset of File 2. File 1 missing: {sorted(missing_in_file1)}")
            return "file1_subset_of_file2", differences
        
        elif articles2_ids.issubset(articles1_ids):
            missing_in_file2 = articles1_ids - articles2_ids
            differences.append(f"File 2 is a subset of File 1. File 2 missing: {sorted(missing_in_file2)}")
            return "file2_subset_of_file1", differences
        
        else:
            only_in_file1 = articles1_ids - articles2_ids
            only_in_file2 = articles2_ids - articles1_ids
            differences.extend([
                f"Only in File 1: {sorted(only_in_file1)}" if only_in_file1 else "",
                f"Only in File 2: {sorted(only_in_file2)}" if only_in_file2 else ""
            ])
            differences = [d for d in differences if d]  # Remove empty strings
            return "different_articles", differences
    
    def extract_articles(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract article information from HTML"""
        articles = {}
        for article in soup.find_all('article'):
            article_id = article.get('id', 'unknown')
            # Get the title from h4 element
            title_elem = article.find('h4')
            title = title_elem.get_text().strip() if title_elem else 'No title'
            articles[article_id] = title
        return articles
    
    def generate_detailed_differences(self) -> List[str]:
        """Generate detailed list of differences between files"""
        differences = []
        
        # File size comparison
        size1 = len(self.file1_content)
        size2 = len(self.file2_content)
        if size1 != size2:
            differences.append(f"File sizes differ: {size1} vs {size2} characters")
        
        # Article count comparison
        articles1 = self.extract_articles(self.soup1)
        articles2 = self.extract_articles(self.soup2)
        if len(articles1) != len(articles2):
            differences.append(f"Article counts differ: {len(articles1)} vs {len(articles2)}")
        
        # Title comparison
        title1 = self.soup1.find('title')
        title2 = self.soup2.find('title')
        title1_text = title1.get_text() if title1 else "No title"
        title2_text = title2.get_text() if title2 else "No title"
        if title1_text != title2_text:
            differences.append(f"Titles differ: '{title1_text}' vs '{title2_text}'")
        
        return differences
    
    def determine_relationship_summary(self, relationship: str, similarity: float, 
                                     is_identical: bool) -> Tuple[bool, str]:
        """Determine if files are 'the same thing' and generate summary"""
        
        if is_identical:
            return True, "Files are identical - they are exactly the same thing."
        
        if relationship == "file1_subset_of_file2":
            return True, ("File 1 is a subset of File 2. File 1 contains content that is "
                         "completely included in File 2, so they represent the same type of "
                         "content but File 2 is more comprehensive.")
        
        elif relationship == "file2_subset_of_file1":
            return True, ("File 2 is a subset of File 1. File 2 contains content that is "
                         "completely included in File 1, so they represent the same type of "
                         "content but File 1 is more comprehensive.")
        
        elif relationship == "identical_articles":
            return True, "Files contain identical articles - they are the same thing."
        
        elif similarity > 0.9:
            return True, f"Files are highly similar ({similarity:.1%}) - they are essentially the same thing."
        
        elif similarity > 0.5:
            return False, f"Files are moderately similar ({similarity:.1%}) but have significant differences."
        
        else:
            return False, f"Files are quite different ({similarity:.1%}) - they are not the same thing."
    
    def compare(self) -> ComparisonResult:
        """Perform comprehensive comparison of the two HTML files"""
        if not self.load_files():
            return None
        
        # Perform all comparisons
        is_identical = self.check_exact_match()
        similarity = self.calculate_content_similarity()
        relationship, rel_differences = self.check_subset_relationship()
        detailed_differences = self.generate_detailed_differences()
        
        # Get file statistics
        file1_stats = self.get_file_stats(self.file1_content, self.soup1)
        file2_stats = self.get_file_stats(self.file2_content, self.soup2)
        
        # Determine if they're "the same thing"
        are_same_thing, summary = self.determine_relationship_summary(
            relationship, similarity, is_identical
        )
        
        # Combine all differences
        all_differences = detailed_differences + rel_differences
        
        return ComparisonResult(
            are_identical=is_identical,
            are_same_thing=are_same_thing,
            relationship=relationship,
            similarity_score=similarity,
            file1_stats=file1_stats,
            file2_stats=file2_stats,
            differences=all_differences,
            summary=summary
        )


def print_comparison_report(result: ComparisonResult, file1_path: str, file2_path: str):
    """Print a detailed comparison report"""
    print("=" * 80)
    print("HTML FILE COMPARISON REPORT")
    print("=" * 80)
    print(f"File 1: {file1_path}")
    print(f"File 2: {file2_path}")
    print()
    
    # Main answer
    print("🔍 MAIN QUESTION: Are these files the same thing?")
    print(f"   Answer: {'YES' if result.are_same_thing else 'NO'}")
    print()
    
    # Summary
    print("📋 SUMMARY:")
    print(f"   {result.summary}")
    print()
    
    # Detailed results
    print("📊 DETAILED ANALYSIS:")
    print(f"   Identical files: {'Yes' if result.are_identical else 'No'}")
    print(f"   Content similarity: {result.similarity_score:.1%}")
    print(f"   Relationship: {result.relationship.replace('_', ' ').title()}")
    print()
    
    # File statistics
    print("📈 FILE STATISTICS:")
    print("   File 1:")
    for key, value in result.file1_stats.items():
        print(f"     {key.replace('_', ' ').title()}: {value:,}")
    print("   File 2:")
    for key, value in result.file2_stats.items():
        print(f"     {key.replace('_', ' ').title()}: {value:,}")
    print()
    
    # Differences
    if result.differences:
        print("🔍 DIFFERENCES FOUND:")
        for i, diff in enumerate(result.differences, 1):
            print(f"   {i}. {diff}")
    else:
        print("✅ NO SIGNIFICANT DIFFERENCES FOUND")
    
    print("=" * 80)


def main():
    """Main function to run the comparison tool"""
    if len(sys.argv) != 3:
        print("Usage: python html_file_comparator.py <file1.html> <file2.html>")
        print("\nExample:")
        print("python html_file_comparator.py HTML_Parser/output/52.203/52.203-1.html HTML_Parser/output/52.203/52.203.html")
        sys.exit(1)
    
    file1_path = sys.argv[1]
    file2_path = sys.argv[2]
    
    # Check if files exist
    if not os.path.exists(file1_path):
        print(f"Error: File '{file1_path}' not found.")
        sys.exit(1)
    
    if not os.path.exists(file2_path):
        print(f"Error: File '{file2_path}' not found.")
        sys.exit(1)
    
    # Perform comparison
    comparator = HTMLComparator(file1_path, file2_path)
    result = comparator.compare()
    
    if result is None:
        print("Error: Failed to compare files.")
        sys.exit(1)
    
    # Print report
    print_comparison_report(result, file1_path, file2_path)


if __name__ == "__main__":
    main()
