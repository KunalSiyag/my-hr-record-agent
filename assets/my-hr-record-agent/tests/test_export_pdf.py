"""Unit tests for hr_export.generate_pdf()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from hr_export import generate_pdf
from hr_completeness import check_completeness

HR_DATA = {
    "personal_info": {
        "firstName": "Jane",
        "lastName": "Smith",
        "dateOfBirth": "1986-01-01",
        "countryOfBirth": "US",
        "gender": "F",
        "nationality": "US",
    },
    "employment": {
        "startDate": "2004-01-01",
        "jobTitle": "Senior Software Engineer",
        "department": "Engineering",
        "company": "ACME Corp",
        "employmentType": "Regular",
        "emplStatus": "A",
    },
    "skills_profile": [{"skillName": "Python"}],
    "emergency_contacts": [{"name": "John Smith", "phone": "+1-555-0456"}],
    "addresses": [{"address1": "123 Main St", "city": "San Francisco", "country": "US"}],
    "global_assignments": [],
}


class TestGeneratePdf:
    def test_returns_bytes(self):
        completeness = check_completeness(HR_DATA)
        result = generate_pdf(HR_DATA, completeness)
        assert isinstance(result, bytes)

    def test_returns_non_empty_bytes(self):
        completeness = check_completeness(HR_DATA)
        result = generate_pdf(HR_DATA, completeness)
        assert len(result) > 0

    def test_pdf_magic_bytes(self):
        """PDF files should start with %PDF."""
        completeness = check_completeness(HR_DATA)
        result = generate_pdf(HR_DATA, completeness)
        assert result[:4] == b"%PDF"

    def test_empty_hr_data(self):
        """generate_pdf should handle empty hr_data gracefully."""
        empty_data = {}
        completeness = check_completeness(empty_data)
        result = generate_pdf(empty_data, completeness)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_with_global_assignments(self):
        data = {
            **HR_DATA,
            "global_assignments": [{"assignmentId": "GA-001", "hostCountry": "DE"}],
        }
        completeness = check_completeness(data)
        result = generate_pdf(data, completeness)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_list_section_rendered(self):
        """Exercises list-based section rendering in PDF."""
        data = {
            **HR_DATA,
            "skills_profile": [
                {"skillName": "Python", "level": "Expert"},
                {"skillName": "Java", "level": "Advanced"},
            ],
        }
        completeness = check_completeness(data)
        result = generate_pdf(data, completeness)
        assert isinstance(result, bytes)

    def test_render_value_none(self):
        from hr_export import _render_value
        assert _render_value(None) == "—"

    def test_render_value_list(self):
        from hr_export import _render_value
        assert "Python" in _render_value(["Python", "Java"])

    def test_render_value_dict(self):
        from hr_export import _render_value
        result = _render_value({"key": "val"})
        assert "key" in result

    def test_get_employee_name_with_data(self):
        from hr_export import _get_employee_name
        data = {"personal_info": {"firstName": "Jane", "lastName": "Smith"}}
        assert _get_employee_name(data) == "Jane Smith"

    def test_get_employee_name_no_data(self):
        from hr_export import _get_employee_name
        assert _get_employee_name({}) == "Unknown Employee"
