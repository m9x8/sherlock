"""
Sherlock High-End Real-Time Scraping Module
Provides direct scraping methods for phone numbers, companies, and people
by requesting web pages directly with high-end randomized headers and extracting verified findings.
"""

import re
from bs4 import BeautifulSoup
from sherlock_project.headers import get_high_end_headers
from damru.bypass import fetch_html_bypass

class HighEndScraper:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def scrape_phone_nl_registries(self, clean_number: str) -> list[dict[str, str]]:
        """
        Directly scrapes popular Dutch telephone spam/registries like wieheeftgebeld.nl and tellows.nl
        to extract real-time reports and comments regarding the target phone number.
        """
        results = []
        if not clean_number:
            return results

        # Clean number to standard Dutch search format if it starts with 31/06/0
        search_num = clean_number
        if search_num.startswith("+31"):
            search_num = "0" + search_num[3:]
        elif search_num.startswith("31") and not search_num.startswith("316"):
            search_num = "0" + search_num[2:]

        # --- 1. WieHeeftGebeld.nl direct scraping ---
        try:
            url = f"https://www.wieheeftgebeld.nl/nummer/{search_num}"
            headers = get_high_end_headers(referer="https://www.wieheeftgebeld.nl/")
            status, text = fetch_html_bypass(
                url=url,
                user_agent=headers.get("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"),
                accept_language=headers.get("Accept-Language", "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7"),
                timeout=self.timeout
            )
            if status == 200 and text:
                soup = BeautifulSoup(text, "html.parser")
                comments_section = soup.find_all("div", class_="comment-text")
                if comments_section:
                    for i, comment in enumerate(comments_section[:5], 1):
                        text = comment.get_text(strip=True)
                        if text:
                            results.append({
                                "title": f"WieHeeftGebeld.nl - Melding #{i}",
                                "url": url,
                                "snippet": text[:200] + "..." if len(text) > 200 else text
                            })
                # Fallback check for user score / evaluation
                score_box = soup.find("div", class_="rating-badge")
                if score_box:
                    score_text = score_box.get_text(strip=True)
                    results.append({
                        "title": "WieHeeftGebeld.nl - Spamscore Badge",
                        "url": url,
                        "snippet": f"Gevonden score/beoordeling voor dit nummer: {score_text}"
                    })
        except Exception as e:
            # Silent fallback
            pass

        # --- 2. Tellows.nl direct scraping ---
        try:
            url = f"https://www.tellows.nl/num/{search_num}"
            headers = get_high_end_headers(referer="https://www.tellows.nl/")
            status, text = fetch_html_bypass(
                url=url,
                user_agent=headers.get("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"),
                accept_language=headers.get("Accept-Language", "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7"),
                timeout=self.timeout
            )
            if status == 200 and text:
                soup = BeautifulSoup(text, "html.parser")
                # Look for tellows score or user comments
                score = soup.find("div", class_="tellows-score")
                score_str = score.get_text(strip=True) if score else "Onbekend"

                comment_divs = soup.find_all("div", class_="comment-content")
                if comment_divs:
                    for i, c_div in enumerate(comment_divs[:5], 1):
                        text = c_div.get_text(strip=True)
                        if text:
                            results.append({
                                "title": f"Tellows.nl - Gebruikerscommentaar #{i} (Score: {score_str})",
                                "url": url,
                                "snippet": text[:200] + "..." if len(text) > 200 else text
                            })
                elif score:
                    results.append({
                        "title": "Tellows.nl Score",
                        "url": url,
                        "snippet": f"Dit nummer heeft een tellows-score van {score_str}."
                    })
        except Exception:
            pass

        return results

    def scrape_company_direct_details(self, company_name: str) -> list[dict[str, str]]:
        """
        Directly queries open business indexes for live company information and returns validated hits.
        """
        results = []
        if not company_name:
            return results

        try:
            import urllib.parse
            # Query OpenKVK search API or standard landing endpoint
            query_url = f"https://openkvk.nl/zoeken/{urllib.parse.quote(company_name)}"
            headers = get_high_end_headers(referer="https://openkvk.nl/")
            status, text = fetch_html_bypass(
                url=query_url,
                user_agent=headers.get("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"),
                accept_language=headers.get("Accept-Language", "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7"),
                timeout=self.timeout
            )
            if status == 200 and text:
                soup = BeautifulSoup(text, "html.parser")
                # Find search result links on openkvk.nl
                links = soup.find_all("a", href=re.compile(r"/openkvk/"))
                for link in links[:5]:
                    title = link.get_text(strip=True)
                    href = link.get("href")
                    if title and href:
                        full_url = f"https://openkvk.nl{href}" if href.startswith("/") else href
                        results.append({
                            "title": f"OpenKVK NL - {title}",
                            "url": full_url,
                            "snippet": f"Live registratie koppeling voor {title} op OpenKVK index."
                        })
        except Exception:
            pass

        return results
