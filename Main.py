"""
Interactive Data Scraper - Main Application
Entry point for the desktop application
Author: Sangeeth S
Reg No: 12416188
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Gui import DataScraperGUI
from Scraper import TableScraper
from Processor import DataProcessor
from Exporter import DataExporter
from Utils import validate_url   

class InteractiveDataScraper:
    """Main application controller"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Interactive Data Scraper v1.0")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)

        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        self.scraper = TableScraper()
        self.processor = DataProcessor()
        self.exporter = DataExporter()

        self.gui = DataScraperGUI(self.root, self)

        self.current_dataframes = []
        self.current_url = ""

    def scrape_data(self, url):
        try:
            if not validate_url(url):
                raise ValueError("Please enter a valid URL (starting with http:// or https://)")

            self.current_url = url
            self.gui.update_status("Fetching webpage...", "info")

            soup = self.scraper.fetch_webpage(url)
            self.gui.update_status("Extracting tables...", "info")

            tables = self.scraper.extract_tables(soup)
            if not tables:
                raise ValueError("No HTML tables found on this webpage.")

            self.current_dataframes = self.processor.convert_to_dataframes(tables)
            self.gui.display_dataframes(self.current_dataframes)

            self.gui.update_status(
                f"Successfully extracted {len(self.current_dataframes)} table(s)", "success"
            )

        except Exception as e:
            self.gui.update_status(f"Error: {str(e)}", "error")
            messagebox.showerror("Error", str(e))

    def export_data(self, format_type, filepath):
        try:
            if not self.current_dataframes:
                raise ValueError("No data to export.")

            selected_index = self.gui.table_selector.current()
            df = self.current_dataframes[selected_index]
            
            if format_type == "csv":
                self.exporter.export_to_csv([df], filepath)
            elif format_type == "excel":
                self.exporter.export_to_excel([df], filepath)


            self.gui.update_status("Export completed successfully", "success")
            messagebox.showinfo("Success", "Data exported successfully")

        except Exception as e:
            self.gui.update_status(f"Export failed: {str(e)}", "error")
            messagebox.showerror("Export Error", str(e))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = InteractiveDataScraper()
    app.run()
