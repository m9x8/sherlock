import re
from typing import Dict, List, Set

class TrackerCorrelator:
    def __init__(self):
        # Regex patterns for various trackers
        self.patterns = {
            "google_analytics": re.compile(r"UA-\d{4,10}-\d{1,4}|G-[A-Z0-9]{10}"),
            "adsense": re.compile(r"pub-\d{16}|ca-pub-\d{16}"),
            "gtm": re.compile(r"GTM-[A-Z0-9]{4,7}"),
            "yandex": re.compile(r"yaCounter\d{8}"),
        }

    def extract_trackers(self, html_content: str) -> Dict[str, List[str]]:
        """
        Extracts tracker IDs from HTML source code.
        Returns a dictionary mapping tracker type to a list of unique found IDs.
        """
        found_trackers: Dict[str, Set[str]] = {key: set() for key in self.patterns.keys()}

        if not html_content:
            return {k: list(v) for k, v in found_trackers.items()}

        for tracker_type, pattern in self.patterns.items():
            matches = pattern.findall(html_content)
            if matches:
                found_trackers[tracker_type].update(matches)

        return {k: list(v) for k, v in found_trackers.items() if v}

    def correlate(self, sites_data: Dict[str, str]) -> Dict[str, Dict[str, List[str]]]:
        """
        sites_data: Dict mapping a site identifier (e.g., URL or domain) to its HTML content.
        Returns a mapping of tracker ID to a list of site identifiers where it was found,
        grouped by tracker type.
        """
        correlation: Dict[str, Dict[str, List[str]]] = {key: {} for key in self.patterns.keys()}

        for site_id, html_content in sites_data.items():
            extracted = self.extract_trackers(html_content)
            for tracker_type, tracker_ids in extracted.items():
                for tracker_id in tracker_ids:
                    if tracker_id not in correlation[tracker_type]:
                        correlation[tracker_type][tracker_id] = []
                    correlation[tracker_type][tracker_id].append(site_id)

        # Remove empty tracker types
        return {k: v for k, v in correlation.items() if v}
