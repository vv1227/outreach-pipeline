import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


def get_logger(name: str = "outreach") -> logging.Logger:
    """Create a logger with console output.

    Logging is kept simple for CLI usage.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def now_utc_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def safe_json_loads(s: Any) -> Optional[Dict[str, Any]]:
    if s is None:
        return None
    if isinstance(s, dict):
        return s
    try:
        return json.loads(s)
    except Exception:
        return None


def dedupe_contacts_by_email(contacts: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate list of contact dicts using Email as the key."""
    seen = set()
    out: List[Dict[str, Any]] = []
    for c in contacts:
        email = (c.get("Email") or "").strip().lower()
        if not email or email in seen:
            continue
        seen.add(email)
        out.append(c)
    return out


def export_contacts_to_csv(contacts: List[Dict[str, Any]], out_path: str = "results.csv") -> None:
    """Export contacts to CSV using the required column names."""
    columns = ["Name", "Company", "LinkedIn", "Email", "Status"]

    rows: List[Dict[str, Any]] = []
    for c in contacts:
        rows.append(
            {
                "Name": c.get("Name", ""),
                "Company": c.get("Company", ""),
                "LinkedIn": c.get("LinkedIn", ""),
                "Email": c.get("Email", ""),
                "Status": c.get("Status", ""),
            }
        )

    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(out_path, index=False, encoding="utf-8")


def read_env(name: str, default: str = "") -> str:
    """Helper to read environment variables with a default."""
    return os.environ.get(name, default)

