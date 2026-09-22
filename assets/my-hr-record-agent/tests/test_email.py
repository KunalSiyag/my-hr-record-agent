"""Tests for email_service + send_hr_record_email tool (SMTP mocked, offline)."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

import email_service
from email_tools import _send_hr_record_email_tool, get_email_tools

SAMPLE_HR = json.dumps({
    "personal_info": {"firstName": "Jane", "lastName": "Doe"},
    "employment": {"jobTitle": "Engineer"},
    "skills_profile": [],
    "emergency_contacts": [],
    "addresses": [],
    "global_assignments": [],
})


@pytest.fixture
def smtp_env(monkeypatch):
    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "sender@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "secret")
    monkeypatch.setenv("SMTP_FROM", "sender@example.com")


def _mock_smtp(monkeypatch):
    server = MagicMock()
    server.__enter__.return_value = server
    server.__exit__.return_value = False
    cls = MagicMock(return_value=server)
    monkeypatch.setattr(email_service.smtplib, "SMTP", cls)
    return server


class TestValidateEmail:
    def test_valid(self):
        assert email_service.validate_email(" alex@example.com ") == "alex@example.com"

    def test_invalid(self):
        with pytest.raises(ValueError):
            email_service.validate_email("not-an-email")


class TestSendEmail:
    def test_success(self, smtp_env, monkeypatch):
        server = _mock_smtp(monkeypatch)
        result = email_service.send_email("a@b.com", "Sub", "Body", [("f.pdf", b"%PDF", "application/pdf")])
        assert result["status"] == "success"
        server.send_message.assert_called_once()

    def test_unconfigured(self, monkeypatch):
        monkeypatch.delenv("SMTP_HOST", raising=False)
        with pytest.raises(RuntimeError):
            email_service.send_email("a@b.com", "Sub", "Body")


class TestEmailTool:
    def test_tool_registered(self):
        tools = get_email_tools()
        assert [t.name for t in tools] == ["send_hr_record_email"]

    def test_generate_and_send_pdf(self, smtp_env, monkeypatch):
        _mock_smtp(monkeypatch)
        payload = json.loads(_send_hr_record_email_tool("me@x.com", SAMPLE_HR, employee_id="E1"))
        assert payload["status"] == "success"
        assert payload["to"] == "me@x.com"
        assert payload["filename"].endswith(".pdf")

    def test_generate_and_send_json(self, smtp_env, monkeypatch):
        _mock_smtp(monkeypatch)
        payload = json.loads(_send_hr_record_email_tool(
            "me@x.com", SAMPLE_HR, employee_id="E1", file_format="json"))
        assert payload["status"] == "success"
        assert payload["filename"].endswith(".json")

    def test_reuse_stored_file(self, smtp_env, monkeypatch):
        from export_tools import _generate_pdf_tool, _file_store
        _generate_pdf_tool(SAMPLE_HR, employee_id="E2")
        assert "hr-record-E2.pdf" in _file_store
        _mock_smtp(monkeypatch)
        payload = json.loads(_send_hr_record_email_tool("me@x.com", filename="hr-record-E2.pdf"))
        assert payload["status"] == "success"

    def test_invalid_email(self, smtp_env, monkeypatch):
        payload = json.loads(_send_hr_record_email_tool("bad", SAMPLE_HR))
        assert payload["status"] == "error"

    def test_missing_data_and_file(self, smtp_env, monkeypatch):
        payload = json.loads(_send_hr_record_email_tool("me@x.com"))
        assert payload["status"] == "error"

    def test_unconfigured_smtp(self, monkeypatch):
        monkeypatch.delenv("SMTP_HOST", raising=False)
        payload = json.loads(_send_hr_record_email_tool("me@x.com", SAMPLE_HR))
        assert payload["status"] == "error"
