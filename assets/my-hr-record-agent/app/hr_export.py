"""HR Record Export Utilities.

Provides PDF and JSON export functions for a consolidated HR record.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from io import BytesIO
from typing import Any

logger = logging.getLogger(__name__)

# Status badge labels for PDF rendering
_BADGE_LABELS = {
    "complete": "[OK] Complete",
    "partial": "[!] Partial",
    "missing": "[X] Missing",
    "not_applicable": "[-] Not Applicable",
}

# Unicode badges for JSON/display use only (not PDF)
_BADGE_LABELS_UNICODE = {
    "complete": "\u2713 Complete",
    "partial": "\u26a0 Partial",
    "missing": "\u2717 Missing",
    "not_applicable": "\u2014 Not Applicable",
}

# Human-readable section titles
_SECTION_TITLES = {
    "personal_info": "Personal Information",
    "employment": "Employment Details",
    "skills_profile": "Skills & Profile",
    "emergency_contacts": "Emergency Contacts",
    "addresses": "Addresses",
    "global_assignments": "Global Assignments",
}


def _get_employee_name(hr_data: dict) -> str:
    """Extract the employee's display name from personal_info, if available."""
    personal = hr_data.get("personal_info") or {}
    first = personal.get("firstName", "")
    last = personal.get("lastName", "")
    name = f"{first} {last}".strip()
    return name if name else "Unknown Employee"


def _render_value(value: Any) -> str:
    """Render a field value as a readable string."""
    if value is None:
        return "—"
    if isinstance(value, list):
        if not value:
            return "—"
        return ", ".join(str(v) for v in value)
    if isinstance(value, dict):
        return json.dumps(value)
    return str(value)


def generate_pdf(hr_data: dict, completeness: dict) -> bytes:
    """Generate a PDF export of the consolidated HR record.

    Args:
        hr_data: Consolidated HR data dict with sections as keys.
        completeness: Completeness report from check_completeness().

    Returns:
        PDF content as bytes.
    """
    try:
        from fpdf import FPDF  # type: ignore
    except ImportError:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            return _generate_pdf_reportlab(hr_data, completeness)
        except ImportError:
            logger.error("Neither fpdf2 nor reportlab is available for PDF generation")
            raise RuntimeError(
                "PDF generation requires fpdf2 or reportlab. "
                "Add 'fpdf2' to requirements.txt."
            )

    return _generate_pdf_fpdf(hr_data, completeness)


def _generate_pdf_fpdf(hr_data: dict, completeness: dict) -> bytes:
    """Generate PDF using fpdf2."""
    from fpdf import FPDF  # type: ignore

    employee_name = _get_employee_name(hr_data)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections_status = completeness.get("sections", {})

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "My HR Record", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, employee_name, ln=True, align="C")
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, f"Generated: {generated_at}", ln=True, align="C")
    pdf.ln(8)

    # Completeness Summary
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Completeness Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for section_key, status in sections_status.items():
        title = _SECTION_TITLES.get(section_key, section_key)
        badge = _BADGE_LABELS.get(status, status)
        pdf.cell(0, 7, f"  {title}: {badge}", ln=True)
    pdf.ln(6)

    # HR Data Sections
    section_order = ["personal_info", "employment", "skills_profile", "emergency_contacts", "addresses", "global_assignments"]
    for section_key in section_order:
        title = _SECTION_TITLES.get(section_key, section_key)
        status = sections_status.get(section_key, "missing")
        badge = _BADGE_LABELS.get(status, status)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 9, f"{title}  [{badge}]", ln=True)
        pdf.set_font("Helvetica", "", 10)

        section_data = hr_data.get(section_key)
        if not section_data:
            pdf.cell(0, 7, "  No data available.", ln=True)
        elif isinstance(section_data, dict):
            for k, v in section_data.items():
                pdf.cell(0, 7, f"  {k}: {_render_value(v)}", ln=True)
        elif isinstance(section_data, list):
            for i, item in enumerate(section_data, 1):
                if isinstance(item, dict):
                    pdf.cell(0, 7, f"  Entry {i}:", ln=True)
                    for k, v in item.items():
                        pdf.cell(0, 7, f"    {k}: {_render_value(v)}", ln=True)
                else:
                    pdf.cell(0, 7, f"  {i}. {_render_value(item)}", ln=True)
        pdf.ln(4)

    return bytes(pdf.output())


def _generate_pdf_reportlab(hr_data: dict, completeness: dict) -> bytes:
    """Generate PDF using reportlab as fallback."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib import colors

    employee_name = _get_employee_name(hr_data)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections_status = completeness.get("sections", {})

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("My HR Record", styles["Title"]))
    story.append(Paragraph(employee_name, styles["h2"]))
    story.append(Paragraph(f"Generated: {generated_at}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("Completeness Summary", styles["h2"]))
    for section_key, status in sections_status.items():
        title = _SECTION_TITLES.get(section_key, section_key)
        badge = _BADGE_LABELS.get(status, status)
        story.append(Paragraph(f"{title}: {badge}", styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))

    section_order = ["personal_info", "employment", "skills_profile", "emergency_contacts", "addresses", "global_assignments"]
    for section_key in section_order:
        title = _SECTION_TITLES.get(section_key, section_key)
        status = sections_status.get(section_key, "missing")
        badge = _BADGE_LABELS.get(status, status)
        story.append(Paragraph(f"{title} [{badge}]", styles["h3"]))
        section_data = hr_data.get(section_key)
        if not section_data:
            story.append(Paragraph("No data available.", styles["Normal"]))
        elif isinstance(section_data, dict):
            for k, v in section_data.items():
                story.append(Paragraph(f"<b>{k}:</b> {_render_value(v)}", styles["Normal"]))
        elif isinstance(section_data, list):
            for i, item in enumerate(section_data, 1):
                if isinstance(item, dict):
                    story.append(Paragraph(f"Entry {i}:", styles["Normal"]))
                    for k, v in item.items():
                        story.append(Paragraph(f"  {k}: {_render_value(v)}", styles["Normal"]))
                else:
                    story.append(Paragraph(f"{i}. {_render_value(item)}", styles["Normal"]))
        story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    return buffer.getvalue()


def generate_json(hr_data: dict, completeness: dict, employee_id: str = "unknown") -> str:
    """Generate a JSON export of the consolidated HR record.

    Args:
        hr_data: Consolidated HR data dict with sections as keys.
        completeness: Completeness report from check_completeness().
        employee_id: The employee's ID for metadata.

    Returns:
        Formatted JSON string.
    """
    generated_at = datetime.now(timezone.utc).isoformat()
    sections_status = completeness.get("sections", {})
    summary = completeness.get("summary", {})

    export_payload = {
        "metadata": {
            "generated_at": generated_at,
            "employee_id": employee_id,
            "export_version": "1.0",
            "completeness_summary": {
                "complete": summary.get("complete", []),
                "partial": summary.get("partial", []),
                "missing": summary.get("missing", []),
                "not_applicable": summary.get("not_applicable", []),
            },
        },
        "completeness": sections_status,
        "hr_record": hr_data,
    }

    return json.dumps(export_payload, indent=2, default=str)
