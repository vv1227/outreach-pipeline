import os
from typing import Dict, List

from dotenv import load_dotenv

from brevo import send_email
from eazyreach import get_verified_email
from ocean import get_similar_companies
from prospeo import get_decision_makers
from utils import (
    dedupe_contacts_by_email,
    export_contacts_to_csv,
    get_logger,
    now_utc_iso,
)


logger = get_logger("main")


def _print_progress(msg: str) -> None:
    logger.info(msg)


def _collect_contacts(similar_companies: List[str]) -> List[Dict[str, str]]:
    contacts: List[Dict[str, str]] = []
    for idx, company_domain in enumerate(similar_companies, start=1):
        _print_progress(f"Stage 2 | ({idx}/{len(similar_companies)}) Getting decision makers for {company_domain}")
        try:
            makers = get_decision_makers(company_domain)
        except Exception as e:
            logger.warning("Stage 2 failed for %s: %s", company_domain, e)
            makers = []

        for m in makers:
            contacts.append(
                {
                    "Name": m.get("Name", ""),
                    "Company": m.get("Company", ""),
                    "LinkedIn": m.get("LinkedIn", ""),
                    "Email": "",
                    "Status": "pending_email_verification",
                }
            )

    return contacts


def _verify_emails(contacts: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for i, c in enumerate(contacts, start=1):
        linkedin = c.get("LinkedIn", "")
        _print_progress(f"Stage 3 | ({i}/{len(contacts)}) Verifying email for {c.get('Name','')} ({linkedin})")
        try:
            email = get_verified_email(linkedin)
        except Exception as e:
            logger.warning("Stage 3 failed for %s: %s", linkedin, e)
            email = None

        status = "email_verified" if email else "email_not_found"
        c2 = dict(c)
        c2["Email"] = email or ""
        c2["Status"] = status
        out.append(c2)
    return out


def _show_summary(contacts: List[Dict[str, str]]) -> None:
    total = len(contacts)
    verified = sum(1 for c in contacts if c.get("Email"))
    _print_progress("\n===== Summary =====")
    _print_progress(f"Total contacts: {total}")
    _print_progress(f"Verified emails: {verified}")

    preview = contacts[:10]
    if preview:
        _print_progress("Preview (up to 10):")
        for c in preview:
            logger.info(
                "- %s | %s | %s | %s | %s",
                c.get("Name", ""),
                c.get("Company", ""),
                c.get("LinkedIn", ""),
                c.get("Email", ""),
                c.get("Status", ""),
            )


def main() -> None:
    load_dotenv()

    _print_progress(f"Start | {now_utc_iso()}")

    domain = input("Enter company domain (e.g., acme.com): ").strip()
    if not domain:
        logger.error("No domain provided. Exiting.")
        return

    _print_progress(f"Stage 1 | Finding similar companies for {domain}")
    try:
        similar_companies = get_similar_companies(domain)
    except Exception as e:
        logger.exception("Stage 1 failed: %s", e)
        similar_companies = []

    if not similar_companies:
        logger.warning("No similar companies found. Exiting.")
        return

    _print_progress(f"Stage 1 | Found {len(similar_companies)} similar companies")

    contacts = _collect_contacts(similar_companies)
    if not contacts:
        logger.warning("No decision makers found. Exiting.")
        return

    contacts = _verify_emails(contacts)
    contacts = [c for c in contacts if (c.get("Email") or "").strip()]

    # Dedupe by email
    contacts = dedupe_contacts_by_email(contacts)

    # Export results
    export_contacts_to_csv(contacts, out_path="results.csv")
    _print_progress("Exported results to results.csv")

    # Display summary
    _show_summary(contacts)

    # Confirmation gate
    while True:
        cont = input("Continue? (y/n): ").strip().lower()
        if cont in {"y", "yes"}:
            break
        if cont in {"n", "no"}:
            _print_progress("Sending cancelled by user. Exiting.")
            return
        _print_progress("Please enter 'y' or 'n'.")

    # Send emails
    _print_progress("\n===== Sending Emails =====")
    for i, c in enumerate(contacts, start=1):
        email = c.get("Email", "")
        name = c.get("Name", "")
        company = c.get("Company", "")
        _print_progress(f"Send | ({i}/{len(contacts)}) {name} <{email}>")
        try:
            result = send_email(email=email, name=name, company=company)
            c["Status"] = result.get("Status", c.get("Status", ""))
        except Exception as e:
            logger.warning("Send failed for %s: %s", email, e)
            c["Status"] = "send_failed"

    # Re-export with updated statuses
    export_contacts_to_csv(contacts, out_path="results.csv")
    _print_progress("Done. Updated results.csv with send status.")


if __name__ == "__main__":
    main()

