"""
GUI Module for Interactive Data Scraper
Modern UI + scrolling + column rename (stable)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd


class DataScraperGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.setup_styles()
        self.create_widgets()

    # --------------------------------------------------
    # STYLES
    # --------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        self.bg_white = "#FFFFFF"
        self.header_bg = "#F6F8FA"
        self.primary = "#22A06B"
        self.text = "#111827"

        self.root.configure(background=self.bg_white)

        style.configure(
            "Header.TLabel",
            background=self.bg_white,
            foreground=self.text,
            font=("Segoe UI", 16, "bold")
        )

        style.configure(
            "Primary.TButton",
            background=self.primary,
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 8),
            relief="flat"
        )

        style.map(
            "Primary.TButton",
            background=[("active", "#1E8E5A")]
        )

        style.configure(
            "Treeview",
            background=self.bg_white,
            fieldbackground=self.bg_white,
            foreground=self.text,
            rowheight=26,
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background=self.header_bg,
            foreground=self.text,
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )

        style.map(
            "Treeview",
            background=[("selected", "#D1FAE5")]
        )
    def _add_placeholder(self, entry, text):
        entry.insert(0, text)
        entry.config(foreground="#9CA3AF")  # light grey
        entry.placeholder_text = text

    def _on_focus_in(self, event):
        entry = event.widget
        if entry.get() == entry.placeholder_text:
            entry.delete(0, tk.END)
            entry.config(foreground="#111827")

    def _on_focus_out(self, event):
        entry = event.widget
        if not entry.get():
            entry.insert(0, entry.placeholder_text)
            entry.config(foreground="#9CA3AF")

    # --------------------------------------------------
    # UI
    # --------------------------------------------------
    def create_widgets(self):
        container = ttk.Frame(self.root, padding=20)
        container.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)

        # Title
        ttk.Label(
            container,
            text="Interactive Data Scraper",
            style="Header.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        # URL input
        url_frame = ttk.Frame(container)
        url_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        url_frame.columnconfigure(0, weight=1)

        self.url_entry = ttk.Entry(url_frame, font=("Segoe UI", 10))
        self.url_entry.grid(row=0, column=0, sticky="ew", ipady=6)
        self._add_placeholder(self.url_entry, "Paste your URL here")

        self.url_entry.bind("<FocusIn>", self._on_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_focus_out)
        ttk.Button(
            url_frame,
            text="Scrape",
            style="Primary.TButton",
            command=self.on_scrape
        ).grid(row=0, column=1, padx=(10, 0))

        # Action bar
        action_bar = ttk.Frame(container)
        action_bar.grid(row=2, column=0, sticky="w", pady=(0, 12))

        ttk.Button(
            action_bar,
            text="Export ▼",
            style="Primary.TButton",
            command=self.show_export_menu
        ).pack(side=tk.LEFT)

        self.table_selector = ttk.Combobox(
            action_bar,
            state="readonly",
            width=30
        )
        self.table_selector.pack(side=tk.LEFT, padx=12)
        self.table_selector.bind("<<ComboboxSelected>>", self.on_table_select)

        # ---------------- TABLE AREA ----------------
        table_frame = ttk.Frame(container)
        table_frame.grid(row=4, column=0, sticky="nsew")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        v_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        v_scroll.grid(row=0, column=1, sticky="ns")

        h_scroll = ttk.Scrollbar(
            table_frame,
            orient=tk.HORIZONTAL,
            command=self.tree.xview
        )
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.tree.configure(
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )

        self.tree.bind("<Double-1>", self.on_header_double_click)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            container,
            textvariable=self.status_var,
            background=self.bg_white,
            foreground="#374151",
            anchor=tk.W,
            padding=(6, 4)
        )
        self.status_bar.grid(row=5, column=0, sticky="ew", pady=(12, 0))

    # --------------------------------------------------
    # ACTIONS
    # --------------------------------------------------
    def on_scrape(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a website URL.")
            return
        self.controller.scrape_data(url)

    def show_export_menu(self):
        if not self.controller.current_dataframes:
            messagebox.showwarning("No Data", "Please scrape data first.")
            return

        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Export as CSV", command=lambda: self.on_export("csv"))
        menu.add_command(label="Export as Excel", command=lambda: self.on_export("excel"))

        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def on_export(self, fmt):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv" if fmt == "csv" else ".xlsx"
        )
        if path:
            self.controller.export_data(fmt, path)

    def on_table_select(self, event):
        idx = self.table_selector.current()
        if idx >= 0:
            self.display_dataframe(self.controller.current_dataframes[idx])

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------
    def display_dataframes(self, dfs):
        if not dfs:
            return

        self.table_selector["values"] = [f"Table {i+1}" for i in range(len(dfs))]
        self.table_selector.current(0)
        self.display_dataframe(dfs[0])

    def display_dataframe(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="w")

        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    # --------------------------------------------------
    # COLUMN RENAME (CUSTOM DIALOG)
    # --------------------------------------------------
    def open_rename_dialog(self, old_name):
        dialog = tk.Toplevel(self.root)
        dialog.title("Rename Column")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, False)
        dialog.geometry("650x160")

        ttk.Label(
            dialog,
            text="Edit column name:",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        entry = ttk.Entry(dialog, font=("Segoe UI", 10))
        entry.pack(fill="x", padx=15)
        entry.insert(0, old_name)
        entry.select_range(0, tk.END)
        entry.focus()

        result = {"value": None}

        def confirm():
            result["value"] = entry.get().strip()
            dialog.destroy()

        def cancel():
            dialog.destroy()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=15)

        ttk.Button(btn_frame, text="OK", command=confirm).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=cancel).pack(side=tk.LEFT)

        self.root.wait_window(dialog)
        return result["value"]

    def on_header_double_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "heading":
            return

        col_index = int(self.tree.identify_column(event.x)[1:]) - 1
        if col_index < 0:
            return

        old_name = self.tree["columns"][col_index]
        new_name = self.open_rename_dialog(old_name)

        if not new_name:
            return

        columns = list(self.tree["columns"])
        columns[col_index] = new_name
        self.tree["columns"] = columns

        df = self.controller.current_dataframes[self.table_selector.current()]
        df.columns = columns
        self.display_dataframe(df)

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------
    def update_status(self, message, msg_type="info"):
        self.status_var.set(message)
