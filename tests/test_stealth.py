import pytest
import asyncio
from unittest.mock import patch, MagicMock
from sherlock_project.stealth_browser import StealthBrowser

@pytest.mark.asyncio
async def test_stealth_browser_init_camoufox_mocked():
    """Verify StealthBrowser properly routes through Camoufox cleanly in context manager."""
    with patch("sherlock_project.stealth_browser.CAMOUFOX_AVAILABLE", True):
        with patch("sherlock_project.stealth_browser.AsyncCamoufox") as MockCamoufox:
            mock_browser = MagicMock()
            mock_page = MagicMock()
            mock_browser.new_page.return_value = asyncio.Future()
            mock_browser.new_page.return_value.set_result(mock_page)

            MockCamoufox.return_value.__aenter__.return_value = mock_browser

            async with StealthBrowser() as browser:
                assert browser.use_camoufox is True
                assert browser.camoufox_browser is not None

@pytest.mark.asyncio
async def test_stealth_browser_close():
    async with StealthBrowser() as browser:
        pass
    assert browser.camoufox_browser is None
    assert browser.nodriver_browser is None
    assert browser.stealth_engine is None
