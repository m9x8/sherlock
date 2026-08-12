"""
Sherlock Phone Search Module
Provides phone number validation, formatting, metadata lookup,
and OSINT web dorking across search engines and social platforms.
"""

import urllib.parse
import re
import requests
import html
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from typing import Dict, List, Any

# A list of standard User-Agents to mimic real browsers and avoid blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

class PhoneOSINT:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENTS[0],
            "Accept-Language": "en-US,en;q=0.9,nl;q=0.8"
        })

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
        Performs a search on DuckDuckGo's HTML/Lite version to fetch results without JavaScript.
        """
        results = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                # DDG HTML structures results inside class="result results_links results_links_deep web-result "
                # Let's extract them properly.
                blocks = re.split(r'<div class="result results_links', resp.text)
                for block in blocks[1:]:
                    # Extract URL
                    href_match = re.search(r'href="([^"]+)"[^>]*class="result__url"', block)
                    if not href_match:
                        href_match = re.search(r'<a class="result__snippet"[^>]*href="([^"]+)"', block) or re.search(r'class="result__snippet"[^>]*href="([^"]+)"', block)

                    # Extract Title and Snippet
                    title_match = re.search(r'<a class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL) or re.search(r'<h2 class="result__title"[^>]*>(.*?)</h2>', block, re.DOTALL)
                    snippet_match = re.search(r'<a class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL) or re.search(r'<div class="result__snippet"[^>]*>(.*?)</div>', block, re.DOTALL)

                    if href_match:
                        raw_href = href_match.group(1)
                        if "uddg=" in raw_href:
                            parsed_url = urllib.parse.urlparse(raw_href)
                            query_params = urllib.parse.parse_qs(parsed_url.query)
                            url_str = query_params.get("uddg", [raw_href])[0]
                        else:
                            url_str = raw_href

                        if url_str.startswith("//"):
                            url_str = "https:" + url_str
                        elif url_str.startswith("/"):
                            continue

                        title = "No Title"
                        if title_match:
                            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()

                        snippet = "No Snippet"
                        if snippet_match:
                            snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()

                        title = html.unescape(title)
                        snippet = html.unescape(snippet)
                        url_str = html.unescape(url_str)

                        results.append({
                            "title": title,
                            "url": url_str,
                            "snippet": snippet
                        })
        except Exception as e:
            print(f"Error searching DuckDuckGo: {e}")
        return results

    def search_phone_mentions(self, meta: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
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

        general_results = self._duckduckgo_search(query_general)
        social_results = self._duckduckgo_search(query_social)

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

    def search_phone_advanced_dorks(self, meta: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """
        Runs advanced dorking queries across the 5 specific categories for phone numbers.
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
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co) ({terms_or})",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt) ({terms_or})",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com) ({terms_or})",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me) ({terms_or})",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl) ({terms_or})"
        }

        results = {}
        for category, query in dorks.items():
            results[category] = self._duckduckgo_search(query)
        return results

    def search_username_advanced_dorks(self, username: str) -> Dict[str, List[Dict[str, str]]]:
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
            "Lek- & Paste-sites": f"(site:pastebin.com OR site:paste.org OR site:github.com OR site:gitlab.com OR site:gitter.im OR site:paste2.org OR site:ghostbin.co) {escaped_username}",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt) {escaped_username}",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com) {escaped_username}",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me) {escaped_username}",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl) {escaped_username}"
        }

        results = {}
        for category, query in dorks.items():
            results[category] = self._duckduckgo_search(query)
        return results
