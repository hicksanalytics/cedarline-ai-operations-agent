# Publish Cedarline

1. At https://share.streamlit.io connect GitHub and create an app.
2. Repository: hicksanalytics/cedarline-ai-operations-agent. Branch: main. Entrypoint: streamlit_app.py. Choose Python 3.12.
3. Deploy. The dashboard works without any model credentials.
4. In app settings / Secrets, add AI_API_KEY, AI_BASE_URL, and AI_MODEL using .streamlit/secrets.toml.example. Choose an available tool-capable model. Never commit actual secrets. Configure model-provider quotas/budget; fees and availability depend on the account.
5. Test all three example questions. Confirm both tools run for the combined question, missing data is disclosed, and answers cite IDs. A live provider has not yet been tested in this build.
6. Copy the real deployed URL. Add a “Try Cedarline AI” link on hicksanalytics.com pointing to that URL. No invented subdomain or URL is configured by this project.

## Local Windows launch

Open the full project folder in VS Code, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

The application builds its synthetic database automatically. For live AI locally, copy the example to `.streamlit/secrets.toml` and fill it in locally. The original Ollama terminal agent remains in src/agent_local.py.

## Three-minute demo

Show company totals; switch profitability branch; inspect the missing-cost job; change collections date; ask for both reports; expand the tool trace; explain why calculations use SQL and why the model cannot send messages.

## Architecture

Streamlit → model tool request → validated allowlisted functions → SQLite → tool evidence → model explanation. Dashboard queries operate independently of AI.

The invoice report uses current synthetic balances and date-based aging, not historical payment reconstruction. Request caps are in-process and reset on restart. This demo is not a production service.
