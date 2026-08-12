from typing import List, Dict, Any, Optional
from sherlock_project.stealth_engine import StealthEngine

class ASNMapper:
    def __init__(self, stealth_engine: StealthEngine):
        self.stealth_engine = stealth_engine

    async def get_asn_info(self, asn: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves BGP/ASN information from RDAP.
        asn: Should be the ASN string, e.g., 'AS15169' or '15169'
        """
        clean_asn = asn.upper().replace('AS', '')
        # Using ARIN RDAP as the bootstrap, it will redirect to the correct RIR
        url = f"https://rdap.arin.net/registry/autnum/{clean_asn}"

        try:
            response = await self.stealth_engine.request('GET', url)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    def extract_cidr_blocks(self, rdap_data: Dict[str, Any]) -> List[str]:
        """
        Extracts CIDR blocks from the RDAP JSON response.
        Note: The actual representation varies by RIR. This attempts to pull v4/v6 blocks.
        """
        cidrs = []
        if not rdap_data:
            return cidrs

        # Some RIRs return it in 'remarks', others in 'v4/v6' specific objects.
        # This is a generalized approach.

        # Checking for direct arrays or embedded entities
        if 'v4' in rdap_data:
            cidrs.extend(rdap_data['v4'])
        if 'v6' in rdap_data:
            cidrs.extend(rdap_data['v6'])

        # Often IP ranges are mapped in related links or entities for ASNs,
        # but for specific ASN to CIDR mappings, one might need bgpview or similar APIs
        # as RDAP autnum responses don't always list all advertised prefixes.
        # For a truly zero-API approach for ASN -> CIDR, we might fallback to Hurricane Electric or RIPE stat.

        return cidrs

    async def get_asn_prefixes(self, asn: str) -> List[str]:
        """
        Since RDAP doesn't always provide all advertised prefixes for an ASN,
        we can use RIPE stat API which is open and doesn't require a key.
        """
        clean_asn = asn.upper().replace('AS', '')
        url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{clean_asn}"

        try:
            response = await self.stealth_engine.request('GET', url)
            if response.status_code == 200:
                data = response.json()
                prefixes = data.get('data', {}).get('prefixes', [])
                return [p.get('prefix') for p in prefixes if 'prefix' in p]
        except Exception:
            pass
        return []
