import pytest
from sherlock_project.phone_search import PhoneOSINT

def test_phone_osint_validation():
    p = PhoneOSINT()
    # Test valid Dutch phone number
    meta = p.validate_and_meta("+31612345678")
    assert meta["valid"] is True
    assert meta["carrier"] == "KPN"
    assert meta["type"] == "Mobile"
    assert meta["location"] == "Netherlands"
    assert meta["country_code"] == 31

    # Test invalid format
    meta_invalid = p.validate_and_meta("not-a-number")
    assert meta_invalid["valid"] is False

def test_phone_osint_dorking():
    from unittest.mock import patch
    with patch("sherlock_project.phone_search.PhoneOSINT._advanced_search", return_value=[{"title": "test", "url": "http", "snippet": "test"}]):
        p = PhoneOSINT()
        meta = p.validate_and_meta("+31612345678")
        mentions = p.search_phone_mentions(meta)
    assert "General Web Mentions" in mentions
    assert "Social Media Matches" in mentions

def test_phone_osint_advanced_dorks():
    from unittest.mock import patch
    with patch("sherlock_project.phone_search.PhoneOSINT._advanced_search", return_value=[{"title": "test", "url": "http", "snippet": "test"}]):
        p = PhoneOSINT()
        meta = p.validate_and_meta("+31612345678")
        dorks = p.search_phone_advanced_dorks(meta)
    assert "Lek- & Paste-sites" in dorks
    assert "Documenten & Resumes" in dorks
    assert "Professionele Netwerken" in dorks
    assert "Chat- & Messenger-groepen" in dorks
    assert "Adresboeken & Spam-registries" in dorks

def test_username_advanced_dorks():
    from unittest.mock import patch
    with patch("sherlock_project.phone_search.PhoneOSINT._advanced_search", return_value=[{"title": "test", "url": "http", "snippet": "test"}]):
        p = PhoneOSINT()
        dorks = p.search_username_advanced_dorks("testuser")
    assert "Lek- & Paste-sites" in dorks
    assert "Documenten & Resumes" in dorks
    assert "Professionele Netwerken" in dorks
    assert "Chat- & Messenger-groepen" in dorks
    assert "Adresboeken & Spam-registries" in dorks
