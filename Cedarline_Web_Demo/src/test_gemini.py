import os
from google import genai

key = os.environ.get("GEMINI_API_KEY")

if not key:
    raise SystemExit("GEMINI_API_KEY is missing in this terminal.")

with genai.Client(api_key=key) as client:
    print("Checking Gemini connection...\n")

    for model in client.models.list():
        if "flash" in (model.name or "").lower():
            print(model.name)

    print("\nModel listing succeeded.")
    