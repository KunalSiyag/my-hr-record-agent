"""Email service — sends HR record exports via Brevo HTTP API (preferred)
or SMTP fallback.

Configuration (all via environment variables, never hardcoded):
  BREVO_API_KEY   Brevo API key (xkeysib-...). Uses HTTPS port 443,
                  works on corp networks where SMTP is filtered.
  SMTP_HOST       e.g. smtp-relay.brevo.com (Brevo), smtp.gmail.com, ...
  SMTP_PORT       default 587 (STARTTLS). Use 465 for implicit SSL,
                  2525 as Brevo alternate for blocked networks.
  SMTP_USER       login username
  SMTP_PASSWORD   login password / app password / Brevo SMTP key (xsmtps-...)
  SMTP_FROM       From address (defaults to SMTP_USER, must be verified in Brevo)
  SMTP_USE_TLS    "1"/"true" (default) for STARTTLS on port 587; "0" to disable

Send order: Brevo HTTP API if BREVO_API_KEY is set, else SMTP.
Uses stdlib (smtplib + email + urllib) so no new dependency is required.
"""

from __future__ import annotations

import logging
import os
import re
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_configured() -> bool:
    """True when Brevo API key or minimum SMTP settings are present."""
    if os.environ.get("BREVO_API_KEY"):
        return True
    return bool(os.environ.get("SMTP_HOST") and os.environ.get("SMTP_USER"))


def _sender_address() -> str:
    return os.environ.get("SMTP_FROM", "") or os.environ.get("SMTP_USER", "")


def _send_via_brevo_api(
    to_email: str,
    subject: str,
    body: str,
    attachments: list[tuple[str, bytes, str]] | None = None,
) -> dict:
    """Send via Brevo transactional HTTP API (port 443)."""
    import base64
    import json as _json
    import urllib.request

    api_key = os.environ.get("BREVO_API_KEY", "")
    sender = _sender_address()
    if not api_key:
        raise RuntimeError("BREVO_API_KEY is not set.")
    if not sender:
        raise RuntimeError(
            "Email sender is not configured: set SMTP_FROM (verified in Brevo)."
        )
    payload = {
        "sender": {"email": sender},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": body,
    }
    if attachments:
        payload["attachment"] = [
            {"content": base64.b64encode(raw).decode(), "name": name}
            for name, raw, _mime in attachments
        ]
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=_json.dumps(payload).encode(),
        headers={"api-key": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode(errors="replace")
    except Exception as exc:
        logger.exception("Brevo API send failed to %s", to_email)
        raise RuntimeError(f"Failed to send email via Brevo API: {exc}") from exc
    logger.info("Email sent to %s via Brevo API (%d attachment(s))",
                to_email, len(attachments or []))
    return {
        "status": "success",
        "to": to_email,
        "attachments": [a[0] for a in (attachments or [])],
        "provider": "brevo-api",
        "response": resp_body[:500],
    }


def _smtp_settings() -> dict:
    host = os.environ.get("SMTP_HOST", "")
    if not host:
        raise RuntimeError(
            "Email is not configured: set SMTP_HOST, SMTP_USER, SMTP_PASSWORD "
            "(and optionally SMTP_PORT / SMTP_FROM) as environment variables."
        )
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM", user)
    use_tls = os.environ.get("SMTP_USE_TLS", "1").lower() in ("1", "true", "yes")
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "sender": sender,
        "use_tls": use_tls,
    }


def validate_email(address: str) -> str:
    """Normalise + validate an email address. Raises ValueError if invalid."""
    address = (address or "").strip()
    if not _EMAIL_RE.match(address):
        raise ValueError(f"Invalid email address: {address!r}")
    return address


def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachments: list[tuple[str, bytes, str]] | None = None,
) -> dict:
    """Send an email with optional attachments.

    Args:
        to_email: recipient address.
        subject: email subject.
        body: plain-text body.
        attachments: list of (filename, raw_bytes, mime_type).

    Returns:
        {"status": "success", "to": ..., "attachments": [filenames]}.

    Raises:
        ValueError: on invalid recipient.
        RuntimeError: when SMTP is not configured or delivery fails.
    """
    to_email = validate_email(to_email)
    # Preferred path: Brevo HTTP API over 443 (works where SMTP is filtered).
    if os.environ.get("BREVO_API_KEY"):
        return _send_via_brevo_api(to_email, subject, body, attachments)
    cfg = _smtp_settings()

    msg = EmailMessage()
    msg["From"] = cfg["sender"]
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    for filename, raw_bytes, mime_type in attachments or []:
        maintype, _, subtype = (mime_type or "application/octet-stream").partition("/")
        msg.add_attachment(
            raw_bytes,
            maintype=maintype or "application",
            subtype=subtype or "octet-stream",
            filename=filename,
        )

    try:
        if cfg["port"] == 465:
            # Implicit SSL
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=30) as smtp:
                if cfg["user"]:
                    smtp.login(cfg["user"], cfg["password"])
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as smtp:
                smtp.ehlo()
                if cfg["use_tls"]:
                    smtp.starttls()
                    smtp.ehlo()
                if cfg["user"]:
                    smtp.login(cfg["user"], cfg["password"])
                smtp.send_message(msg)
    except Exception as exc:
        logger.exception("SMTP send failed to %s via %s", to_email, cfg["host"])
        raise RuntimeError(f"Failed to send email via {cfg['host']}: {exc}") from exc

    logger.info(
        "Email sent to %s via %s (%d attachment(s))",
        to_email,
        cfg["host"],
        len(attachments or []),
    )
    return {
        "status": "success",
        "to": to_email,
        "attachments": [a[0] for a in (attachments or [])],
    }
