"""
Utility Module
Helper functions for the application
"""

import re
import pandas as pd
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid
    """
    if not url:
        return False
    
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)

def format_file_size(bytes_size: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        bytes_size (int): Size in bytes
        
    Returns:
        str: Formatted size
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        
    Returns:
        str: Truncated text
    """
    if not isinstance(text, str):
        text = str(text)
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def create_sample_data():
    """
    Create sample DataFrame for testing
    
    Returns:
        pandas.DataFrame: Sample data
    """
    data = {
        'Country': ['USA', 'China', 'Japan', 'Germany', 'India'],
        'GDP (Trillions)': [21.43, 14.34, 5.08, 3.86, 2.87],
        'Population (Millions)': [331, 1441, 126, 83, 1380],
        'GDP per Capita': [64796, 10261, 40247, 46445, 2100]
    }
    
    return pd.DataFrame(data)

def get_website_name(url: str) -> str:
    """
    Extract website name from URL
    
    Args:
        url (str): Full URL
        
    Returns:
        str: Website name
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Remove www. and get base domain
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Split by dots and get first part
    name = domain.split('.')[0]
    
    # Capitalize first letter
    return name.capitalize()