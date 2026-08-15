import asyncio
import logging
from typing import Optional

try:
    import nodriver
    NODRIVER_AVAILABLE = True
except ImportError:
    NODRIVER_AVAILABLE = False

from sherlock_project.stealth_engine import StealthEngine

logger = logging.getLogger(__name__)

class StealthBrowser:
    """
    A unified async stealth browser abstraction.
    Attempts to use `nodriver` for deep CDP-based stealth evasion (like Cloudflare, DataDome).
    If `nodriver` is unavailable or fails, falls back gracefully to `curl_cffi` via `StealthEngine`.
    """

    def __init__(self, use_nodriver: bool = True, timeout: int = 15, proxy: Optional[str] = None):
        self.use_nodriver = use_nodriver and NODRIVER_AVAILABLE
        self.timeout = timeout
        self.proxy = proxy

        self.browser = None
        self.stealth_engine: Optional[StealthEngine] = None

    async def _init_browser(self):
        if self.use_nodriver and self.browser is None:
            try:
                browser_args = ['--headless=new', '--no-sandbox', '--disable-gpu']
                if self.proxy:
                    browser_args.append(f'--proxy-server={self.proxy}')

                self.browser = await nodriver.start(
                    browser_args=browser_args,
                    sandbox=False
                )
            except Exception as e:
                logger.warning(f"nodriver failed to start, falling back to curl_cffi: {e}")
                self.use_nodriver = False

        if not self.use_nodriver and self.stealth_engine is None:
            self.stealth_engine = StealthEngine()

    async def get_html(self, url: str) -> tuple[int, str]:
        """
        Fetches the HTML of the page, using nodriver first, then falling back to curl_cffi.
        Returns a tuple of (status_code, html_content).
        """
        await self._init_browser()

        if self.use_nodriver and self.browser:
            try:
                # Use nodriver to get the page
                page = await self.browser.get(url)

                # We can add humanize behavior here, like a small random sleep
                await asyncio.sleep(1)

                html = await page.get_content()

                # Assume 200 if we got HTML without throwing, nodriver doesn't expose status easily
                return 200, html
            except Exception as e:
                logger.error(f"nodriver failed to fetch {url}: {e}, trying fallback")
                # Fallback to curl_cffi
                pass

        # Fallback using curl_cffi
        if not self.stealth_engine:
            self.stealth_engine = StealthEngine()

        try:
            # We don't have the context of the async block, StealthEngine has `request` method
            # Assuming StealthEngine.request is an async method returning a Response object
            if asyncio.iscoroutinefunction(self.stealth_engine.request):
                response = await self.stealth_engine.request("GET", url, timeout=self.timeout)
            else:
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(None, lambda: self.stealth_engine.request("GET", url, timeout=self.timeout))
            return response.status_code, response.text
        except Exception as e:
            logger.error(f"Fallback stealth engine failed for {url}: {e}")
            return 0, ""

    async def screenshot(self, url: str, path: str):
        """
        Takes a screenshot of the url. Only works if nodriver is active.
        """
        await self._init_browser()
        if self.use_nodriver and self.browser:
            try:
                page = await self.browser.get(url)
                await asyncio.sleep(2)  # Wait for rendering
                await page.save_screenshot(path)
                return True
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")
                return False
        return False

    async def close(self):
        """
        Closes the browser or engine instances.
        """
        if self.browser:
            try:
                self.browser.stop()
                # give nodriver time to cleanup so we don't get the base_subprocess error
                await asyncio.sleep(0.1)
            except Exception:
                pass
            self.browser = None

        if self.stealth_engine:
            await self.stealth_engine.close()
            self.stealth_engine = None

    async def __aenter__(self):
        await self._init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
