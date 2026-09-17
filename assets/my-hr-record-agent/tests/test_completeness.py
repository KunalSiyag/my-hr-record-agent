"""Unit tests for hr_completeness.check_completeness()."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from hr_completeness import check_completeness


FULL_HR_DATA = {
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
    "skills_profile": [
        {"skillId": "S1", "skillName": "Python"},
        {"skillId": "S2", "skillName": "Cloud"},
    ],
    "emergency_contacts": [
        {"name": "John Smith", "relationship": "Spouse", "phone": "+1-555-0456"},
    ],
    "addresses": [
        {"address1": "123 Main St", "city": "San Francisco", "country": "US"},
    ],
    "global_assignments": [],
}


class TestAllSectionsComplete:
    def test_personal_info_complete(self):
        result = check_completeness(FULL_HR_DATA)
        assert result["sections"]["personal_info"] == "complete"

    def test_employment_complete(self):
        result = check_completeness(FULL_HR_DATA)
        assert result["sections"]["employment"] == "complete"

    def test_skills_complete(self):
        result = check_completeness(FULL_HR_DATA)
        assert result["sections"]["skills_profile"] == "complete"

    def test_emergency_contacts_complete(self):
        result = check_completeness(FULL_HR_DATA)
        assert result["sections"]["emergency_contacts"] == "complete"

    def test_addresses_complete(self):
        result = check_completeness(FULL_HR_DATA)
        assert result["sections"]["addresses"] == "complete"

    def test_global_assignments_not_applicable_when_empty(self):
        result = check_completeness(FULL_HR_DATA)
        assert result["sections"]["global_assignments"] == "not_applicable"

    def test_summary_not_applicable_includes_global_assignments(self):
        result = check_completeness(FULL_HR_DATA)
        assert "global_assignments" in result["summary"]["not_applicable"]


class TestMissingSections:
    def test_empty_emergency_contacts_is_missing(self):
        data = {**FULL_HR_DATA, "emergency_contacts": []}
        result = check_completeness(data)
        assert result["sections"]["emergency_contacts"] == "missing"

    def test_none_emergency_contacts_is_missing(self):
        data = {**FULL_HR_DATA, "emergency_contacts": None}
        result = check_completeness(data)
        assert result["sections"]["emergency_contacts"] == "missing"

    def test_empty_skills_is_missing(self):
        data = {**FULL_HR_DATA, "skills_profile": []}
        result = check_completeness(data)
        assert result["sections"]["skills_profile"] == "missing"

    def test_none_personal_info_is_missing(self):
        data = {**FULL_HR_DATA, "personal_info": None}
        result = check_completeness(data)
        assert result["sections"]["personal_info"] == "missing"

    def test_empty_addresses_is_missing(self):
        data = {**FULL_HR_DATA, "addresses": []}
        result = check_completeness(data)
        assert result["sections"]["addresses"] == "missing"


class TestPartialSections:
    def test_partial_employment_data(self):
        data = {
            **FULL_HR_DATA,
            "employment": {
                "startDate": "2004-01-01",
                "jobTitle": "Engineer",
                # missing: department, company, employmentType, emplStatus
            },
        }
        result = check_completeness(data)
        assert result["sections"]["employment"] == "partial"

    def test_partial_personal_info(self):
        data = {
            **FULL_HR_DATA,
            "personal_info": {
                "firstName": "Jane",
                "lastName": "Smith",
                # missing: dateOfBirth, countryOfBirth, gender, nationality
            },
        }
        result = check_completeness(data)
        assert result["sections"]["personal_info"] == "partial"

    def test_partial_address_no_city(self):
        data = {
            **FULL_HR_DATA,
            "addresses": [{"address1": "123 Main St"}],  # missing city
        }
        result = check_completeness(data)
        assert result["sections"]["addresses"] == "partial"


class TestGlobalAssignments:
    def test_global_assignments_complete_when_present(self):
        data = {
            **FULL_HR_DATA,
            "global_assignments": [{"assignmentId": "GA-001", "hostCountry": "DE"}],
        }
        result = check_completeness(data)
        assert result["sections"]["global_assignments"] == "complete"

    def test_global_assignments_not_applicable_when_empty(self):
        data = {**FULL_HR_DATA, "global_assignments": []}
        result = check_completeness(data)
        assert result["sections"]["global_assignments"] == "not_applicable"

    def test_global_assignments_not_in_missing(self):
        """Empty global assignments should NOT appear in the missing bucket."""
        data = {**FULL_HR_DATA, "global_assignments": []}
        result = check_completeness(data)
        assert "global_assignments" not in result["summary"]["missing"]


class TestSummaryStructure:
    def test_summary_has_all_buckets(self):
        result = check_completeness(FULL_HR_DATA)
        assert "complete" in result["summary"]
        assert "partial" in result["summary"]
        assert "missing" in result["summary"]
        assert "not_applicable" in result["summary"]

    def test_sections_key_present(self):
        result = check_completeness(FULL_HR_DATA)
        assert "sections" in result
        assert len(result["sections"]) == 6
