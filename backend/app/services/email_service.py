"""Email service using Resend for quote delivery.

This service provides email sending functionality for quote delivery to clients.
Uses the Resend Python SDK with lazy initialization and graceful error handling.

Key features:
- Lazy client initialization (only loads when RESEND_API_KEY available)
- Support for PDF and DOCX attachments
- Graceful error handling with detailed logging
- Configurable from_email and filename prefix
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_resend_client = None


def get_resend_client():
    """Lazy-init Resend client. Returns None if API key not configured.

    This pattern allows the service to be imported without requiring
    RESEND_API_KEY to be set, enabling graceful degradation.

    Returns:
        Resend module if API key is configured, None otherwise
    """
    global _resend_client
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        return None
    if _resend_client is None:
        import resend
        resend.api_key = api_key
        _resend_client = resend
    return _resend_client


async def send_quote_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: Optional[bytes] = None,
    docx_bytes: Optional[bytes] = None,
    from_email: str = "soumissions@toiturelv.com",
    filename_prefix: str = "Soumission"
) -> dict:
    """Send quote email with optional PDF and DOCX attachments.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body (HTML supported)
        pdf_bytes: Optional PDF attachment as bytes
        docx_bytes: Optional DOCX attachment as bytes
        from_email: Sender email (default: soumissions@toiturelv.com)
        filename_prefix: Attachment filename prefix (default: Soumission)

    Returns:
        Dict with 'id' field containing the Resend email ID

    Raises:
        RuntimeError: If RESEND_API_KEY not configured or send fails
    """
    client = get_resend_client()
    if client is None:
        raise RuntimeError("RESEND_API_KEY not configured")

    attachments = []
    if pdf_bytes:
        # Resend Python SDK accepts list of ints for attachment content
        attachments.append({
            "filename": f"{filename_prefix}.pdf",
            "content": list(pdf_bytes),
        })
    if docx_bytes:
        attachments.append({
            "filename": f"{filename_prefix}.docx",
            "content": list(docx_bytes),
        })

    params = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "html": body,
    }
    if attachments:
        params["attachments"] = attachments

    try:
        result = client.Emails.send(params)
        logger.info(f"Email sent to {to_email}, id={result.get('id', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        raise RuntimeError(f"Email send failed: {str(e)}")
