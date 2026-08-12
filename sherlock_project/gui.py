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
import json
import subprocess

from sherlock_project.sherlock import sherlock, SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus, QueryResult
from sherlock_project.phone_search import PhoneOSINT
from sherlock_project.company_search import CompanyOSINT
from sherlock_project.reports import ReportGenerator
from sherlock_project import __version__

# Setup CustomTkinter Theme and Colors
ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")

SETTINGS_FILE = os.path.expanduser("~/.sherlock_settings.json")

TRANSLATIONS = {
    "nl": {
        "title": "Sherlock Professional OSINT Suite",
        "tab_username": "Gebruikersnaam Zoeken",
        "tab_phone": "Telefoonnummer Zoeken",
        "tab_company": "Bedrijven Zoeken",
        "tab_settings": "Instellingen",
        "theme": "Thema:",
        "username_header": "Hunt down Social Media Accounts",
        "username_placeholder": "Voer een gebruikersnaam in (bijv. john_doe)...",
        "btn_start_osint": "Start OSINT Zoekopdracht",
        "nsfw_checkbox": "Inclusief NSFW Sites",
        "all_sites_checkbox": "Toon ook niet-gevonden",
        "ready_to_search": "Klaar om te zoeken",
        "searching_username": "Zoeken naar gebruikersnaam: '{message}'...",
        "fast_filter": "Snel Filter:",
        "filter_placeholder": "Type om te filteren op platform of URL...",
        "social_networks_header": "Social Media Netwerken",
        "dorking_header": "Geavanceerde Dorking Web Mentions",
        "export_report": "Rapport Exporteren:",
        "export_pdf": "PDF Rapport (Mooi)",
        "phone_header": "Telefoonnummer OSINT & Tracker",
        "phone_placeholder": "Voer telefoonnummer in (bijv. +31612345678 of 0612345678)...",
        "btn_start_phone": "Start Telefoon OSINT",
        "validation_metadata": "Validatie & Metadata",
        "advanced_dorks": "Geavanceerde Dorking Resultaten",
        "company_header": "Bedrijven Informatie & OSINT Zoeken",
        "company_placeholder": "Voer een bedrijfsnaam in (bijv. ASML of Philips)...",
        "btn_start_company": "Start Bedrijf OSINT",
        "registers_header": "Officiële Registers & Bedrijfsvermeldingen",
        "settings_title": "Applicatie Instellingen",
        "language_section": "Taal Selectie",
        "updates_section": "Applicatie Updates",
        "btn_check_updates": "Controleer op updates",
        "current_version": "Huidige versie",
        "latest_version": "Laatste versie",
        "update_status_idle": "Nog niet gecontroleerd",
        "update_status_checking": "Bezig met controleren op updates...",
        "update_status_up_to_date": "Applicatie is up-to-date!",
        "update_status_available": "Update beschikbaar!",
        "update_status_error": "Fout bij controleren van updates.",
        "update_prompt_title": "Update Beschikbaar",
        "update_prompt_msg": "Er is een nieuwe update beschikbaar op de master branch. Wilt u deze nu installeren en de applicatie opnieuw opstarten?",
        "update_success_title": "Update Succesvol",
        "update_success_msg": "De applicatie is succesvol geüpdatet naar de nieuwste versie op master! De applicatie start nu opnieuw op.",
        "error": "Fout",
        "success": "Succes",
        "search_active_warning": "Er is momenteel al een zoekopdracht actief.",
        "input_missing": "Invoer ontbreekt",
        "username_input_missing_msg": "Vul alsjeblieft een gebruikersnaam in.",
        "phone_input_missing_msg": "Vul alsjeblieft een telefoonnummer in.",
        "company_input_missing_msg": "Vul alsjeblieft een bedrijfsnaam in.",
        "search_finished": "Zoekopdracht voltooid!",
        "accounts_found_msg": "Zoekopdracht voltooid!\nTotaal {count} accounts gevonden.",
        "analyzing_phone": "[*] Analyseren van telefoonnummer...\n",
        "dorking_methods": "[*] Zoeken met geavanceerde dorking methodes...\n",
        "valid_phone": "✓ GELDIG TELEFOONNUMMER\n\n",
        "invalid_phone": "✗ ONGEDLIG NUMMER OF FOUTFOLDING\n\n",
        "phone_aborted": "Zoeken afgebroken vanwege ongeldig nummer format.",
        "company_searching": "[*] Zoeken naar bedrijf '{company}' via officiële registers...\n",
        "company_hits_found": "Bedrijf OSINT voltooid!\nTotaal {count} register vermeldingen gevonden.",
        "no_phone_search_yet": "Er is nog geen telefoonnummer gezocht.",
        "no_company_search_yet": "Er is nog geen bedrijf gezocht.",
        "no_username_search_yet": "Er is nog geen gebruikersnaam gezocht.",
        "save_osint_report": "Sla het OSINT Rapport op",
        "export_success": "Het rapport is succesvol opgeslagen:\n{filepath}",
        "export_failed": "Fout bij opslaan rapport: {error}",
        "all_countries": "Alle",
        "nl_country": "Nederland",
        "uk_country": "Verenigd Koninkrijk",
        "be_country": "België",
        "de_country": "Duitsland",
        "global_linkedin": "Wereldwijd / LinkedIn",
    },
    "en": {
        "title": "Sherlock Professional OSINT Suite",
        "tab_username": "Username Search",
        "tab_phone": "Phone Number Search",
        "tab_company": "Company Search",
        "tab_settings": "Settings",
        "theme": "Theme:",
        "username_header": "Hunt down Social Media Accounts",
        "username_placeholder": "Enter a username (e.g. john_doe)...",
        "btn_start_osint": "Start OSINT Search",
        "nsfw_checkbox": "Include NSFW Sites",
        "all_sites_checkbox": "Show not found sites",
        "ready_to_search": "Ready to search",
        "searching_username": "Searching for username: '{message}'...",
        "fast_filter": "Quick Filter:",
        "filter_placeholder": "Type to filter by platform or URL...",
        "social_networks_header": "Social Media Networks",
        "dorking_header": "Advanced Dorking Web Mentions",
        "export_report": "Export Report:",
        "export_pdf": "PDF Report (Beautiful)",
        "phone_header": "Phone Number OSINT & Tracker",
        "phone_placeholder": "Enter phone number (e.g. +31612345678 or 0612345678)...",
        "btn_start_phone": "Start Phone OSINT",
        "validation_metadata": "Validation & Metadata",
        "advanced_dorks": "Advanced Dorking Results",
        "company_header": "Company Info & OSINT Search",
        "company_placeholder": "Enter a company name (e.g. ASML or Philips)...",
        "btn_start_company": "Start Company OSINT",
        "registers_header": "Official Registers & Business Listings",
        "settings_title": "Application Settings",
        "language_section": "Language Selection",
        "updates_section": "Application Updates",
        "btn_check_updates": "Check for Updates",
        "current_version": "Current version",
        "latest_version": "Latest version",
        "update_status_idle": "Not checked yet",
        "update_status_checking": "Checking for updates...",
        "update_status_up_to_date": "Application is up-to-date!",
        "update_status_available": "Update available!",
        "update_status_error": "Error checking for updates.",
        "update_prompt_title": "Update Available",
        "update_prompt_msg": "A new update is available on the master branch. Do you want to install it now and restart the application?",
        "update_success_title": "Update Successful",
        "update_success_msg": "The application has been successfully updated to the latest master version! The application will now restart.",
        "error": "Error",
        "success": "Success",
        "search_active_warning": "A search is currently already active.",
        "input_missing": "Input missing",
        "username_input_missing_msg": "Please enter a username.",
        "phone_input_missing_msg": "Please enter a phone number.",
        "company_input_missing_msg": "Please enter a company name.",
        "search_finished": "Search finished!",
        "accounts_found_msg": "Search finished!\nTotal {count} accounts found.",
        "analyzing_phone": "[*] Analyzing phone number...\n",
        "dorking_methods": "[*] Searching with advanced dorking methods...\n",
        "valid_phone": "✓ VALID PHONE NUMBER\n\n",
        "invalid_phone": "✗ INVALID NUMBER OR ERROR\n\n",
        "phone_aborted": "Search aborted due to invalid number format.",
        "company_searching": "[*] Searching for company '{company}' via official registers...\n",
        "company_hits_found": "Company OSINT completed!\nTotal {count} register listings found.",
        "no_phone_search_yet": "No phone search has been conducted yet.",
        "no_company_search_yet": "No company search has been conducted yet.",
        "no_username_search_yet": "No username search has been conducted yet.",
        "save_osint_report": "Save the OSINT Report",
        "export_success": "The report was successfully saved:\n{filepath}",
        "export_failed": "Failed to save report: {error}",
        "all_countries": "All",
        "nl_country": "Netherlands",
        "uk_country": "United Kingdom",
        "be_country": "Belgium",
        "de_country": "Germany",
        "global_linkedin": "Worldwide / LinkedIn",
    }
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"language": "nl"}


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception:
        pass


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
        # Callback will handle localization using get_text
        self.status_callback(message)

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

        # Load persisted settings
        self.settings = load_settings()
        self.language_var = tk.StringVar(value=self.settings.get("language", "nl"))

        self.title(f"{self.get_text('title')} v{__version__}")
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

    def get_text(self, key):
        lang = self.language_var.get()
        return TRANSLATIONS.get(lang, TRANSLATIONS["nl"]).get(key, key)

    def change_language(self, language_name):
        new_lang = "en" if language_name == "English" else "nl"
        self.language_var.set(new_lang)
        self.settings["language"] = new_lang
        save_settings(self.settings)
        self.update_ui_texts()

    def update_ui_texts(self):
        # Update Window Title
        self.title(f"{self.get_text('title')} v{__version__}")

        # Update Sidebar buttons
        self.btn_username_tab.configure(text=self.get_text("tab_username"))
        self.btn_phone_tab.configure(text=self.get_text("tab_phone"))
        self.btn_company_tab.configure(text=self.get_text("tab_company"))
        self.btn_settings_tab.configure(text=self.get_text("tab_settings"))
        self.theme_label.configure(text=self.get_text("theme"))

        # Update Username Tab
        self.username_title_lbl.configure(text=self.get_text("username_header"))
        self.entry_username.configure(placeholder_text=self.get_text("username_placeholder"))
        self.btn_search_username.configure(text=self.get_text("btn_start_osint"))
        self.chk_nsfw.configure(text=self.get_text("nsfw_checkbox"))
        self.chk_all_sites.configure(text=self.get_text("all_sites_checkbox"))
        self.filter_lbl.configure(text=self.get_text("fast_filter"))
        self.entry_filter_username.configure(placeholder_text=self.get_text("filter_placeholder"))
        self.left_lbl.configure(text=self.get_text("social_networks_header"))
        self.right_lbl.configure(text=self.get_text("dorking_header"))
        self.export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_pdf.configure(text=self.get_text("export_pdf"))

        if not self.searching:
            self.status_lbl.configure(text=self.get_text("ready_to_search"))

        # Update Phone Tab
        self.phone_title_lbl.configure(text=self.get_text("phone_header"))
        self.entry_phone.configure(placeholder_text=self.get_text("phone_placeholder"))
        self.btn_search_phone.configure(text=self.get_text("btn_start_phone"))
        self.meta_lbl.configure(text=self.get_text("validation_metadata"))
        self.mentions_lbl.configure(text=self.get_text("advanced_dorks"))
        self.phone_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_phone_pdf.configure(text=self.get_text("export_pdf"))

        # Update Company Tab
        self.company_title_lbl.configure(text=self.get_text("company_header"))
        self.entry_company.configure(placeholder_text=self.get_text("company_placeholder"))
        self.btn_search_company.configure(text=self.get_text("btn_start_company"))
        self.company_results_lbl.configure(text=self.get_text("registers_header"))
        self.company_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_company_pdf.configure(text=self.get_text("export_pdf"))

        # Country Filter combobox values
        countries = [
            self.get_text("all_countries"),
            self.get_text("nl_country"),
            self.get_text("uk_country"),
            self.get_text("be_country"),
            self.get_text("de_country"),
            self.get_text("global_linkedin")
        ]
        # Keep track of previous selection index to keep it if possible
        prev_val = self.country_filter_var.get()
        self.combo_country.configure(values=countries)
        # Default or update selection
        if prev_val not in countries:
            self.country_filter_var.set(countries[0])

        # Update Settings Tab
        self.settings_title_lbl.configure(text=self.get_text("settings_title"))
        self.lang_section_lbl.configure(text=self.get_text("language_section"))
        self.updates_section_lbl.configure(text=self.get_text("updates_section"))
        self.current_version_lbl.configure(text=f"{self.get_text('current_version')}: Sherlock v{__version__}")
        self.btn_check_updates.configure(text=self.get_text("btn_check_updates"))

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
        self.btn_username_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_username"), command=self.show_username_tab)
        self.btn_username_tab.grid(row=1, column=0, padx=20, pady=10)

        self.btn_phone_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_phone"), command=self.show_phone_tab)
        self.btn_phone_tab.grid(row=2, column=0, padx=20, pady=10)

        self.btn_company_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_company"), command=self.show_company_tab)
        self.btn_company_tab.grid(row=3, column=0, padx=20, pady=10)

        self.btn_settings_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_settings"), command=self.show_settings_tab)
        self.btn_settings_tab.grid(row=4, column=0, padx=20, pady=10)

        # Theme / Appearance controls
        self.theme_label = ctk.CTkLabel(self.sidebar, text=self.get_text("theme"), font=ctk.CTkFont(size=12))
        self.theme_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        self.theme_combo = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_appearance_mode)
        self.theme_combo.grid(row=7, column=0, padx=20, pady=(5, 20))

        # Create Main Content Area
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create the Four Tabs
        self.create_username_tab()
        self.create_phone_tab()
        self.create_company_tab()
        self.create_settings_tab()

        # Show initial tab
        self.show_username_tab()

    def create_username_tab(self):
        self.tab_username = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_username.grid_rowconfigure(2, weight=1)
        self.tab_username.grid_columnconfigure(0, weight=1)

        # Title
        self.username_title_lbl = ctk.CTkLabel(self.tab_username, text=self.get_text("username_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.username_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Controls row
        ctrl_frame = ctk.CTkFrame(self.tab_username)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_username = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("username_placeholder"))
        self.entry_username.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_username.bind("<Return>", lambda e: self.start_username_search())

        self.btn_search_username = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_osint"), width=160, command=self.start_username_search)
        self.btn_search_username.grid(row=0, column=1, padx=10, pady=10)

        # Options Row
        options_frame = ctk.CTkFrame(self.tab_username)
        options_frame.grid(row=1, column=1, sticky="ns", pady=10, padx=(10, 5))

        self.nsfw_var = tk.BooleanVar(value=False)
        self.chk_nsfw = ctk.CTkCheckBox(options_frame, text=self.get_text("nsfw_checkbox"), variable=self.nsfw_var)
        self.chk_nsfw.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.all_sites_var = tk.BooleanVar(value=False)
        self.chk_all_sites = ctk.CTkCheckBox(options_frame, text=self.get_text("all_sites_checkbox"), variable=self.all_sites_var, command=self._update_username_results_display)
        self.chk_all_sites.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Table & Output Area - SPLIT LAYOUT (Social Media & Advanced Dorks)
        output_frame = ctk.CTkFrame(self.tab_username)
        output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        output_frame.grid_rowconfigure(2, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Status & Progress indicators
        self.status_lbl = ctk.CTkLabel(output_frame, text=self.get_text("ready_to_search"), font=ctk.CTkFont(size=13, weight="bold"))
        self.status_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=5)

        self.progress_bar = ctk.CTkProgressBar(output_frame)
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=15, pady=5)
        self.progress_bar.set(0)

        # Filter Panel inside output_frame
        filter_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
        filter_frame.grid_columnconfigure(1, weight=1)

        self.filter_lbl = ctk.CTkLabel(filter_frame, text=self.get_text("fast_filter"), font=ctk.CTkFont(size=12, weight="bold"))
        self.filter_lbl.grid(row=0, column=0, padx=(0, 10), pady=2, sticky="w")

        self.entry_filter_username = ctk.CTkEntry(filter_frame, placeholder_text=self.get_text("filter_placeholder"))
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

        self.left_lbl = ctk.CTkLabel(left_panel, text=self.get_text("social_networks_header"), font=ctk.CTkFont(size=13, weight="bold"))
        self.left_lbl.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.text_username_results = ctk.CTkTextbox(left_panel, font=ctk.CTkFont(family="Courier", size=13))
        self.text_username_results.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.text_username_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_username_results)

        # Right panel: Advanced Dorks
        right_panel = ctk.CTkFrame(username_splitter)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        self.right_lbl = ctk.CTkLabel(right_panel, text=self.get_text("dorking_header"), font=ctk.CTkFont(size=13, weight="bold"))
        self.right_lbl.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.text_username_dorks = ctk.CTkTextbox(right_panel, font=ctk.CTkFont(size=13))
        self.text_username_dorks.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.text_username_dorks.configure(state="disabled")
        self._setup_textbox_tags(self.text_username_dorks)

        # Export frame
        export_frame = ctk.CTkFrame(self.tab_username)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt"))
        self.btn_export_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx"))
        self.btn_export_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf"))
        self.btn_export_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_phone_tab(self):
        self.tab_phone = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_phone.grid_rowconfigure(2, weight=1)
        self.tab_phone.grid_columnconfigure(0, weight=1)

        # Title
        self.phone_title_lbl = ctk.CTkLabel(self.tab_phone, text=self.get_text("phone_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.phone_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Controls row
        ctrl_frame = ctk.CTkFrame(self.tab_phone)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_phone = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("phone_placeholder"))
        self.entry_phone.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_phone.bind("<Return>", lambda e: self.start_phone_search())

        self.btn_search_phone = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_phone"), width=160, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_phone_search)
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

        self.meta_lbl = ctk.CTkLabel(meta_panel, text=self.get_text("validation_metadata"), font=ctk.CTkFont(size=14, weight="bold"))
        self.meta_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.text_phone_meta = ctk.CTkTextbox(meta_panel, font=ctk.CTkFont(size=13))
        self.text_phone_meta.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        self.text_phone_meta.configure(state="disabled")
        self._setup_textbox_tags(self.text_phone_meta)

        # Right Web Mentions Panel
        mentions_panel = ctk.CTkFrame(results_splitter)
        mentions_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        mentions_panel.grid_rowconfigure(1, weight=1)
        mentions_panel.grid_columnconfigure(0, weight=1)

        self.mentions_lbl = ctk.CTkLabel(mentions_panel, text=self.get_text("advanced_dorks"), font=ctk.CTkFont(size=14, weight="bold"))
        self.mentions_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.text_phone_mentions = ctk.CTkTextbox(mentions_panel, font=ctk.CTkFont(size=13))
        self.text_phone_mentions.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        self.text_phone_mentions.configure(state="disabled")
        self._setup_textbox_tags(self.text_phone_mentions)

        # Export row for phone searches
        export_frame = ctk.CTkFrame(self.tab_phone)
        export_frame.grid(row=3, column=0, sticky="ew", pady=10)

        self.phone_export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.phone_export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_phone_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_phone=True))
        self.btn_export_phone_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_phone_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_phone=True))
        self.btn_export_phone_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_phone_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_phone=True))
        self.btn_export_phone_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_company_tab(self):
        self.tab_company = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_company.grid_rowconfigure(2, weight=1)
        self.tab_company.grid_columnconfigure(0, weight=1)

        # Title
        self.company_title_lbl = ctk.CTkLabel(self.tab_company, text=self.get_text("company_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.company_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Controls row
        ctrl_frame = ctk.CTkFrame(self.tab_company)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_company = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("company_placeholder"))
        self.entry_company.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_company.bind("<Return>", lambda e: self.start_company_search())

        # Country Filter
        self.country_filter_var = tk.StringVar(value=self.get_text("all_countries"))
        countries = [
            self.get_text("all_countries"),
            self.get_text("nl_country"),
            self.get_text("uk_country"),
            self.get_text("be_country"),
            self.get_text("de_country"),
            self.get_text("global_linkedin")
        ]
        self.combo_country = ctk.CTkOptionMenu(ctrl_frame, variable=self.country_filter_var, values=countries)
        self.combo_country.grid(row=0, column=1, padx=10, pady=10)

        self.btn_search_company = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_company"), width=160, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_company_search)
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

        self.company_results_lbl = ctk.CTkLabel(results_panel, text=self.get_text("registers_header"), font=ctk.CTkFont(size=14, weight="bold"))
        self.company_results_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.text_company_results = ctk.CTkTextbox(results_panel, font=ctk.CTkFont(size=13))
        self.text_company_results.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        self.text_company_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_company_results)

        # Export row for company searches
        export_frame = ctk.CTkFrame(self.tab_company)
        export_frame.grid(row=3, column=0, sticky="ew", pady=10)

        self.company_export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.company_export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_company_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_company=True))
        self.btn_export_company_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_company_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_company=True))
        self.btn_export_company_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_company_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_company=True))
        self.btn_export_company_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_settings_tab(self):
        self.tab_settings = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_settings.grid_rowconfigure(3, weight=1)
        self.tab_settings.grid_columnconfigure(0, weight=1)

        # Title
        self.settings_title_lbl = ctk.CTkLabel(self.tab_settings, text=self.get_text("settings_title"), font=ctk.CTkFont(size=22, weight="bold"))
        self.settings_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Language Frame
        lang_frame = ctk.CTkFrame(self.tab_settings)
        lang_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        lang_frame.grid_columnconfigure(1, weight=1)

        self.lang_section_lbl = ctk.CTkLabel(lang_frame, text=self.get_text("language_section"), font=ctk.CTkFont(size=14, weight="bold"))
        self.lang_section_lbl.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        # Combobox for language
        self.lang_combo = ctk.CTkOptionMenu(
            lang_frame,
            values=["Nederlands", "English"],
            command=self.change_language
        )
        self.lang_combo.grid(row=0, column=1, padx=15, pady=15, sticky="e")
        if self.language_var.get() == "nl":
            self.lang_combo.set("Nederlands")
        else:
            self.lang_combo.set("English")

        # Updates Frame
        update_frame = ctk.CTkFrame(self.tab_settings)
        update_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=5)
        update_frame.grid_columnconfigure(0, weight=1)

        self.updates_section_lbl = ctk.CTkLabel(update_frame, text=self.get_text("updates_section"), font=ctk.CTkFont(size=14, weight="bold"))
        self.updates_section_lbl.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.current_version_lbl = ctk.CTkLabel(update_frame, text=f"{self.get_text('current_version')}: Sherlock v{__version__}", font=ctk.CTkFont(size=13))
        self.current_version_lbl.grid(row=1, column=0, padx=15, pady=5, sticky="w")

        self.update_status_lbl = ctk.CTkLabel(update_frame, text=f"Status: {self.get_text('update_status_idle')}", font=ctk.CTkFont(size=13))
        self.update_status_lbl.grid(row=2, column=0, padx=15, pady=5, sticky="w")

        self.btn_check_updates = ctk.CTkButton(
            update_frame,
            text=self.get_text("btn_check_updates"),
            command=self.start_check_updates,
            fg_color="#2B6CB0",
            hover_color="#1A365D"
        )
        self.btn_check_updates.grid(row=3, column=0, padx=15, pady=15, sticky="w")

    # Navigation Tabs switching logic
    def show_username_tab(self):
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_username.grid(row=0, column=0, sticky="nsew")
        self.btn_username_tab.configure(fg_color="#1F538D") # Active tab color
        self.btn_phone_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_company_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_settings_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def show_phone_tab(self):
        self.tab_username.grid_remove()
        self.tab_company.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_phone.grid(row=0, column=0, sticky="nsew")
        self.btn_phone_tab.configure(fg_color="#1F538D") # Active tab color
        self.btn_username_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_company_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_settings_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def show_company_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_company.grid(row=0, column=0, sticky="nsew")
        self.btn_company_tab.configure(fg_color="#1F538D") # Active tab color
        self.btn_username_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_phone_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_settings_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def show_settings_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_settings.grid(row=0, column=0, sticky="nsew")
        self.btn_settings_tab.configure(fg_color="#1F538D") # Active tab color
        self.btn_username_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_phone_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.btn_company_tab.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    # Username Search logic
    def start_username_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        username = self.entry_username.get().strip()
        if not username:
            messagebox.showwarning(self.get_text("input_missing"), self.get_text("username_input_missing_msg"))
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
        # Translate dynamic status message
        if "Zoeken naar" in msg:
            self.status_lbl.configure(text=self.get_text("searching_username").format(message=self.current_username))
        else:
            self.status_lbl.configure(text=msg)

    def _on_search_finished(self):
        self.searching = False
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self._update_search_status(self.get_text("search_finished"))

        self._update_username_results_display()
        self._update_username_dorks_display()

        claimed_count = sum(
            1 for info in self.search_results.values()
            if "claimed" in str(getattr(info.get("status"), "status", info.get("status"))).lower() or "gevonden" in str(getattr(info.get("status"), "status", info.get("status"))).lower()
        )

        # Notify visually via popup
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), self.get_text("accounts_found_msg").format(count=claimed_count)))

    # Phone Search Logic
    def start_phone_search(self):
        phone_input = self.entry_phone.get().strip()
        if not phone_input:
            messagebox.showwarning(self.get_text("input_missing"), self.get_text("phone_input_missing_msg"))
            return

        self.current_phone = phone_input
        self._clear_textbox(self.text_phone_meta)
        self._insert_text(self.text_phone_meta, self.get_text("analyzing_phone"))

        self._clear_textbox(self.text_phone_mentions)
        self._insert_text(self.text_phone_mentions, self.get_text("dorking_methods"))

        # Run phone OSINT in separate thread
        threading.Thread(target=self._run_phone_search, args=(phone_input,), daemon=True).start()

    def _run_phone_search(self, phone_str):
        p = PhoneOSINT()
        meta = p.validate_and_meta(phone_str)
        self.phone_meta = meta

        # Real-time display of metadata
        self._clear_textbox(self.text_phone_meta)
        if meta.get("valid"):
            self._insert_text(self.text_phone_meta, self.get_text("valid_phone"))
            self._insert_text(self.text_phone_meta, f"E.164 indeling:   {meta['e164']}\n")
            self._insert_text(self.text_phone_meta, f"Internationaal:   {meta['international']}\n")
            self._insert_text(self.text_phone_meta, f"Nationaal:        {meta['national']}\n")
            self._insert_text(self.text_phone_meta, f"Type Lijn:        {meta['type']}\n")
            self._insert_text(self.text_phone_meta, f"Provider:         {meta['carrier']}\n")
            self._insert_text(self.text_phone_meta, f"Geregistreerd in: {meta['location']}\n")
            self._insert_text(self.text_phone_meta, f"Tijdzones:        {', '.join(meta['timezones'])}\n")
        else:
            self._insert_text(self.text_phone_meta, self.get_text("invalid_phone"))
            self._insert_text(self.text_phone_meta, f"Invoer: {phone_str}\n")
            self._insert_text(self.text_phone_meta, f"Error details: {meta.get('error') or 'Onbekende fout'}\n")

        # If invalid, abort internet mentions search
        if not meta.get("valid"):
            self._clear_textbox(self.text_phone_mentions)
            self._insert_text(self.text_phone_mentions, self.get_text("phone_aborted"))
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

        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), "Telefoon OSINT & tracker dorking voltooid!"))

    # Company Search Logic
    def start_company_search(self):
        company_input = self.entry_company.get().strip()
        if not company_input:
            messagebox.showwarning(self.get_text("input_missing"), self.get_text("company_input_missing_msg"))
            return

        self.current_company = company_input
        self._clear_textbox(self.text_company_results)
        self._insert_text(self.text_company_results, self.get_text("company_searching").format(company=company_input))

        # Run company OSINT in separate thread
        threading.Thread(target=self._run_company_search, args=(company_input,), daemon=True).start()

    def _run_company_search(self, company_str):
        co = CompanyOSINT()
        # Map localized selection back to search filter
        selected = self.country_filter_var.get()
        if selected == self.get_text("nl_country"):
            country_filter = "Nederland"
        elif selected == self.get_text("uk_country"):
            country_filter = "Verenigd Koninkrijk"
        elif selected == self.get_text("be_country"):
            country_filter = "België"
        elif selected == self.get_text("de_country"):
            country_filter = "Duitsland"
        elif selected == self.get_text("global_linkedin"):
            country_filter = "Wereldwijd / LinkedIn"
        else:
            country_filter = "Alle"

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

        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), self.get_text("company_hits_found").format(count=total_hits)))

    # Export Report Routing
    def export_results(self, file_format, is_phone=False, is_company=False):
        if is_phone:
            if not self.phone_meta:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_phone_search_yet"))
                return
            target_name = self.phone_meta.get("e164") or "telefoon"
        elif is_company:
            if not self.company_results:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_company_search_yet"))
                return
            target_name = self.current_company
        else:
            if not self.search_results:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_username_search_yet"))
                return
            target_name = self.current_username

        # Get file save location from user
        filetypes_map = {
            "txt": ("TXT Bestanden (*.txt)" if self.language_var.get() == "nl" else "TXT Files (*.txt)", "*.txt"),
            "docx": ("Microsoft Word (*.docx)", "*.docx"),
            "pdf": ("PDF Documenten (*.pdf)" if self.language_var.get() == "nl" else "PDF Documents (*.pdf)", "*.pdf")
        }

        extension = f".{file_format}"
        initial_filename = f"sherlock_rapport_{target_name}{extension}".replace("+", "")
        filepath = filedialog.asksaveasfilename(
            defaultextension=extension,
            filetypes=[filetypes_map[file_format]],
            initialfile=initial_filename,
            title=self.get_text("save_osint_report")
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

            messagebox.showinfo(self.get_text("success"), self.get_text("export_success").format(filepath=filepath))
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("export_failed").format(error=e))

    # Update Checking and Execution
    def start_check_updates(self):
        self.update_status_lbl.configure(text=f"Status: {self.get_text('update_status_checking')}")
        self.btn_check_updates.configure(state="disabled")
        threading.Thread(target=self._run_check_updates, daemon=True).start()

    def _run_check_updates(self):
        try:
            # 1. Fetch from master branch of origin
            subprocess.run(["git", "fetch", "origin", "master"], check=True, capture_output=True, text=True)

            # 2. Find if we are lagging behind origin/master
            res = subprocess.run(["git", "rev-list", "--count", "HEAD..origin/master"], check=True, capture_output=True, text=True)
            lagging_count = int(res.stdout.strip())

            if lagging_count > 0:
                self.after(0, lambda: self._update_available_action())
            else:
                self.after(0, lambda: self._update_up_to_date_action())
        except Exception as e:
            self.after(0, lambda: self._update_error_action(e))

    def _update_available_action(self):
        self.update_status_lbl.configure(text=f"Status: {self.get_text('update_status_available')}")
        self.btn_check_updates.configure(state="normal")

        # Ask the user if they want to install the update
        response = messagebox.askyesno(self.get_text("update_prompt_title"), self.get_text("update_prompt_msg"))
        if response:
            threading.Thread(target=self._run_install_update, daemon=True).start()

    def _update_up_to_date_action(self):
        self.update_status_lbl.configure(text=f"Status: {self.get_text('update_status_up_to_date')}")
        self.btn_check_updates.configure(state="normal")
        messagebox.showinfo(self.get_text("success"), self.get_text("update_status_up_to_date"))

    def _update_error_action(self, error):
        self.update_status_lbl.configure(text=f"Status: {self.get_text('update_status_error')}\nDetails: {error}")
        self.btn_check_updates.configure(state="normal")
        messagebox.showerror(self.get_text("error"), f"{self.get_text('update_status_error')}\n{error}")

    def _run_install_update(self):
        try:
            # Perform hard reset to origin/master
            subprocess.run(["git", "reset", "--hard", "origin/master"], check=True, capture_output=True, text=True)

            # Re-run pip install -e . to apply any new metadata if package structure changed
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True, capture_output=True, text=True)

            # Inform user of success with a beautiful popup and trigger restart
            self.after(0, lambda: self._show_update_success_and_restart())
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(self.get_text("error"), f"Update failed: {e}"))

    def _show_update_success_and_restart(self):
        messagebox.showinfo(self.get_text("update_success_title"), self.get_text("update_success_msg"))
        self.destroy()

        # Restart application
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(f"Error restarting: {e}")
            sys.exit(0)


def main():
    app = SherlockGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
