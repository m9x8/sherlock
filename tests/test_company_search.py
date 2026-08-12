import pytest
from sherlock_project.company_search import CompanyOSINT

def test_company_osint_search():
    co = CompanyOSINT()
    # Test that filtering on Nederland works and contains the correct registries
    nl_results = co.search_company("Philips", "Nederland")
    assert "Nederland" in nl_results
    assert "Verenigd Koninkrijk" not in nl_results

    # Test that Alle returns all categories
    all_results = co.search_company("ASML", "Alle")
    assert "Nederland" in all_results
    assert "Verenigd Koninkrijk" in all_results
    assert "Duitsland" in all_results
    assert "België" in all_results
    assert "Wereldwijd / LinkedIn" in all_results

    # Test empty company name scenario
    empty_results = co.search_company("", "Alle")
    assert empty_results == {}
