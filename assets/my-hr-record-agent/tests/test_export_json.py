"""Unit tests for hr_export.generate_json()."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from hr_export import generate_json
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
    "addresses": [{"address1": "123 Main St", "city": "San Francisco"}],
    "global_assignments": [],
}


class TestGenerateJson:
    def test_returns_valid_json_string(self):
        completeness = check_completeness(HR_DATA)
        result = generate_json(HR_DATA, completeness)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_has_metadata_key(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        assert "metadata" in result

    def test_has_hr_record_key(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        assert "hr_record" in result

    def test_has_completeness_key(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        assert "completeness" in result

    def test_metadata_has_generated_at(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        assert "generated_at" in result["metadata"]

    def test_metadata_has_employee_id(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness, employee_id="EMP-10001"))
        assert result["metadata"]["employee_id"] == "EMP-10001"

    def test_metadata_has_completeness_summary(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        assert "completeness_summary" in result["metadata"]

    def test_completeness_summary_has_buckets(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        summary = result["metadata"]["completeness_summary"]
        assert "complete" in summary
        assert "partial" in summary
        assert "missing" in summary
        assert "not_applicable" in summary

    def test_hr_record_contains_personal_info(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        assert "personal_info" in result["hr_record"]

    def test_hr_record_contains_employment(self):
        completeness = check_completeness(HR_DATA)
        result = json.loads(generate_json(HR_DATA, completeness))
        assert "employment" in result["hr_record"]

    def test_empty_hr_data(self):
        """generate_json should handle empty hr_data gracefully."""
        empty_data = {}
        completeness = check_completeness(empty_data)
        result = generate_json(empty_data, completeness)
        parsed = json.loads(result)
        assert "hr_record" in parsed
