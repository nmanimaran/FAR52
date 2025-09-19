#!/usr/bin/env python3
"""
FAR HTML Parser - Splits large FAR Part 52 HTML file into smaller, organized files
Following the naming convention: 52.XXX.html (main parts) and 52.XXX-Y.html (subparts)
"""

import re
import os
from pathlib import Path
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FARHTMLParser:
    def __init__(self, input_file: str, output_dir: str = "output"):
        """
        Initialize the FAR HTML Parser
        
        Args:
            input_file (str): Path to the large HTML file to parse
            output_dir (str): Directory to save the split files
        """
        self.input_file = input_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Regex patterns for identifying FAR clauses
        self.clause_id_pattern = re.compile(r'FAR_52_(\d+)_(\d+)')
        self.clause_number_pattern = re.compile(r'52\.(\d+)-(\d+)')
        
    def load_html(self) -> BeautifulSoup:
        """Load and parse the HTML file"""
        logger.info(f"Loading HTML file: {self.input_file}")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            logger.info("HTML file loaded successfully")
            return soup
            
        except Exception as e:
            logger.error(f"Error loading HTML file: {e}")
            raise
    
    def extract_html_template(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract HTML template components (head, styles, etc.)"""
        # Get the original doctype
        doctype = '<!DOCTYPE html>'
        if soup.contents and hasattr(soup.contents[0], 'string'):
            doctype_content = str(soup.contents[0]).strip()
            if doctype_content.startswith('<!DOCTYPE'):
                doctype = doctype_content
        
        template = {
            'doctype': doctype,
            'html_attrs': ' '.join([f'{k}="{v}"' for k, v in soup.html.attrs.items()]) if soup.html and soup.html.attrs else 'lang="en"',
            'head': str(soup.head) if soup.head else '<head><title>FAR Clause</title></head>',
            'body_attrs': ''
        }
        
        if soup.body and soup.body.attrs:
            template['body_attrs'] = ' '.join([f'{k}="{v}"' for k, v in soup.body.attrs.items()])
        
        return template
    
    def find_clause_articles(self, soup: BeautifulSoup) -> List[Dict]:
        """Find all clause articles in the HTML"""
        logger.info("Finding clause articles in HTML")
        
        clauses = []
        
        # Look for article elements with FAR clause IDs
        articles = soup.find_all('article', id=self.clause_id_pattern)
        
        for article in articles:
            clause_id = article.get('id', '')
            match = self.clause_id_pattern.match(clause_id)
            
            if match:
                part_num = match.group(1)
                subpart_num = match.group(2)
                clause_number = f"52.{part_num}-{subpart_num}"
                
                # Extract title from h1 element
                title_elem = article.find('h1', class_='title')
                title = "Unknown Title"
                
                if title_elem:
                    # Remove the clause number from the title
                    title_text = title_elem.get_text(strip=True)
                    # Remove the "52.XXX-Y" part from the beginning
                    title_clean = re.sub(r'^52\.\d+-\d+\s*', '', title_text)
                    if title_clean:
                        title = title_clean
                
                clause_info = {
                    'number': clause_number,
                    'part': part_num,
                    'subpart': subpart_num,
                    'title': title,
                    'article': article,
                    'id': clause_id
                }
                
                clauses.append(clause_info)
                logger.info(f"Found clause: {clause_number} - {title}")
        
        return clauses
    
    def create_html_file(self, template: Dict[str, str], clause: Dict) -> str:
        """Create a complete HTML file for a clause"""
        title = f"{clause['number']} {clause['title']}"
        
        # Update the head section with the correct title and metadata
        head_content = template['head']
        
        # Replace title
        head_content = re.sub(
            r'<title>.*?</title>', 
            f'<title>{title}</title>', 
            head_content, 
            flags=re.DOTALL
        )
        
        # Update DC.Identifier if present
        head_content = re.sub(
            r'<meta content="[^"]*" name="DC\.Identifier"/>',
            f'<meta content="{clause["id"]}" name="DC.Identifier"/>',
            head_content
        )
        
        # Create the complete HTML structure
        html_content = f"""{template['doctype']}
<html {template['html_attrs']}>
{head_content}
<body {template['body_attrs']}>
<main role="main">
{clause['article']}
</main>
</body>
</html>"""
        
        return html_content
    
    def save_individual_clauses(self, clauses: List[Dict], template: Dict[str, str]):
        """Save individual clause files in organized folders"""
        logger.info("Saving individual clause files in organized folders")
        
        for clause in clauses:
            # Create folder structure: output/52.203/52.203-2.html
            part_folder = f"52.{clause['part']}"
            part_dir = self.output_dir / part_folder
            part_dir.mkdir(exist_ok=True)
            
            filename = f"{clause['number']}.html"
            filepath = part_dir / filename
            
            html_content = self.create_html_file(template, clause)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            logger.info(f"Saved: {part_folder}/{filename}")
    
    def group_by_parts(self, clauses: List[Dict]) -> Dict[str, List[Dict]]:
        """Group clauses by their main part number"""
        parts = {}
        
        for clause in clauses:
            part_key = f"52.{clause['part']}"
            if part_key not in parts:
                parts[part_key] = []
            parts[part_key].append(clause)
        
        return parts
    
    def save_main_part_files(self, parts: Dict[str, List[Dict]], template: Dict[str, str]):
        """Save main part files containing all clauses for each part"""
        logger.info("Saving main part files")
        
        for part_key, part_clauses in parts.items():
            # Create the part folder
            part_dir = self.output_dir / part_key
            part_dir.mkdir(exist_ok=True)
            
            filename = f"{part_key}.html"
            filepath = part_dir / filename
            
            # Combine all clauses in this part
            combined_articles = ""
            for clause in part_clauses:
                combined_articles += f"\n{clause['article']}\n"
            
            title = f"FAR {part_key} - All Clauses"
            
            # Update head for combined file
            head_content = template['head']
            head_content = re.sub(
                r'<title>.*?</title>', 
                f'<title>{title}</title>', 
                head_content, 
                flags=re.DOTALL
            )
            
            html_content = f"""{template['doctype']}
<html {template['html_attrs']}>
{head_content}
<body {template['body_attrs']}>
<main role="main">
{combined_articles}
</main>
</body>
</html>"""
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(html_content)
            
            logger.info(f"Saved main part: {part_key}/{filename} ({len(part_clauses)} clauses)")
    
    def parse(self):
        """Main parsing method"""
        logger.info("Starting FAR HTML parsing")
        
        try:
            # Load the HTML file
            soup = self.load_html()
            
            # Extract HTML template
            template = self.extract_html_template(soup)
            
            # Find clause articles
            clauses = self.find_clause_articles(soup)
            
            if not clauses:
                logger.warning("No clauses found in the HTML file")
                return
            
            # Save individual clause files in folders
            self.save_individual_clauses(clauses, template)
            
            # Group by parts and save main part files
            parts = self.group_by_parts(clauses)
            self.save_main_part_files(parts, template)
            
            logger.info(f"Parsing complete! Generated {len(clauses)} individual files and {len(parts)} main part files")
            logger.info(f"Output directory: {self.output_dir.absolute()}")
            
        except Exception as e:
            logger.error(f"Error during parsing: {e}")
            raise

def main():
    """Main function to run the parser"""
    # Default input file path
    input_file = "Part-52_html_9182025 (1)/Part-52_html/FAR_Part_52.html"
    
    # Check if file exists
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return
    
    # Create parser and run
    parser = FARHTMLParser(input_file)
    parser.parse()

if __name__ == "__main__":
    main()
