#!/usr/bin/env python3
"""
Simple script to run the FAR HTML Parser with different options
"""

import sys
import os
from parser import FARHTMLParser

def main():
    """Main function with command line options"""
    
    # Default values
    input_file = "Part-52_html_9182025 (1)/Part-52_html/FAR_Part_52.html"
    output_dir = "output"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        print("\nUsage:")
        print(f"  python3 {sys.argv[0]} [input_file] [output_dir]")
        print(f"  python3 {sys.argv[0]} FAR_Part_52.html output")
        return 1
    
    print(f"Input file: {input_file}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    # Create and run parser
    try:
        parser = FARHTMLParser(input_file, output_dir)
        parser.parse()
        print("\n" + "=" * 50)
        print("SUCCESS: Parsing completed successfully!")
        print(f"Check the '{output_dir}' directory for the generated files.")
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
