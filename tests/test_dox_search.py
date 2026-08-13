import pytest
from unittest.mock import MagicMock
from sherlock_project.dox_search import DoxProfiler

def test_dox_profiler_search():
    dp = DoxProfiler()
    dp.phone_osint._advanced_search = MagicMock(return_value=[
        {"title": "Target Dox Found", "url": "https://doxsite.com/target", "snippet": "A fake dox result"}
    ])

    results = dp.search_dox_dossier(username="testuser", name="John Doe", city="Amsterdam")
    assert "Gevonden Adressen & Kadaster" in results
    assert "Relaties, Familie & Connecties" in results
    assert "Gekoppelde Bedrijven & Directies" in results
    assert "Lekken, Gegevensbreuken & Pastes" in results
    assert "Social Media & Online Voetafdruk" in results

    assert len(results["Gevonden Adressen & Kadaster"]) == 1
    assert results["Gevonden Adressen & Kadaster"][0]["title"] == "Target Dox Found"

    empty_results = dp.search_dox_dossier()
    assert empty_results["Gevonden Adressen & Kadaster"] == []
