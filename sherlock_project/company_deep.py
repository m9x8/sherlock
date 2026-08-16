"""
Company & Financial Intelligence Engine
Resolves corporate details using public registries like EU VIES and SEC EDGAR.
"""

import asyncio
from curl_cffi.requests import AsyncSession

class CompanyDeepEngine:
    def __init__(self):
        pass

    async def validate_eu_vies_vat(self, session: AsyncSession, vat_number: str) -> dict:
        """Passive verification of European VAT numbers via VIES REST API."""
        vat_number = vat_number.replace(" ", "").upper()
        if len(vat_number) < 3:
            return {"platform": "EU_VIES", "found": False, "error": "Invalid VAT format"}

        country_code = vat_number[:2]
        vat = vat_number[2:]
        url = f"https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country_code}/vat/{vat}"

        try:
            response = await session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("isValid"):
                    return {
                        "platform": "EU_VIES",
                        "found": True,
                        "name": data.get("name"),
                        "address": data.get("address")
                    }
            return {"platform": "EU_VIES", "found": False}
        except Exception as e:
            return {"platform": "EU_VIES", "error": str(e)}

    async def search_opencorporates(self, session: AsyncSession, company_name: str) -> dict:
        url = f"https://opencorporates.com/companies?q={company_name}"
        try:
            response = await session.get(url, timeout=10)
            # A more robust check for a real app, looking for actual result list items:
            if response.status_code == 200 and 'class="companies search-results"' in response.text:
                 return {"platform": "OpenCorporates", "found": True, "info": f"Results available at {url}"}
            return {"platform": "OpenCorporates", "found": False}
        except Exception as e:
             return {"platform": "OpenCorporates", "error": str(e)}

    async def search_sec_edgar(self, session: AsyncSession, company_name: str) -> dict:
        # SEC EDGAR requires a specific user agent format according to fair access policy.
        headers = {'User-Agent': 'SherlockProject (contact@noshitsherlock.io)'}
        url = f"https://www.sec.gov/cgi-bin/browse-edgar?company={company_name}&owner=exclude&action=getcompany"
        try:
            response = await session.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and "No matching Ticker Symbol." not in response.text and "No matching companies." not in response.text:
                return {"platform": "SEC EDGAR", "found": True, "info": f"Filings found at {url}"}
            return {"platform": "SEC EDGAR", "found": False}
        except Exception as e:
            return {"platform": "SEC EDGAR", "error": str(e)}

    async def run_all(self, company_name: str = None, vat_number: str = None) -> list:
        async with AsyncSession(impersonate="chrome") as session:
            tasks = []
            if vat_number:
                tasks.append(self.validate_eu_vies_vat(session, vat_number))
            if company_name:
                tasks.append(self.search_opencorporates(session, company_name))
                tasks.append(self.search_sec_edgar(session, company_name))

            if tasks:
                results = await asyncio.gather(*tasks)
                return list(results)
            return []
