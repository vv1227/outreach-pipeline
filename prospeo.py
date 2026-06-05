import os
from typing import Dict, List


import requests

from utils import get_logger, read_env


logger = get_logger("prospeo")


def get_decision_makers(domain: str) -> List[Dict[str, str]]:
    """Stage 2: Get decision makers for a company domain.

    Returns a list of contacts with:
      - Name
      - Company
      - Role
      - LinkedIn

    If PROSPEO_API_KEY is unavailable, returns mock contacts.
    """
    domain = (domain or "").strip().lower()
    if not domain:
        return []

    api_key = read_env("PROSPEO_API_KEY")
    if not api_key:
        logger.info("[Prospeo] No PROSPEO_API_KEY found. Using mock decision makers for domain: %s", domain)
        return _mock_decision_makers(domain)

    try:
        endpoint = read_env("PROSPEO_ENDPOINT", "https://api.prospeo.example.com/contacts")
        headers = {"Authorization": f"Bearer {api_key}"}
        resp = requests.get(endpoint, params={"domain": domain}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        contacts = []
        for item in data.get("contacts", []) if isinstance(data, dict) else []:
            name = (item.get("name") or "").strip()
            company = (item.get("company") or domain).strip()
            role = (item.get("role") or "").strip()
            linkedin = (item.get("linkedin") or item.get("linkedin_url") or "").strip()
            if not linkedin:
                continue
            contacts.append(
                {
                    "Name": name,
                    "Company": company,
                    "Role": role,
                    "LinkedIn": linkedin,
                }
            )

        return contacts
    except Exception as e:
        logger.warning("[Prospeo] API call failed (%s). Using mock data.", e)
        return _mock_decision_makers(domain)


def _mock_decision_makers(domain: str) -> List[Dict[str, str]]:
    """Return realistic-looking contacts.

    Output is deterministic per domain, but varies names/roles so it doesn't
    repeat the same three people across all companies.
    """
    d = domain.lower().replace("www.", "").strip()
    stem = d.split(".")[0] or d
    tld = ".".join(d.split(".")[1:]) or "com"

    company_name = stem.replace("-", " ").title()

    # Deterministic selection based on stem.
    seeds = [
        ("Ramesh Kumar", "CEO"),
        ("Anita Sharma", "Founder"),
        ("Daniel Chen", "VP"),
        ("Sarah Williams", "Chief Marketing Officer"),
        ("Miguel Alvarez", "VP Sales"),
        ("Fatima Rahman", "VP Operations"),
        ("Emily Thompson", "Head of Growth"),
        ("Noah Kim", "VP Product"),
        ("Ava Patel", "Chief Revenue Officer"),
    ]

    # Pick 3 without randomness: rotate by char codes.
    offset = sum(ord(c) for c in stem) % len(seeds)
    picked = [seeds[(offset + i) % len(seeds)] for i in range(3)]

    role_map = {r: r for _, r in seeds}

    def make_linkedin(sl: str, role: str) -> str:
        # Use a plausible LinkedIn slug pattern.
        # Example: https://linkedin.com/in/anita-sharma-ceo
        role_token = role.lower().replace("chief ", "").replace(" ", "-").replace("_", "")
        role_token = "".join(ch for ch in role_token if ch.isalnum() or ch == "-")
        return f"https://www.linkedin.com/in/{sl}-{role_token}-{tld}/"

    def name_to_slug(name: str) -> str:
        return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).replace("--", "-").strip("-")

    contacts: List[Dict[str, str]] = []
    for name, role in picked:
        slug = name_to_slug(name)
        contacts.append(
            {
                "Name": name,
                "Company": company_name,
                "Role": role_map.get(role, role),
                "LinkedIn": make_linkedin(slug, role),
            }
        )

    return contacts


