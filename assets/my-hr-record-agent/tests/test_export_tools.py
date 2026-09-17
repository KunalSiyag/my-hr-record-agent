"""Tests for the export_tools module (generate_hr_pdf and generate_hr_json tools)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from export_tools import (
    get_export_tools,
    get_stored_file,
    _generate_pdf_tool,
    _generate_json_tool,
    _file_store,
)

_SAMPLE_HR_DATA = {
    "personal_info": {
        "firstName": "Jane",
        "lastName": "Doe",
        "dateOfBirth": "1985-03-15",
        "gender": "F",
        "nationality": "US",
        "email": "jane.doe@example.com",
    },
    "employment": {
        "startDate": "2015-06-01",
        "jobTitle": "Senior Engineer",
        "department": "Engineering",
        "company": "ACME Corp",
        "employmentType": "fulltime",
        "emplStatus": "A",
    },
    "skills_profile": [{"skill": "Python"}, {"skill": "SAP"}],
    "emergency_contacts": [{"name": "John Doe", "relationship": "Spouse", "phone": "555-1234"}],
    "addresses": [{"address1": "123 Main St", "city": "Springfield", "country": "US"}],
    "global_assignments": [],
}
_SAMPLE_HR_DATA_JSON = json.dumps(_SAMPLE_HR_DATA)


class TestGetExportTools:
    def test_returns_two_tools(self):
        tools = get_export_tools()
        assert len(tools) == 2

    def test_tool_names(self):
        tools = get_export_tools()
        names = {t.name for t in tools}
        assert "generate_hr_pdf" in names
        assert "generate_hr_json" in names

    def test_tools_have_descriptions(self):
        for tool in get_export_tools():
            assert tool.description and len(tool.description) > 10


class TestGeneratePdfTool:
    def test_success_returns_json_with_status(self):
        result = _generate_pdf_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert payload["status"] == "success"

    def test_success_contains_filename(self):
        result = _generate_pdf_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert payload["filename"] == "hr-record-EMP001.pdf"

    def test_success_contains_size(self):
        result = _generate_pdf_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert payload["size_bytes"] > 0

    def test_success_contains_download_url(self):
        result = _generate_pdf_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert "download_url" in payload
        assert "hr-record-EMP001.pdf" in payload["download_url"]

    def test_file_stored_in_store(self):
        _generate_pdf_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP-STORE-001")
        stored = get_stored_file("hr-record-EMP-STORE-001.pdf")
        assert stored is not None
        assert stored["mime"] == "application/pdf"
        assert stored["bytes"][:4] == b"%PDF"

    def test_get_stored_file_returns_none_for_unknown(self):
        assert get_stored_file("nonexistent-file.pdf") is None

    def test_default_employee_id(self):
        result = _generate_pdf_tool(_SAMPLE_HR_DATA_JSON)
        payload = json.loads(result)
        assert "unknown" in payload["filename"]

    def test_accepts_dict_directly(self):
        result = _generate_pdf_tool(_SAMPLE_HR_DATA)  # type: ignore
        payload = json.loads(result)
        assert payload["status"] == "success"

    def test_error_on_bad_input(self):
        result = _generate_pdf_tool("not-valid-json")
        payload = json.loads(result)
        assert payload["status"] == "error"
        assert "message" in payload

    def test_download_url_uses_env_base_url(self, monkeypatch):
        monkeypatch.setenv("AGENT_PUBLIC_URL", "https://myagent.example.com")
        result = _generate_pdf_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP-URL")
        payload = json.loads(result)
        assert payload["download_url"].startswith("https://myagent.example.com/download/")


class TestGenerateJsonTool:
    def test_success_returns_json_with_status(self):
        result = _generate_json_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert payload["status"] == "success"

    def test_success_contains_filename(self):
        result = _generate_json_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert payload["filename"] == "hr-record-EMP001.json"

    def test_success_contains_size(self):
        result = _generate_json_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert payload["size_bytes"] > 0

    def test_success_contains_download_url(self):
        result = _generate_json_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP001")
        payload = json.loads(result)
        assert "download_url" in payload
        assert "hr-record-EMP001.json" in payload["download_url"]

    def test_file_stored_in_store(self):
        _generate_json_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP-STORE-002")
        stored = get_stored_file("hr-record-EMP-STORE-002.json")
        assert stored is not None
        assert stored["mime"] == "application/json"
        export = json.loads(stored["bytes"])
        assert "hr_record" in export

    def test_default_employee_id(self):
        result = _generate_json_tool(_SAMPLE_HR_DATA_JSON)
        payload = json.loads(result)
        assert "unknown" in payload["filename"]

    def test_accepts_dict_directly(self):
        result = _generate_json_tool(_SAMPLE_HR_DATA)  # type: ignore
        payload = json.loads(result)
        assert payload["status"] == "success"

    def test_error_on_bad_input(self):
        result = _generate_json_tool("not-valid-json")
        payload = json.loads(result)
        assert payload["status"] == "error"

    def test_download_url_uses_env_base_url(self, monkeypatch):
        monkeypatch.setenv("AGENT_PUBLIC_URL", "https://myagent.example.com")
        result = _generate_json_tool(_SAMPLE_HR_DATA_JSON, employee_id="EMP-URL2")
        payload = json.loads(result)
        assert payload["download_url"].startswith("https://myagent.example.com/download/")
