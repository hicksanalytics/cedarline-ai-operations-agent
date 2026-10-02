# Cedarline AI Operations Demo

Interactive synthetic HVAC profitability and collections dashboard with optional live tool-calling AI. Built by Ben Hicks / Hicks Analytics.

Start with [DEPLOYMENT.md](DEPLOYMENT.md) for local launch and Streamlit publishing. Entry point: `streamlit_app.py`. Python 3.12 recommended.

Validation: five unittest checks passed, including simulated Streamlit branch/date changes, financial evidence, mocked tool orchestration, rejection of unsupported answers, and invalid tool dates. Live hosted model calls and public deployment have not been tested.

Run tests from the project root: `python -m unittest discover -s tests -v`.

The data folder contains all required CSVs. Database initialization is automatic. No API secrets are included. AI is visibly disabled until configured.
