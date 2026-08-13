"""
GEOINT Engine
IP Geolocation and GPS conversion via public endpoints.
"""

import asyncio
from curl_cffi.requests import AsyncSession
from geopy.geocoders import Nominatim

class GeointEngine:
    def __init__(self):
        # geopy needs a custom user_agent to comply with Nominatim ToS
        self.geolocator = Nominatim(user_agent="sherlock_geoint_engine_v1")

    async def get_ip_geolocation(self, session: AsyncSession, ip_address: str) -> dict:
        url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as"
        try:
            response = await session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {"type": "IP", "found": True, "data": data}
            return {"type": "IP", "found": False}
        except Exception as e:
            return {"type": "IP", "error": str(e)}

    def reverse_geocode(self, lat: float, lon: float) -> dict:
        """Synchronous reverse geocoding via geopy, needs to be wrapped for async usage if used in heavy loops."""
        try:
            location = self.geolocator.reverse(f"{lat}, {lon}", timeout=10)
            if location:
                return {"type": "GPS", "found": True, "address": location.address, "raw": location.raw}
            return {"type": "GPS", "found": False}
        except Exception as e:
             return {"type": "GPS", "error": str(e)}

    async def run_all(self, ip_address: str = None, lat: float = None, lon: float = None) -> list:
        results = []
        if ip_address:
            async with AsyncSession(impersonate="chrome") as session:
                ip_res = await self.get_ip_geolocation(session, ip_address)
                results.append(ip_res)

        if lat is not None and lon is not None:
             # Run synchronous geopy call in a non-blocking way using asyncio.to_thread
             gps_res = await asyncio.to_thread(self.reverse_geocode, lat, lon)
             results.append(gps_res)

        return results
