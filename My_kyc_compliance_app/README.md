# KYC Compliance Dashboard

A demonstration Know Your Customer (KYC) workflow dashboard built with Python, Streamlit, and SQLite. It uses synthetic sample records only; do not enter real customer or identity data.

## Features
- Customer register with name/email search and customer creation
- Risk-level and beneficial-owner fields
- Document register with verification status and expiry dates
- KYC review decisions: Pending, Approved, Rejected, Review
- Document expiry alerts (next 90 days)
- Audit history for customer and review actions
- SQLite persistence

## Requirements
- Python 3.10+
- pip

## Run locally
```bash
git clone <YOUR_PUBLIC_REPOSITORY_URL>
cd kyc_compliance_app
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```
Open the local URL printed by Streamlit (usually http://localhost:8501).

## Run tests
```bash
python -m pytest -q
```

## Project structure
```text
.
├── app.py
├── schema.sql
├── validate_data.py
├── requirements.txt
├── README.md
└── tests/
    └── test_validation.py
```

## Notes and limitations
This is an educational prototype, not a production KYC platform. It does not connect to identity providers, sanctions/PEP databases, or regulatory systems. Risk levels are user-entered rather than automatically determined. Production deployment would require authentication, authorization, encryption, secure secrets management, retention controls, robust audit immutability, and jurisdiction-specific compliance review.
