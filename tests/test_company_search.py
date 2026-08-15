import pytest
from sherlock_project.company_search import CompanyOSINT

def test_company_osint_search():
    from unittest.mock import patch
    with patch("sherlock_project.phone_search.PhoneOSINT._advanced_search", return_value=[{"title": "test", "url": "http", "snippet": "test"}]):
        co = CompanyOSINT()
        # Test that filtering on Nederland works and contains the correct registries
        nl_results = co.search_company("Philips", "Nederland")
    assert "Officiële Registers (NL)" in nl_results
    assert "Officiële Registers (UK)" not in nl_results

    # Test that Alle returns all categories
    all_results = co.search_company("ASML", "Alle")
    assert "Officiële Registers" in all_results
    assert "Social Media & Profielen" in all_results
    assert "Website & Domein Vermeldingen" in all_results
    assert "Nieuws & Persberichten" in all_results
    assert "Lekken & Databases" in all_results

    # Test empty company name scenario
    empty_results = co.search_company("", "Alle")
    assert empty_results == {}
