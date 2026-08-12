import asyncio
import random
from urllib.parse import urlparse
from curl_cffi import requests
from typing import Optional, Dict, Any

class StealthEngine:
    def __init__(self, concurrency_per_domain: int = 5):
        self.concurrency_per_domain = concurrency_per_domain
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        # Chrome v120 impersonation
        self.impersonate = "chrome120"
        self._session: Optional[requests.AsyncSession] = None

    def _get_semaphore(self, domain: str) -> asyncio.Semaphore:
        if domain not in self._semaphores:
            self._semaphores[domain] = asyncio.Semaphore(self.concurrency_per_domain)
        return self._semaphores[domain]

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Upgrade-Insecure-Requests": "1"
        }

    async def get_session(self) -> requests.AsyncSession:
        if self._session is None:
            self._session = requests.AsyncSession(
                impersonate=self.impersonate,
                headers=self._get_headers()
            )
        return self._session

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

                if response.status_code in (429, 503) and retries < max_retries:
                    # Exponential backoff with Gaussian jitter (outside the lock)
                    jitter = random.gauss(0, 0.1 * base_delay)
                    delay = base_delay + jitter
                    delay = max(0.1, delay) # ensure positive delay

                    await asyncio.sleep(delay)

                    retries += 1
                    base_delay *= 2.0
                    continue

                return response
            except Exception as e:
                if retries < max_retries:
                    jitter = random.gauss(0, 0.1 * base_delay)
                    delay = max(0.1, base_delay + jitter)
                    await asyncio.sleep(delay)
                    retries += 1
                    base_delay *= 2.0
                    continue
                raise e

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
