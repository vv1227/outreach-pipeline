from typing import Dict, Optional

import requests

from utils import get_logger, read_env


logger = get_logger("brevo")


def _build_personalized_email(email: str, name: str, company: str) -> str:
    # Minimal, template-style personalization (no external content fetching).
    return (
        f"Hi {name},\n\n"
        f"I came across {company} and wanted to share a quick idea that could help your team. "
        f"We’ve been helping similar companies streamline outbound outreach and improve reply rates.\n\n"
        "If it’s useful, I can send a short overview and a couple of examples tailored to your business.\n\n"
        "Would you be open to a 10-minute chat next week?\n\n"
        "Best regards,\n"
        "Automated Outreach Pipeline"
    )


def send_email(email: str, name: str, company: str) -> Dict[str, str]:
    """Stage 4: Send outreach email using Brevo if BREVO_API_KEY exists.

    Returns dict:
      - Status: success/failed/simulated
      - Message: provider response or simulated message
    """
    api_key = read_env("BREVO_API_KEY")
    subject = read_env(
        "BREVO_EMAIL_SUBJECT",
        "Quick question about improving outbound outreach",
    )

    body = _build_personalized_email(email=email, name=name, company=company)

    if not api_key:
        logger.info("[Brevo] No BREVO_API_KEY found. Simulating send to %s (%s)", name, email)
        return {
            "Status": "simulated",
            "Message": f"Simulated send to {email} for {name} at {company}",
        }

    try:
        endpoint = read_env("BREVO_ENDPOINT", "https://api.brevo.com/v3/smtp/email")
        headers = {"api-key": api_key, "content-type": "application/json"}
        payload = {
            "sender": {
                "name": read_env("BREVO_SENDER_NAME", "Outreach Team"),
                "email": read_env("BREVO_SENDER_EMAIL"),
            },
            "to": [{"email": email, "name": name}],
            "subject": subject,
            "htmlContent": f"<pre style='font-family: inherit'>{body}</pre>",
        }

        # BREVO requires sender email; fail fast with a clearer message.
        if not payload["sender"]["email"]:
            return {
                "Status": "failed",
                "Message": "BREVO_SENDER_EMAIL is missing in .env",
            }

        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return {
            "Status": "success",
            "Message": f"Brevo accepted message for {email}.",
        }
    except Exception as e:
        logger.exception("[Brevo] Send failed: %s", e)
        return {
            "Status": "failed",
            "Message": str(e),
        }

