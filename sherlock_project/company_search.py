"""
Sherlock Company Search Module
Provides company registration information lookups and OSINT web dorking
across official registries and business directories worldwide.
"""

import urllib.parse
import re
from typing import Dict, List, Any
from sherlock_project.phone_search import PhoneOSINT

class CompanyOSINT:
    def __init__(self, timeout: int = 15):
        self.phone_osint = PhoneOSINT(timeout=timeout)

    def search_company(self, company_name: str, country_filter: str = "Alle") -> Dict[str, List[Dict[str, str]]]:
        """
        Searches for company information across several registries and websites via DuckDuckGo.
        The search can be filtered by country.
        """
        if not company_name:
            return {}

        escaped_name = f'"{company_name}"'

        # Map registry websites by country
        registries = {
            "Nederland": {
                "KVK": f"site:kvk.nl {escaped_name}",
                "CompanyInfo": f"site:companyinfo.nl {escaped_name}",
                "OpenKVK": f"site:openkvk.nl OR site:opencorporates.com/companies/nl {escaped_name}",
                "Drimble": f"site:drimble.nl {escaped_name}"
            },
            "Verenigd Koninkrijk": {
                "Companies House": f"site:find-and-update.company-information.service.gov.uk {escaped_name}",
                "OpenCorporates UK": f"site:opencorporates.com/companies/gb {escaped_name}"
            },
            "Duitsland": {
                "Handelsregister": f"site:handelsregister.de {escaped_name}",
                "Unternehmensregister": f"site:unternehmensregister.de {escaped_name}"
            },
            "België": {
                "KBO / KBO-BCE": f"site:kbopub.economie.fgov.be {escaped_name}",
                "Staatsbladmonitor": f"site:staatsbladmonitor.be {escaped_name}"
            },
            "Wereldwijd / LinkedIn": {
                "OpenCorporates Global": f"site:opencorporates.com {escaped_name} -site:opencorporates.com/companies/nl -site:opencorporates.com/companies/gb",
                "LinkedIn Companies": f"site:linkedin.com/company {escaped_name}"
            }
        }

        # Filter categories to search
        categories_to_search = {}
        if country_filter == "Alle":
            categories_to_search = registries
        elif country_filter in registries:
            categories_to_search = {country_filter: registries[country_filter]}
        else:
            # Fallback if country not specifically mapped
            categories_to_search = registries

        results = {}
        for country, sites in categories_to_search.items():
            country_results = []
            for site_name, query in sites.items():
                site_hits = self.phone_osint._duckduckgo_search(query)
                # Annotate hits with source register
                for hit in site_hits:
                    hit["register"] = site_name
                    country_results.append(hit)
            results[country] = country_results

        return results
