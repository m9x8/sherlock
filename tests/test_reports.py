import os
import pytest
from sherlock_project.reports import ReportGenerator

def test_report_generator_txt(tmp_path):
    txt_file = tmp_path / "test_report.txt"
    phone_meta = {
        "valid": True,
        "clean": "+31612345678",
        "e164": "+31612345678",
        "international": "+31 6 12345678",
        "national": "06 12345678",
        "type": "Mobile",
        "carrier": "KPN",
        "location": "Netherlands",
        "timezones": ["Europe/Amsterdam"]
    }
    phone_results = {
        "General Web Mentions": [
            {"title": "Test Title", "url": "https://example.com/test", "snippet": "Test snippet info"}
        ]
    }

    ReportGenerator.export_txt(str(txt_file), "", {}, phone_meta, phone_results)
    assert os.path.exists(txt_file)
    with open(txt_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "SHERLOCK" in content
        assert "+31612345678" in content
        assert "KPN" in content
        assert "Test Title" in content

def test_report_generator_docx(tmp_path):
    docx_file = tmp_path / "test_report.docx"
    phone_meta = {
        "valid": True,
        "clean": "+31612345678",
        "e164": "+31612345678",
        "international": "+31 6 12345678",
        "national": "06 12345678",
        "type": "Mobile",
        "carrier": "KPN",
        "location": "Netherlands",
        "timezones": ["Europe/Amsterdam"]
    }
    phone_results = {
        "General Web Mentions": [
            {"title": "Test Title", "url": "https://example.com/test", "snippet": "Test snippet info"}
        ]
    }
    ReportGenerator.export_docx(str(docx_file), "", {}, phone_meta, phone_results)
    assert os.path.exists(docx_file)

def test_report_generator_pdf(tmp_path):
    pdf_file = tmp_path / "test_report.pdf"
    phone_meta = {
        "valid": True,
        "clean": "+31612345678",
        "e164": "+31612345678",
        "international": "+31 6 12345678",
        "national": "06 12345678",
        "type": "Mobile",
        "carrier": "KPN",
        "location": "Netherlands",
        "timezones": ["Europe/Amsterdam"]
    }
    phone_results = {
        "General Web Mentions": [
            {"title": "Test Title", "url": "https://example.com/test", "snippet": "Test snippet info"}
        ]
    }
    ReportGenerator.export_pdf(str(pdf_file), "", {}, phone_meta, phone_results)
    assert os.path.exists(pdf_file)
