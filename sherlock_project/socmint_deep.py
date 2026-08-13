"""
SOCMINT Deep Engine
Resolves social and identity platforms using unauthenticated public endpoints.
"""

import asyncio
import hashlib
from curl_cffi.requests import AsyncSession

class SocmintDeepEngine:
    def __init__(self):
        pass

    async def get_github_events(self, session: AsyncSession, username: str) -> dict:
        url = f"https://api.github.com/users/{username}/events/public"
        try:
            response = await session.get(url, timeout=10)
            if response.status_code == 200:
                events = response.json()
                return {"platform": "GitHub", "found": True, "events_count": len(events), "username": username}
            return {"platform": "GitHub", "found": False}
        except Exception as e:
            return {"platform": "GitHub", "error": str(e)}

    async def get_keybase_identity(self, session: AsyncSession, username: str) -> dict:
        url = f"https://keybase.io/_/api/1.0/user/lookup.json?usernames={username}"
        try:
            response = await session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("them") and len(data["them"]) > 0 and data["them"][0]:
                    return {"platform": "Keybase", "found": True, "proofs": len(data["them"][0].get("proofs_summary", {}).get("all", [])), "username": username}
            return {"platform": "Keybase", "found": False}
        except Exception as e:
            return {"platform": "Keybase", "error": str(e)}

    async def get_steam_profile(self, session: AsyncSession, username: str) -> dict:
        # Steam community custom URL
        url = f"https://steamcommunity.com/id/{username}/?xml=1"
        try:
            response = await session.get(url, timeout=10)
            if response.status_code == 200 and b"<steamID64>" in response.content:
                # Basic parsing since we avoid heavy XML libs if not needed, but defusedxml is available
                content = response.text
                if "<steamID64>" in content:
                    start = content.find("<steamID64>") + len("<steamID64>")
                    end = content.find("</steamID64>")
                    steam_id = content[start:end]
                    return {"platform": "Steam", "found": True, "steamID64": steam_id, "username": username}
            return {"platform": "Steam", "found": False}
        except Exception as e:
            return {"platform": "Steam", "error": str(e)}

    async def get_gravatar(self, session: AsyncSession, email: str) -> dict:
        email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
        url = f"https://en.gravatar.com/{email_hash}.json"
        try:
            response = await session.get(url, timeout=10, impersonate="chrome")
            if response.status_code == 200:
                data = response.json()
                if data.get("entry"):
                    entry = data["entry"][0]
                    return {"platform": "Gravatar", "found": True, "display_name": entry.get("displayName"), "profile_url": entry.get("profileUrl")}
            return {"platform": "Gravatar", "found": False}
        except Exception as e:
            return {"platform": "Gravatar", "error": str(e)}

    async def run_all(self, username: str, email: str = None) -> list:
        async with AsyncSession(impersonate="chrome") as session:
            tasks = [
                self.get_github_events(session, username),
                self.get_keybase_identity(session, username),
                self.get_steam_profile(session, username)
            ]
            if email:
                tasks.append(self.get_gravatar(session, email))
            results = await asyncio.gather(*tasks)
            return list(results)
