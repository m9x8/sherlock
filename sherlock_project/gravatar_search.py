import hashlib
from typing import Optional, Dict, Any
from sherlock_project.stealth_engine import StealthEngine

class GravatarSearch:
    def __init__(self, stealth_engine: StealthEngine):
        self.stealth_engine = stealth_engine

    async def search_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Searches Gravatar profiles by email address.
        Gravatar uses MD5 hash of the lowercase email.
        """
        clean_email = email.strip().lower()
        email_hash = hashlib.md5(clean_email.encode('utf-8')).hexdigest()

        return await self.search_by_hash(email_hash)

    async def search_by_hash(self, email_hash: str) -> Optional[Dict[str, Any]]:
        """
        Searches Gravatar by MD5 hash.
        """
        url = f"https://en.gravatar.com/{email_hash}.json"

        try:
            # We specifically set headers to mimic a normal browser request
            response = await self.stealth_engine.request('GET', url)
            if response.status_code == 200:
                data = response.json()
                if "entry" in data and len(data["entry"]) > 0:
                    return data["entry"][0]
        except Exception:
            pass

        return None
