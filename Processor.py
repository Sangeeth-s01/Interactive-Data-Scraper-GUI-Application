"""
Data Processing Module
Handles conversion and cleaning of extracted data
"""

import pandas as pd
import numpy as np
from typing import List, Optional

class DataProcessor:
    """Handles data processing and DataFrame operations"""
    
    def __init__(self):
        self.dataframes = []
    
    def convert_to_dataframes(self, tables):
        """
        Convert extracted HTML tables to pandas DataFrames
        
        Args:
            tables (list): List of BeautifulSoup table objects
            
        Returns:
            list: List of pandas DataFrames
        """
        dataframes = []
        
        for i, table in enumerate(tables):
            try:
                # Extract raw data from table
                table_data = self._extract_table_data(table)
                
                if not table_data:
                    continue
                
                # Convert to DataFrame
                df = self._create_dataframe(table_data)
                
                # Clean the DataFrame
                df = self.clean_dataframe(df)
                
                if not df.empty:
                    dataframes.append(df)
                    
            except Exception as e:
                print(f"Error processing table {i}: {str(e)}")
                continue
        
        return dataframes
    
    def _extract_table_data(self, table):
        """Extract data from HTML table"""
        data = []
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:  # Skip empty rows
                data.append(row_data)
        
        return data
    
    def _create_dataframe(self, table_data):
        """
        Create DataFrame from table data with header detection
        
        Args:
            table_data (list): List of rows
            
        Returns:
            pandas.DataFrame
        """
        if not table_data:
            return pd.DataFrame()
        
        # Try to detect if first row is header
        is_header = self._detect_header(table_data)
        
        if is_header and len(table_data) > 1:
            # Use first row as header
            header = table_data[0]
            data = table_data[1:]
            
            # Create DataFrame with column names
            df = pd.DataFrame(data, columns=header)
        else:
            # Use default column names
            max_cols = max(len(row) for row in table_data)
            column_names = [f"Column_{i+1}" for i in range(max_cols)]
            df = pd.DataFrame(table_data, columns=column_names)
        
        return df
    
    def _detect_header(self, table_data):
        """
        Detect if first row is a header row
        
        Criteria:
        1. First row has fewer numeric values than subsequent rows
        2. First row has more string values than subsequent rows
        """
        if len(table_data) < 2:
            return False
        
        first_row = table_data[0]
        
        # Check if first row contains mostly strings
        string_count = sum(1 for cell in first_row if isinstance(cell, str) and not self._is_numeric(cell))
        
        # Check second row for comparison
        if len(table_data) > 1:
            second_row = table_data[1]
            second_string_count = sum(1 for cell in second_row if isinstance(cell, str) and not self._is_numeric(cell))
            
            # If first row has significantly more strings, it's likely a header
            if string_count > second_string_count * 1.5:
                return True
        
        return string_count > len(first_row) * 0.7  # More than 70% strings
    
    def _is_numeric(self, value):
        """Check if a string can be converted to numeric"""
        try:
            float(value.replace(',', '').replace('%', ''))
            return True
        except (ValueError, TypeError):
            return False
    
    def clean_dataframe(self, df):
        """
        Clean and preprocess DataFrame
        
        Args:
            df (pandas.DataFrame): Input DataFrame
            
        Returns:
            pandas.DataFrame: Cleaned DataFrame
        """
        if df.empty:
            return df
        
        # Make a copy to avoid modifying original
        df_clean = df.copy()
        
        # Remove completely empty rows and columns
        df_clean = df_clean.dropna(how='all')
        df_clean = df_clean.dropna(axis=1, how='all')
        
        # Reset index
        df_clean = df_clean.reset_index(drop=True)
        
        # Clean column names
        df_clean.columns = [self._clean_column_name(col) for col in df_clean.columns]
        
        # Convert numeric columns where possible
        for col in df_clean.columns:
            # Try to convert to numeric
            df_clean[col] = pd.to_numeric(df_clean[col], errors='ignore')
        
        return df_clean
    
    def _clean_column_name(self, name):
        """Clean column name string"""
        if not isinstance(name, str):
            name = str(name)
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Replace problematic characters
        name = name.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Limit length
        if len(name) > 50:
            name = name[:47] + "..."
        
        return name.strip()
    
    def merge_dataframes(self, dataframes):
        """
        Merge multiple DataFrames horizontally or vertically
        
        Args:
            dataframes (list): List of DataFrames
            
        Returns:
            pandas.DataFrame: Merged DataFrame
        """
        if not dataframes:
            return pd.DataFrame()
        
        if len(dataframes) == 1:
            return dataframes[0]
        
        # Try to merge based on similar columns
        try:
            # Check if DataFrames have same columns
            first_cols = set(dataframes[0].columns)
            same_columns = all(set(df.columns) == first_cols for df in dataframes[1:])
            
            if same_columns:
                # Vertical concatenation
                return pd.concat(dataframes, ignore_index=True)
            else:
                # Horizontal concatenation (with same number of rows)
                row_counts = [len(df) for df in dataframes]
                if len(set(row_counts)) == 1:  # All have same row count
                    return pd.concat(dataframes, axis=1)
                else:
                    return dataframes[0]  # Return first if can't merge
        except:
            return dataframes[0]