# Automated Outreach Pipeline (CLI)

A modular Python CLI that runs an automated outreach workflow.

When API keys are not configured, the pipeline uses mock data and simulates sending.

---

## Workflow

Input Company Domain
        ↓
Find Similar Companies
        ↓
Find Decision Makers
        ↓
Verify Emails
        ↓
Export Contacts to CSV
        ↓
User Confirmation
        ↓
Send Personalized Emails

---

## Features

- Modular architecture
- CSV export
- Email deduplication
- Progress logging
- User confirmation before sending
- Mock provider fallback when API keys are unavailable

---

## Project Structure
- `main.py` - CLI entry point and orchestration
- `ocean.py` - `get_similar_companies(domain)`
- `prospeo.py` - `get_decision_makers(domain)`
- `eazyreach.py` - `get_verified_email(linkedin_url)`
- `brevo.py` - `send_email(email, name, company)`
- `utils.py` - logging + CSV export + helpers

---

## Setup


### 1) Create and activate a virtual environment (recommended)
**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Configure environment variables
Create a `.env` file (a template is included as guidance below):
```env
# Optional API keys (if absent, mock/simulated mode is used)
OCEAN_API_KEY=
PROSPEO_API_KEY=
EAZYREACH_API_KEY=
BREVO_API_KEY=

# Optional endpoints (placeholders)
OCEAN_ENDPOINT=https://api.ocean.example.com/similar
PROSPEO_ENDPOINT=https://api.prospeo.example.com/contacts
EAZYREACH_ENDPOINT=https://api.eazyreach.example.com/verify
BREVO_ENDPOINT=https://api.brevo.com/v3/smtp/email

# Brevo email settings (required for real sending)
BREVO_SENDER_EMAIL=
BREVO_SENDER_NAME=Outreach Team
BREVO_EMAIL_SUBJECT=Quick question about improving outbound outreach
```

---

## Run
```powershell
python main.py
```

- Enter a company domain (e.g., `acme.com`)
- The tool will:
  - run all stages
  - export results to `results.csv`
  - show a summary
  - ask for confirmation before sending:

`Continue? (y/n)`

---

## Output
- `results.csv`

Columns:
- `Name`, `Company`, `LinkedIn`, `Email`, `Status`

---

## Notes
- Real integrations for Ocean/Prospeo/EazyReach are left as placeholders (API specifics vary). 
- The app is designed to be modular: you can replace the provider sections with your actual API calls.

