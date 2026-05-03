#!/usr/bin/env python3
"""
Zendesk Voice Lines API GUI Console Application

A comprehensive GUI application for interacting with the Zendesk Voice Lines API.
Supports pagination, export to multiple formats (JSON, CSV, Excel), and advanced
navigation features.

Features:
- Connection testing with Zendesk API
- Paginated data retrieval from Voice Lines endpoint
- Export to JSON, CSV, and Excel formats
- Page navigation and preview
- Search functionality across pages
- Rate limit handling with automatic retry

Author: Codex Team
License: MIT
"""

import json
import os
import time
from dataclasses import dataclass, field
from tkinter import (
    Button,
    Entry,
    Frame,
    Label,
    Menu,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.constants import BOTH, BOTTOM, END, HORIZONTAL, LEFT, RIGHT, TOP, X, Y
from typing import Any

import requests


@dataclass
class ZendeskVoiceLinesConfig:
    """Configuration for Zendesk Voice Lines API."""

    subdomain: str
    base64_auth: str
    base_url: str = field(init=False)

    def __post_init__(self):
        """Initialize computed fields."""
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"

    def get_auth_header(self) -> dict[str, str]:
        """Get authorization header from base64 encoded credentials."""
        return {"Authorization": f"Basic {self.base64_auth}"}


class ZendeskVoiceLinesClient:
    """
    Zendesk Voice Lines API Client.

    Handles API requests to the Zendesk Voice Lines endpoint with pagination,
    rate limiting, and error handling.

    Rate Limits (as per Zendesk API documentation):
    - Team: 200 requests/minute
    - Growth/Professional: 400 requests/minute
    - Enterprise: 700 requests/minute
    - Enterprise Plus/High Volume: 2500 requests/minute

    Reference: https://developer.zendesk.com/api-reference/introduction/rate-limits/
    """

    def __init__(self, config: ZendeskVoiceLinesConfig):
        """
        Initialize the API client.

        Args:
            config: Zendesk Voice Lines configuration
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        self.session.headers.update(config.get_auth_header())

        # Track rate limiting
        self.rate_limit_remaining = None
        self.rate_limit_total = None

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """
        Handle rate limit headers from API response.

        Args:
            response: API response object
        """
        # Extract rate limit information from headers
        self.rate_limit_remaining = response.headers.get("X-Rate-Limit-Remaining")
        self.rate_limit_total = response.headers.get("X-Rate-Limit")

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise requests.exceptions.RequestException(
                f"Rate limit exceeded. Retry after {retry_after} seconds."
            )

    def test_connection(self) -> tuple[bool, str, int]:
        """
        Test connection to Zendesk API.

        Returns:
            Tuple of (success: bool, message: str, status_code: int)
        """
        try:
            url = f"{self.config.base_url}/channels/voice/lines.json"
            params = {"per_page": 1}
            response = self.session.get(url, params=params, timeout=10)
            self._handle_rate_limit(response)

            if response.status_code == 200:
                return (True, "Connection successful!", response.status_code)
            if response.status_code == 401:
                return (False, "Authentication failed. Check your credentials.", response.status_code)
            if response.status_code == 403:
                return (False, "Access forbidden. Check your API permissions.", response.status_code)
            return (
                False,
                f"Connection failed with status {response.status_code}",
                response.status_code,
            )
        except requests.exceptions.Timeout:
            return (False, "Connection timeout. Check your subdomain.", 0)
        except requests.exceptions.ConnectionError:
            return (False, "Connection error. Check your network and subdomain.", 0)
        except Exception as e:
            return (False, f"Error: {str(e)}", 0)

    def get_voice_lines(
        self,
        page: int = 1,
        per_page: int = 100,
        include_talk_embeddables: bool = True,
        include_digital_lines: bool = True,
        minimal_mode: bool = True,
    ) -> dict[str, Any]:
        """
        Get voice lines from Zendesk API.

        Args:
            page: Page number (1-indexed)
            per_page: Results per page (max 100)
            include_talk_embeddables: Include Talk embeddable widgets
            include_digital_lines: Include digital lines
            minimal_mode: Use minimal mode for faster responses

        Returns:
            API response as dictionary

        Raises:
            requests.exceptions.RequestException: On API errors
        """
        url = f"{self.config.base_url}/channels/voice/lines.json"
        params = {
            "page": page,
            "per_page": per_page,
            "include_talk_embeddables": str(include_talk_embeddables).lower(),
            "include_digital_lines": str(include_digital_lines).lower(),
            "minimal_mode": str(minimal_mode).lower(),
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            self._handle_rate_limit(response)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"API request failed: {str(e)}"
            ) from e

    def get_all_pages(
        self,
        per_page: int = 100,
        progress_callback: callable = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve all pages of voice lines data.

        Args:
            per_page: Results per page (max 100)
            progress_callback: Optional callback function(page, total_items)

        Returns:
            List of all pages (each page is a dict)
        """
        pages = []
        page = 1
        total_items = 0

        while True:
            try:
                data = self.get_voice_lines(page=page, per_page=per_page)
                pages.append(data)

                # Track total items
                if "lines" in data:
                    total_items += len(data.get("lines", []))

                # Call progress callback if provided
                if progress_callback:
                    progress_callback(page, total_items)

                # Check for next page
                next_page = data.get("next_page")
                if next_page is None:
                    break

                page += 1
                time.sleep(0.1)  # Small delay to respect rate limits

            except requests.exceptions.RequestException as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    # Wait and retry on rate limit
                    time.sleep(5)
                    continue
                raise

        return pages

    def download_greeting_file(
        self,
        greeting_path: str,
    ) -> bytes:
        """
        Download a greeting file (e.g., MP3) from Zendesk Voice API.

        Args:
            greeting_path: Path to greeting file (e.g., "29136121135501/74a7c698af52a08dc12eaa7b1c5dc31b.mp3")

        Returns:
            File content as bytes

        Raises:
            requests.exceptions.RequestException: On API errors
        """
        # Clean up path - remove leading slash if present
        greeting_path = greeting_path.lstrip("/")

        url = f"{self.config.base_url}/channels/voice/greetings/{greeting_path}"

        try:
            response = self.session.get(url, timeout=30)
            self._handle_rate_limit(response)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"File download failed: {str(e)}"
            ) from e


class ZendeskVoiceLinesGUI:
    """
    GUI Application for Zendesk Voice Lines API.

    Provides a user-friendly interface for:
    - Testing connection
    - Retrieving voice lines data
    - Navigating through pages
    - Searching data
    - Exporting to JSON/CSV/Excel
    """

    def __init__(self, root: Tk):
        """
        Initialize the GUI application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Zendesk Voice Lines API Client")
        self.root.geometry("1000x700")

        # Application state
        self.client: ZendeskVoiceLinesClient | None = None
        self.pages: list[dict[str, Any]] = []
        self.current_page_index: int = 0
        self.search_results: list[tuple[int, dict]] = []

        # Initialize UI
        self._create_menu()
        self._create_config_frame()
        self._create_download_frame()
        self._create_status_frame()
        self._create_preview_frame()
        self._create_navigation_frame()
        self._create_export_frame()

    def _create_menu(self):
        """Create application menu bar."""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export JSON", command=self._export_json)
        file_menu.add_command(label="Export CSV", command=self._export_csv)
        file_menu.add_command(label="Export Excel", command=self._export_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_docs)

    def _create_config_frame(self):
        """Create configuration input frame."""
        config_frame = Frame(self.root, padx=10, pady=10)
        config_frame.pack(side=TOP, fill=X)

        # Subdomain
        Label(config_frame, text="Subdomain:").grid(row=0, column=0, sticky="w", padx=5)
        self.subdomain_var = StringVar()
        subdomain_entry = Entry(config_frame, textvariable=self.subdomain_var, width=40)
        subdomain_entry.grid(row=0, column=1, padx=5, pady=5)
        Label(config_frame, text=".zendesk.com").grid(row=0, column=2, sticky="w")

        # Base64 Auth
        Label(config_frame, text="Base64 Auth:").grid(row=1, column=0, sticky="w", padx=5)
        self.auth_var = StringVar()
        auth_entry = Entry(config_frame, textvariable=self.auth_var, width=60, show="*")
        auth_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)

        # Info label
        info_label = Label(
            config_frame,
            text="Format: base64(email@domain.com/token:api_key)",
            font=("Arial", 8),
            fg="gray",
        )
        info_label.grid(row=2, column=1, sticky="w", padx=5)

        # Buttons
        button_frame = Frame(config_frame)
        button_frame.grid(row=3, column=1, pady=10)

        Button(
            button_frame,
            text="Test Connection",
            command=self._test_connection,
            bg="#4CAF50",
            fg="white",
            padx=10,
        ).pack(side=LEFT, padx=5)

        Button(
            button_frame,
            text="Get Voice Lines",
            command=self._get_voice_lines,
            bg="#2196F3",
            fg="white",
            padx=10,
        ).pack(side=LEFT, padx=5)

    def _create_download_frame(self):
        """Create file download frame."""
        download_frame = Frame(self.root, padx=10, pady=10, relief="groove", borderwidth=2)
        download_frame.pack(side=TOP, fill=X)

        # Title
        Label(download_frame, text="Download Greeting File:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=5, pady=(0, 5)
        )

        # Greeting path input
        Label(download_frame, text="Greeting Path:").grid(row=1, column=0, sticky="w", padx=5)
        self.greeting_path_var = StringVar()
        greeting_path_entry = Entry(download_frame, textvariable=self.greeting_path_var, width=60)
        greeting_path_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Info label with example
        info_label = Label(
            download_frame,
            text="Example: 29136121135501/74a7c698af52a08dc12eaa7b1c5dc31b.mp3",
            font=("Arial", 8),
            fg="gray",
        )
        info_label.grid(row=2, column=1, sticky="w", padx=5)

        # API info label
        api_label = Label(
            download_frame,
            text="API: /api/v2/channels/voice/greetings/{path}",
            font=("Arial", 8),
            fg="blue",
        )
        api_label.grid(row=3, column=1, sticky="w", padx=5)

        # Download button
        self.download_btn = Button(
            download_frame,
            text="Download File",
            command=self._download_greeting_file,
            bg="#E91E63",
            fg="white",
            padx=15,
            state="disabled",
        )
        self.download_btn.grid(row=1, column=3, padx=5)

        # Configure column weights for resizing
        download_frame.columnconfigure(1, weight=1)

    def _create_status_frame(self):
        """Create status display frame."""
        status_frame = Frame(self.root, padx=10, pady=5)
        status_frame.pack(side=TOP, fill=X)

        Label(status_frame, text="Status:").pack(side=LEFT)
        self.status_var = StringVar(value="Ready")
        status_label = Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 9, "bold"),
            fg="blue",
        )
        status_label.pack(side=LEFT, padx=10)

        # Progress bar
        self.progress_var = StringVar(value="")
        progress_label = Label(status_frame, textvariable=self.progress_var, fg="gray")
        progress_label.pack(side=RIGHT)

    def _create_preview_frame(self):
        """Create data preview frame."""
        preview_frame = Frame(self.root, padx=10, pady=5)
        preview_frame.pack(side=TOP, fill=BOTH, expand=True)

        Label(preview_frame, text="Data Preview:", font=("Arial", 10, "bold")).pack(
            side=TOP, anchor="w"
        )

        # Text widget with scrollbar
        text_frame = Frame(preview_frame)
        text_frame.pack(side=TOP, fill=BOTH, expand=True)

        scrollbar_y = Scrollbar(text_frame)
        scrollbar_y.pack(side=RIGHT, fill=Y)

        scrollbar_x = Scrollbar(text_frame, orient=HORIZONTAL)
        scrollbar_x.pack(side=BOTTOM, fill=X)

        self.preview_text = Text(
            text_frame,
            wrap="none",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            font=("Courier", 9),
        )
        self.preview_text.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar_y.config(command=self.preview_text.yview)
        scrollbar_x.config(command=self.preview_text.xview)

    def _create_navigation_frame(self):
        """Create page navigation frame."""
        nav_frame = Frame(self.root, padx=10, pady=10)
        nav_frame.pack(side=TOP, fill=X)

        # Page navigation
        Button(nav_frame, text="◄ Previous", command=self._prev_page).pack(side=LEFT, padx=5)

        self.page_info_var = StringVar(value="No data loaded")
        Label(nav_frame, textvariable=self.page_info_var, font=("Arial", 9)).pack(
            side=LEFT, padx=20
        )

        Button(nav_frame, text="Next ►", command=self._next_page).pack(side=LEFT, padx=5)

        # Page jump
        Label(nav_frame, text="Jump to page:").pack(side=LEFT, padx=10)
        self.page_jump_var = StringVar()
        page_jump_entry = Entry(nav_frame, textvariable=self.page_jump_var, width=5)
        page_jump_entry.pack(side=LEFT)
        Button(nav_frame, text="Go", command=self._jump_to_page).pack(side=LEFT, padx=5)

        # Search
        Label(nav_frame, text="Search:").pack(side=LEFT, padx=10)
        self.search_var = StringVar()
        search_entry = Entry(nav_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=LEFT)
        Button(nav_frame, text="Find", command=self._search_data).pack(side=LEFT, padx=5)

    def _create_export_frame(self):
        """Create export options frame."""
        export_frame = Frame(self.root, padx=10, pady=10)
        export_frame.pack(side=BOTTOM, fill=X)

        Label(export_frame, text="Export Options:", font=("Arial", 10, "bold")).pack(
            side=LEFT
        )

        self.export_json_btn = Button(
            export_frame,
            text="Export as JSON",
            command=self._export_json,
            state="disabled",
            bg="#FF9800",
            fg="white",
        )
        self.export_json_btn.pack(side=LEFT, padx=5)

        self.export_csv_btn = Button(
            export_frame,
            text="Export as CSV",
            command=self._export_csv,
            state="disabled",
            bg="#9C27B0",
            fg="white",
        )
        self.export_csv_btn.pack(side=LEFT, padx=5)

        self.export_excel_btn = Button(
            export_frame,
            text="Export as Excel",
            command=self._export_excel,
            state="disabled",
            bg="#009688",
            fg="white",
        )
        self.export_excel_btn.pack(side=LEFT, padx=5)

    def _test_connection(self):
        """Test connection to Zendesk API."""
        subdomain = self.subdomain_var.get().strip()
        auth = self.auth_var.get().strip()

        if not subdomain or not auth:
            messagebox.showerror("Error", "Please provide both subdomain and auth key.")
            return

        try:
            config = ZendeskVoiceLinesConfig(subdomain=subdomain, base64_auth=auth)
            client = ZendeskVoiceLinesClient(config)
            success, message, status_code = client.test_connection()

            if success:
                messagebox.showinfo(
                    "Connection Test",
                    f"{message}\nStatus Code: {status_code}",
                )
                self.status_var.set("Connected")
                self.client = client
                # Enable download button when connected
                self.download_btn.config(state="normal")
            else:
                messagebox.showerror(
                    "Connection Test Failed",
                    f"{message}\nStatus Code: {status_code}",
                )
                self.status_var.set("Connection failed")

        except Exception as e:
            messagebox.showerror("Error", f"Connection test failed: {str(e)}")
            self.status_var.set("Error")

    def _get_voice_lines(self):
        """Retrieve all voice lines data."""
        if not self.client:
            messagebox.showerror(
                "Error",
                "Please test connection first to initialize the client.",
            )
            return

        self.status_var.set("Fetching data...")
        self.progress_var.set("Starting...")
        self.root.update()

        try:

            def progress_callback(page: int, total_items: int):
                """Update progress display."""
                self.progress_var.set(f"Page {page} | Total items: {total_items}")
                self.root.update()

            self.pages = self.client.get_all_pages(progress_callback=progress_callback)

            if self.pages:
                self.current_page_index = 0
                self._display_current_page()
                self._enable_export_buttons()
                self.status_var.set(f"Loaded {len(self.pages)} page(s)")
                messagebox.showinfo(
                    "Success",
                    f"Retrieved {len(self.pages)} page(s) successfully!",
                )
            else:
                messagebox.showwarning("No Data", "No voice lines data found.")
                self.status_var.set("No data")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve data: {str(e)}")
            self.status_var.set("Error")
            self.progress_var.set("")

    def _display_current_page(self):
        """Display current page in preview."""
        if not self.pages:
            return

        self.preview_text.delete(1.0, END)
        page_data = self.pages[self.current_page_index]
        formatted_json = json.dumps(page_data, indent=2, sort_keys=True)
        self.preview_text.insert(1.0, formatted_json)

        total_pages = len(self.pages)
        self.page_info_var.set(f"Page {self.current_page_index + 1} of {total_pages}")

    def _prev_page(self):
        """Navigate to previous page."""
        if not self.pages:
            return

        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._display_current_page()

    def _next_page(self):
        """Navigate to next page."""
        if not self.pages:
            return

        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            self._display_current_page()

    def _jump_to_page(self):
        """Jump to specific page."""
        if not self.pages:
            return

        try:
            page_num = int(self.page_jump_var.get())
            if 1 <= page_num <= len(self.pages):
                self.current_page_index = page_num - 1
                self._display_current_page()
            else:
                messagebox.showerror(
                    "Error",
                    f"Invalid page number. Must be between 1 and {len(self.pages)}",
                )
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid page number.")

    def _search_data(self):
        """Search through all pages."""
        if not self.pages:
            messagebox.showwarning("No Data", "No data loaded to search.")
            return

        query = self.search_var.get().strip().lower()
        if not query:
            messagebox.showwarning("Search", "Please enter a search term.")
            return

        self.search_results = []

        for page_idx, page_data in enumerate(self.pages):
            page_json = json.dumps(page_data, indent=2).lower()
            if query in page_json:
                self.search_results.append((page_idx, page_data))

        if self.search_results:
            result_text = f"Found '{query}' in {len(self.search_results)} page(s)."
            if messagebox.askyesno("Search Results", f"{result_text}\n\nJump to first result?"):
                self.current_page_index = self.search_results[0][0]
                self._display_current_page()
        else:
            messagebox.showinfo("Search Results", f"No results found for '{query}'")

    def _enable_export_buttons(self):
        """Enable export buttons."""
        self.export_json_btn.config(state="normal")
        self.export_csv_btn.config(state="normal")
        self.export_excel_btn.config(state="normal")

    def _export_json(self):
        """Export data as JSON."""
        if not self.pages:
            messagebox.showwarning("No Data", "No data to export.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="zendesk_voice_lines.json",
        )

        if filename:
            try:
                # Combine all pages into single object
                combined_data = {
                    "metadata": {
                        "total_pages": len(self.pages),
                        "export_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    "pages": self.pages,
                }

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(combined_data, f, indent=2, sort_keys=True)

                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")

    def _export_csv(self):
        """Export data as CSV."""
        if not self.pages:
            messagebox.showwarning("No Data", "No data to export.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="zendesk_voice_lines.csv",
        )

        if filename:
            try:
                import csv

                # Flatten all voice lines from all pages
                all_lines = []
                for page in self.pages:
                    lines = page.get("lines", [])
                    all_lines.extend(lines)

                if not all_lines:
                    messagebox.showwarning("No Data", "No voice lines found to export.")
                    return

                # Get all unique keys for CSV headers
                all_keys = set()
                for line in all_lines:
                    all_keys.update(line.keys())

                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    writer.writerows(all_lines)

                messagebox.showinfo(
                    "Success",
                    f"Exported {len(all_lines)} records to {filename}",
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")

    def _export_excel(self):
        """Export data as Excel."""
        if not self.pages:
            messagebox.showwarning("No Data", "No data to export.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="zendesk_voice_lines.xlsx",
        )

        if filename:
            try:
                try:
                    import pandas as pd
                except ImportError:
                    messagebox.showerror(
                        "Missing Dependency",
                        "pandas is required for Excel export.\nInstall with: pip install pandas openpyxl",
                    )
                    return

                # Flatten all voice lines from all pages
                all_lines = []
                for page in self.pages:
                    lines = page.get("lines", [])
                    all_lines.extend(lines)

                if not all_lines:
                    messagebox.showwarning("No Data", "No voice lines found to export.")
                    return

                # Create DataFrame and export
                df = pd.DataFrame(all_lines)
                df.to_excel(filename, index=False, engine="openpyxl")

                messagebox.showinfo(
                    "Success",
                    f"Exported {len(all_lines)} records to {filename}",
                )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export Excel: {str(e)}")

    def _show_about(self):
        """Show about dialog."""
        about_text = """
Zendesk Voice Lines API Client
Version 1.0.0

A comprehensive GUI application for interacting with
the Zendesk Voice Lines API.

Features:
• Connection testing
• Paginated data retrieval
• Export to JSON, CSV, Excel
• Page navigation
• Search functionality
• Rate limit handling

Developed by: Codex Team
License: MIT
        """
        messagebox.showinfo("About", about_text)

    def _show_docs(self):
        """Show documentation reference."""
        docs_text = """
Documentation Resources:

1. Application User Guide:
   See: apps/dev/docs/USER_GUIDE.md

2. Development Guide:
   See: apps/dev/docs/DEVELOPMENT.md

3. Zendesk API Reference:
   https://developer.zendesk.com/api-reference/

4. Rate Limits Documentation:
   https://developer.zendesk.com/api-reference/introduction/rate-limits/

5. Pagination Guide:
   https://developer.zendesk.com/api-reference/introduction/pagination/
        """
        messagebox.showinfo("Documentation", docs_text)

    def _download_greeting_file(self):
        """Download a greeting file from Zendesk Voice API."""
        if not self.client:
            messagebox.showerror(
                "Error",
                "Please test connection first to initialize the client.",
            )
            return

        greeting_path = self.greeting_path_var.get().strip()
        if not greeting_path:
            messagebox.showerror("Error", "Please provide a greeting file path.")
            return

        try:
            self.status_var.set("Downloading file...")
            self.root.update()

            # Download file content
            file_content = self.client.download_greeting_file(greeting_path)

            # Extract filename from path
            filename = os.path.basename(greeting_path)
            if not filename:
                filename = "greeting_file.mp3"

            # Ask user where to save
            save_path = filedialog.asksaveasfilename(
                defaultextension=os.path.splitext(filename)[1] or ".mp3",
                initialfile=filename,
                filetypes=[
                    ("MP3 files", "*.mp3"),
                    ("Audio files", "*.mp3 *.wav *.ogg"),
                    ("All files", "*.*"),
                ],
            )

            if save_path:
                # Write file to disk
                with open(save_path, "wb") as f:
                    f.write(file_content)

                file_size_kb = len(file_content) / 1024
                messagebox.showinfo(
                    "Success",
                    f"File downloaded successfully!\n\n"
                    f"Location: {save_path}\n"
                    f"Size: {file_size_kb:.1f} KB",
                )
                self.status_var.set("File downloaded")
            else:
                self.status_var.set("Download cancelled")

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "404" in error_msg:
                messagebox.showerror(
                    "File Not Found",
                    f"The greeting file was not found.\n\n"
                    f"Please check the path:\n{greeting_path}",
                )
            elif "403" in error_msg:
                messagebox.showerror(
                    "Access Forbidden",
                    "You don't have permission to access this file.\n\n"
                    "Please check your API permissions.",
                )
            else:
                messagebox.showerror("Download Error", f"Failed to download file:\n\n{error_msg}")
            self.status_var.set("Download failed")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")
            self.status_var.set("Error")


def main():
    """Main entry point for the application."""
    root = Tk()
    _ = ZendeskVoiceLinesGUI(root)  # GUI needs to be instantiated but stored reference is unused
    root.mainloop()


if __name__ == "__main__":
    main()
