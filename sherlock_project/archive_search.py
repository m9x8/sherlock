import urllib.parse
from typing import List, Dict, Any
from sherlock_project.stealth_engine import StealthEngine

class ArchiveSearch:
    def __init__(self, stealth_engine: StealthEngine):
        self.stealth_engine = stealth_engine

    async def get_snapshots(self, url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Queries the Internet Archive CDX API for historical snapshots of a URL.
        """
        encoded_url = urllib.parse.quote_plus(url)
        # Using output=json for structured data
        cdx_url = f"https://web.archive.org/cdx/search/cdx?url={encoded_url}&output=json&limit={limit}&fl=timestamp,original,statuscode,mimetype,digest"

        snapshots = []
        try:
            response = await self.stealth_engine.request('GET', cdx_url)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1:
                    # First row is headers: ["timestamp", "original", "statuscode", "mimetype", "digest"]
                    headers = data[0]
                    for row in data[1:]:
                        snapshot = dict(zip(headers, row))
                        # Construct the playback URL
                        ts = snapshot.get("timestamp", "")
                        orig = snapshot.get("original", "")
                        if ts and orig:
                            snapshot["playback_url"] = f"https://web.archive.org/web/{ts}/{orig}"
                        snapshots.append(snapshot)
        except Exception:
            pass

        return snapshots
