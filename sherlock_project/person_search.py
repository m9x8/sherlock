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
        Runs high-end name OSINT queries across several categories using DuckDuckGo
        to locate exact matches on social profiles, resumes, news, directories, and leak platforms.
        """
        if not first_name or not last_name:
            return {}

        full_name = f"{first_name} {last_name}"
        escaped_name = f'"{full_name}"'

        # Build extra query additions if provided (e.g. city or company)
        extra_query = ""
        if extra_info:
            extra_query = f' AND "{extra_info}"'

        # Expanded and precise categories for name dorks
        dorks = {
            "Sociale Media & Profielen": f"(site:linkedin.com/in OR site:facebook.com OR site:instagram.com OR site:twitter.com OR site:x.com OR site:pinterest.com OR site:linktr.ee OR site:tiktok.com OR site:youtube.com OR site:github.com OR site:gravatar.com OR site:xing.com OR site:reddit.com/user OR site:flickr.com OR site:vimeo.com OR site:soundcloud.com OR site:behance.net) {escaped_name}{extra_query}",
            "CV's & Resumes (Documenten)": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv) (resume OR cv OR \"curriculum vitae\" OR portfolio OR bio OR biography OR \"personal profile\") {escaped_name}{extra_query}",
            "Nieuws, Artikelen & Pers": f"(site:nieuws.nl OR site:telegraaf.nl OR site:nu.nl OR site:nos.nl OR site:ad.nl OR site:medium.com OR site:linkedin.com/pulse OR site:reuters.com OR site:bloomberg.com OR site:nytimes.com OR site:theguardian.com OR site:ft.com OR site:volkskrant.nl OR site:nrc.nl) {escaped_name}{extra_query}",
            "Bedrijfsconnecties & Directies": f"(site:kvk.nl OR site:opencorporates.com OR site:companyinfo.nl OR site:drimble.nl OR site:find-and-update.company-information.service.gov.uk OR site:croco.nl OR site:staatsbladmonitor.be OR site:unternehmensregister.de OR site:apollo.io OR site:zoominfo.com OR site:rocketreach.co) {escaped_name}{extra_query}",
            "Lekken, Paste & Code Gidsen": f"(site:pastebin.com OR site:paste.org OR site:paste.fo OR site:rentry.co OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:controlc.com OR site:ghostbin.co OR site:pastelink.net OR site:leak-lookup.com OR site:dehashed.com) {escaped_name}{extra_query}",
            "Academisch & Onderzoek": f"(site:researchgate.net OR site:academia.edu OR site:scholar.google.com OR site:orcid.org OR site:pubmed.ncbi.nlm.nih.gov OR site:ssrn.com) {escaped_name}{extra_query}",
            "Sport & Hobby's": f"(site:strava.com/athletes OR site:runkeeper.com OR site:chess.com/member OR site:lichess.org/@) {escaped_name}{extra_query}",
            "Genealogie & Publieke Registers": f"(site:wiewaswie.nl OR site:stamboomzoeker.nl OR site:genealogieonline.nl OR site:myheritage.nl OR site:familysearch.org) {escaped_name}{extra_query}",
            "Overheid & Juridisch": f"(site:rechtspraak.nl OR site:officielebekendmakingen.nl OR site:faillissementsdossier.nl OR site:insolventies.rechtspraak.nl) {escaped_name}{extra_query}"
        }

        results = {}
        total_steps = len(dorks)
        current_step = 0

        for category, query in dorks.items():
            if stop_event and stop_event.is_set():
                break

            results[category] = self.phone_osint._advanced_search(query)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)

        return results
