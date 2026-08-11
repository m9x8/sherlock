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
    p = PhoneOSINT()
    meta = p.validate_and_meta("+31612345678")
    mentions = p.search_phone_mentions(meta)
    assert "General Web Mentions" in mentions
    assert "Social Media Matches" in mentions
