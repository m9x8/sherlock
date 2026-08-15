"""
Sherlock Company Search Module
Provides company registration information lookups and OSINT web dorking
across official registries, business directories, websites, socials, and news worldwide.
"""

import urllib.parse
import re
from typing import Dict, List, Any
from sherlock_project.phone_search import PhoneOSINT

class CompanyOSINT:
    def __init__(self, timeout: int = 15):
        self.phone_osint = PhoneOSINT(timeout=timeout)

    def search_company(self, company_name: str, country_filter: str = "Alle", stop_event=None, progress_callback=None) -> Dict[str, List[Dict[str, str]]]:
        """
        Performs high-end company OSINT dorking across multiple categories (Registers, Socials, Domain mentions, News, Leaks).
        Supports country filter, stop event, and progress tracking.
        """
        if not company_name:
            return {}

        escaped_name = f'"{company_name}"'

        # Main categories
        categories = {
            "Officiële Registers": {
                "KVK (NL)": f"site:kvk.nl {escaped_name}",
                "CompanyInfo (NL)": f"site:companyinfo.nl {escaped_name}",
                "OpenKVK (NL)": f"site:openkvk.nl OR site:opencorporates.com/companies/nl {escaped_name}",
                "Drimble (NL)": f"site:drimble.nl {escaped_name}",
                "Companies House (UK)": f"site:find-and-update.company-information.service.gov.uk {escaped_name}",
                "Handelsregister (DE)": f"site:handelsregister.de {escaped_name}",
                "KBO / KBO-BCE (BE)": f"site:kbopub.economie.fgov.be {escaped_name}",
                "OpenCorporates Global": f"site:opencorporates.com {escaped_name} -site:opencorporates.com/companies/nl -site:opencorporates.com/companies/gb",
                "Kompass (Global)": f"site:kompass.com {escaped_name}",
                "Dun & Bradstreet": f"site:dnb.com {escaped_name}"
            },
            "Social Media & Profielen": {
                "LinkedIn": f"site:linkedin.com/company {escaped_name}",
                "Facebook": f"site:facebook.com {escaped_name}",
                "Twitter / X": f"site:twitter.com OR site:x.com {escaped_name}",
                "Instagram": f"site:instagram.com {escaped_name}",
                "YouTube": f"site:youtube.com {escaped_name}"
            },
            "Website & Domein Vermeldingen": {
                "Algemeen Web": f'"{company_name}" contact OR over-ons OR about-us OR "adres"',
                "E-mail & Contact": f'"{company_name}" "email" OR "contact" OR "support"',
                "Domein / Vacatures": f"site:indeed.com OR site:glassdoor.com OR site:linkedin.com/jobs {escaped_name}"
            },
            "Nieuws & Persberichten": {
                "Nederlands Nieuws": f"(site:nu.nl OR site:nos.nl OR site:ad.nl OR site:telegraaf.nl OR site:rtlnieuws.nl) {escaped_name}",
                "Global News / Medium": f"(site:reuters.com OR site:bloomberg.com OR site:medium.com OR site:news.google.com) {escaped_name}"
            },
            "Lekken & Databases": {
                "Pastebin / Code Gidsen": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com) {escaped_name}",
                "Lek Vermeldingen": f"(site:leak-lookup.com OR site:haveibeenpwned.com OR site:dehashed.com) {escaped_name}"
            },
            "Reviews & Klantenfeedback": {
                "Trustpilot & Klachten": f"(site:trustpilot.com OR site:klachtenkompas.nl OR site:klacht.nl OR site:radar.avrotros.nl OR site:kassa.bnnvara.nl) {escaped_name}",
                "Google Reviews / Local": f"(site:google.com/maps OR site:yelp.com OR site:tripadvisor.com) {escaped_name}"
            },
            "Financieel & Faillissementen": {
                "Insolventies & Faillissementen": f"(site:faillissementsdossier.nl OR site:insolventies.rechtspraak.nl OR site:rechtspraak.nl) {escaped_name} (failliet OR surseance OR insolventie)",
                "Trademarks & Octrooien": f"(site:tmdn.org OR site:wipo.int OR site:euipo.europa.eu OR site:boip.int) {escaped_name}"
            },
            "Aanbestedingen & Contracten": {
                "Tenders & Overheidsopdrachten": f"(site:tenderned.nl OR site:aanbestedingskalender.nl OR site:eu-supply.com OR site:ted.europa.eu) {escaped_name}"
            },
            "Documenten & Bestanden": {
                "Index & Verborgen Bestanden": f"(intitle:\"index of\" OR inurl:wp-content/uploads) {escaped_name}",
                "PDF & Rapportages": f"(filetype:pdf OR filetype:xls OR filetype:xlsx OR filetype:doc OR filetype:docx) {escaped_name} (jaarverslag OR rapport OR report OR confidential OR vertrouwelijk)"
            }
        }

        # Handle Country Filtering
        filtered_categories = {}
        if country_filter == "Nederland":
            filtered_categories = {
                "Officiële Registers (NL)": {
                    "KVK (NL)": f"site:kvk.nl {escaped_name}",
                    "CompanyInfo (NL)": f"site:companyinfo.nl {escaped_name}",
                    "OpenKVK (NL)": f"site:openkvk.nl OR site:opencorporates.com/companies/nl {escaped_name}",
                    "Drimble (NL)": f"site:drimble.nl {escaped_name}"
                },
                "Social Media & Profielen": categories["Social Media & Profielen"],
                "Website & Domein Vermeldingen": categories["Website & Domein Vermeldingen"],
                "Nieuws & Persberichten (NL)": {
                    "Nederlands Nieuws": categories["Nieuws & Persberichten"]["Nederlands Nieuws"]
                },
                "Lekken & Databases": categories["Lekken & Databases"],
                "Reviews & Klantenfeedback": categories["Reviews & Klantenfeedback"],
                "Financieel & Faillissementen (NL)": {
                    "Insolventies & Faillissementen": categories["Financieel & Faillissementen"]["Insolventies & Faillissementen"]
                },
                "Aanbestedingen (NL/EU)": categories["Aanbestedingen & Contracten"],
                "Documenten & Bestanden": categories["Documenten & Bestanden"]
            }
        elif country_filter == "Verenigd Koninkrijk":
            filtered_categories = {
                "Officiële Registers (UK)": {
                    "Companies House (UK)": f"site:find-and-update.company-information.service.gov.uk {escaped_name}",
                "Handelsregister (DE)": f"site:handelsregister.de {escaped_name}",
                "KBO / KBO-BCE (BE)": f"site:kbopub.economie.fgov.be {escaped_name}",
                "OpenCorporates Global": f"site:opencorporates.com {escaped_name} -site:opencorporates.com/companies/nl -site:opencorporates.com/companies/gb",
                "Kompass (Global)": f"site:kompass.com {escaped_name}",
                "Dun & Bradstreet": f"site:dnb.com {escaped_name}"
            },
                "Social Media & Profielen": categories["Social Media & Profielen"],
                "Website & Domein Vermeldingen": categories["Website & Domein Vermeldingen"],
                "Nieuws & Persberichten": {
                    "Global News": categories["Nieuws & Persberichten"]["Global News / Medium"]
                },
                "Lekken & Databases": categories["Lekken & Databases"],
                "Reviews & Klantenfeedback": categories["Reviews & Klantenfeedback"],
                "Financieel & Trademarks": {
                    "Trademarks & Octrooien": categories["Financieel & Faillissementen"]["Trademarks & Octrooien"]
                },
                "Aanbestedingen (EU/Global)": categories["Aanbestedingen & Contracten"],
                "Documenten & Bestanden": categories["Documenten & Bestanden"]
            }
        elif country_filter == "Duitsland":
            filtered_categories = {
                "Officiële Registers (DE)": {
                    "Handelsregister (DE)": f"site:handelsregister.de {escaped_name}",
                    "Unternehmensregister (DE)": f"site:unternehmensregister.de {escaped_name}"
                },
                "Social Media & Profielen": categories["Social Media & Profielen"],
                "Website & Domein Vermeldingen": categories["Website & Domein Vermeldingen"],
                "Nieuws & Persberichten": {
                    "Global News": categories["Nieuws & Persberichten"]["Global News / Medium"]
                },
                "Lekken & Databases": categories["Lekken & Databases"],
                "Reviews & Klantenfeedback": categories["Reviews & Klantenfeedback"],
                "Financieel & Trademarks": {
                    "Trademarks & Octrooien": categories["Financieel & Faillissementen"]["Trademarks & Octrooien"]
                },
                "Aanbestedingen (EU/Global)": categories["Aanbestedingen & Contracten"],
                "Documenten & Bestanden": categories["Documenten & Bestanden"]
            }
        elif country_filter == "België":
            filtered_categories = {
                "Officiële Registers (BE)": {
                    "KBO / KBO-BCE (BE)": f"site:kbopub.economie.fgov.be {escaped_name}",
                    "Staatsbladmonitor (BE)": f"site:staatsbladmonitor.be {escaped_name}"
                },
                "Social Media & Profielen": categories["Social Media & Profielen"],
                "Website & Domein Vermeldingen": categories["Website & Domein Vermeldingen"],
                "Nieuws & Persberichten": {
                    "Global News": categories["Nieuws & Persberichten"]["Global News / Medium"]
                },
                "Lekken & Databases": categories["Lekken & Databases"],
                "Reviews & Klantenfeedback": categories["Reviews & Klantenfeedback"],
                "Financieel & Trademarks": {
                    "Trademarks & Octrooien": categories["Financieel & Faillissementen"]["Trademarks & Octrooien"]
                },
                "Aanbestedingen (EU/Global)": categories["Aanbestedingen & Contracten"],
                "Documenten & Bestanden": categories["Documenten & Bestanden"]
            }
        elif country_filter == "Wereldwijd / LinkedIn":
            filtered_categories = {
                "Officiële Registers (Global)": {
                    "OpenCorporates Global": categories["Officiële Registers"]["OpenCorporates Global"]
                },
                "Social Media & Profielen": {
                    "LinkedIn": categories["Social Media & Profielen"]["LinkedIn"]
                },
                "Website & Domein Vermeldingen": categories["Website & Domein Vermeldingen"],
                "Nieuws & Persberichten": {
                    "Global News": categories["Nieuws & Persberichten"]["Global News / Medium"]
                },
                "Lekken & Databases": categories["Lekken & Databases"],
                "Reviews & Klantenfeedback": categories["Reviews & Klantenfeedback"],
                "Financieel & Trademarks": categories["Financieel & Faillissementen"],
                "Aanbestedingen & Contracten": categories["Aanbestedingen & Contracten"],
                "Documenten & Bestanden": categories["Documenten & Bestanden"]
            }
        else:
            filtered_categories = categories

        # Calculate total queries for progress tracking
        total_queries = sum(len(sites) for sites in filtered_categories.values())
        completed_queries = 0

        results = {}
        for category_name, sites in filtered_categories.items():
            category_results = []
            for site_name, query in sites.items():
                if stop_event and stop_event.is_set():
                    break
                site_hits = self.phone_osint._advanced_search(query)
                # Fallback to loose search query if exact matches yield 0 results
                if not site_hits:
                    loose_query = query.replace(escaped_name, company_name)
                    site_hits = self.phone_osint._advanced_search(loose_query)

                for hit in site_hits:
                    hit["register"] = site_name
                    category_results.append(hit)
                completed_queries += 1
                if progress_callback and total_queries > 0:
                    progress_callback(completed_queries, total_queries)
            results[category_name] = category_results
            if stop_event and stop_event.is_set():
                break

        # Run direct OpenKVK scraper fallback if Nederland country was filter or general search
        if not (stop_event and stop_event.is_set()) and country_filter in ["Alle", "Nederland"]:
            from sherlock_project.scraper import HighEndScraper
            try:
                import asyncio

                async def _scrape_and_close():
                    async with HighEndScraper() as scraper:
                        return await scraper.scrape_company_direct_details(company_name)

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(1) as pool:
                        def run_in_thread():
                            return asyncio.run(_scrape_and_close())
                        direct_hits = pool.submit(run_in_thread).result()
                else:
                    direct_hits = asyncio.run(_scrape_and_close())

                if direct_hits:
                    target_cat = "Officiële Registers (NL)" if "Officiële Registers (NL)" in results else "Officiële Registers"
                    if target_cat not in results:
                        results[target_cat] = []
                    for dh in direct_hits:
                        dh["register"] = "OpenKVK Direct"
                    results[target_cat] = direct_hits + results[target_cat]
            except Exception:
                pass

        return results
