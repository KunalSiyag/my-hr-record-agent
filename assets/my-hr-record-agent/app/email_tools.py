"""Email tool — exposes send_hr_record_email as a LangChain tool.

The tool either:
  (a) attaches an already-generated file from _file_store (by filename), or
  (b) generates the PDF/JSON on the fly from hr_data_json and emails it.

This keeps one conversational step: "Email my HR record to me@x.com".
"""

from __future__ import annotations

import json
import logging
from typing import Literal

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import email_service
from export_tools import _file_store, _parse_hr_data
from hr_completeness import check_completeness
from hr_export import generate_json, generate_pdf

logger = logging.getLogger(__name__)


class EmailInput(BaseModel):
    to_email: str = Field(description="Recipient email address, e.g. 'alex@example.com'.")
    hr_data_json: str = Field(
        default="",
        description=(
            "Consolidated HR data as a JSON string (same shape as generate_hr_pdf). "
            "Required unless 'filename' names an already-generated file."
        ),
    )
    filename: str = Field(
        default="",
        description=(
            "Optional name of an already-generated file (e.g. 'hr-record-EMP001.pdf') "
            "to attach instead of generating a new one."
        ),
    )
    employee_id: str = Field(default="unknown", description="Employee ID for filename/metadata.")
    file_format: Literal["pdf", "json"] = Field(
        default="pdf", description="Export format to generate and attach ('pdf' or 'json')."
    )


def _send_hr_record_email_tool(
    to_email: str,
    hr_data_json: str = "",
    filename: str = "",
    employee_id: str = "unknown",
    file_format: str = "pdf",
) -> str:
    try:
        to_email = email_service.validate_email(to_email)

        # (a) Reuse an already-generated file if requested and present.
        stored = _file_store.get(filename) if filename else None
        if stored:
            raw_bytes: bytes = stored["bytes"]
            mime: str = stored.get("mime", "application/octet-stream")
            attach_name = filename
        else:
            # (b) Generate on the fly — hr_data_json is required here.
            if not hr_data_json:
                return json.dumps({
                    "status": "error",
                    "message": (
                        "No file to send: generate the HR record first "
                        "(generate_hr_pdf / generate_hr_json) or pass hr_data_json."
                    ),
                })
            hr_data = _parse_hr_data(hr_data_json)
            completeness = check_completeness(hr_data)
            if (file_format or "pdf").lower() == "json":
                encoded = generate_json(hr_data, completeness, employee_id=employee_id).encode()
                raw_bytes, mime = encoded, "application/json"
                attach_name = filename or f"hr-record-{employee_id}.json"
            else:
                raw_bytes = generate_pdf(hr_data, completeness)
                mime = "application/pdf"
                attach_name = filename or f"hr-record-{employee_id}.pdf"
            # Cache so /download serves the same bytes.
            _file_store[attach_name] = {"bytes": raw_bytes, "mime": mime}

        subject = f"My HR Record — {employee_id}"
        body = (
            f"Hello,\n\nAttached is the requested HR record export ({attach_name}).\n"
            f"If you did not request this, please contact HR.\n"
        )
        result = email_service.send_email(to_email, subject, body, [(attach_name, raw_bytes, mime)])
        logger.info("[M5.achieved]: export delivered — formats=[email:%s]", attach_name)
        return json.dumps({
            "status": "success",
            "to": result["to"],
            "filename": attach_name,
            "size_bytes": len(raw_bytes),
            "message": f"HR record sent to {result['to']} as {attach_name}.",
        })
    except ValueError as exc:
        return json.dumps({"status": "error", "message": str(exc)})
    except RuntimeError as exc:
        logger.warning("[M5.missed]: export was not generated or delivered — reason=[%s]", exc)
        return json.dumps({"status": "error", "message": str(exc)})
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Email export failed")
        return json.dumps({"status": "error", "message": str(exc)})


def get_email_tools() -> list[StructuredTool]:
    return [
        StructuredTool(
            name="send_hr_record_email",
            description=(
                "Email the employee's HR record PDF/JSON to an address. "
                "Pass to_email plus EITHER hr_data_json (to generate+send) "
                "OR filename of an already-generated file. "
                "Use file_format 'pdf' (default) or 'json'. "
                "Always confirm the recipient address with the user first, "
                "and after success tell them the file was emailed and to which address."
            ),
            args_schema=EmailInput,
            func=_send_hr_record_email_tool,
        ),
    ]
