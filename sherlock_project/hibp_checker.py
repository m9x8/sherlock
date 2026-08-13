"""
Privacy-Preserving Leak Checker
Uses HIBP k-Anonymity API to check passwords/emails.
"""

import asyncio
import hashlib
from curl_cffi.requests import AsyncSession

class HIBPChecker:
    def __init__(self):
        pass

    def _hash_and_split(self, data: str) -> tuple:
        """Returns the first 5 chars of SHA-1 hash and the remainder."""
        sha1 = hashlib.sha1(data.encode('utf-8')).hexdigest().upper()
        return sha1[:5], sha1[5:]

    async def check_pwned_password(self, session: AsyncSession, password: str) -> dict:
        prefix, suffix = self._hash_and_split(password)
        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            # Requires valid user agent or might be blocked, impersonate Chrome
            response = await session.get(url, timeout=10)
            if response.status_code == 200:
                # The response is a list of suffixes and counts: SUFFIX:COUNT
                lines = response.text.splitlines()
                for line in lines:
                    if line.startswith(suffix):
                        count = int(line.split(':')[1])
                        return {"platform": "HIBP", "type": "Password", "found": True, "count": count}
                return {"platform": "HIBP", "type": "Password", "found": False}
            return {"platform": "HIBP", "type": "Password", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"platform": "HIBP", "type": "Password", "error": str(e)}

    # Checking email leaks on HIBP requires an API key, so we cannot do that
    # strictly under "zero-API" constraints. Only password hashes are supported via k-anonymity.
    # However, there are some other endpoints or services. We'll stick to the password one here
    # as it perfectly fits the k-anonymity description.

    async def run_all(self, password: str) -> list:
        async with AsyncSession(impersonate="chrome") as session:
            res = await self.check_pwned_password(session, password)
            return [res]
