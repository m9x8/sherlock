"""
Sherlock GUI Module
A beautiful, modern, responsive CustomTkinter interface
for username hunting, phone number OSINT, company searches,
e-mail lookups, domain/network OSINT, name-based people search, and deep-dive Dox profiling.
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
import random

# Core Sherlock imports
from sherlock_project.ui_orchestrator import UIOrchestrator
from sherlock_project.maigret_engine import MaigretEngine
from sherlock_project.socmint_deep import SocmintDeepEngine
from sherlock_project.company_deep import CompanyDeepEngine
from sherlock_project.phone_recon import PhoneReconEngine
from sherlock_project.geoint_engine import GeointEngine
from sherlock_project.hibp_checker import HIBPChecker
from sherlock_project.sherlock import sherlock, SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus, QueryResult
from sherlock_project.phone_search import PhoneOSINT
from sherlock_project.company_search import CompanyOSINT
from sherlock_project.person_search import PersonOSINT
from sherlock_project.dox_search import DoxProfiler
from sherlock_project.reports import ReportGenerator
from sherlock_project import __version__

# Dynamic DNS / Network imports
import dns.resolver
import whois
import shodan

# Setup CustomTkinter Theme and Colors
ctk.set_appearance_mode("Dark")
# Load a custom modern, sophisticated dark/cyberpunk color theme with deep blues & clean grays
ctk.set_default_color_theme("dark-blue")

SETTINGS_FILE = os.path.expanduser("~/.sherlock_settings.json")

TRANSLATIONS = {
    "nl": {
        "title": "No shit Sherlock Professional OSINT Suite",
        "tab_username": "Gebruikersnaam Zoeken",
        "tab_phone": "Telefoonnummer Zoeken",
        "tab_company": "Bedrijven Zoeken",
        "tab_email": "E-mail Zoeken",
        "tab_network": "Netwerk & Domein OSINT",
        "tab_person": "Personen Zoeken",
        "tab_dox": "Dox Sectie",
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
        "update_prompt_msg": "Er is een nieuwe update beschikbaar ({commits} commit(s) achter) op de Advance-osint branch. Wilt u deze nu installeren en de applicatie opnieuw opstarten?",
        "update_success_title": "Update Succesvol",
        "update_success_msg": "De applicatie is succesvol geüpdatet naar de nieuwste versie op Advance-osint! De applicatie start nu opnieuw op.",
        "error": "Fout",
        "success": "Succes",
        "search_active_warning": "Er is momenteel al een zoekopdracht actief of stopgezet.",
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
        "company_searching": "[*] Zoeken naar bedrijf '{company}' via officiële registers & dorks...\n",
        "company_hits_found": "Bedrijf OSINT voltooid!\nTotaal {count} vermeldingen gevonden.",
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

        # New translations
        "btn_stop": "Stop Zoeken",
        "email_header": "E-mailadres OSINT & Gekoppelde Accounts",
        "email_placeholder": "Voer een e-mailadres in (bijv. info@bedrijf.nl)...",
        "btn_start_email": "Start E-mail OSINT",
        "network_header": "Domein, DNS & Netwerk OSINT (incl. gratis IP-API/Shodan alternatief)",
        "network_placeholder": "Voer domein of IP in (bijv. bedrijf.nl of 8.8.8.8)...",
        "btn_start_network": "Start Netwerk OSINT",
        "person_header": "Personen Zoeken via Naam OSINT",
        "first_name_placeholder": "Voornaam...",
        "last_name_placeholder": "Achternaam...",
        "extra_info_placeholder": "Extra info (bijv. Amsterdam of ASML)...",
        "btn_start_person": "Start Personen OSINT",
        "no_email_search_yet": "Er is nog geen e-mailadres gezocht.",
        "no_network_search_yet": "Er is nog geen domein/netwerk gezocht.",
        "no_person_search_yet": "Er is nog geen persoon gezocht.",
        "email_searching": "[*] Analyseren van e-mail '{email}' met holehe & socialscan...\n",
        "network_searching": "[*] Analyseren van '{target}' via DNS, Whois, IP-API & Shodan...\n",
        "person_searching": "[*] Zoeken naar persoon '{first} {last}' met geavanceerde dorks...\n",
        "search_stopped": "Zoekopdracht gestopt door gebruiker.",
        "shodan_api_label": "Shodan API Sleutel:",
        "shodan_api_placeholder": "Voer uw Shodan API-key in...",

        # Dox Translations
        "dox_header": "Dox & Doelwit OSINT Dossier Profiler",
        "dox_btn_start": "Start Dox Profiler",
        "no_dox_search_yet": "Er is nog geen dox-zoekopdracht uitgevoerd.",
        "dox_searching": "[*] Bezig met samenstellen van dox-dossier...\n",
        "dox_finished": "Dox Dossier succesvol gegenereerd!"
    },
    "en": {
        "title": "No shit Sherlock Professional OSINT Suite",
        "tab_username": "Username Search",
        "tab_phone": "Phone Number Search",
        "tab_company": "Company Search",
        "tab_email": "Email Search",
        "tab_network": "Network & Domain OSINT",
        "tab_person": "Person Search",
        "tab_dox": "Dox Section",
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
        "update_prompt_msg": "A new update is available ({commits} commit(s) behind) on the Advance-osint branch. Do you want to install it now and restart the application?",
        "update_success_title": "Update Successful",
        "update_success_msg": "The application has been successfully updated to the latest Advance-osint version! The application will now restart.",
        "error": "Error",
        "success": "Success",
        "search_active_warning": "A search is currently already active or stopping.",
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
        "company_searching": "[*] Searching for company '{company}' via official registers & dorks...\n",
        "company_hits_found": "Company OSINT completed!\nTotal {count} listings found.",
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

        # New translations
        "btn_stop": "Stop Search",
        "email_header": "Email Address OSINT & Linked Accounts",
        "email_placeholder": "Enter an email address (e.g. info@company.com)...",
        "btn_start_email": "Start Email OSINT",
        "network_header": "Domain, DNS & Network OSINT (incl. free IP-API/Shodan alternative)",
        "network_placeholder": "Enter domain or IP (e.g. company.com or 8.8.8.8)...",
        "btn_start_network": "Start Network OSINT",
        "person_header": "Person Search via Name OSINT",
        "first_name_placeholder": "First Name...",
        "last_name_placeholder": "Last Name...",
        "extra_info_placeholder": "Extra info (e.g. London or ASML)...",
        "btn_start_person": "Start Person OSINT",
        "no_email_search_yet": "No email search has been conducted yet.",
        "no_network_search_yet": "No network search has been conducted yet.",
        "no_person_search_yet": "No person search has been conducted yet.",
        "email_searching": "[*] Analyzing email '{email}' with holehe & socialscan...\n",
        "network_searching": "[*] Analyzing '{target}' via DNS, Whois, IP-API & Shodan...\n",
        "person_searching": "[*] Searching for person '{first} {last}' with advanced dorks...\n",
        "search_stopped": "Search stopped by user.",
        "shodan_api_label": "Shodan API Key:",
        "shodan_api_placeholder": "Enter your Shodan API key...",

        # Dox Translations
        "dox_header": "Dox & Target OSINT Dossier Profiler",
        "dox_btn_start": "Start Dox Profiler",
        "no_dox_search_yet": "No dox search has been conducted yet.",
        "dox_searching": "[*] Compiling dox dossier...\n",
        "dox_finished": "Dox Dossier successfully generated!"
    }
}


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"language": "nl", "shodan_api_key": ""}


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception:
        pass


class GUIQueryNotify(QueryNotify):
    def __init__(self, update_callback, status_callback, finish_callback):
        super().__init__()
        self.update_callback = update_callback
        self.status_callback = status_callback
        self.finish_callback = finish_callback

    def start(self, message):
        self.status_callback(message)

    def update(self, result: QueryResult):
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
        self.geometry("1150x850")
        self.minsize(1000, 700)

        # Threadsafe Cancellation & Progress Variables
        self.stop_event = threading.Event()
        self.active_processes = []

        # Async Orchestrator
        self.orchestrator = UIOrchestrator(
            gui_callback_msg=self._orchestrator_msg_callback,
            gui_callback_progress=self._orchestrator_progress_callback,
            gui_callback_result=self._orchestrator_result_callback
        )
        self.after(100, self.orchestrator.process_queue_sync, self)

        # Deep engines
        self.socmint_engine = SocmintDeepEngine()
        self.company_engine = CompanyDeepEngine()
        self.phone_engine = PhoneReconEngine()
        self.geoint_engine = GeointEngine()
        self.hibp_engine = HIBPChecker()

        # Main active variables
        self.search_results = {}
        self.username_dorks_results = {}
        self.phone_meta = {}
        self.phone_results = {}
        self.company_results = {}
        self.person_results = {}
        self.dox_results = {}
        self.current_username = ""
        self.current_phone = ""
        self.current_company = ""
        self.current_email = ""
        self.current_network = ""
        self.current_person_first = ""
        self.current_person_last = ""

        # Dox form fields
        self.current_dox_username = ""
        self.current_dox_email = ""
        self.current_dox_phone = ""
        self.current_dox_name = ""
        self.current_dox_city = ""

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
        self.title(f"{self.get_text('title')} v{__version__}")

        # Sidebar buttons
        self.btn_username_tab.configure(text=self.get_text("tab_username"))
        self.btn_phone_tab.configure(text=self.get_text("tab_phone"))
        self.btn_company_tab.configure(text=self.get_text("tab_company"))
        self.btn_email_tab.configure(text=self.get_text("tab_email"))
        self.btn_network_tab.configure(text=self.get_text("tab_network"))
        self.btn_person_tab.configure(text=self.get_text("tab_person"))
        self.btn_dox_tab.configure(text=self.get_text("tab_dox"))
        self.btn_settings_tab.configure(text=self.get_text("tab_settings"))
        self.theme_label.configure(text=self.get_text("theme"))

        # Stop Buttons
        for btn in [self.btn_stop_username, self.btn_stop_phone, self.btn_stop_company, self.btn_stop_email, self.btn_stop_network, self.btn_stop_person, self.btn_stop_dox]:
            btn.configure(text=self.get_text("btn_stop"))

        # Username Tab
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

        # Phone Tab
        self.phone_title_lbl.configure(text=self.get_text("phone_header"))
        self.entry_phone.configure(placeholder_text=self.get_text("phone_placeholder"))
        self.btn_search_phone.configure(text=self.get_text("btn_start_phone"))
        self.meta_lbl.configure(text=self.get_text("validation_metadata"))
        self.mentions_lbl.configure(text=self.get_text("advanced_dorks"))
        self.phone_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_phone_pdf.configure(text=self.get_text("export_pdf"))

        # Company Tab
        self.company_title_lbl.configure(text=self.get_text("company_header"))
        self.entry_company.configure(placeholder_text=self.get_text("company_placeholder"))
        self.btn_search_company.configure(text=self.get_text("btn_start_company"))
        self.company_results_lbl.configure(text=self.get_text("registers_header"))
        self.company_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_company_pdf.configure(text=self.get_text("export_pdf"))

        # Email Tab
        self.email_title_lbl.configure(text=self.get_text("email_header"))
        self.entry_email.configure(placeholder_text=self.get_text("email_placeholder"))
        self.btn_search_email.configure(text=self.get_text("btn_start_email"))
        self.email_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_email_pdf.configure(text=self.get_text("export_pdf"))

        # Network Tab
        self.network_title_lbl.configure(text=self.get_text("network_header"))
        self.entry_network.configure(placeholder_text=self.get_text("network_placeholder"))
        self.btn_search_network.configure(text=self.get_text("btn_start_network"))
        self.network_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_network_pdf.configure(text=self.get_text("export_pdf"))

        # Person Tab
        self.person_title_lbl.configure(text=self.get_text("person_header"))
        self.entry_first_name.configure(placeholder_text=self.get_text("first_name_placeholder"))
        self.entry_last_name.configure(placeholder_text=self.get_text("last_name_placeholder"))
        self.entry_person_extra.configure(placeholder_text=self.get_text("extra_info_placeholder"))
        self.btn_search_person.configure(text=self.get_text("btn_start_person"))
        self.person_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_person_pdf.configure(text=self.get_text("export_pdf"))

        # Dox Tab
        self.dox_title_lbl.configure(text=self.get_text("dox_header"))
        self.entry_dox_username.configure(placeholder_text=self.get_text("username_placeholder"))
        self.entry_dox_email.configure(placeholder_text=self.get_text("email_placeholder"))
        self.entry_dox_phone.configure(placeholder_text=self.get_text("phone_placeholder"))
        self.entry_dox_name.configure(placeholder_text=f"{self.get_text('first_name_placeholder')} {self.get_text('last_name_placeholder')}")
        self.entry_dox_city.configure(placeholder_text=self.get_text("extra_info_placeholder"))
        self.btn_search_dox.configure(text=self.get_text("dox_btn_start"))
        self.dox_export_lbl.configure(text=self.get_text("export_report"))
        self.btn_export_dox_pdf.configure(text=self.get_text("export_pdf"))

        # Company Combobox Filter values
        countries = [
            self.get_text("all_countries"),
            self.get_text("nl_country"),
            self.get_text("uk_country"),
            self.get_text("be_country"),
            self.get_text("de_country"),
            self.get_text("global_linkedin")
        ]
        prev_val = self.country_filter_var.get()
        self.combo_country.configure(values=countries)
        if prev_val not in countries:
            self.country_filter_var.set(countries[0])

        # Settings Tab
        self.settings_title_lbl.configure(text=self.get_text("settings_title"))
        self.lang_section_lbl.configure(text=self.get_text("language_section"))
        self.updates_section_lbl.configure(text=self.get_text("updates_section"))
        self.current_version_lbl.configure(text=f"{self.get_text('current_version')}: No shit Sherlock v{__version__}")
        self.btn_check_updates.configure(text=self.get_text("btn_check_updates"))
        self.shodan_label.configure(text=self.get_text("shodan_api_label"))
        self.entry_shodan.configure(placeholder_text=self.get_text("shodan_api_placeholder"))

    def stop_all_searches(self):
        """Immediately sets the stop event and kills active processes."""
        self.stop_event.set()
        for proc in self.active_processes:
            try:
                proc.terminate()
                proc.kill()
            except Exception:
                pass
        self.active_processes.clear()
        self.searching = False
        if hasattr(self, 'orchestrator'):
            self.orchestrator.stop()

    # ------------------ ORCHESTRATOR CALLBACKS ------------------
    def _orchestrator_msg_callback(self, text):
        if hasattr(self, 'text_dox_results'):
            self._insert_text(self.text_dox_results, f"{text}\n")

    def _orchestrator_progress_callback(self, current, total):
        pass

    def _orchestrator_result_callback(self, category, data):
        # Create filter checkbox if it doesn't exist
        if hasattr(self, 'filter_panel') and category not in self.filter_checkboxes:
            cb = ctk.CTkCheckBox(self.filter_panel, text=category.capitalize(), command=self._apply_dox_filters)
            cb.select()
            cb.pack(pady=5, anchor="w", padx=10)
            self.filter_checkboxes[category] = cb

        if not hasattr(self, 'dox_async_results'):
            self.dox_async_results = []
        self.dox_async_results.append((category, data))

        self._apply_dox_filters()

    def _apply_dox_filters(self):
        if not hasattr(self, 'text_dox_results') or not hasattr(self, 'dox_async_results'):
            return

        active_categories = [cat for cat, cb in getattr(self, 'filter_checkboxes', {}).items() if cb.get()]

        self._clear_textbox(self.text_dox_results)
        # Redisplay base results if they exist
        if hasattr(self, 'dox_results'):
            for category, items in self.dox_results.items():
                self._insert_text(self.text_dox_results, f"[ {category.upper()} ]\n")
                if not items:
                    self._insert_text(self.text_dox_results, " Geen vermeldingen gevonden.\n\n")
                else:
                    for item in items:
                        self._insert_text(self.text_dox_results, f"• {item['title']}\n  Link: {item['url']}\n\n")

        self._insert_text(self.text_dox_results, "\n[ ASYNC DEEP INTEL ]\n")
        for cat, data in self.dox_async_results:
            if not active_categories or cat in active_categories:
                 self._insert_text(self.text_dox_results, f"• {cat.upper()}: {data}\n")



    def _on_link_click(self, event):
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
        textbox.configure(state="normal")
        url_pattern = re.compile(r'(https?://[^\s\)]+)')
        parts = []
        last_idx = 0
        for match in url_pattern.finditer(text):
            start, end = match.span()
            matched_url = text[start:end]
            stripped_url = matched_url.rstrip(".,?!;:)")
            stripped_len = len(stripped_url)
            extra_len = len(matched_url) - stripped_len

            if start > last_idx:
                parts.append((text[last_idx:start], False))
            parts.append((stripped_url, True))
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
                start_index = textbox.index("insert")
                textbox.insert("insert", part_text)
                end_index = textbox.index("insert")
                # Add highlighting tags for status prefixes/icons
                if "[+]" in part_text or "✓" in part_text or "FOUND" in part_text or "Gevonden" in part_text:
                    textbox.tag_add("green", start_index, end_index)
                elif "[-]" in part_text or "✗" in part_text or "Niet Gevonden" in part_text:
                    textbox.tag_add("yellow", start_index, end_index)
                elif "[*]" in part_text:
                    textbox.tag_add("cyan", start_index, end_index)
                elif "Fout" in part_text or "Foutmelding" in part_text or "Error" in part_text:
                    textbox.tag_add("red", start_index, end_index)
                elif part_text.startswith("[ ") and part_text.endswith(" ]\n"):
                    textbox.tag_add("bold", start_index, end_index)

        textbox.see("insert")
        textbox.configure(state="disabled")

    def _setup_textbox_tags(self, textbox):
        textbox.tag_config("link", foreground="#3182CE", underline=True)
        textbox.tag_bind("link", "<Button-1>", self._on_link_click)
        textbox.tag_bind("link", "<Enter>", lambda e: textbox.configure(cursor="hand2"))
        textbox.tag_bind("link", "<Leave>", lambda e: textbox.configure(cursor="xterm"))
        # High-end text highlighting tags
        textbox._textbox.tag_config("cyan", foreground="#00E5FF", font=ctk.CTkFont(weight="bold"))
        textbox._textbox.tag_config("green", foreground="#38A169", font=ctk.CTkFont(weight="bold"))
        textbox._textbox.tag_config("yellow", foreground="#D69E2E", font=ctk.CTkFont(weight="bold"))
        textbox._textbox.tag_config("red", foreground="#E53E3E", font=ctk.CTkFont(weight="bold"))
        textbox._textbox.tag_config("bold", font=ctk.CTkFont(weight="bold"))

    def _clear_textbox(self, textbox):
        textbox.configure(state="normal")
        textbox.delete("1.0", tk.END)
        textbox.configure(state="disabled")

    def create_widgets(self):
        # Grid layout configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create Left Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar, text="NO SHIT SHERLOCK", font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Subtitle for high-end feel
        self.logo_sub = ctk.CTkLabel(self.sidebar, text="PRO OSINT INTELLIGENCE", font=ctk.CTkFont(family="Helvetica", size=10, weight="bold"), text_color="#718096")
        self.logo_sub.grid(row=0, column=0, padx=20, pady=(45, 10))

        # Sidebar Switching Tab buttons
        self.btn_username_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_username"), command=self.show_username_tab)
        self.btn_username_tab.grid(row=1, column=0, padx=20, pady=5)

        self.btn_phone_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_phone"), command=self.show_phone_tab)
        self.btn_phone_tab.grid(row=2, column=0, padx=20, pady=5)

        self.btn_company_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_company"), command=self.show_company_tab)
        self.btn_company_tab.grid(row=3, column=0, padx=20, pady=5)

        self.btn_email_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_email"), command=self.show_email_tab)
        self.btn_email_tab.grid(row=4, column=0, padx=20, pady=5)

        self.btn_network_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_network"), command=self.show_network_tab)
        self.btn_network_tab.grid(row=5, column=0, padx=20, pady=5)

        self.btn_person_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_person"), command=self.show_person_tab)
        self.btn_person_tab.grid(row=6, column=0, padx=20, pady=5)

        self.btn_dox_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_dox"), command=self.show_dox_tab)
        self.btn_dox_tab.grid(row=7, column=0, padx=20, pady=5)

        self.btn_settings_tab = ctk.CTkButton(self.sidebar, text=self.get_text("tab_settings"), command=self.show_settings_tab)
        self.btn_settings_tab.grid(row=8, column=0, padx=20, pady=5)

        # Theme selection
        self.theme_label = ctk.CTkLabel(self.sidebar, text=self.get_text("theme"), font=ctk.CTkFont(size=12))
        self.theme_label.grid(row=10, column=0, padx=20, pady=(10, 0), sticky="w")
        self.theme_combo = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"], command=self.change_appearance_mode)
        self.theme_combo.grid(row=11, column=0, padx=20, pady=(5, 20))

        # Create Main Content Area
        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Create all Tabs
        self.create_username_tab()
        self.create_phone_tab()
        self.create_company_tab()
        self.create_email_tab()
        self.create_network_tab()
        self.create_person_tab()
        self.create_dox_tab()
        self.create_maigret_tab()
        self.create_settings_tab()

        # Show initial tab
        self.show_username_tab()

    # --- TAB CREATORS ---

    def create_username_tab(self):
        self.tab_username = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_username.grid_rowconfigure(2, weight=1)
        self.tab_username.grid_columnconfigure(0, weight=1)

        self.username_title_lbl = ctk.CTkLabel(self.tab_username, text=self.get_text("username_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.username_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.tab_username)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_username = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("username_placeholder"))
        self.entry_username.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_username.bind("<Return>", lambda e: self.start_username_search())

        self.btn_search_username = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_osint"), width=160, command=self.start_username_search)
        self.btn_search_username.grid(row=0, column=1, padx=5, pady=10)

        self.btn_stop_username = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_stop"), fg_color="#C53030", hover_color="#9B2C2C", width=120, command=self.stop_all_searches)
        self.btn_stop_username.grid(row=0, column=2, padx=5, pady=10)

        # Options Box
        options_frame = ctk.CTkFrame(self.tab_username)
        options_frame.grid(row=1, column=1, sticky="ns", pady=10, padx=(10, 5))

        self.nsfw_var = tk.BooleanVar(value=False)
        self.chk_nsfw = ctk.CTkCheckBox(options_frame, text=self.get_text("nsfw_checkbox"), variable=self.nsfw_var)
        self.chk_nsfw.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.all_sites_var = tk.BooleanVar(value=False)
        self.chk_all_sites = ctk.CTkCheckBox(options_frame, text=self.get_text("all_sites_checkbox"), variable=self.all_sites_var, command=self._update_username_results_display)
        self.chk_all_sites.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Output Layout
        output_frame = ctk.CTkFrame(self.tab_username)
        output_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        output_frame.grid_rowconfigure(2, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        self.status_lbl = ctk.CTkLabel(output_frame, text=self.get_text("ready_to_search"), font=ctk.CTkFont(size=13, weight="bold"))
        self.status_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=5)

        self.progress_bar = ctk.CTkProgressBar(output_frame)
        self.progress_bar.grid(row=0, column=1, sticky="e", padx=15, pady=5)
        self.progress_bar.set(0)

        # Filtering UI
        filter_frame = ctk.CTkFrame(output_frame, fg_color="transparent")
        filter_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=5)
        filter_frame.grid_columnconfigure(1, weight=1)

        self.filter_lbl = ctk.CTkLabel(filter_frame, text=self.get_text("fast_filter"), font=ctk.CTkFont(size=12, weight="bold"))
        self.filter_lbl.grid(row=0, column=0, padx=(0, 10), pady=2, sticky="w")

        self.entry_filter_username = ctk.CTkEntry(filter_frame, placeholder_text=self.get_text("filter_placeholder"))
        self.entry_filter_username.grid(row=0, column=1, sticky="ew", pady=2)
        self.entry_filter_username.bind("<KeyRelease>", lambda e: self._update_username_results_display())

        # Split results view
        username_splitter = ctk.CTkFrame(output_frame, fg_color="transparent")
        username_splitter.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=15, pady=10)
        username_splitter.grid_rowconfigure(0, weight=1)
        username_splitter.grid_columnconfigure(0, weight=1)
        username_splitter.grid_columnconfigure(1, weight=1)

        # Accounts
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

        # Dorks
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

        # Export row
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

        self.phone_title_lbl = ctk.CTkLabel(self.tab_phone, text=self.get_text("phone_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.phone_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.tab_phone)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_phone = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("phone_placeholder"))
        self.entry_phone.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_phone.bind("<Return>", lambda e: self.start_phone_search())

        self.btn_search_phone = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_phone"), width=160, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_phone_search)
        self.btn_search_phone.grid(row=0, column=1, padx=5, pady=10)

        self.btn_stop_phone = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_stop"), fg_color="#C53030", hover_color="#9B2C2C", width=120, command=self.stop_all_searches)
        self.btn_stop_phone.grid(row=0, column=2, padx=5, pady=10)

        # Progress bar
        self.progress_bar_phone = ctk.CTkProgressBar(self.tab_phone)
        self.progress_bar_phone.grid(row=1, column=1, padx=10, pady=10)
        self.progress_bar_phone.set(0)

        # Split views
        results_splitter = ctk.CTkFrame(self.tab_phone, fg_color="transparent")
        results_splitter.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        results_splitter.grid_rowconfigure(0, weight=1)
        results_splitter.grid_columnconfigure(0, weight=2)
        results_splitter.grid_columnconfigure(1, weight=3)

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

        # Export Panel
        export_frame = ctk.CTkFrame(self.tab_phone)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

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

        self.company_title_lbl = ctk.CTkLabel(self.tab_company, text=self.get_text("company_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.company_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.tab_company)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_company = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("company_placeholder"))
        self.entry_company.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_company.bind("<Return>", lambda e: self.start_company_search())

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
        self.btn_search_company.grid(row=0, column=2, padx=5, pady=10)

        self.btn_stop_company = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_stop"), fg_color="#C53030", hover_color="#9B2C2C", width=120, command=self.stop_all_searches)
        self.btn_stop_company.grid(row=0, column=3, padx=5, pady=10)

        # Progress bar
        self.progress_bar_company = ctk.CTkProgressBar(self.tab_company)
        self.progress_bar_company.grid(row=1, column=1, padx=10, pady=10)
        self.progress_bar_company.set(0)

        # Split views
        results_splitter = ctk.CTkFrame(self.tab_company, fg_color="transparent")
        results_splitter.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        results_splitter.grid_rowconfigure(0, weight=1)
        results_splitter.grid_columnconfigure(0, weight=1)

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

        # Export row
        export_frame = ctk.CTkFrame(self.tab_company)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.company_export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.company_export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_company_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_company=True))
        self.btn_export_company_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_company_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_company=True))
        self.btn_export_company_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_company_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_company=True))
        self.btn_export_company_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_email_tab(self):
        self.tab_email = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_email.grid_rowconfigure(2, weight=1)
        self.tab_email.grid_columnconfigure(0, weight=1)

        self.email_title_lbl = ctk.CTkLabel(self.tab_email, text=self.get_text("email_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.email_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.tab_email)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_email = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("email_placeholder"))
        self.entry_email.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_email.bind("<Return>", lambda e: self.start_email_search())

        self.btn_search_email = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_email"), width=160, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_email_search)
        self.btn_search_email.grid(row=0, column=1, padx=5, pady=10)

        self.btn_stop_email = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_stop"), fg_color="#C53030", hover_color="#9B2C2C", width=120, command=self.stop_all_searches)
        self.btn_stop_email.grid(row=0, column=2, padx=5, pady=10)

        # Progress bar
        self.progress_bar_email = ctk.CTkProgressBar(self.tab_email)
        self.progress_bar_email.grid(row=1, column=1, padx=10, pady=10)
        self.progress_bar_email.set(0)

        # Text results Box
        results_panel = ctk.CTkFrame(self.tab_email)
        results_panel.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        results_panel.grid_rowconfigure(0, weight=1)
        results_panel.grid_columnconfigure(0, weight=1)

        self.text_email_results = ctk.CTkTextbox(results_panel, font=ctk.CTkFont(family="Courier", size=13))
        self.text_email_results.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.text_email_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_email_results)

        # Export row
        export_frame = ctk.CTkFrame(self.tab_email)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.email_export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.email_export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_email_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_email=True))
        self.btn_export_email_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_email_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_email=True))
        self.btn_export_email_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_email_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_email=True))
        self.btn_export_email_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_network_tab(self):
        self.tab_network = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_network.grid_rowconfigure(2, weight=1)
        self.tab_network.grid_columnconfigure(0, weight=1)

        self.network_title_lbl = ctk.CTkLabel(self.tab_network, text=self.get_text("network_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.network_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.tab_network)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_network = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("network_placeholder"))
        self.entry_network.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.entry_network.bind("<Return>", lambda e: self.start_network_search())

        self.btn_search_network = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_network"), width=160, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_network_search)
        self.btn_search_network.grid(row=0, column=1, padx=5, pady=10)

        self.btn_stop_network = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_stop"), fg_color="#C53030", hover_color="#9B2C2C", width=120, command=self.stop_all_searches)
        self.btn_stop_network.grid(row=0, column=2, padx=5, pady=10)

        # Progress bar
        self.progress_bar_network = ctk.CTkProgressBar(self.tab_network)
        self.progress_bar_network.grid(row=1, column=1, padx=10, pady=10)
        self.progress_bar_network.set(0)

        # Results TextBox
        results_panel = ctk.CTkFrame(self.tab_network)
        results_panel.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        results_panel.grid_rowconfigure(0, weight=1)
        results_panel.grid_columnconfigure(0, weight=1)

        self.text_network_results = ctk.CTkTextbox(results_panel, font=ctk.CTkFont(family="Courier", size=13))
        self.text_network_results.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.text_network_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_network_results)

        # Export row
        export_frame = ctk.CTkFrame(self.tab_network)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.network_export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.network_export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_network_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_network=True))
        self.btn_export_network_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_network_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_network=True))
        self.btn_export_network_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_network_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_network=True))
        self.btn_export_network_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_person_tab(self):
        self.tab_person = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_person.grid_rowconfigure(2, weight=1)
        self.tab_person.grid_columnconfigure(0, weight=1)

        self.person_title_lbl = ctk.CTkLabel(self.tab_person, text=self.get_text("person_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.person_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.tab_person)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)
        ctrl_frame.grid_columnconfigure(1, weight=1)
        ctrl_frame.grid_columnconfigure(2, weight=1)

        self.entry_first_name = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("first_name_placeholder"))
        self.entry_first_name.grid(row=0, column=0, padx=5, pady=10, sticky="ew")

        self.entry_last_name = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("last_name_placeholder"))
        self.entry_last_name.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.entry_person_extra = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("extra_info_placeholder"))
        self.entry_person_extra.grid(row=0, column=2, padx=5, pady=10, sticky="ew")

        self.btn_search_person = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_start_person"), width=150, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_person_search)
        self.btn_search_person.grid(row=0, column=3, padx=5, pady=10)

        self.btn_stop_person = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_stop"), fg_color="#C53030", hover_color="#9B2C2C", width=120, command=self.stop_all_searches)
        self.btn_stop_person.grid(row=0, column=4, padx=5, pady=10)

        # Progress bar
        self.progress_bar_person = ctk.CTkProgressBar(self.tab_person)
        self.progress_bar_person.grid(row=1, column=1, padx=10, pady=10)
        self.progress_bar_person.set(0)

        # Results panel
        results_panel = ctk.CTkFrame(self.tab_person)
        results_panel.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        results_panel.grid_rowconfigure(0, weight=1)
        results_panel.grid_columnconfigure(0, weight=1)

        self.text_person_results = ctk.CTkTextbox(results_panel, font=ctk.CTkFont(size=13))
        self.text_person_results.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.text_person_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_person_results)

        # Export row
        export_frame = ctk.CTkFrame(self.tab_person)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.person_export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.person_export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_person_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_person=True))
        self.btn_export_person_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_person_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_person=True))
        self.btn_export_person_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_person_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_person=True))
        self.btn_export_person_pdf.grid(row=0, column=3, padx=10, pady=10)

    def create_dox_tab(self):
        self.tab_dox = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_dox.grid_rowconfigure(2, weight=1)
        self.tab_dox.grid_columnconfigure(0, weight=1)

        self.dox_title_lbl = ctk.CTkLabel(self.tab_dox, text=self.get_text("dox_header"), font=ctk.CTkFont(size=22, weight="bold"))
        self.dox_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        ctrl_frame = ctk.CTkFrame(self.tab_dox)
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        ctrl_frame.grid_columnconfigure(0, weight=1)
        ctrl_frame.grid_columnconfigure(1, weight=1)
        ctrl_frame.grid_columnconfigure(2, weight=1)
        ctrl_frame.grid_columnconfigure(3, weight=1)
        ctrl_frame.grid_columnconfigure(4, weight=1)

        # Deep Dox Form fields
        self.entry_dox_username = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("username_placeholder"))
        self.entry_dox_username.grid(row=0, column=0, padx=3, pady=10, sticky="ew")

        self.entry_dox_email = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("email_placeholder"))
        self.entry_dox_email.grid(row=0, column=1, padx=3, pady=10, sticky="ew")

        self.entry_dox_phone = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("phone_placeholder"))
        self.entry_dox_phone.grid(row=0, column=2, padx=3, pady=10, sticky="ew")

        self.entry_dox_name = ctk.CTkEntry(ctrl_frame, placeholder_text=f"{self.get_text('first_name_placeholder')} {self.get_text('last_name_placeholder')}")
        self.entry_dox_name.grid(row=0, column=3, padx=3, pady=10, sticky="ew")

        self.entry_dox_city = ctk.CTkEntry(ctrl_frame, placeholder_text=self.get_text("extra_info_placeholder"))
        self.entry_dox_city.grid(row=0, column=4, padx=3, pady=10, sticky="ew")

        self.btn_search_dox = ctk.CTkButton(ctrl_frame, text=self.get_text("dox_btn_start"), width=150, fg_color="#2B6CB0", hover_color="#1A365D", command=self.start_dox_search)
        self.btn_search_dox.grid(row=0, column=5, padx=5, pady=10)

        self.btn_stop_dox = ctk.CTkButton(ctrl_frame, text=self.get_text("btn_stop"), fg_color="#C53030", hover_color="#9B2C2C", width=120, command=self.stop_all_searches)
        self.btn_stop_dox.grid(row=0, column=6, padx=5, pady=10)

        # Progress bar
        self.progress_bar_dox = ctk.CTkProgressBar(self.tab_dox)
        self.progress_bar_dox.grid(row=1, column=1, padx=10, pady=10)
        self.progress_bar_dox.set(0)

        # Results panel
        results_panel = ctk.CTkFrame(self.tab_dox)
        results_panel.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        results_panel.grid_rowconfigure(0, weight=1)
        results_panel.grid_columnconfigure(0, weight=1)

        self.text_dox_results = ctk.CTkTextbox(results_panel, font=ctk.CTkFont(size=13))
        self.filter_panel = ctk.CTkFrame(results_panel, width=200)
        self.filter_panel.grid(row=0, column=1, sticky="ns", padx=5, pady=15)
        ctk.CTkLabel(self.filter_panel, text="Live Filters", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.filter_checkboxes = {}
        self.text_dox_results.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.text_dox_results.configure(state="disabled")
        self._setup_textbox_tags(self.text_dox_results)

        # Export row
        export_frame = ctk.CTkFrame(self.tab_dox)
        export_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.dox_export_lbl = ctk.CTkLabel(export_frame, text=self.get_text("export_report"), font=ctk.CTkFont(size=13, weight="bold"))
        self.dox_export_lbl.grid(row=0, column=0, padx=15, pady=10)

        self.btn_export_dox_txt = ctk.CTkButton(export_frame, text="TXT Rapport", width=120, command=lambda: self.export_results("txt", is_dox=True))
        self.btn_export_dox_txt.grid(row=0, column=1, padx=10, pady=10)

        self.btn_export_dox_docx = ctk.CTkButton(export_frame, text="Word (.docx)", width=120, command=lambda: self.export_results("docx", is_dox=True))
        self.btn_export_dox_docx.grid(row=0, column=2, padx=10, pady=10)

        self.btn_export_dox_pdf = ctk.CTkButton(export_frame, text=self.get_text("export_pdf"), fg_color="#2B6CB0", hover_color="#1A365D", width=150, command=lambda: self.export_results("pdf", is_dox=True))
        self.btn_export_dox_pdf.grid(row=0, column=3, padx=10, pady=10)

    # Tab views switches

    def show_email_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_network.grid_remove()
        self.tab_person.grid_remove()
        self.tab_dox.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_email.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_email_tab)

    def show_network_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_email.grid_remove()
        self.tab_person.grid_remove()
        self.tab_dox.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_network.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_network_tab)

    def show_person_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_email.grid_remove()
        self.tab_network.grid_remove()
        self.tab_dox.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_person.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_person_tab)

    def show_dox_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_email.grid_remove()
        self.tab_network.grid_remove()
        self.tab_person.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_dox.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_dox_tab)


    def show_maigret_tab(self):
        self.hide_all_tabs()
        self.maigret_btn.configure(fg_color=("gray75", "gray25"))
        self.maigret_frame.grid(row=0, column=1, sticky="nsew")

    def show_username_tab(self):
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_email.grid_remove()
        self.tab_network.grid_remove()
        self.tab_person.grid_remove()
        self.tab_dox.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_username.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_username_tab)

    def show_phone_tab(self):
        self.tab_username.grid_remove()
        self.tab_company.grid_remove()
        self.tab_email.grid_remove()
        self.tab_network.grid_remove()
        self.tab_person.grid_remove()
        self.tab_dox.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_phone.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_phone_tab)

    def show_company_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_email.grid_remove()
        self.tab_network.grid_remove()
        self.tab_person.grid_remove()
        self.tab_dox.grid_remove()
        self.tab_settings.grid_remove()
        self.tab_company.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_company_tab)

    def show_settings_tab(self):
        self.tab_username.grid_remove()
        self.tab_phone.grid_remove()
        self.tab_company.grid_remove()
        self.tab_email.grid_remove()
        self.tab_network.grid_remove()
        self.tab_person.grid_remove()
        self.tab_dox.grid_remove()
        self.tab_settings.grid(row=0, column=0, sticky="nsew")
        self._set_active_button(self.btn_settings_tab)

    def _set_active_button(self, active_btn):
        for btn in [self.btn_username_tab, self.btn_phone_tab, self.btn_company_tab, self.btn_email_tab, self.btn_network_tab, self.btn_person_tab, self.btn_dox_tab, self.btn_settings_tab]:
            if btn == active_btn:
                btn.configure(fg_color="#1F538D")
            else:
                btn.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])

    # --- MAIN SEARCH LOGIC ROUTING ---

    def start_username_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        username = self.entry_username.get().strip()
        if not username:
            messagebox.showwarning(self.get_text("input_missing"), self.get_text("username_input_missing_msg"))
            return

        self.searching = True
        self.stop_event.clear()
        self.current_username = username
        self.search_results = {}
        self.username_dorks_results = {}

        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self._clear_textbox(self.text_username_results)
        self._insert_text(self.text_username_results, f"[*] Initialiseren van No shit Sherlock zoekopdracht voor '{username}'...\n\n")

        self._clear_textbox(self.text_username_dorks)
        self._insert_text(self.text_username_dorks, f"[*] Geavanceerde dorking wordt op de achtergrond uitgevoerd...\n")

        self.search_thread = threading.Thread(target=self._run_username_search, args=(username,), daemon=True)
        self.search_thread.start()

    def _run_username_search(self, username):
        site_data_all = {site.name: site.information for site in self.sites} if self.sites else {}
        if not self.nsfw_var.get():
            site_data = {k: v for k, v in site_data_all.items() if not v.get("isNSFW")}
        else:
            site_data = site_data_all

        notify_obj = GUIQueryNotify(
            update_callback=self._on_search_result_found,
            status_callback=self._update_search_status,
            finish_callback=self._on_search_finished
        )

        try:
            # Perform advanced name dorks
            p = PhoneOSINT()
            dorks = p.search_username_advanced_dorks(username, stop_event=self.stop_event)
            self.username_dorks_results = dorks
            self._update_username_dorks_display()

            # Run Sherlock core
            results = sherlock(
                username=username,
                site_data=site_data,
                query_notify=notify_obj,
                timeout=15,
                stop_event=self.stop_event
            )
            self.search_results = results
        except Exception as e:
            self._update_search_status(f"Fout tijdens het zoeken: {e}")
            self._on_search_finished()

    def _on_search_result_found(self, site, url, status):
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
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), self.get_text("accounts_found_msg").format(count=claimed_count)))

    # PHONE SEARCH

    def start_phone_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        phone_input = self.entry_phone.get().strip()
        if not phone_input:
            messagebox.showwarning(self.get_text("input_missing"), self.get_text("phone_input_missing_msg"))
            return

        self.searching = True
        self.stop_event.clear()
        self.current_phone = phone_input
        self.progress_bar_phone.set(0)

        self._clear_textbox(self.text_phone_meta)
        self._insert_text(self.text_phone_meta, self.get_text("analyzing_phone"))

        self._clear_textbox(self.text_phone_mentions)
        self._insert_text(self.text_phone_mentions, self.get_text("dorking_methods"))

        threading.Thread(target=self._run_phone_search, args=(phone_input,), daemon=True).start()

    def _run_phone_search(self, phone_str):
        p = PhoneOSINT()
        meta = p.validate_and_meta(phone_str)
        self.phone_meta = meta

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

        if not meta.get("valid"):
            self._clear_textbox(self.text_phone_mentions)
            self._insert_text(self.text_phone_mentions, self.get_text("phone_aborted"))
            self.searching = False
            self.progress_bar_phone.set(1.0)
            return

        def update_progress(current, total):
            fraction = float(current) / float(total)
            self.progress_bar_phone.set(fraction)

        mentions = p.search_phone_advanced_dorks(meta, stop_event=self.stop_event, progress_callback=update_progress)
        self.phone_results = mentions

        self._clear_textbox(self.text_phone_mentions)
        for category, items in mentions.items():
            self._insert_text(self.text_phone_mentions, f"[ {category.upper()} ]\n")
            if not items:
                self._insert_text(self.text_phone_mentions, " Geen vermeldingen gevonden.\n\n")
            else:
                for item in items:
                    self._insert_text(self.text_phone_mentions, f"• {item['title']}\n  Link: {item['url']}\n\n")

        self.searching = False
        self.progress_bar_phone.set(1.0)
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), "Telefoon OSINT & tracker dorking voltooid!"))

    # COMPANY SEARCH

    def start_company_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        company_input = self.entry_company.get().strip()
        if not company_input:
            messagebox.showwarning(self.get_text("input_missing"), self.get_text("company_input_missing_msg"))
            return

        self.searching = True
        self.stop_event.clear()
        self.current_company = company_input
        self.progress_bar_company.set(0)

        self._clear_textbox(self.text_company_results)
        self._insert_text(self.text_company_results, self.get_text("company_searching").format(company=company_input))

        threading.Thread(target=self._run_company_search, args=(company_input,), daemon=True).start()

    def _run_company_search(self, company_str):
        co = CompanyOSINT()
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

        def update_progress(current, total):
            fraction = float(current) / float(total)
            self.progress_bar_company.set(fraction)

        results = co.search_company(company_str, country_filter, stop_event=self.stop_event, progress_callback=update_progress)
        self.company_results = results

        self._clear_textbox(self.text_company_results)
        total_hits = 0

        for country, items in results.items():
            self._insert_text(self.text_company_results, f"[ CATEGORIE / LAND: {country.upper()} ]\n")
            if not items:
                self._insert_text(self.text_company_results, " Geen vermeldingen gevonden in de geselecteerde registers.\n\n")
            else:
                for item in items:
                    register_name = item.get("register", "Onbekend Register")
                    self._insert_text(self.text_company_results, f"• [{register_name}] {item['title']}\n  Link: {item['url']}\n\n")
                    total_hits += 1

        self.searching = False
        self.progress_bar_company.set(1.0)
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), self.get_text("company_hits_found").format(count=total_hits)))

    # EMAIL SEARCH (holehe & socialscan)

    def start_email_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        email = self.entry_email.get().strip()
        if not email:
            messagebox.showwarning(self.get_text("input_missing"), "Vul een e-mailadres in.")
            return

        self.searching = True
        self.stop_event.clear()
        self.current_email = email
        self.progress_bar_email.set(0)

        self._clear_textbox(self.text_email_results)
        self._insert_text(self.text_email_results, self.get_text("email_searching").format(email=email))

        threading.Thread(target=self._run_email_search, args=(email,), daemon=True).start()

    def _run_email_search(self, email):
        bin_dir = os.path.dirname(sys.executable)
        ext = ".exe" if os.name == "nt" else ""
        holehe_exec = os.path.join(bin_dir, f"holehe{ext}")
        socialscan_exec = os.path.join(bin_dir, f"socialscan{ext}")

        # Fallback to local script name if bin directory resolve fails
        if not os.path.exists(holehe_exec):
            holehe_exec = "holehe"
        if not os.path.exists(socialscan_exec):
            socialscan_exec = "socialscan"

        try:
            self.progress_bar_email.set(0.1)
            # Run holehe
            self._insert_text(self.text_email_results, "[*] Uitvoeren van holehe e-mailzoeker...\n")
            proc1 = subprocess.Popen(
                [holehe_exec, "--only-used", "--no-color", email],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            self.active_processes.append(proc1)

            while True:
                if self.stop_event.is_set():
                    proc1.terminate()
                    break
                line = proc1.stdout.readline()
                if not line:
                    break
                line_cleaned = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
                self._insert_text(self.text_email_results, line_cleaned)

            self.progress_bar_email.set(0.6)

            # Run socialscan
            if not self.stop_event.is_set():
                self._insert_text(self.text_email_results, "\n[*] Uitvoeren van socialscan e-mailzoeker...\n")
                proc2 = subprocess.Popen(
                    [socialscan_exec, email, "--show-urls"],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
                self.active_processes.append(proc2)

                while True:
                    if self.stop_event.is_set():
                        proc2.terminate()
                        break
                    line = proc2.stdout.readline()
                    if not line:
                        break
                    self._insert_text(self.text_email_results, line)

            if self.stop_event.is_set():
                self._insert_text(self.text_email_results, f"\n{self.get_text('search_stopped')}\n")

            self.progress_bar_email.set(1.0)
        except Exception as e:
            self._insert_text(self.text_email_results, f"\nFout bij uitvoeren e-mail scans: {e}\n")

        self.searching = False
        self.active_processes.clear()
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), "E-mail OSINT lookup voltooid!"))

    # NETWORK SEARCH (dnspython, whois, shodan)

    def start_network_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        target = self.entry_network.get().strip()
        if not target:
            messagebox.showwarning(self.get_text("input_missing"), "Vul een domein of IP-adres in.")
            return

        self.searching = True
        self.stop_event.clear()
        self.current_network = target
        self.progress_bar_network.set(0)

        self._clear_textbox(self.text_network_results)
        self._insert_text(self.text_network_results, self.get_text("network_searching").format(target=target))

        threading.Thread(target=self._run_network_search, args=(target,), daemon=True).start()

    def _run_network_search(self, target):
        self.progress_bar_network.set(0.1)

        # 1. DNS Lookup
        self._insert_text(self.text_network_results, "[ DNS RECORD LOOKUP ]\n")
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME']
        for i, r_type in enumerate(record_types, 1):
            if self.stop_event.is_set():
                break
            try:
                answers = dns.resolver.resolve(target, r_type)
                for rdata in answers:
                    self._insert_text(self.text_network_results, f" {r_type} -> {rdata}\n")
            except Exception:
                pass
            self.progress_bar_network.set(0.1 + (i / len(record_types)) * 0.3)

        self._insert_text(self.text_network_results, "\n")

        # 2. WHOIS Lookup
        if not self.stop_event.is_set():
            self._insert_text(self.text_network_results, "[ WHOIS DOMEIN INFORMATIE ]\n")
            try:
                domain_info = whois.whois(target)
                self._insert_text(self.text_network_results, str(domain_info) + "\n")
            except Exception as e:
                self._insert_text(self.text_network_results, f" Fout bij Whois lookup: {e}\n")
            self.progress_bar_network.set(0.6)

        # 3. IP-API PASSIVE GEOLOCATION & NETWORK OSINT (Free Shodan Alternative)
        if not self.stop_event.is_set():
            self._insert_text(self.text_network_results, "\n[ IP-API PASSIVE GEOLOCATION & NETWORK OSINT ]\n")
            try:
                resolved_ip = target
                try:
                    resolved_ip = str(dns.resolver.resolve(target, 'A')[0])
                except Exception:
                    pass
                from sherlock_project.headers import get_high_end_headers
                headers = get_high_end_headers()
                response = requests.get(f"http://ip-api.com/json/{resolved_ip}", headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        self._insert_text(self.text_network_results, f" IP Adres:      {data.get('query')}\n")
                        self._insert_text(self.text_network_results, f" Land:          {data.get('country')} ({data.get('countryCode')})\n")
                        self._insert_text(self.text_network_results, f" Regio/Stad:    {data.get('regionName')}, {data.get('city')}\n")
                        self._insert_text(self.text_network_results, f" ISP:           {data.get('isp')}\n")
                        self._insert_text(self.text_network_results, f" Organisatie:   {data.get('org')}\n")
                        self._insert_text(self.text_network_results, f" AS / Netwerk:  {data.get('as')}\n")
                        self._insert_text(self.text_network_results, f" Coördinaten:   Lat: {data.get('lat')}, Lon: {data.get('lon')}\n")
                    else:
                        self._insert_text(self.text_network_results, f" IP-API lookup mislukt: {data.get('message', 'Onbekende fout')}\n")
                else:
                    self._insert_text(self.text_network_results, f" IP-API lookup mislukt met status code: {response.status_code}\n")
            except Exception as e:
                self._insert_text(self.text_network_results, f" IP-API query mislukt: {e}\n")

        # 4. SHODAN Lookup
        if not self.stop_event.is_set():
            self._insert_text(self.text_network_results, "\n[ SHODAN OPEN POORTEN & KWETSBAARHEDEN ]\n")
            shodan_key = self.settings.get("shodan_api_key", "").strip()
            if not shodan_key:
                self._insert_text(self.text_network_results, " Geen Shodan API-sleutel geconfigureerd in de Instellingen tab.\n")
            else:
                try:
                    api = shodan.Shodan(shodan_key)
                    # Resolve IP if domein given, or use direct
                    resolved_ip = target
                    try:
                        resolved_ip = str(dns.resolver.resolve(target, 'A')[0])
                        self._insert_text(self.text_network_results, f" Geresolveerd IP voor Shodan scan: {resolved_ip}\n")
                    except Exception:
                        pass

                    host = api.host(resolved_ip)
                    self._insert_text(self.text_network_results, f" IP: {host.get('ip_str')}\n")
                    self._insert_text(self.text_network_results, f" Organisatie: {host.get('org', 'Onbekend')}\n")
                    self._insert_text(self.text_network_results, f" Open poorten: {host.get('ports', [])}\n")
                    if host.get('vulns'):
                        self._insert_text(self.text_network_results, f" Kwetsbaarheden (CVEs): {host.get('vulns')}\n")
                    else:
                        self._insert_text(self.text_network_results, " Geen bekende kwetsbaarheden gedetecteerd door Shodan.\n")
                except Exception as e:
                    self._insert_text(self.text_network_results, f" Shodan query mislukt: {e}\n")

        if self.stop_event.is_set():
            self._insert_text(self.text_network_results, f"\n{self.get_text('search_stopped')}\n")

        self.searching = False
        self.progress_bar_network.set(1.0)
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), "Netwerk OSINT lookup voltooid!"))

    # PERSON SEARCH

    def start_person_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        first = self.entry_first_name.get().strip()
        last = self.entry_last_name.get().strip()
        extra = self.entry_person_extra.get().strip()

        if not first or not last:
            messagebox.showwarning(self.get_text("input_missing"), "Vul tenminste een voor- en achternaam in.")
            return

        self.searching = True
        self.stop_event.clear()
        self.current_person_first = first
        self.current_person_last = last
        self.progress_bar_person.set(0)

        self._clear_textbox(self.text_person_results)
        self._insert_text(self.text_person_results, self.get_text("person_searching").format(first=first, last=last))

        threading.Thread(target=self._run_person_search, args=(first, last, extra), daemon=True).start()

    def _run_person_search(self, first, last, extra):
        po = PersonOSINT()

        def update_progress(current, total):
            fraction = float(current) / float(total)
            self.progress_bar_person.set(fraction)

        results = po.search_person(first, last, extra, stop_event=self.stop_event, progress_callback=update_progress)
        self.person_results = results

        self._clear_textbox(self.text_person_results)
        for category, items in results.items():
            self._insert_text(self.text_person_results, f"[ {category.upper()} ]\n")
            if not items:
                self._insert_text(self.text_person_results, " Geen vermeldingen gevonden.\n\n")
            else:
                for item in items:
                    self._insert_text(self.text_person_results, f"• {item['title']}\n  Link: {item['url']}\n\n")

        if self.stop_event.is_set():
            self._insert_text(self.text_person_results, f"\n{self.get_text('search_stopped')}\n")

        self.searching = False
        self.progress_bar_person.set(1.0)
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), "Personen OSINT lookup voltooid!"))

    # DOX SEARCH

    def start_dox_search(self):
        if self.searching:
            messagebox.showwarning(self.get_text("warning"), self.get_text("search_active_warning"))
            return

        username = self.entry_dox_username.get().strip()
        email = self.entry_dox_email.get().strip()
        phone = self.entry_dox_phone.get().strip()
        name = self.entry_dox_name.get().strip()
        city = self.entry_dox_city.get().strip()

        if not any([username, email, phone, name, city]):
            messagebox.showwarning(self.get_text("input_missing"), "Vul tenminste één formulier-veld in.")
            return

        self.searching = True
        self.stop_event.clear()

        self.current_dox_username = username
        self.current_dox_email = email
        self.current_dox_phone = phone
        self.current_dox_name = name
        self.current_dox_city = city

        self.progress_bar_dox.set(0)

        self._clear_textbox(self.text_dox_results)
        self._insert_text(self.text_dox_results, self.get_text("dox_searching"))

        threading.Thread(target=self._run_dox_search, daemon=True).start()

    def _run_dox_search(self):
        dp = DoxProfiler()

        def update_progress(current, total):
            fraction = float(current) / float(total)
            self.progress_bar_dox.set(fraction)

        results = dp.search_dox_dossier(
            username=self.current_dox_username,
            email=self.current_dox_email,
            phone=self.current_dox_phone,
            name=self.current_dox_name,
            city=self.current_dox_city,
            stop_event=self.stop_event,
            progress_callback=update_progress
        )

        # Fire off our async deep engines as background tasks to demonstrate orchestrator
        if self.current_dox_username:
            self.orchestrator.submit_task("socmint", self.socmint_engine.run_all(self.current_dox_username))
        if self.current_dox_phone:
            self.orchestrator.submit_task("phone", self.phone_engine.run_all(self.current_dox_phone))

        self.dox_results = results

        self._clear_textbox(self.text_dox_results)
        for category, items in results.items():
            self._insert_text(self.text_dox_results, f"[ {category.upper()} ]\n")
            if not items:
                self._insert_text(self.text_dox_results, " Geen vermeldingen gevonden.\n\n")
            else:
                for item in items:
                    self._insert_text(self.text_dox_results, f"• {item['title']}\n  Link: {item['url']}\n\n")

        if self.stop_event.is_set():
            self._insert_text(self.text_dox_results, f"\n{self.get_text('search_stopped')}\n")

        self.searching = False
        self.progress_bar_dox.set(1.0)
        self.after(100, lambda: messagebox.showinfo(self.get_text("success"), self.get_text("dox_finished")))

    # Display update logic helpers

    def _update_username_results_display(self):
        self._clear_textbox(self.text_username_results)
        if self.current_username:
            self._insert_text(self.text_username_results, f"[*] No shit Sherlock zoekopdracht resultaten voor '{self.current_username}':\n\n")

        filter_query = self.entry_filter_username.get().strip().lower()
        claimed_count = 0
        display_count = 0

        for site, info in self.search_results.items():
            status_obj = info.get("status")
            status_str = str(status_obj.status) if hasattr(status_obj, "status") else str(status_obj)

            is_claimed = "claimed" in status_str.lower() or "exists" in status_str.lower() or "gevonden" in status_str.lower()
            if is_claimed:
                claimed_count += 1

            if filter_query and (filter_query not in site.lower() and filter_query not in (info.get("url_user") or "").lower()):
                continue

            if is_claimed:
                self._insert_text(self.text_username_results, f"[+] {site}: {info.get('url_user')}\n")
                display_count += 1
            elif self.all_sites_var.get():
                self._insert_text(self.text_username_results, f"[-] {site}: {status_str}\n")
                display_count += 1

        filter_suffix = f" (gefilterd, {display_count} getoond)" if filter_query else ""
        if not self.searching:
            self._insert_text(self.text_username_results, f"\n[*] Klaar! Totaal {claimed_count} accounts gedetecteerd{filter_suffix}.")

    def _update_username_dorks_display(self):
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

    # --- REPORT EXPORTS ---

    def export_results(self, file_format, is_phone=False, is_company=False, is_email=False, is_network=False, is_person=False, is_dox=False):
        # Resolve target and metadata names
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
        elif is_email:
            if not self.current_email:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_email_search_yet"))
                return
            target_name = self.current_email
        elif is_network:
            if not self.current_network:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_network_search_yet"))
                return
            target_name = self.current_network
        elif is_person:
            if not self.person_results:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_person_search_yet"))
                return
            target_name = f"{self.current_person_first}_{self.current_person_last}"
        elif is_dox:
            if not self.dox_results:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_dox_search_yet"))
                return
            target_name = f"dox_dossier_{self.current_dox_name or self.current_dox_username or 'target'}"
        else:
            if not self.search_results:
                messagebox.showwarning(self.get_text("error"), self.get_text("no_username_search_yet"))
                return
            target_name = self.current_username

        # Save dialog setup
        filetypes_map = {
            "txt": ("TXT Bestanden (*.txt)" if self.language_var.get() == "nl" else "TXT Files (*.txt)", "*.txt"),
            "docx": ("Microsoft Word (*.docx)", "*.docx"),
            "pdf": ("PDF Documenten (*.pdf)" if self.language_var.get() == "nl" else "PDF Documents (*.pdf)", "*.pdf")
        }

        extension = f".{file_format}"
        initial_filename = f"no_shit_sherlock_rapport_{target_name}{extension}".replace("+", "")
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
                elif is_email:
                    ReportGenerator.export_simple_txt(filepath, "No shit Sherlock E-mail OSINT Rapport", f"E-mail: {self.current_email}", self.text_email_results.get("1.0", tk.END))
                elif is_network:
                    ReportGenerator.export_simple_txt(filepath, "No shit Sherlock Netwerk & Domein OSINT", f"Domein/IP: {self.current_network}", self.text_network_results.get("1.0", tk.END))
                elif is_person:
                    ReportGenerator.export_company_txt(filepath, f"{self.current_person_first} {self.current_person_last}", self.person_results)
                elif is_dox:
                    ReportGenerator.export_company_txt(filepath, f"Dox Dossier: {self.current_dox_name or self.current_dox_username}", self.dox_results)
                else:
                    ReportGenerator.export_txt(filepath, self.current_username, self.search_results, username_dorks=self.username_dorks_results)
            elif file_format == "docx":
                if is_phone:
                    ReportGenerator.export_docx(filepath, "", {}, self.phone_meta, self.phone_results)
                elif is_company:
                    ReportGenerator.export_company_docx(filepath, self.current_company, self.company_results)
                elif is_email:
                    ReportGenerator.export_simple_docx(filepath, "No shit Sherlock E-mail OSINT Rapport", f"E-mail: {self.current_email}", self.text_email_results.get("1.0", tk.END))
                elif is_network:
                    ReportGenerator.export_simple_docx(filepath, "No shit Sherlock Netwerk & Domein OSINT", f"Domein/IP: {self.current_network}", self.text_network_results.get("1.0", tk.END))
                elif is_person:
                    ReportGenerator.export_company_docx(filepath, f"{self.current_person_first} {self.current_person_last}", self.person_results)
                elif is_dox:
                    ReportGenerator.export_company_docx(filepath, f"Dox Dossier: {self.current_dox_name or self.current_dox_username}", self.dox_results)
                else:
                    ReportGenerator.export_docx(filepath, self.current_username, self.search_results, username_dorks=self.username_dorks_results)
            elif file_format == "pdf":
                if is_phone:
                    ReportGenerator.export_pdf(filepath, "", {}, self.phone_meta, self.phone_results)
                elif is_company:
                    ReportGenerator.export_company_pdf(filepath, self.current_company, self.company_results)
                elif is_email:
                    ReportGenerator.export_simple_pdf(filepath, "No shit Sherlock E-mail OSINT Rapport", f"E-mail: {self.current_email}", self.text_email_results.get("1.0", tk.END))
                elif is_network:
                    ReportGenerator.export_simple_pdf(filepath, "No shit Sherlock Netwerk & Domein OSINT", f"Domein/IP: {self.current_network}", self.text_network_results.get("1.0", tk.END))
                elif is_person:
                    ReportGenerator.export_company_pdf(filepath, f"{self.current_person_first} {self.current_person_last}", self.person_results)
                elif is_dox:
                    ReportGenerator.export_company_pdf(filepath, f"Dox Dossier: {self.current_dox_name or self.current_dox_username}", self.dox_results)
                else:
                    ReportGenerator.export_pdf(filepath, self.current_username, self.search_results, username_dorks=self.username_dorks_results)

            messagebox.showinfo(self.get_text("success"), self.get_text("export_success").format(filepath=filepath))
        except Exception as e:
            messagebox.showerror(self.get_text("error"), self.get_text("export_failed").format(error=e))

    # --- SETTINGS TAB & UPDATES ---

    def create_settings_tab(self):
        self.tab_settings = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_settings.grid_rowconfigure(4, weight=1)
        self.tab_settings.grid_columnconfigure(0, weight=1)

        self.settings_title_lbl = ctk.CTkLabel(self.tab_settings, text=self.get_text("settings_title"), font=ctk.CTkFont(size=22, weight="bold"))
        self.settings_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Language Selection Panel
        lang_frame = ctk.CTkFrame(self.tab_settings)
        lang_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        lang_frame.grid_columnconfigure(1, weight=1)

        self.lang_section_lbl = ctk.CTkLabel(lang_frame, text=self.get_text("language_section"), font=ctk.CTkFont(size=14, weight="bold"))
        self.lang_section_lbl.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.lang_combo = ctk.CTkOptionMenu(lang_frame, values=["Nederlands", "English"], command=self.change_language)
        self.lang_combo.grid(row=0, column=1, padx=15, pady=15, sticky="e")
        if self.language_var.get() == "nl":
            self.lang_combo.set("Nederlands")
        else:
            self.lang_combo.set("English")

        # Shodan API Key configuration panel
        shodan_frame = ctk.CTkFrame(self.tab_settings)
        shodan_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=5)
        shodan_frame.grid_columnconfigure(1, weight=1)

        self.shodan_label = ctk.CTkLabel(shodan_frame, text=self.get_text("shodan_api_label"), font=ctk.CTkFont(size=14, weight="bold"))
        self.shodan_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.entry_shodan = ctk.CTkEntry(shodan_frame, placeholder_text=self.get_text("shodan_api_placeholder"), width=300)
        self.entry_shodan.grid(row=0, column=1, padx=15, pady=15, sticky="e")
        self.entry_shodan.insert(0, self.settings.get("shodan_api_key", ""))
        self.entry_shodan.bind("<KeyRelease>", self.save_shodan_key)

        # Updates Panel
        update_frame = ctk.CTkFrame(self.tab_settings)
        update_frame.grid(row=3, column=0, sticky="ew", pady=10, padx=5)
        update_frame.grid_columnconfigure(0, weight=1)

        self.updates_section_lbl = ctk.CTkLabel(update_frame, text=self.get_text("updates_section"), font=ctk.CTkFont(size=14, weight="bold"))
        self.updates_section_lbl.grid(row=0, column=0, padx=15, pady=15, sticky="w")

        self.current_version_lbl = ctk.CTkLabel(update_frame, text=f"{self.get_text('current_version')}: No shit Sherlock v{__version__}", font=ctk.CTkFont(size=13))
        self.current_version_lbl.grid(row=1, column=0, padx=15, pady=5, sticky="w")

        self.update_status_lbl = ctk.CTkLabel(update_frame, text=f"Status: {self.get_text('update_status_idle')}", font=ctk.CTkFont(size=13))
        self.update_status_lbl.grid(row=2, column=0, padx=15, pady=5, sticky="w")

        self.btn_check_updates = ctk.CTkButton(update_frame, text=self.get_text("btn_check_updates"), command=self.start_check_updates, fg_color="#2B6CB0", hover_color="#1A365D")
        self.btn_check_updates.grid(row=3, column=0, padx=15, pady=15, sticky="w")

    def save_shodan_key(self, event=None):
        key = self.entry_shodan.get().strip()
        self.settings["shodan_api_key"] = key
        save_settings(self.settings)

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    # Core system updates checking logic
    def start_check_updates(self):
        self.update_status_lbl.configure(text=f"Status: {self.get_text('update_status_checking')}")
        self.btn_check_updates.configure(state="disabled")
        threading.Thread(target=self._run_check_updates, daemon=True).start()

    def _run_check_updates(self):
        try:
            # Check if git is available and we are inside a git work tree
            git_check = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
            if git_check.returncode != 0:
                raise RuntimeError("Not in a Git repository or Git is not installed.")

            default_branch = "Advance-osint"

            # Fetch target branch
            fetch_res = subprocess.run(["git", "fetch", "origin", default_branch], capture_output=True, text=True)
            if fetch_res.returncode != 0:
                raise RuntimeError(f"Failed to fetch updates from remote repository. Check your internet connection or git permissions.\nDetails: {fetch_res.stderr.strip()}")

            # Check lagging commits count
            res = subprocess.run(["git", "rev-list", "--count", f"HEAD..origin/{default_branch}"], capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"Failed to check commit history.\nDetails: {res.stderr.strip()}")

            lagging_count = int(res.stdout.strip())

            if lagging_count > 0:
                self.after(0, lambda count=lagging_count: self._update_available_action(count))
            else:
                self.after(0, lambda: self._update_up_to_date_action())
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda msg=err_msg: self._update_error_action(msg))

    def _update_available_action(self, lagging_count):
        msg = f"{self.get_text('update_status_available')} ({lagging_count} commit(s) achter)"
        self.update_status_lbl.configure(text=f"Status: {msg}")
        self.btn_check_updates.configure(state="normal")

        prompt_title = self.get_text("update_prompt_title")
        prompt_msg = self.get_text("update_prompt_msg").format(commits=lagging_count)

        response = messagebox.askyesno(prompt_title, prompt_msg)
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
            default_branch = "Advance-osint"

            # Reset to origin branch
            reset_res = subprocess.run(["git", "reset", "--hard", f"origin/{default_branch}"], capture_output=True, text=True)
            if reset_res.returncode != 0:
                raise RuntimeError(f"Failed to apply the update (git reset).\nDetails: {reset_res.stderr.strip()}")

            # Install dependencies if needed
            pip_res = subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], capture_output=True, text=True)
            if pip_res.returncode != 0:
                raise RuntimeError(f"Failed to install updated dependencies (pip install).\nDetails: {pip_res.stderr.strip()}")

            self.after(0, lambda: self._show_update_success_and_restart())
        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror(self.get_text("error"), f"Update failed: {err}"))

    def _show_update_success_and_restart(self):
        messagebox.showinfo(self.get_text("update_success_title"), self.get_text("update_success_msg"))
        self.destroy()
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(f"Error restarting: {e}")
            sys.exit(0)


    def create_maigret_tab(self):
        self.maigret_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.maigret_frame.grid_columnconfigure(0, weight=1)
        self.maigret_frame.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkLabel(self.maigret_frame, text="Deep Username Search (Maigret)", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Input Section
        input_frame = ctk.CTkFrame(self.maigret_frame)
        input_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.maigret_target_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter username...")
        self.maigret_target_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.maigret_sites_entry = ctk.CTkEntry(input_frame, placeholder_text="Top N sites (default 100)", width=150)
        self.maigret_sites_entry.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.maigret_proxy_entry = ctk.CTkEntry(input_frame, placeholder_text="Proxy (optional)", width=200)
        self.maigret_proxy_entry.grid(row=0, column=2, padx=5, pady=10, sticky="w")

        self.maigret_search_btn = ctk.CTkButton(input_frame, text="Deep Search", command=self.start_maigret_search)
        self.maigret_search_btn.grid(row=0, column=3, padx=(5, 10), pady=10)

        # Results Textbox
        self.maigret_result_box = ctk.CTkTextbox(self.maigret_frame, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.maigret_result_box.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        self.maigret_result_box._textbox.tag_config("found", foreground="light green")
        self.maigret_result_box._textbox.tag_config("header", foreground="cyan", font=("Consolas", 12, "bold"))
        self.maigret_result_box._textbox.tag_config("error", foreground="red")

        # Progress Bar
        self.maigret_progress = ctk.CTkProgressBar(self.maigret_frame)
        self.maigret_progress.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.maigret_progress.set(0)

        self.maigret_is_running = False

    def start_maigret_search(self):
        if self.maigret_is_running:
            return

        username = self.maigret_target_entry.get().strip()
        if not username:
            self.maigret_result_box.insert("end", "[!] Please enter a username.\n", "error")
            return

        proxy = self.maigret_proxy_entry.get().strip() or None
        top_sites_str = self.maigret_sites_entry.get().strip()
        top_sites = 100
        if top_sites_str.isdigit():
            top_sites = int(top_sites_str)

        self.maigret_is_running = True
        self.maigret_search_btn.configure(state="disabled", text="Searching...")
        self.maigret_progress.set(0)
        self.maigret_progress.start()

        self.maigret_result_box.delete("1.0", "end")
        self.maigret_result_box.insert("end", f"[*] Starting Deep Username Search for '{username}' (Top {top_sites} sites)...\n", "header")

        # Run in thread
        import threading
        import asyncio
        threading.Thread(target=self._run_maigret_async, args=(username, proxy, top_sites), daemon=True).start()

    def _run_maigret_async(self, username, proxy, top_sites):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            engine = MaigretEngine(logger=self.logger)
            results = loop.run_until_complete(engine.search(username, timeout=10, proxy=proxy, top=top_sites))

            self.after(0, self._on_maigret_complete, results)
        except Exception as e:
            self.after(0, self._on_maigret_error, str(e))
        finally:
            loop.close()

    def _on_maigret_complete(self, results):
        self.maigret_progress.stop()
        self.maigret_progress.set(1)
        self.maigret_is_running = False
        self.maigret_search_btn.configure(state="normal", text="Deep Search")

        if not results:
            self.maigret_result_box.insert("end", "[-] No accounts found.\n")
            return

        self.maigret_result_box.insert("end", f"[+] Found {len(results)} accounts:\n", "header")
        for res in results:
            self.maigret_result_box.insert("end", f" - {res['site']}: ", "header")
            self.maigret_result_box.insert("end", f"{res['url_user']}\n", "found")

            # Print additional profile data if any
            data = res.get('data', {})
            if data:
                for k, v in data.items():
                    if v:
                        self.maigret_result_box.insert("end", f"      {k}: {v}\n")
        self.maigret_result_box.insert("end", "\n[*] Deep Search Completed.\n", "header")

    def _on_maigret_error(self, err):
        self.maigret_progress.stop()
        self.maigret_progress.set(0)
        self.maigret_is_running = False
        self.maigret_search_btn.configure(state="normal", text="Deep Search")
        self.maigret_result_box.insert("end", f"[!] Error during search: {err}\n", "error")

def main():
    app = SherlockGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
