"""Export tools — exposes generate_pdf and generate_json as LangChain tools.

Files are stored in a module-level registry during tool execution.
The AgentExecutor reads the registry after the agent completes and emits
the file as a proper A2A FilePart artifact so the UI can offer a download.
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from hr_completeness import check_completeness
from hr_export import generate_json, generate_pdf

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-request file registry — keyed by context_id set before agent.stream()
# ---------------------------------------------------------------------------

_pending_files: dict[str, dict] = {}  # context_id -> {filename, mime_type, b64_bytes}


def get_pending_file(context_id: str) -> dict | None:
    """Return and clear the pending file for a given context_id."""
    return _pending_files.pop(context_id, None)


def set_context_id(context_id: str) -> None:
    """Called by AgentExecutor before streaming so tools know where to store."""
    _current_context_id.set(context_id)


# Use a simple module-level variable — single async execution per request
_current_context: dict[str, str] = {}  # maps "current" -> context_id


# ---------------------------------------------------------------------------
# Input schema
# ---------------------------------------------------------------------------

class ExportInput(BaseModel):
    hr_data_json: str = Field(
        description=(
            "The consolidated HR data serialized as a JSON string. "
            "Must be a JSON object with any of these keys: personal_info, employment, "
            "skills_profile, emergency_contacts, addresses, global_assignments. "
            "Example: '{\"personal_info\": {\"firstName\": \"Jane\"}, \"employment\": {...}}'"
        )
    )
    employee_id: str = Field(
        default="unknown",
        description="The employee's external person ID, used as the export filename.",
    )


def _parse_hr_data(hr_data_json: str) -> dict[str, Any]:
    if isinstance(hr_data_json, dict):
        return hr_data_json
    try:
        return json.loads(hr_data_json)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(f"hr_data_json is not valid JSON: {exc}") from exc


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _generate_pdf_tool(hr_data_json: str, employee_id: str = "unknown") -> str:
    try:
        hr_data = _parse_hr_data(hr_data_json)
        completeness = check_completeness(hr_data)
        pdf_bytes = generate_pdf(hr_data, completeness)
        b64 = base64.b64encode(pdf_bytes).decode("ascii")
        filename = f"hr-record-{employee_id}.pdf"

        # Store for AgentExecutor to pick up and emit as FilePart
        ctx_id = _current_context.get("current", "default")
        _pending_files[ctx_id] = {
            "filename": filename,
            "mime_type": "application/pdf",
            "b64_bytes": b64,
        }

        logger.info("PDF generated for %s (%d bytes), stored under ctx=%s", employee_id, len(pdf_bytes), ctx_id)
        return json.dumps({
            "status": "success",
            "filename": filename,
            "size_bytes": len(pdf_bytes),
            "message": f"PDF generated successfully ({len(pdf_bytes)} bytes). It will be attached for download.",
        })
    except Exception as exc:
        logger.exception("PDF generation failed")
        return json.dumps({"status": "error", "message": str(exc)})


def _generate_json_tool(hr_data_json: str, employee_id: str = "unknown") -> str:
    try:
        hr_data = _parse_hr_data(hr_data_json)
        completeness = check_completeness(hr_data)
        json_str = generate_json(hr_data, completeness, employee_id=employee_id)
        encoded = json_str.encode()
        b64 = base64.b64encode(encoded).decode("ascii")
        filename = f"hr-record-{employee_id}.json"

        ctx_id = _current_context.get("current", "default")
        _pending_files[ctx_id] = {
            "filename": filename,
            "mime_type": "application/json",
            "b64_bytes": b64,
        }

        logger.info("JSON generated for %s (%d bytes), stored under ctx=%s", employee_id, len(encoded), ctx_id)
        return json.dumps({
            "status": "success",
            "filename": filename,
            "size_bytes": len(encoded),
            "message": f"JSON generated successfully ({len(encoded)} bytes). It will be attached for download.",
        })
    except Exception as exc:
        logger.exception("JSON generation failed")
        return json.dumps({"status": "error", "message": str(exc)})


# ---------------------------------------------------------------------------
# Tool factory
# ---------------------------------------------------------------------------

def get_export_tools() -> list[StructuredTool]:
    return [
        StructuredTool(
            name="generate_hr_pdf",
            description=(
                "Generate a PDF document of the employee's HR record. "
                "Serialize all retrieved HR data as a JSON string and pass it as hr_data_json. "
                "Include all sections: personal_info, employment, skills_profile, "
                "emergency_contacts, addresses, global_assignments. "
                "After calling this tool, tell the user their PDF is ready and will be downloaded automatically."
            ),
            args_schema=ExportInput,
            func=_generate_pdf_tool,
        ),
        StructuredTool(
            name="generate_hr_json",
            description=(
                "Generate a JSON export of the employee's HR record. "
                "Serialize all retrieved HR data as a JSON string and pass it as hr_data_json. "
                "Include all sections: personal_info, employment, skills_profile, "
                "emergency_contacts, addresses, global_assignments. "
                "After calling this tool, tell the user their JSON export is ready and will be downloaded automatically."
            ),
            args_schema=ExportInput,
            func=_generate_json_tool,
        ),
    ]


# Legacy helper
def get_stored_file(filename: str):  # noqa: ANN001
    return None
