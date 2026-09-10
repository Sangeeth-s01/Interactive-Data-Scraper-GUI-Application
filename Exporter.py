"""
Export Module
Handles data export to CSV and Excel formats
"""

import pandas as pd
import os
from datetime import datetime
from typing import List

class DataExporter:
    """Handles data export operations"""
    
    def __init__(self):
        self.default_dir = os.path.expanduser("~/Downloads")
    
    def export_to_csv(self, dataframes: List[pd.DataFrame], filepath: str):
        """
        Export DataFrame(s) to CSV file
        
        Args:
            dataframes (list): List of DataFrames to export
            filepath (str): Output file path
            
        Returns:
            bool: True if successful
        """
        try:
            if not dataframes:
                raise ValueError("No data to export")
            
            if len(dataframes) == 1:
                # Single DataFrame
                dataframes[0].to_csv(filepath, index=False, encoding='utf-8')
            else:
                # Multiple DataFrames - create directory
                base_name = os.path.splitext(filepath)[0]
                os.makedirs(base_name, exist_ok=True)
                
                for i, df in enumerate(dataframes):
                    table_file = os.path.join(base_name, f"table_{i+1}.csv")
                    df.to_csv(table_file, index=False, encoding='utf-8')
            
            return True
            
        except PermissionError:
            raise PermissionError(f"Permission denied. Please close the file if open: {filepath}")
        except Exception as e:
            raise Exception(f"Failed to export CSV: {str(e)}")
    
    def export_to_excel(self, dataframes: List[pd.DataFrame], filepath: str):
        """
        Export DataFrame(s) to Excel file
        
        Args:
            dataframes (list): List of DataFrames to export
            filepath (str): Output file path
            
        Returns:
            bool: True if successful
        """
        try:
            if not dataframes:
                raise ValueError("No data to export")
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for i, df in enumerate(dataframes):
                    # Limit sheet name to 31 characters (Excel limitation)
                    sheet_name = f"Table_{i+1}"[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Auto-adjust column widths
                for sheet in writer.sheets:
                    worksheet = writer.sheets[sheet]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return True
            
        except PermissionError:
            raise PermissionError(f"Permission denied. Please close the file if open: {filepath}")
        except ImportError:
            raise ImportError("Openpyxl library required for Excel export. Install with: pip install openpyxl")
        except Exception as e:
            raise Exception(f"Failed to export Excel: {str(e)}")
    
    def generate_filename(self, base_name: str, format_type: str) -> str:
        """
        Generate timestamped filename
        
        Args:
            base_name (str): Base name for file
            format_type (str): 'csv' or 'excel'
            
        Returns:
            str: Generated filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = '.csv' if format_type == 'csv' else '.xlsx'
        
        # Clean base name
        clean_name = ''.join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')[:50]
        
        filename = f"{clean_name}_{timestamp}{extension}"
        return os.path.join(self.default_dir, filename)