"""
Sherlock Person Search Module
Provides advanced OSINT name dorking for finding a person's digital footprint.
"""

import urllib.parse
import re
from typing import Dict, List, Any
from sherlock_project.phone_search import PhoneOSINT

class PersonOSINT:
    def __init__(self, timeout: int = 15):
        self.phone_osint = PhoneOSINT(timeout=timeout)

    def search_person(self, first_name: str, last_name: str, extra_info: str = "", stop_event=None, progress_callback=None) -> Dict[str, List[Dict[str, str]]]:
        """
        Runs advanced dorking queries across several categories using Google/DuckDuckGo
        to find information about a person by First Name and Last Name.
        """
        if not first_name or not last_name:
            return {}

        full_name = f"{first_name} {last_name}"
        escaped_name = f'"{full_name}"'

        # Build extra query additions if provided (e.g. city or company)
        extra_query = ""
        if extra_info:
            extra_query = f' AND "{extra_info}"'

        # Categories for name dorks
        dorks = {
            "Sociale Media & Profielen": f"(site:linkedin.com/in OR site:facebook.com OR site:instagram.com OR site:twitter.com OR site:x.com OR site:pinterest.com OR site:linktr.ee) {escaped_name}{extra_query}",
            "CV's & Resumes (Documenten)": f"(filetype:pdf OR filetype:doc OR filetype:docx) (resume OR cv OR \"curriculum vitae\" OR portfolio) {escaped_name}{extra_query}",
            "Nieuws & Artikelen": f"(site:nieuws.nl OR site:telegraaf.nl OR site:nu.nl OR site:nos.nl OR site:ad.nl OR site:medium.com OR site:linkedin.com/pulse) {escaped_name}{extra_query}",
            "Bedrijfsconnecties & Directies": f"(site:kvk.nl OR site:opencorporates.com OR site:companyinfo.nl OR site:drimble.nl OR site:find-and-update.company-information.service.gov.uk) {escaped_name}{extra_query}",
            "Lekken & Paste Vermeldingen": f"(site:pastebin.com OR site:paste.org OR site:paste.fo OR site:rentry.co OR site:github.com OR site:gitlab.com) {escaped_name}{extra_query}"
        }

        results = {}
        total_steps = len(dorks)
        current_step = 0

        for category, query in dorks.items():
            if stop_event and stop_event.is_set():
                break

            results[category] = self.phone_osint._duckduckgo_search(query)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)

        return results
