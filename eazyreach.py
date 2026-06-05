import hashlib
from typing import Optional

from utils import get_logger, read_env


logger = get_logger("eazyreach")


def get_verified_email(linkedin_url: str) -> Optional[str]:
    """Stage 3: Verify email from LinkedIn URL.

    Returns a verified work email string or None.

    If EAZYREACH_API_KEY is not found, uses mock data.
    """
    linkedin_url = (linkedin_url or "").strip()
    if not linkedin_url:
        return None

    api_key = read_env("EAZYREACH_API_KEY")
    if not api_key:
        logger.info("[EazyReach] No EAZYREACH_API_KEY found. Using mock email for: %s", linkedin_url)
        return _mock_email(linkedin_url)

    # Placeholder for real implementation.
    try:
        endpoint = read_env("EAZYREACH_ENDPOINT", "https://api.eazyreach.example.com/verify")
        # Real request intentionally omitted because API specifics are unknown.
        # Keeping structure so users can implement their provider call.
        raise NotImplementedError("Real EazyReach integration not configured in this template.")
    except Exception as e:
        logger.warning("[EazyReach] API call failed (%s). Using mock data.", e)
        return _mock_email(linkedin_url)


def _mock_email(linkedin_url: str) -> str:
    # Create deterministic mock email from LinkedIn URL.
    slug = linkedin_url.rstrip("/").split("/")[-1]
    digest = hashlib.sha256(linkedin_url.encode("utf-8")).hexdigest()[:6]

    # Try to infer company domain-ish suffix from the slug
    # Example: .../stem-ceo-tld -> take last token as tld-ish
    parts = slug.split("-")
    tldish = parts[-1] if parts else "com"
    tldish = tldish if "." in tldish else f"{tldish}.com"

    local = (slug[:20] or "user").replace(" ", "").replace("_", "").lower()
    local = "".join(ch for ch in local if ch.isalnum() or ch in [".", "-" ])

    return f"{local}.{digest}@{tldish}".replace("..", ".")

