"""
Sherlock GUI Module
A beautiful, modern, responsive CustomTkinter interface
for username hunting, phone number OSINT, and company searches.
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import re
import webbrowser

from sherlock_project.sherlock import sherlock, SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus, QueryResult
from sherlock_project.phone_search import PhoneOSINT
from sherlock_project.company_search import CompanyOSINT
from sherlock_project.reports import ReportGenerator

# Setup CustomTkinter Theme and Colors
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

class GUIQueryNotify(QueryNotify):
    """
    QueryNotify subclass to update the CustomTkinter GUI in real-time
    during username searches.
    """
    def __init__(self, update_callback, status_callback, finish_callback):
        super().__init__()
        self.update_callback = update_callback
        self.status_callback = status_callback
        self.finish_callback = finish_callback

    def start(self, message):
        self.status_callback(f"Zoeken naar gebruikersnaam: '{message}'...")

    def update(self, result: QueryResult):
        # Update progress and output results in GUI
        if result.status == QueryStatus.CLAIMED:
            self.update_callback(result.site_name, result.site_url_user, "Gevonden")
        elif result.status == QueryStatus.AVAILABLE:
            self.update_callback(result.site_name, result.site_url_user, "Niet Gevonden")
        elif result.status == QueryStatus.ILLEGAL:
            self.update_callback(result.site_name, result.site_url_user, "Ongeldige Gebruikersnaam")
        elif result.status == QueryStatus.WAF:
            self.update_callback(result.site_name, result.site_url_user, "Geblokkeerd (WAF/Cloudflare)")
        else:
            self.update_callback(result.site_name, result.site_url_user, "Onbekend / Fout")

    def finish(self):
        self.finish_callback()


class SherlockGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sherlock Professional OSINT Suite v0.16.1")
        self.geometry("1150x800")
        self.minsize(950, 650)

        # Main active variables
        self.search_results = {}
        self.username_dorks_results = {}
        self.phone_meta = {}
        self.phone_results = {}
        self.company_results = {}
        self.current_username = ""
        self.current_phone = ""
        self.current_company = ""
        self.search_thread = None
        self.searching = False

        # Load sites info
        try:
            self.sites = SitesInformation(
                os.path.join(os.path.dirname(__file__), "resources/data.json"),
                honor_exclusions=True
            )
        except Exception as e:
            messagebox.showerror("Fout bij laden sites", f"Kon data.json niet laden: {e}")
            self.sites = None

        # Build GUI layout
        self.create_widgets()

    def _on_link_click(self, event):
        """
        Handles click on the link in results textbox.
        """
        try:
            widget = event.widget
            index = widget.index(f"@{event.x},{event.y}")
            ranges = widget.tag_ranges("link")
            for i in range(0, len(ranges), 2):
                start = ranges[i]
                end = ranges[i+1]
                if widget.compare(start, "<=", index) and widget.compare(index, "<=", end):
                    url = widget.get(start, end).strip()
                    webbrowser.open(url)
                    break
        except Exception as e:
            print(f"Error opening link: {e}")

    def _insert_text(self, textbox, text):
        """
        Inserts text into the given textbox. Parses any URLs present, strips trailing punctuation, and tags them as 'link'.
        """
        textbox.configure(state="normal")

        # Regex to match URLs (HTTP/HTTPS)
        url_pattern = re.compile(r'(https?://[^\s\)]+)')

        parts = []
        last_idx = 0
        for match in url_pattern.finditer(text):
            start, end = match.span()
            matched_url = text[start:end]

            # Strip trailing punctuation if any
            stripped_url = matched_url.rstrip(".,?!;:)")
            stripped_len = len(stripped_url)
            extra_len = len(matched_url) - stripped_len

            # Text before url
            if start > last_idx:
                parts.append((text[last_idx:start], False))

            # Link part
            parts.append((stripped_url, True))

            # Trailing extra characters part (not link)
            if extra_len > 0:
                parts.append((matched_url[stripped_len:], False))

            last_idx = end

        if last_idx < len(text):
            parts.append((text[last_idx:], False))

        for part_text, is_link in parts:
            if is_link:
                start_index = textbox.index("insert")
                textbox.insert("insert", part_text)
                end_index = textbox.index("insert")
                textbox.tag_add("link", start_index, end_index)
            else:
                textbox.insert("insert", part_text)

        textbox.see("insert")
        textbox.configure(state="disabled")

    def _setup_textbox_tags(self, textbox):
        textbox.tag_config("link", foreground="#3182CE", underline=True)
        textbox.tag_bind("link", "<Button-1>", self._on_link_click)
        textbox.tag_bind("link", "<Enter>", lambda e: textbox.configure(cursor="hand2"))
        textbox.tag_bind("link", "<Leave>", lambda e: textbox.configure(cursor="xterm"))

    def _clear_textbox(self, textbox):
        textbox.configure(state="normal")
        textbox.delete("1.0", tk.END)
        textbox.configure(state="disabled")

    def _update_username_results_display(self):
        """
        Refreshes the username search results textbox, optionally filtering by query.
        """
        self._clear_textbox(self.text_username_results)

        # Initial status
        if self.current_username:
            self._insert_text(self.text_username_results, f"[*] Sherlock zoekopdracht resultaten voor '{self.current_username}':\n\n")

        filter_query = ""
        if hasattr(self, "entry_filter_username"):
            filter_query = self.entry_filter_username.get().strip().lower()

        claimed_count = 0
        display_count = 0

        for site, info in self.search_results.items():
            status_obj = info.get("status")
            status_str = ""
            if hasattr(status_obj, "status"):
                status_str = str(status_obj.status)
            else:
                status_str = str(status_obj)

            is_claimed = "claimed" in status_str.lower() or "exists" in status_str.lower() or "gevonden" in status_str.lower()
            if is_claimed:
                claimed_count += 1

            # Filter condition
            url_val = info.get("url_user") or ""
            if filter_query and (filter_query not in site.lower() and filter_query not in url_val.lower()):
                continue

            if is_claimed:
                self._insert_text(self.text_username_results, f"[+] {site}: {url_val}\n")
                display_count += 1
            elif self.all_sites_var.get():
                self._insert_text(self.text_username_results, f"[-] {site}: {status_str}\n")
                display_count += 1

        # Total line
        filter_suffix = f" (gefilterd, {display_count} getoond)" if filter_query else ""
        if not self.searching:
            self._insert_text(self.text_username_results, f"\n[*] Klaar! Totaal {claimed_count} accounts gedetecteerd{filter_suffix}.")

    def _update_username_dorks_display(self):
        """
        Refreshes the username advanced dorks results textbox.
        """
        self._clear_textbox(self.text_username_dorks)
        if not self.username_dorks_results:
            if self.searching:
                self._insert_text(self.text_username_dorks, "[*] Bezig met dorking zoekopdrachten...\n")
            else:
                self._insert_text(self.text_username_dorks, "Start een zoekopdracht om dorking resultaten te zien.\n")
            return

        for category, items in self.username_dorks_results.items():
            self._insert_text(self.text_username_dorks, f"[ {category.upper()} ]\n")
            if not items:
                self._insert_text(self.text_username_dorks, " Geen vermeldingen gevonden.\n\n")
            else:
                for item in items:
                    self._insert_text(self.text_username_dorks, f"• {item['title']}\n  Link: {item['url']}\n\n")

    def create_widgets(self):
        # Grid layout configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create Left Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Sidebar Title / Logo
        self.logo_label = ctk.CTkLabel(self.sidebar, text="SHERLOCK OSINT", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Sidebar Buttons for Switching Tabs
        self.btn_username_tab = ctk.CTkButton(self.sidebar, text="Gebruikersnaam Zoeken", command=self.show_username_tab)
        self.btn_username_tab.grid(row=1, column=0, padx=20, pady=10)

        self.btn_phone_tab = ctk.CTkButton(self.sidebar, text="Telefoonnummer Zoeken", command=self.show_phone_tab)
        self.btn_phone_tab.grid(row=2, column=0, padx=20, pady=10)

        self.btn_company_tab = ctk.CTkButton(self.sidebar, text="Bedrijven Zoeken", command=self.show_company_tab)
        self.btn_company_tab.grid(row=3, column=0, padx=20, pady=10)

        # Theme / Appearance controls
        self.theme_label = ctk.CTkLabel(self.sidebar, text="Thema:", font=ctk.CTkFont(size=12))
        self.theme_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        self.theme_combo = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_appearance_mode)
        self.theme_combo.grid(row=7, column=0, padx=20, pady=(5, 20))

        # Create Main Content Area
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create the Three Tabs
        self.create_username_tab()
        self.create_phone_tab()
        self.create_company_tab()

        # Show initial tab
        self.show_username_tab()

    def create_username_tab(self):
        self.tab_username = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_username.grid_rowconfigure(2, weight=1)
        self.tab_username.grid_columnconfigure(0, weight=1)

        # Title
        title_lbl = ctk.CTkLabel(self.tab_username, text="Hunt down Social Media Accounts", font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Controls row
        ctrl_frame = ctk.CTkFrame(self.tab_username)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_username = ctk.CTkEntry(ctrl_frame, placeholder_text="Voer een gebruikersnaam in (bijv. john_doe)...")
        self.entry_username.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_username.bind("<Return>", lambda e: self.start_username_search())

        self.btn_search_username = ctk.CTkButton(ctrl_frame, text="Start OSINT Zoekopdracht", width=160, command=self.start_username_search)
        self.btn_search_username.grid(row=0, column=1, padx=10, pady=10)

        # Options Row
        options_frame = ctk.CTkFrame(self.tab_username)
        options_frame.grid(row=1, column=1, sticky="ns", pady=10, padx=(10, 5))

        self.nsfw_var = tk.BooleanVar(value=False)
        self.chk_nsfw = ctk.CTkCheckBox(options_frame, text="Inclusief NSFW Sites", variable=self.nsfw_var)
        self.chk_nsfw.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.all_sites_var = tk.BooleanVar(value=False)
        self.chk_all_sites = ctk.CTkCheckBox(options_frame, text="Toon ook niet-gevonden", variable=self.all_sites_var, command=self._update_username_results_display)
        self.chk_all_sites.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Table & Output Area - SPLIT LAYOUT (Social Media & Advanced Dorks)
        output_frame = ctk.CTkFrame(self.tab_username)
        output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        output_frame.grid_rowconfigure(2, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Status & Progress indicators
        self.status_lbl = ctk.CTkLabel(output_frame, text="Klaar om te zoeken", font=ctk.CTkFont(size=13, weight="bold"))
        self.status_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=5)

        self.progress_bar = ctk.CTkProgressBar(output_frame)
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=15, pady=5)
        self.progress_bar.set(0)

        # Filter Panel inside output_frame
        filter_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
        filter_frame.grid_columnconfigure(1, weight=1)

        filter_lbl = ctk.CTkLabel(filter_frame, text="Snel Filter:", font=ctk.CTkFont(size=12, weight="bold"))
        filter_lbl.grid(row=0, column=0, padx=(0, 10), pady=2, sticky="w")

        self.entry_filter_username = ctk.CTkEntry(filter_frame, placeholder_text="Type om te filteren op platform of URL...")
        self.entry_filter_username.grid(row=0, column=1, sticky="ew", pady=2)
        self.entry_filter_username.bind("<KeyRelease>", lambda e: self._update_username_results_display())

        # Split Container
        username_splitter = ctk.CTkFrame(output_frame, fg_color="transparent")
        username_splitter.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=15, pady=10)
        username_splitter.grid_rowconfigure(0, weight=1)
        username_splitter.grid_columnconfigure(0, weight=1)
        username_splitter.grid_columnconfigure(1, weight=1)

        # Left panel: Accounts
        left_panel = ctk.CTkFrame(username_splitter)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        left_panel.grid_rowconfigure(1, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)

        left_lbl = ctk.CTkLabel(left_panel, text="Social Media Netwerken", font=ctk.CTkFont(size=13, weight="bold"))
        left_lbl.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.text_username_results = ctk.CTkTextbox(left_panel, font=ctk.CTkFont(family="Courier", size=13))
        self.text_username_results.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.text_username_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_username_results)

        # Right panel: Advanced Dorks
        right_panel = ctk.CTkFrame(username_splitter)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        right_lbl = ctk.CTkLabel(right_panel, text="Geavanceerde Dorking Web Mentions", font=ctk.CTkFont(size=13, weight="bold"))
        right_lbl.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.text_username_dorks = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(size=13))
        self.text_username_dorks.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.text_username_dorks.configure(state="disabled")
        self._setup_textbox_tags(self.text_username_dorks)

        # Export frame
        export_frame = ctk.CTkFrame(self.tab_username)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        export_lbl = ctk.CTkLabel(export_frame, text="Rapport Exporteren:", font=ctk.CTkFont(size=13, weight="bold"))
        export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt"))
        self.btn_export_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx"))
        self.btn_export_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_pdf = ctk.CTkButton(export_frame, text="PDF Rapport (Mooi)", fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf"))
        self.btn_export_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_phone_tab(self):
        self.tab_phone = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_phone.grid_rowconfigure(2, weight=1)
        self.tab_phone.grid_columnconfigure(0, weight=1)

        # Title
        title_lbl = ctk.CTkLabel(self.tab_phone, text="Telefoonnummer OSINT & Tracker", font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Controls row
        ctrl_frame = ctk.CTkFrame(self.tab_phone)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_phone = ctk.CTkEntry(ctrl_frame, placeholder_text="Voer telefoonnummer in (bijv. +31612345678 of 0612345678)...")
        self.entry_phone.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_phone.bind("<Return>", lambda e: self.start_phone_search())

        self.btn_search_phone = ctk.CTkButton(ctrl_frame, text="Start Telefoon OSINT", width=160, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_phone_search)
        self.btn_search_phone.grid(row=0, column=1, padx=10, pady=10)

        # Phone results layout with Metadata frame and Web mentions frame
        results_splitter = ctk.CTkFrame(self.tab_phone, fg_color="transparent")
        results_splitter.grid(row=2, column=0, sticky="nsew", pady=10)
        results_splitter.grid_rowconfigure(0, weight=1)
        results_splitter.grid_columnconfigure(0, weight=2) # Left column for metadata (lighter)
        results_splitter.grid_columnconfigure(1, weight=3) # Right column for internet links (heavier)

        # Left Metadata Panel
        meta_panel = ctk.CTkFrame(results_splitter)
        meta_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        meta_panel.grid_rowconfigure(1, weight=1)
        meta_panel.grid_columnconfigure(0, weight=1)

        meta_lbl = ctk.CTkLabel(meta_panel, text="Validatie & Metadata", font=ctk.CTkFont(size=14, weight="bold"))
        meta_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.text_phone_meta = ctk.CTkTextbox(meta_panel, font=ctk.CTkFont(size=13))
        self.text_phone_meta.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        self.text_phone_meta.configure(state="disabled")
        self._setup_textbox_tags(self.text_phone_meta)

        # Right Web Mentions Panel
        mentions_panel = ctk.CTkFrame(results_splitter)
        mentions_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        mentions_panel.grid_rowconfigure(1, weight=1)
        mentions_panel.grid_columnconfigure(0, weight=1)

        mentions_lbl = ctk.CTkLabel(mentions_panel, text="Geavanceerde Dorking Resultaten", font=ctk.CTkFont(size=14, weight="bold"))
        mentions_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.text_phone_mentions = ctk.CTkTextbox(mentions_panel, font=ctk.CTkFont(size=13))
        self.text_phone_mentions.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        self.text_phone_mentions.configure(state="disabled")
        self._setup_textbox_tags(self.text_phone_mentions)

        # Export row for phone searches
        export_frame = ctk.CTkFrame(self.tab_phone)
        export_frame.grid(row=3, column=0, sticky="ew", pady=10)

        export_lbl = ctk.CTkLabel(export_frame, text="Rapport Exporteren:", font=ctk.CTkFont(size=13, weight="bold"))
        export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_phone_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_phone=True))
        self.btn_export_phone_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_phone_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_phone=True))
        self.btn_export_phone_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_phone_pdf = ctk.CTkButton(export_frame, text="PDF Rapport (Mooi)", fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_phone=True))
        self.btn_export_phone_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_company_tab(self):
        self.tab_company = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_company.grid_rowconfigure(2, weight=1)
        self.tab_company.grid_columnconfigure(0, weight=1)

        # Title
        title_lbl = ctk.CTkLabel(self.tab_company, text="Bedrijven Informatie & OSINT Zoeken", font=ctk.CTkFont(size=22, weight="bold"))
        title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Controls row
        ctrl_frame = ctk.CTkFrame(self.tab_company)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_company = ctk.CTkEntry(ctrl_frame, placeholder_text="Voer een bedrijfsnaam in (bijv. ASML of Philips)...")
        self.entry_company.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_company.bind("<Return>", lambda e: self.start_company_search())

        # Country Filter
        self.country_filter_var = tk.StringVar(value="Alle")
        self.combo_country = ctk.CTkOptionMenu(ctrl_frame, variable=self.country_filter_var, values=["Alle", "Nederland", "Verenigd Koninkrijk", "België", "Duitsland", "Wereldwijd / LinkedIn"])
        self.combo_country.grid(row=0, column=1, padx=10, pady=10)

        self.btn_search_company = ctk.CTkButton(ctrl_frame, text="Start Bedrijf OSINT", width=160, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_company_search)
        self.btn_search_company.grid(row=0, column=2, padx=10, pady=10)

        # Company results layout (Split results)
        results_splitter = ctk.CTkFrame(self.tab_company, fg_color="transparent")
        results_splitter.grid(row=2, column=0, sticky="nsew", pady=10)
        results_splitter.grid_rowconfigure(0, weight=1)
        results_splitter.grid_columnconfigure(0, weight=1)

        # Results Panel
        results_panel = ctk.CTkFrame(results_splitter)
        results_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        results_panel.grid_rowconfigure(1, weight=1)
        results_panel.grid_columnconfigure(0, weight=1)

        results_lbl = ctk.CTkLabel(results_panel, text="Officiële Registers & Bedrijfsvermeldingen", font=ctk.CTkFont(size=14, weight="bold"))
        results_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.text_company_results = ctk.CTkTextbox(results_panel, font=ctk.CTkFont(size=13))
        self.text_company_results.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        self.text_company_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_company_results)

        # Export row for company searches
        export_frame = ctk.CTkFrame(self.tab_company)
        export_frame.grid(row=3, column=0, sticky="ew", pady=10)

        export_lbl = ctk.CTkLabel(export_frame, text="Rapport Exporteren:", font=ctk.CTkFont(size=13, weight="bold"))
        export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_company_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_company=True))
        self.btn_export_company_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_company_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_company=True))
        self.btn_export_company_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_company_pdf = ctk.CTkButton(export_frame, text="PDF Rapport (Mooi)", fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_company=True))
        self.btn_export_company_pdf.grid(row=0, column=3, padx=10, pady=10)

    # Navigation Tabs switching logic
    def show_username_tab(self):
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_username.grid(row=0, column=0, sticky="nsew")
        self.btn_username_tab.configure(fg_color="#1F538D") # Active tab color
        self.btn_phone_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_company_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def show_phone_tab(self):
        self.tab_username.grid_remove()
        self.tab_company.grid_remove()
        self.tab_phone.grid(row=0, column=0, sticky="nsew")
        self.btn_phone_tab.configure(fg_color="#1F538D") # Active tab color
        self.btn_username_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_company_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def show_company_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_company.grid(row=0, column=0, sticky="nsew")
        self.btn_company_tab.configure(fg_color="#1F538D") # Active tab color
        self.btn_username_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_phone_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    # Username Search logic
    def start_username_search(self):
        if self.searching:
            messagebox.showwarning("Zoeken bezig", "Er is momenteel al een zoekopdracht actief.")
            return

        username = self.entry_username.get().strip()
        if not username:
            messagebox.showwarning("Invoer ontbreekt", "Vul alsjeblieft een gebruikersnaam in.")
            return

        self.searching = True
        self.current_username = username
        self.search_results = {}
        self.username_dorks_results = {}
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self._clear_textbox(self.text_username_results)
        self._insert_text(self.text_username_results, f"[*] Initialiseren van Sherlock zoekopdracht voor '{username}'...\n\n")

        self._clear_textbox(self.text_username_dorks)
        self._insert_text(self.text_username_dorks, f"[*] Geavanceerde dorking wordt op de achtergrond uitgevoerd...\n")

        # Run search in background thread to keep UI responsive
        self.search_thread = threading.Thread(target=self._run_username_search, args=(username,), daemon=True)
        self.search_thread.start()

    def _run_username_search(self, username):
        # Prepare sites filtered on NSFW
        site_data_all = {site.name: site.information for site in self.sites} if self.sites else {}
        if not self.nsfw_var.get():
            # Filter nsfw sites out
            site_data = {k: v for k, v in site_data_all.items() if not v.get("isNSFW")}
        else:
            site_data = site_data_all

        # Hook GUI updater callback
        notify_obj = GUIQueryNotify(
            update_callback=self._on_search_result_found,
            status_callback=self._update_search_status,
            finish_callback=self._on_search_finished
        )

        try:
            # First perform the username advanced dorking
            p = PhoneOSINT()
            dorks = p.search_username_advanced_dorks(username)
            self.username_dorks_results = dorks
            self._update_username_dorks_display()

            # Run sherlock core username lookup
            results = sherlock(
                username=username,
                site_data=site_data,
                query_notify=notify_obj,
                timeout=15
            )
            self.search_results = results
        except Exception as e:
            self._update_search_status(f"Fout tijdens het zoeken: {e}")
            self._on_search_finished()

    def _on_search_result_found(self, site, url, status):
        # Insert result to the text box beautifully in real-time by updating self.search_results and refreshing display
        status_map = {
            "Gevonden": QueryStatus.CLAIMED,
            "Niet Gevonden": QueryStatus.AVAILABLE,
            "Ongeldige Gebruikersnaam": QueryStatus.ILLEGAL,
            "Geblokkeerd (WAF/Cloudflare)": QueryStatus.WAF
        }
        mapped_status = status_map.get(status, QueryStatus.UNKNOWN)

        self.search_results[site] = {
            "url_user": url,
            "status": QueryResult(
                username=self.current_username,
                site_name=site,
                site_url_user=url,
                status=mapped_status
            )
        }
        self._update_username_results_display()

    def _update_search_status(self, msg):
        self.status_lbl.configure(text=msg)

    def _on_search_finished(self):
        self.searching = False
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self._update_search_status("Zoekopdracht voltooid!")

        self._update_username_results_display()
        self._update_username_dorks_display()

        claimed_count = sum(
            1 for info in self.search_results.values()
            if "claimed" in str(getattr(info.get("status"), "status", info.get("status"))).lower() or "gevonden" in str(getattr(info.get("status"), "status", info.get("status"))).lower()
        )

        # Notify visually via popup
        self.after(100, lambda: messagebox.showinfo("Succes", f"Zoekopdracht voltooid!\nTotaal {claimed_count} accounts gevonden."))

    # Phone Search Logic
    def start_phone_search(self):
        phone_input = self.entry_phone.get().strip()
        if not phone_input:
            messagebox.showwarning("Invoer ontbreekt", "Vul alsjeblieft een telefoonnummer in.")
            return

        self.current_phone = phone_input
        self._clear_textbox(self.text_phone_meta)
        self._insert_text(self.text_phone_meta, "[*] Analyseren van telefoonnummer...\n")

        self._clear_textbox(self.text_phone_mentions)
        self._insert_text(self.text_phone_mentions, "[*] Zoeken met geavanceerde dorking methodes...\n")

        # Run phone OSINT in separate thread
        threading.Thread(target=self._run_phone_search, args=(phone_input,), daemon=True).start()

    def _run_phone_search(self, phone_str):
        p = PhoneOSINT()
        meta = p.validate_and_meta(phone_str)
        self.phone_meta = meta

        # Real-time display of metadata
        self._clear_textbox(self.text_phone_meta)
        if meta.get("valid"):
            self._insert_text(self.text_phone_meta, "✓ GELDIG TELEFOONNUMMER\n\n")
            self._insert_text(self.text_phone_meta, f"E.164 indeling:   {meta['e164']}\n")
            self._insert_text(self.text_phone_meta, f"Internationaal:   {meta['international']}\n")
            self._insert_text(self.text_phone_meta, f"Nationaal:        {meta['national']}\n")
            self._insert_text(self.text_phone_meta, f"Type Lijn:        {meta['type']}\n")
            self._insert_text(self.text_phone_meta, f"Provider:         {meta['carrier']}\n")
            self._insert_text(self.text_phone_meta, f"Geregistreerd in: {meta['location']}\n")
            self._insert_text(self.text_phone_meta, f"Tijdzones:        {', '.join(meta['timezones'])}\n")
        else:
            self._insert_text(self.text_phone_meta, "✗ ONGEDLIG NUMMER OF FOUTFOLDING\n\n")
            self._insert_text(self.text_phone_meta, f"Invoer: {phone_str}\n")
            self._insert_text(self.text_phone_meta, f"Error details: {meta.get('error') or 'Onbekende fout'}\n")

        # If invalid, abort internet mentions search
        if not meta.get("valid"):
            self._clear_textbox(self.text_phone_mentions)
            self._insert_text(self.text_phone_mentions, "Zoeken afgebroken vanwege ongeldig nummer format.")
            return

        # Perform advanced dorks search
        mentions = p.search_phone_advanced_dorks(meta)
        self.phone_results = mentions

        self._clear_textbox(self.text_phone_mentions)

        for category, items in mentions.items():
            self._insert_text(self.text_phone_mentions, f"[ {category.upper()} ]\n")
            if not items:
                self._insert_text(self.text_phone_mentions, " Geen vermeldingen gevonden.\n\n")
            else:
                for item in items:
                    self._insert_text(self.text_phone_mentions, f"• {item['title']}\n  Link: {item['url']}\n\n")

        self.after(100, lambda: messagebox.showinfo("Succes", "Telefoon OSINT & tracker dorking voltooid!"))

    # Company Search Logic
    def start_company_search(self):
        company_input = self.entry_company.get().strip()
        if not company_input:
            messagebox.showwarning("Invoer ontbreekt", "Vul alsjeblieft een bedrijfsnaam in.")
            return

        self.current_company = company_input
        self._clear_textbox(self.text_company_results)
        self._insert_text(self.text_company_results, f"[*] Zoeken naar bedrijf '{company_input}' via officiële registers...\n")

        # Run company OSINT in separate thread
        threading.Thread(target=self._run_company_search, args=(company_input,), daemon=True).start()

    def _run_company_search(self, company_str):
        co = CompanyOSINT()
        country_filter = self.country_filter_var.get()
        results = co.search_company(company_str, country_filter)
        self.company_results = results

        self._clear_textbox(self.text_company_results)
        total_hits = 0

        for country, items in results.items():
            self._insert_text(self.text_company_results, f"[ LAND: {country.upper()} ]\n")
            if not items:
                self._insert_text(self.text_company_results, " Geen vermeldingen gevonden in de geselecteerde registers.\n\n")
            else:
                for item in items:
                    register_name = item.get("register", "Onbekend Register")
                    self._insert_text(self.text_company_results, f"• [{register_name}] {item['title']}\n  Link: {item['url']}\n\n")
                    total_hits += 1

        self.after(100, lambda: messagebox.showinfo("Succes", f"Bedrijf OSINT voltooid!\nTotaal {total_hits} register vermeldingen gevonden."))

    # Export Report Routing
    def export_results(self, file_format, is_phone=False, is_company=False):
        if is_phone:
            if not self.phone_meta:
                messagebox.showwarning("Geen data", "Er is nog geen telefoonnummer gezocht.")
                return
            target_name = self.phone_meta.get("e164") or "telefoon"
        elif is_company:
            if not self.company_results:
                messagebox.showwarning("Geen data", "Er is nog geen bedrijf gezocht.")
                return
            target_name = self.current_company
        else:
            if not self.search_results:
                messagebox.showwarning("Geen data", "Er is nog geen gebruikersnaam gezocht.")
                return
            target_name = self.current_username

        # Get file save location from user
        filetypes_map = {
            "txt": ("TXT Bestanden (*.txt)", "*.txt"),
            "docx": ("Microsoft Word (*.docx)", "*.docx"),
            "pdf": ("PDF Documenten (*.pdf)", "*.pdf")
        }

        extension = f".{file_format}"
        initial_filename = f"sherlock_rapport_{target_name}{extension}".replace("+", "")
        filepath = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=[filetypes_map[file_format]],
            initialfile=initial_filename,
            title="Sla het OSINT Rapport op"
        )

        if not filepath:
            return

        try:
            if file_format == "txt":
                if is_phone:
                    ReportGenerator.export_txt(filepath, "", {}, self.phone_meta, self.phone_results)
                elif is_company:
                    ReportGenerator.export_company_txt(filepath, self.current_company, self.company_results)
                else:
                    ReportGenerator.export_txt(filepath, self.current_username, self.search_results, username_dorks=self.username_dorks_results)
            elif file_format == "docx":
                if is_phone:
                    ReportGenerator.export_docx(filepath, "", {}, self.phone_meta, self.phone_results)
                elif is_company:
                    ReportGenerator.export_company_docx(filepath, self.current_company, self.company_results)
                else:
                    ReportGenerator.export_docx(filepath, self.current_username, self.search_results, username_dorks=self.username_dorks_results)
            elif file_format == "pdf":
                if is_phone:
                    ReportGenerator.export_pdf(filepath, "", {}, self.phone_meta, self.phone_results)
                elif is_company:
                    ReportGenerator.export_company_pdf(filepath, self.current_company, self.company_results)
                else:
                    ReportGenerator.export_pdf(filepath, self.current_username, self.search_results, username_dorks=self.username_dorks_results)

            messagebox.showinfo("Export Voltooid", f"Het rapport is succesvol opgeslagen:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Mislukt", f"Fout bij opslaan rapport: {e}")


def main():
    app = SherlockGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
