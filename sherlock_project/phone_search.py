"""
Sherlock Phone Search Module
Provides phone number validation, formatting, metadata lookup,
and OSINT web dorking across search engines, databases, and social platforms.
"""

import urllib.parse
import re
import requests
import html
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from typing import Dict, List, Any

# Suppress the duckduckgo_search renaming RuntimeWarning before importing DDGS
import warnings
import sys
try:
    import duckduckgo_search
    # Intercept and disable the specific RuntimeWarning regarding renaming
    _orig_warn = warnings.warn
    def _patched_warn(message, category=None, stacklevel=1, *args, **kwargs):
        if category == RuntimeWarning and "duckduckgo_search" in str(message):
            return
        return _orig_warn(message, category, stacklevel, *args, **kwargs)
    warnings.warn = _patched_warn
    # Also patch inside the duckduckgo_search module's namespace if already bound
    if hasattr(duckduckgo_search, "duckduckgo_search"):
        duckduckgo_search.duckduckgo_search.warnings.warn = _patched_warn
except Exception:
    pass

from duckduckgo_search import DDGS
from sherlock_project.headers import get_high_end_headers

class PhoneOSINT:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(get_high_end_headers())

    def validate_and_meta(self, phone_str: str, default_region: str = "NL") -> Dict[str, Any]:
        """
        Validates the phone number and extracts carrier, region, and timezone information.
        """
        try:
            # Clean string from common chars
            cleaned = re.sub(r"[^\d+]", "", phone_str)
            # If it doesn't start with +, and default_region is provided
            parsed = phonenumbers.parse(phone_str, default_region)

            is_valid = phonenumbers.is_valid_number(parsed)
            number_type = phonenumbers.number_type(parsed)

            # Map type code to readable name
            type_map = {
                0: "Fixed Line",
                1: "Mobile",
                2: "Fixed Line or Mobile",
                3: "Toll Free",
                4: "Premium Rate",
                5: "Shared Cost",
                6: "VoIP",
                7: "Personal Number",
                8: "Pager",
                9: "Universal Access Number",
                10: "Voice Mail",
                -1: "Unknown"
            }
            readable_type = type_map.get(number_type, "Unknown")

            # Formats
            e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            international = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            rfc3966 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.RFC3966)

            # Metadata
            carrier_name = carrier.name_for_number(parsed, "en")
            location = geocoder.description_for_number(parsed, "en")
            timezones_list = list(timezone.time_zones_for_number(parsed))

            return {
                "valid": is_valid,
                "clean": cleaned,
                "e164": e164,
                "international": international,
                "national": national,
                "rfc3966": rfc3966,
                "type": readable_type,
                "carrier": carrier_name or "Unknown Carrier",
                "location": location or "Unknown Location",
                "timezones": timezones_list,
                "country_code": parsed.country_code,
                "national_number": parsed.national_number,
                "error": None
            }
        except Exception as e:
            return {
                "valid": False,
                "clean": phone_str,
                "e164": phone_str,
                "international": phone_str,
                "national": phone_str,
                "rfc3966": phone_str,
                "type": "Unknown",
                "carrier": "Unknown Carrier",
                "location": "Unknown Location",
                "timezones": [],
                "country_code": 0,
                "national_number": 0,
                "error": str(e)
            }

    def _duckduckgo_search(self, query: str) -> List[Dict[str, str]]:
        """
        Performs a search using the professional and robust duckduckgo-search package
        to bypass anomalies, CAPTCHAs, and bot-detection blocks on standard html endpoints.
        If it fails, automatically falls back to raw HTML/Lite scraping via high-end headers.
        """
        results = []
        # Attempt standard library search first
        try:
            with DDGS(timeout=self.timeout) as ddgs:
                ddg_results = ddgs.text(query, max_results=30)
                for r in ddg_results:
                    results.append({
                        "title": r.get("title", "No Title"),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "No Snippet")
                    })
        except Exception as e:
            print(f"DuckDuckGo API search error: {e}. Switching to high-end direct HTML scraping...")

        # Premium high-end fallback: scrape DuckDuckGo Lite directly
        if not results:
            try:
                from bs4 import BeautifulSoup
                from sherlock_project.headers import get_high_end_headers
                url = "https://lite.duckduckgo.com/lite/"
                headers = get_high_end_headers(referer="https://duckduckgo.com/")
                # Use a requests session to persist cookies and bypass bot detection
                session = requests.Session()
                # Get the initial page first
                session.get("https://duckduckgo.com/", headers=headers, timeout=self.timeout)
                # Query the lite search endpoint
                data = {"q": query}
                response = session.post(url, headers=headers, data=data, timeout=self.timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Result rows in duckduckgo lite are table rows (tr)
                    rows = soup.find_all("td", class_="result-snippet")
                    for row in rows:
                        # The link and title are usually in the previous sibling or nearby td elements
                        tr = row.find_parent("tr")
                        if tr:
                            prev_tr = tr.find_previous_sibling("tr")
                            if prev_tr:
                                link_tag = prev_tr.find("a", class_="result-link")
                                if link_tag:
                                    title = link_tag.get_text(strip=True)
                                    href = link_tag.get("href")
                                    # Resolve relative link if any
                                    if href and href.startswith("//"):
                                        href = "https:" + href
                                    elif href and href.startswith("/"):
                                        href = "https://duckduckgo.com" + href

                                    snippet = row.get_text(strip=True)
                                    results.append({
                                        "title": title or "No Title",
                                        "url": href or "",
                                        "snippet": snippet or "No Snippet"
                                    })
            except Exception as fe:
                print(f"Direct HTML fallback search failed: {fe}")

        return results

    def search_phone_mentions(self, meta: Dict[str, Any], stop_event=None, progress_callback=None) -> Dict[str, List[Dict[str, str]]]:
        """
        Runs multiple searches for the phone number variations to find mentions online.
        """
        if not meta.get("valid"):
            return {"General Web Mentions": [], "Social Media Matches": []}

        e164 = meta["e164"]                      # E.g. +31612345678
        national = meta["national"]              # E.g. 06 12345678 or (06) 12345678
        international = meta["international"]    # E.g. +31 6 12345678
        clean_national = re.sub(r"[^\d]", "", national) # E.g. 0612345678 or 612345678

        # Generate search queries for different formats
        query_general = f'"{e164}" OR "{international}" OR "{national}"'
        if clean_national:
            query_general += f' OR "{clean_national}"'

        # Social media targeted search
        social_sites = "site:facebook.com OR site:instagram.com OR site:linkedin.com OR site:twitter.com OR site:x.com OR site:pinterest.com OR site:tiktok.com"
        query_social = f'({social_sites}) ("{e164}" OR "{international}" OR "{national}"'
        if clean_national:
            query_social += f' OR "{clean_national}"'
        query_social += ')'

        if stop_event and stop_event.is_set():
            return {"General Web Mentions": [], "Social Media Matches": []}

        general_results = self._duckduckgo_search(query_general)
        if progress_callback:
            progress_callback(1, 2)

        if stop_event and stop_event.is_set():
            return {"General Web Mentions": general_results, "Social Media Matches": []}

        social_results = self._duckduckgo_search(query_social)
        if progress_callback:
            progress_callback(2, 2)

        # Deduplicate results between lists
        seen_urls = set()
        unique_general = []
        for r in general_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_general.append(r)

        unique_social = []
        for r in social_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique_social.append(r)

        return {
            "General Web Mentions": unique_general,
            "Social Media Matches": unique_social
        }

    def search_phone_advanced_dorks(self, meta: Dict[str, Any], stop_event=None, progress_callback=None) -> Dict[str, List[Dict[str, str]]]:
        """
        Runs advanced dorking queries across the 5 specific categories for phone numbers,
        now upgraded with high-end matching methodologies (Telegram API dorking, TrueCaller, tellows, leak directory lookups).
        """
        if not meta.get("valid"):
            return {
                "Lek- & Paste-sites": [],
                "Documenten & Resumes": [],
                "Professionele Netwerken": [],
                "Chat- & Messenger-groepen": [],
                "Adresboeken & Spam-registries": []
            }

        e164 = meta["e164"]
        national = meta["national"]
        international = meta["international"]
        clean_national = re.sub(r"[^\d]", "", national)

        terms = [f'"{e164}"', f'"{international}"', f'"{national}"']
        if clean_national:
            terms.append(f'"{clean_national}"')
        terms_or = " OR ".join(terms)

        dorks = {
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co OR site:controlc.com OR site:pastelink.net OR site:rentry.co) ({terms_or})",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv OR filetype:tsv) ({terms_or})",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com OR site:lusha.com OR site:signalhire.com OR site:contactout.com) ({terms_or})",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me OR site:viber.com) ({terms_or})",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl OR site:zoeknummer.nl OR site:wieheeftmijgebeld.nl OR site:spamcalls.net) ({terms_or})",
            "Marktplaatsen & Advertenties": f"(site:marktplaats.nl OR site:tweakers.net OR site:2dehands.be OR site:craigslist.org OR site:ebay.com) ({terms_or})",
            "Forums & Blogs": f"(site:forum.fok.nl OR site:gathering.tweakers.net OR site:kassa.bnnvara.nl OR site:radar.avrotros.nl) ({terms_or})",
            "Overheid & Openbare Documenten": f"(site:overheid.nl OR site:rijksoverheid.nl OR site:officielebekendmakingen.nl OR site:rechtspraak.nl) ({terms_or})"
        }

        results = {}
        total_steps = len(dorks) + 1  # include real-time scraper step
        current_step = 0

        for category, query in dorks.items():
            if stop_event and stop_event.is_set():
                break
            results[category] = self._duckduckgo_search(query)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)

        # Run high-end direct scraper for Adresboeken & Spam-registries
        if not (stop_event and stop_event.is_set()):
            from sherlock_project.scraper import HighEndScraper
            try:
                scraper = HighEndScraper(timeout=self.timeout)
                scraped_hits = scraper.scrape_phone_nl_registries(clean_national or e164)
                if scraped_hits:
                    if "Adresboeken & Spam-registries" not in results:
                        results["Adresboeken & Spam-registries"] = []
                    # Append direct scraped live results to the start of the list
                    results["Adresboeken & Spam-registries"] = scraped_hits + results["Adresboeken & Spam-registries"]
            except Exception:
                pass
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)

        return results

    def search_username_advanced_dorks(self, username: str, stop_event=None, progress_callback=None) -> Dict[str, List[Dict[str, str]]]:
        """
        Runs advanced dorking queries across the 5 specific categories for usernames.
        """
        if not username:
            return {
                "Lek- & Paste-sites": [],
                "Documenten & Resumes": [],
                "Professionele Netwerken": [],
                "Chat- & Messenger-groepen": [],
                "Adresboeken & Spam-registries": []
            }

        escaped_username = f'"{username}"'

        dorks = {
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co OR site:controlc.com OR site:pastelink.net OR site:rentry.co) {escaped_username}",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv OR filetype:tsv) {escaped_username}",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com OR site:lusha.com OR site:signalhire.com OR site:contactout.com) {escaped_username}",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me OR site:viber.com) {escaped_username}",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl OR site:zoeknummer.nl OR site:wieheeftmijgebeld.nl OR site:spamcalls.net) {escaped_username}",
            "Tech & Developer Platformen": f"(site:stackoverflow.com OR site:hackernews.com OR site:dev.to OR site:hashnode.com OR site:medium.com OR site:gitlab.com OR site:bitbucket.org OR site:sourceforge.net) {escaped_username}",
            "Gaming & Entertainment": f"(site:steamcommunity.com OR site:twitch.tv OR site:xbox.com OR site:playstation.com OR site:ign.com OR site:roblox.com) {escaped_username}",
            "Forums & Communities": f"(site:reddit.com/user OR site:quora.com/profile OR site:forum.fok.nl OR site:gathering.tweakers.net OR site:4chan.org) {escaped_username}",
            "Dating & Lifestyle": f"(site:tinder.com OR site:badoo.com OR site:okcupid.com OR site:pof.com OR site:last.fm OR site:myanimelist.net) {escaped_username}",
            "Crypto & Darkweb Links": f"(site:bitcointalk.org OR site:etherscan.io/address OR site:opensea.io) {escaped_username}"
        }

        results = {}
        total_steps = len(dorks)
        current_step = 0

        for category, query in dorks.items():
            if stop_event and stop_event.is_set():
                break
            results[category] = self._duckduckgo_search(query)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)
        return results
