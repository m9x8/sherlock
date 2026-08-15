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

    def _advanced_search(self, query: str) -> List[Dict[str, str]]:
        """
        Performs a search using StealthBrowser abstraction (Camoufox -> Nodriver -> curl_cffi)
        to bypass CAPTCHAs and bot-detection, fulfilling the high-end professional search engine requirement.
        """
        import urllib.parse
        from bs4 import BeautifulSoup
        from sherlock_project.stealth_browser import StealthBrowser
        import asyncio

        results = []
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

            async def _fetch():
                async with StealthBrowser(timeout=self.timeout) as browser:
                    return await browser.get_html(url)

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(1) as pool:
                    def run_in_thread():
                        return asyncio.run(_fetch())
                    status, html = pool.submit(run_in_thread).result()
            else:
                status, html = asyncio.run(_fetch())

            if status == 200 and html:
                soup = BeautifulSoup(html, "html.parser")
                elements = soup.select(".result__body")
                for el in elements:
                    try:
                        title_el = el.select_one(".result__title a")
                        if not title_el:
                            continue
                        title = title_el.get_text(strip=True)
                        href = title_el.get("href")

                        if href and 'uddg=' in href:
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if 'uddg' in parsed:
                                href = urllib.parse.unquote(parsed['uddg'][0])

                        snippet_el = el.select_one(".result__snippet")
                        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                        results.append({"title": title, "url": href, "snippet": snippet})
                    except Exception:
                        pass
        except Exception as e:
            import logging
            logging.error(f"Error in _advanced_search: {e}")
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

        general_results = self._advanced_search(query_general)
        if progress_callback:
            progress_callback(1, 2)

        if stop_event and stop_event.is_set():
            return {"General Web Mentions": general_results, "Social Media Matches": []}

        social_results = self._advanced_search(query_social)
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
            "Gelekte Databases (Deep)": f"(site:breached.vc OR site:raidforums.com OR site:nulled.to) ({terms_or})",
            "Documenten & Resumes": f"(filetype:pdf OR filetype:doc OR filetype:docx OR filetype:xls OR filetype:xlsx OR filetype:rtf OR filetype:txt OR filetype:csv OR filetype:tsv) ({terms_or})",
            "Professionele Netwerken": f"(site:linkedin.com/in OR site:linkedin.com/pub OR site:xing.com OR site:rocketreach.co OR site:apollo.io OR site:zoominfo.com OR site:lusha.com OR site:signalhire.com OR site:contactout.com) ({terms_or})",
            "Chat- & Messenger-groepen": f"(site:t.me OR site:chat.whatsapp.com OR site:discord.gg OR site:signal.group OR site:line.me OR site:viber.com) ({terms_or})",
            "Adresboeken & Spam-registries": f"(site:tellows.nl OR site:tellows.com OR site:sync.me OR site:truecaller.com OR site:whocalledme.com OR site:wieheeftgebeld.nl OR site:telefoonboek.nl OR site:openingstijden.nl OR site:zoeknummer.nl OR site:wieheeftmijgebeld.nl OR site:spamcalls.net) ({terms_or})",
            "Marktplaatsen & Advertenties": f"(site:marktplaats.nl OR site:tweakers.net OR site:2dehands.be OR site:craigslist.org OR site:ebay.com) ({terms_or})",
            "Forums & Blogs": f"(site:forum.fok.nl OR site:gathering.tweakers.net OR site:kassa.bnnvara.nl OR site:radar.avrotros.nl) ({terms_or})",
            "Overheid & Openbare Documenten": f"(site:overheid.nl OR site:rijksoverheid.nl OR site:officielebekendmakingen.nl OR site:rechtspraak.nl) ({terms_or})",
            "Archieven & Cached": f"site:archive.org ({terms_or})",
            "KVK & Bedrijvengidsen (Int)": f"(site:opencorporates.com OR site:kompass.com) ({terms_or})"
        }

        results = {}
        total_steps = len(dorks) + 1  # include real-time scraper step
        current_step = 0

        for category, query in dorks.items():
            if stop_event and stop_event.is_set():
                break
            results[category] = self._advanced_search(query)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)

        # Run high-end direct scraper for Adresboeken & Spam-registries
        if not (stop_event and stop_event.is_set()):
            from sherlock_project.scraper import HighEndScraper
            try:
                import asyncio

                async def _scrape_and_close():
                    async with HighEndScraper(timeout=self.timeout) as scraper:
                        return await scraper.scrape_phone_nl_registries(clean_national or e164)

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(1) as pool:
                        def run_in_thread():
                            return asyncio.run(_scrape_and_close())
                        scraped_hits = pool.submit(run_in_thread).result()
                else:
                    scraped_hits = asyncio.run(_scrape_and_close())

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
            results[category] = self._advanced_search(query)
            current_step += 1
            if progress_callback:
                progress_callback(current_step, total_steps)
        return results
