import asyncio
import random
from urllib.parse import urlparse
from curl_cffi import requests
from typing import Optional, Dict, Any, List

BROWSER_PROFILES = [
    {
        "impersonate": "chrome120",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "platform": '"Windows"'
    },
    {
        "impersonate": "chrome124",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "platform": '"Windows"'
    },
    {
        "impersonate": "chrome131",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec_ch_ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "platform": '"Windows"'
    },
    {
        "impersonate": "safari17_0",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "sec_ch_ua": None,
        "platform": None
    },
    {
        "impersonate": "safari18_0",
        "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "sec_ch_ua": None,
        "platform": None
    },
    {
        "impersonate": "firefox133",
        "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "sec_ch_ua": None,
        "platform": None
    }
]

class StealthEngine:
    def __init__(self, concurrency_per_domain: int = 5):
        self.concurrency_per_domain = concurrency_per_domain
        self._semaphores: Dict[str, asyncio.Semaphore] = {}

        # Select a random browser profile for this instance
        self._profile = random.choice(BROWSER_PROFILES)
        self.impersonate = self._profile["impersonate"]
        self._session: Optional[requests.AsyncSession] = None

    def _get_semaphore(self, domain: str) -> asyncio.Semaphore:
        if domain not in self._semaphores:
            self._semaphores[domain] = asyncio.Semaphore(self.concurrency_per_domain)
        return self._semaphores[domain]

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": self._profile["ua"],
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        }

        if self._profile["sec_ch_ua"]:
            headers["Sec-Ch-Ua"] = self._profile["sec_ch_ua"]
            headers["Sec-Ch-Ua-Mobile"] = "?0"
            headers["Sec-Ch-Ua-Platform"] = self._profile["platform"]

        return headers

    async def get_session(self) -> requests.AsyncSession:
        if self._session is None:
            # JA4/JA4T/JA3 spoofing parameters using curl_cffi extra_fp
            # We randomly permute extensions and slight HTTP/2 weight variations
            # to make the JA3/JA4/Akamai fingerprints highly dynamic and evasive.
            extra_fp = {
                "tls_permute_extensions": True,
            }

            # Randomly tweak HTTP/2 stream weight to mutate the AKAMAI fingerprint and JA4H
            if random.random() > 0.5:
                extra_fp["http2_stream_weight"] = random.randint(250, 256)

            # Occasionally disable HTTP2 priority to generate a different HTTP2 fingerprint
            if random.random() > 0.8:
                extra_fp["http2_no_priority"] = True

            self._session = requests.AsyncSession(
                impersonate=self.impersonate,
                headers=self._get_headers(),
                extra_fp=extra_fp
            )
        return self._session

    async def _close_session(self):
        """Helper to safely close the session without multiple calls throwing cffi exceptions"""
        if self._session:
            try:
                if asyncio.iscoroutinefunction(self._session.close):
                    await self._session.close()
                else:
                    self._session.close()
            except Exception:
                pass
            self._session = None

    async def request(self, method: str, url: str, max_retries: int = 3, **kwargs) -> requests.Response:
        domain = urlparse(url).netloc
        semaphore = self._get_semaphore(domain)

        session = await self.get_session()

        # Merge kwargs headers with default headers if provided
        if 'headers' in kwargs:
            kwargs['headers'] = {**self._get_headers(), **kwargs['headers']}

        retries = 0
        base_delay = 1.0

        while True:
            try:
                async with semaphore:
                    response = await session.request(method, url, **kwargs)

                if response.status_code in (429, 403, 503) and retries < max_retries:
                    # Exponential backoff with Gaussian jitter (outside the lock)
                    jitter = random.gauss(0, 0.1 * base_delay)
                    delay = base_delay + jitter
                    delay = max(0.1, delay) # ensure positive delay

                    await asyncio.sleep(delay)

                    retries += 1
                    base_delay *= 2.0

                    # On retry with high backoff, occasionally rotate profile and session
                    # to drop bad JA3/JA4 reputation
                    if retries >= 2:
                        self._profile = random.choice(BROWSER_PROFILES)
                        self.impersonate = self._profile["impersonate"]
                        await self._close_session()
                        session = await self.get_session()
                    continue

                return response
            except Exception as e:
                if retries < max_retries:
                    jitter = random.gauss(0, 0.1 * base_delay)
                    delay = max(0.1, base_delay + jitter)
                    await asyncio.sleep(delay)
                    retries += 1
                    base_delay *= 2.0

                    if retries >= 2:
                        self._profile = random.choice(BROWSER_PROFILES)
                        self.impersonate = self._profile["impersonate"]
                        await self._close_session()
                        session = await self.get_session()
                    continue
                raise e

    async def close(self):
        await self._close_session()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
