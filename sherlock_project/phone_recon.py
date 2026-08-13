"""
Phone Intelligence Engine
Resolves E.164 details and passive social media checking.
"""

import asyncio
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from curl_cffi.requests import AsyncSession

class PhoneReconEngine:
    def __init__(self):
        pass

    def parse_number_local(self, phone_number: str) -> dict:
        try:
            parsed = phonenumbers.parse(phone_number, None)
            if phonenumbers.is_valid_number(parsed):
                return {
                    "valid": True,
                    "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
                    "country": geocoder.description_for_number(parsed, "en"),
                    "carrier": carrier.name_for_number(parsed, "en"),
                    "timezones": list(timezone.time_zones_for_number(parsed))
                }
            return {"valid": False, "error": "Invalid number"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def check_whatsapp_public(self, session: AsyncSession, e164_number: str) -> dict:
        clean_num = e164_number.replace("+", "")
        url = f"https://wa.me/{clean_num}"
        try:
            response = await session.get(url, timeout=10, allow_redirects=True)
            if response.status_code == 200 and 'action="https://api.whatsapp.com/send"' in response.text:
                 return {"platform": "WhatsApp", "found": True, "url": url}
            return {"platform": "WhatsApp", "found": False}
        except Exception as e:
            return {"platform": "WhatsApp", "error": str(e)}

    async def check_telegram_public(self, session: AsyncSession, e164_number: str) -> dict:
        # Telegram usernames don't directly map to phone numbers via unauthenticated endpoints,
        # but a common OSINT check is to test if a number is used as a username or contact link
        # Note: tg://resolve?domain=+12345 won't work in HTTP.
        # Often folks check t.me/+123456789 but this requires auth to actually see the contact info
        # We'll just do a passive check on the t.me/ url just in case it resolves to a public profile/group.
        url = f"https://t.me/{e164_number}"
        try:
            response = await session.get(url, timeout=10)
            if response.status_code == 200 and 'tgme_page_title' in response.text:
                return {"platform": "Telegram", "found": True, "url": url}
            return {"platform": "Telegram", "found": False}
        except Exception as e:
            return {"platform": "Telegram", "error": str(e)}

    async def run_all(self, phone_number: str) -> dict:
        result = {"local_parsing": self.parse_number_local(phone_number), "social": []}

        if result["local_parsing"].get("valid"):
            e164 = result["local_parsing"]["e164"]
            async with AsyncSession(impersonate="chrome") as session:
                social_results = await asyncio.gather(
                    self.check_whatsapp_public(session, e164),
                    self.check_telegram_public(session, e164)
                )
                result["social"] = list(social_results)

        return result
