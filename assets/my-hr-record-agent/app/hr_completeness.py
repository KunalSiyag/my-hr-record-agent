"""HR Record Completeness Checker.

Evaluates each section of a consolidated HR record and returns a structured
completeness report with status: 'complete', 'partial', or 'missing'.
Global assignments return 'not_applicable' when empty (they are optional).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Expected fields per HR section
_PERSONAL_INFO_FIELDS = ["firstName", "lastName", "dateOfBirth", "countryOfBirth", "gender", "nationality"]
_EMPLOYMENT_FIELDS = ["startDate", "jobTitle", "department", "company", "employmentType", "emplStatus"]


def _has_value(data: dict, key: str) -> bool:
    """Return True if the key is present and has a non-None, non-empty value."""
    val = data.get(key)
    return val is not None and val != "" and val != []


def _check_field_section(data: dict | None, expected_fields: list[str]) -> str:
    """Evaluate completeness of a dict-based HR section against expected fields."""
    if not data:
        return "missing"
    populated = [f for f in expected_fields if _has_value(data, f)]
    if len(populated) == len(expected_fields):
        return "complete"
    if len(populated) > 0:
        return "partial"
    return "missing"


def _check_list_section(data: list | None, required_fields: list[str]) -> str:
    """Evaluate completeness of a list-based HR section (e.g. contacts, addresses)."""
    if not data:
        return "missing"
    # Check if at least one entry has all required fields
    for entry in data:
        if isinstance(entry, dict) and all(_has_value(entry, f) for f in required_fields):
            return "complete"
    # At least one entry present but no fully complete entry
    return "partial"


def check_completeness(hr_data: dict) -> dict:
    """Evaluate completeness of each HR section in the consolidated HR record.

    Args:
        hr_data: A dict with keys for each HR section:
            - personal_info: dict with personal information fields
            - employment: dict with employment detail fields
            - skills_profile: list of skill/competency objects
            - emergency_contacts: list of emergency contact objects
            - addresses: list of address objects
            - global_assignments: list of global assignment objects (optional)

    Returns:
        A structured completeness report dict:
        {
            "sections": {
                "personal_info": "complete" | "partial" | "missing",
                "employment": "complete" | "partial" | "missing",
                "skills_profile": "complete" | "partial" | "missing",
                "emergency_contacts": "complete" | "partial" | "missing",
                "addresses": "complete" | "partial" | "missing",
                "global_assignments": "complete" | "not_applicable",
            },
            "summary": {
                "complete": [...],
                "partial": [...],
                "missing": [...],
                "not_applicable": [...],
            }
        }
    """
    sections: dict[str, str] = {}

    # Personal information
    sections["personal_info"] = _check_field_section(
        hr_data.get("personal_info"),
        _PERSONAL_INFO_FIELDS,
    )

    # Employment details
    sections["employment"] = _check_field_section(
        hr_data.get("employment"),
        _EMPLOYMENT_FIELDS,
    )

    # Skills & profile — list; at least one skill present = complete
    skills = hr_data.get("skills_profile")
    if skills and len(skills) > 0:
        sections["skills_profile"] = "complete"
    else:
        sections["skills_profile"] = "missing"

    # Emergency contacts — at least one with name + phone
    sections["emergency_contacts"] = _check_list_section(
        hr_data.get("emergency_contacts"),
        ["name", "phone"],
    )

    # Addresses — at least one with address1 + city
    sections["addresses"] = _check_list_section(
        hr_data.get("addresses"),
        ["address1", "city"],
    )

    # Global assignments — optional: empty = not_applicable, present = complete
    global_assignments = hr_data.get("global_assignments")
    if global_assignments and len(global_assignments) > 0:
        sections["global_assignments"] = "complete"
    else:
        sections["global_assignments"] = "not_applicable"

    # Build summary buckets
    summary: dict[str, list[str]] = {
        "complete": [],
        "partial": [],
        "missing": [],
        "not_applicable": [],
    }
    for section_name, status in sections.items():
        summary[status].append(section_name)

    logger.debug("Completeness report: %s", sections)
    return {"sections": sections, "summary": summary}
