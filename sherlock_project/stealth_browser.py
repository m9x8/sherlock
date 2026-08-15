import asyncio
import logging
from typing import Optional

try:
    from camoufox.async_api import AsyncCamoufox
    CAMOUFOX_AVAILABLE = True
except ImportError:
    CAMOUFOX_AVAILABLE = False

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
    Attempts to use `Camoufox` as the primary engine for top-tier Firefox stealth.
    Falls back to `nodriver` for deep CDP-based Chrome stealth.
    If both fail or are unavailable, falls back gracefully to `curl_cffi` via `StealthEngine`.
    """

    def __init__(self, use_nodriver: bool = True, timeout: int = 15, proxy: Optional[str] = None):
        self.use_camoufox = CAMOUFOX_AVAILABLE
        self.use_nodriver = use_nodriver and NODRIVER_AVAILABLE
        self.timeout = timeout
        self.proxy = proxy

        self.camoufox_context = None
        self.camoufox_browser = None
        self.nodriver_browser = None
        self.stealth_engine: Optional[StealthEngine] = None

    async def _init_browser(self):
        if self.use_camoufox and self.camoufox_browser is None:
            try:
                # Use geoip=True if a proxy is provided (but we use it by default as requested in the instructions)
                kwargs = {"headless": True, "geoip": True}
                if self.proxy:
                    kwargs["proxy"] = {"server": self.proxy}

                # AsyncCamoufox returns a context manager that resolves to the browser instance
                self.camoufox_context = AsyncCamoufox(**kwargs)
                self.camoufox_browser = await self.camoufox_context.__aenter__()
                logger.info("Initialized Camoufox browser backend")
            except Exception as e:
                logger.warning(f"Camoufox failed to start, falling back to nodriver: {e}")
                self.use_camoufox = False
                if self.camoufox_context:
                    try:
                        await self.camoufox_context.__aexit__(None, None, None)
                    except:
                        pass
                self.camoufox_context = None
                self.camoufox_browser = None

        if not self.use_camoufox and self.use_nodriver and self.nodriver_browser is None:
            try:
                browser_args = ['--headless=new', '--no-sandbox', '--disable-gpu']
                if self.proxy:
                    browser_args.append(f'--proxy-server={self.proxy}')

                self.nodriver_browser = await nodriver.start(
                    browser_args=browser_args,
                    sandbox=False
                )
                logger.info("Initialized nodriver browser backend")
            except Exception as e:
                logger.warning(f"nodriver failed to start, falling back to curl_cffi: {e}")
                self.use_nodriver = False

        if not self.use_camoufox and not self.use_nodriver and self.stealth_engine is None:
            logger.info("Initialized curl_cffi StealthEngine backend")
            self.stealth_engine = StealthEngine()

    async def get_html(self, url: str) -> tuple[int, str]:
        """
        Fetches the HTML of the page.
        Tries Camoufox first, then Nodriver, then falls back to curl_cffi.
        Returns a tuple of (status_code, html_content).
        """
        await self._init_browser()

        if self.use_camoufox and self.camoufox_browser:
            page = None
            try:
                page = await self.camoufox_browser.new_page()
                logger.info(f"Using Camoufox engine to fetch {url}")
                response = await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
                await asyncio.sleep(1) # Humanize slightly
                html = await page.content()
                status = response.status if response else 200
                return status, html
            except Exception as e:
                logger.error(f"Camoufox failed to fetch {url}: {e}, trying fallback")
            finally:
                if page:
                    try:
                        await page.close()
                    except Exception:
                        pass

        if self.use_nodriver and self.nodriver_browser:
            page = None
            try:
                logger.info(f"Using nodriver engine to fetch {url}")
                page = await self.nodriver_browser.get(url)
                await asyncio.sleep(1)
                html = await page.get_content()
                return 200, html
            except Exception as e:
                logger.error(f"nodriver failed to fetch {url}: {e}, trying fallback")

        # Fallback using curl_cffi
        if not self.stealth_engine:
            self.stealth_engine = StealthEngine()

        try:
            logger.info(f"Using curl_cffi fallback to fetch {url}")
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
        Takes a screenshot of the url.
        """
        await self._init_browser()

        if self.use_camoufox and self.camoufox_browser:
            page = None
            try:
                page = await self.camoufox_browser.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
                await asyncio.sleep(2)
                await page.screenshot(path=path)
                return True
            except Exception as e:
                logger.error(f"Camoufox screenshot failed: {e}")
            finally:
                if page:
                    try:
                        await page.close()
                    except Exception:
                        pass

        if self.use_nodriver and self.nodriver_browser:
            try:
                page = await self.nodriver_browser.get(url)
                await asyncio.sleep(2)
                await page.save_screenshot(path)
                return True
            except Exception as e:
                logger.error(f"Nodriver screenshot failed: {e}")

        return False

    async def close(self):
        """
        Closes the browser or engine instances cleanly.
        """
        if self.camoufox_context:
            try:
                await self.camoufox_context.__aexit__(None, None, None)
            except Exception:
                pass
            self.camoufox_context = None
            self.camoufox_browser = None

        if self.nodriver_browser:
            try:
                self.nodriver_browser.stop()
                await asyncio.sleep(0.1)
            except Exception:
                pass
            self.nodriver_browser = None

        if self.stealth_engine:
            if asyncio.iscoroutinefunction(self.stealth_engine.close):
                await self.stealth_engine.close()
            self.stealth_engine = None

    async def __aenter__(self):
        await self._init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
