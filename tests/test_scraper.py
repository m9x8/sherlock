import pytest
import asyncio
from unittest.mock import patch, MagicMock
from sherlock_project.scraper import HighEndScraper

@pytest.mark.asyncio
async def test_high_end_scraper_context_manager():
    """Verify HighEndScraper cleanly handles AsyncExitStack during startup and teardown."""
    async with HighEndScraper() as scraper:
        assert scraper.browser is not None
        assert scraper.browser_context is not None

    # Verify everything gets cleaned up after exiting context
    assert scraper.browser is None
    assert scraper.browser_context is None

@pytest.mark.asyncio
@patch("sherlock_project.stealth_browser.StealthBrowser.get_html")
async def test_scrape_company_details(mock_get_html):
    mock_html = '''<html><body><a href="/openkvk/test-company">Test Company B.V.</a></body></html>'''

    # We mock the return as a Future resolving to (status, text)
    async def mock_coro(*args, **kwargs):
        return (200, mock_html)
    mock_get_html.side_effect = mock_coro

    async with HighEndScraper() as scraper:
        results = await scraper.scrape_company_direct_details("test-company")

        assert len(results) == 1
        assert results[0]["title"] == "OpenKVK NL - Test Company B.V."
        assert "https://openkvk.nl/openkvk/test-company" in results[0]["url"]
