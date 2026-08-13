import pytest
from unittest.mock import MagicMock
from sherlock_project.person_search import PersonOSINT

def test_person_osint_search():
    p = PersonOSINT()

    # Mock search so we don't hit the real network during testing
    p.phone_osint._advanced_search = MagicMock(return_value=[
        {"title": "John Doe Profile", "url": "https://linkedin.com/in/johndoe", "snippet": "A dummy LinkedIn bio"}
    ])

    results = p.search_person("John", "Doe", "Amsterdam")
    assert "Sociale Media & Profielen" in results
    assert "CV's & Resumes (Documenten)" in results
    assert "Nieuws, Artikelen & Pers" in results
    assert len(results["Sociale Media & Profielen"]) == 1
    assert results["Sociale Media & Profielen"][0]["title"] == "John Doe Profile"

    # Test empty name inputs
    empty_results = p.search_person("", "")
    assert empty_results == {}
