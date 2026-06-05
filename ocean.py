import os
from typing import List

import requests

from utils import get_logger, read_env


logger = get_logger("ocean")


def get_similar_companies(domain: str) -> List[str]:
    """Stage 1: Find similar companies.

    If OCEAN_API_KEY is present, this function would call the real API.
    For now, when no API key exists, it returns mock data.

    Returns: list of company domains.
    """
    domain = (domain or "").strip().lower()
    if not domain:
        return []

    api_key = read_env("OCEAN_API_KEY")
    if not api_key:
        logger.info("[Ocean] No OCEAN_API_KEY found. Using mock similar companies for domain: %s", domain)
        return _mock_similar_domains(domain)

    # Placeholder for real implementation.
    # Keeping it robust and non-breaking while API specifics are unknown.
    try:
        endpoint = read_env("OCEAN_ENDPOINT", "https://api.ocean.example.com/similar")
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(endpoint, params={"domain": domain}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Expected shape (example): {"domains": ["a.com", "b.com"]}
        domains = data.get("domains") or []
        domains = [str(d).strip().lower() for d in domains if d]
        return domains
    except Exception as e:
        logger.warning("[Ocean] API call failed (%s). Using mock data.", e)
        return _mock_similar_domains(domain)


def _mock_similar_domains(domain: str) -> List[str]:
    """Return more realistic similar-company domains.

    This is deterministic and uses a small mapping for common brands,
    otherwise falls back to a generic pattern.
    """
    d = domain.lower().replace("www.", "").strip()

    known: Dict[str, List[str]] = {
        "zoho.com": [
            "freshworks.com",
            "chargebee.com",
            "kissflow.com",
            "zendesk.com",
            "hubspot.com",
        ],
        "salesforce.com": [
            "monday.com",
            "dynamics.com",
            "pipedrive.com",
            "workday.com",
            "sap.com",
        ],
        "hubspot.com": [
            "salesloft.com",
            "marketo.com",
            "pardot.com",
            "activecampaign.com",
            "intercom.com",
        ],
        "stripe.com": [
            "paypal.com",
            "adyen.com",
            "squareup.com",
            "checkout.com",
            "braintreepayments.com",
        ],
    }

    # If exact match exists, use it.
    if d in known:
        return known[d]

    # Otherwise, infer by second-level domain.
    sld = d.split(".")[0]
    suffix = ".".join(d.split(".")[1:]) or "com"

    # Generic but more plausible alternatives.
    # (Using common SaaS-like naming rather than prefix-based domains.)
    generic: List[str] = [
        f"{sld}-crm.{suffix}",
        f"{sld}-support.{suffix}",
        f"{sld}-automation.{suffix}",
        f"{sld}-analytics.{suffix}",
        f"{sld}-security.{suffix}",
    ]

    return generic


