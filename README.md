# FAR HTML Parser

A Python tool to split large FAR (Federal Acquisition Regulation) HTML files into smaller, organized files following the FAR numbering convention.

## Features

- **Automatic Clause Detection**: Identifies FAR clauses using regex patterns (52.XXX-Y format)
- **Dual Output Format**: Creates both individual clause files and consolidated part files
- **Proper HTML Structure**: Each output file is a complete, standalone HTML document
- **Organized File Naming**: Follows FAR convention (52.203-2.html, 52.203.html, etc.)
- **Progress Logging**: Detailed logging of the parsing process
- **Error Handling**: Robust error handling with informative messages

## File Structure

```
HTML_Parser/
├── parser.py           # Main parser class
├── run_parser.py       # Simple command-line runner
├── README.md          # This documentation
└── output/            # Generated files (created after running)
    ├── 52.203-2.html  # Individual clause files
    ├── 52.203-3.html
    ├── 52.203.html    # Main part file (all 52.203-X clauses)
    └── ...
```

## Usage

### Basic Usage

```bash
# Run with default settings
python3 parser.py

# Or use the runner script
python3 run_parser.py
```

### Custom Input/Output

```bash
# Specify custom input file and output directory
python3 run_parser.py path/to/your/file.html custom_output_dir
```

### Programmatic Usage

```python
from parser import FARHTMLParser

# Create parser instance
parser = FARHTMLParser("input_file.html", "output_directory")

# Run the parsing
parser.parse()
```

## Output Files

The parser generates two types of files:

### Individual Clause Files
- **Format**: `52.XXX-Y.html`
- **Content**: Single FAR clause with complete HTML structure
- **Example**: `52.203-2.html` contains "Certificate of Independent Price Determination"

### Main Part Files
- **Format**: `52.XXX.html`
- **Content**: All clauses for a specific part number
- **Example**: `52.203.html` contains all clauses from 52.203-1 through 52.203-19

## Requirements

- Python 3.6+
- BeautifulSoup4 (`python3-bs4` package on Ubuntu/Debian)

### Installation on Ubuntu/Debian

```bash
sudo apt install python3-bs4
```

### Installation with pip

```bash
pip install beautifulsoup4
```

## How It Works

1. **HTML Loading**: Loads the large FAR HTML file using BeautifulSoup
2. **Pattern Recognition**: Uses regex to identify clause boundaries (52.XXX-Y format)
3. **Content Extraction**: Extracts clause content between start markers and "End of provision/clause" markers
4. **HTML Generation**: Creates complete HTML documents with proper structure
5. **File Organization**: Saves files using FAR naming convention

## Example Output

After running the parser on a FAR Part 52 file, you'll get:

```
output/
├── 52.203-2.html    # Certificate of Independent Price Determination
├── 52.203-3.html    # Gratuities
├── 52.203.html      # All 52.203 clauses combined
├── 52.204-7.html    # System for Award Management
├── 52.204.html      # All 52.204 clauses combined
└── ... (hundreds more files)
```

## Logging

The parser provides detailed logging:

```
2025-09-18 14:01:38,282 - INFO - Starting FAR HTML parsing
2025-09-18 14:01:38,282 - INFO - Loading HTML file: FAR_Part_52.html
2025-09-18 14:01:38,751 - INFO - HTML file loaded successfully
2025-09-18 14:01:38,752 - INFO - Extracting clauses from HTML content
2025-09-18 14:01:38,968 - INFO - Extracted clause: 52.201-1 - [Reserved]
...
2025-09-18 14:02:02,930 - INFO - Parsing complete! Generated 613 individual files and 32 main part files
```

## Troubleshooting

### Common Issues

1. **File Not Found**: Ensure the input HTML file path is correct
2. **Permission Errors**: Make sure you have write permissions for the output directory
3. **Memory Issues**: For very large files, the parser loads everything into memory

### Getting Help

If you encounter issues:

1. Check the log output for specific error messages
2. Verify the input file is a valid HTML file
3. Ensure all dependencies are installed
4. Check file permissions

## Technical Details

- **Regex Pattern**: `^52\.(\d+)-(\d+)\s+(.+?)\.?$` for clause identification
- **End Markers**: `\(End of (provision|clause)\)` for clause boundaries
- **HTML Parser**: BeautifulSoup4 with default parser
- **File Encoding**: UTF-8 for all input/output operations

## License

This tool is provided as-is for processing FAR documentation. Please ensure compliance with any applicable regulations when using FAR content.
