"""
Web Scraping Module
Handles HTTP requests and HTML parsing for table extraction
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
import time

class TableScraper:
    """Handles web scraping operations"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 30
        self.max_retries = 3
    
    def fetch_webpage(self, url):
        """
        Fetch webpage content with error handling
        
        Args:
            url (str): URL to fetch
            
        Returns:
            BeautifulSoup object or None
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'text/html' not in content_type:
                    raise ValueError(f"URL does not contain HTML content. Content-Type: {content_type}")
                
                # Parse HTML with BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    raise ConnectionError(f"Request timed out after {self.timeout} seconds")
                time.sleep(1)  # Wait before retry
                
            except requests.exceptions.HTTPError as e:
                raise ConnectionError(f"HTTP Error: {e}")
                
            except requests.exceptions.ConnectionError:
                raise ConnectionError("Failed to connect. Check internet connection and URL.")
                
            except Exception as e:
                raise ConnectionError(f"Failed to fetch webpage: {str(e)}")
        
        return None
    
    def extract_tables(self, soup):
        """
        Extract all HTML tables from BeautifulSoup object
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            
        Returns:
            list: List of BeautifulSoup table objects
        """
        if not soup:
            return []
        
        tables = soup.find_all('table')
        
        # Filter out tables that are likely not data tables
        data_tables = []
        for table in tables:
            # Check if table has at least one row and column
            rows = table.find_all('tr')
            if len(rows) > 0:
                # Check if any row has cells
                has_cells = any(len(row.find_all(['td', 'th'])) > 0 for row in rows)
                if has_cells:
                    data_tables.append(table)
        
        return data_tables
    
    def extract_table_data(self, table):
        """
        Extract data from a single HTML table
        
        Args:
            table (BeautifulSoup): Table element
            
        Returns:
            list: List of rows, each row is a list of cell data
        """
        data = []
        
        # Extract table rows
        rows = table.find_all('tr')
        
        for row in rows:
            # Get all cells (both th and td)
            cells = row.find_all(['td', 'th'])
            
            # Extract text from each cell, clean whitespace
            row_data = [self._clean_cell(cell) for cell in cells]
            
            if row_data:  # Only add non-empty rows
                data.append(row_data)
        
        return data
    
    def _clean_cell(self, cell):
        """
        Clean and extract text from a table cell
        
        Args:
            cell (BeautifulSoup): Cell element
            
        Returns:
            str: Cleaned cell content
        """
        # Remove script and style elements
        for element in cell(['script', 'style', 'noscript']):
            element.decompose()
        
        # Get text and clean
        text = cell.get_text(strip=True, separator=' ')
        
        # Replace multiple spaces with single space
        text = ' '.join(text.split())
        
        return text if text else ""