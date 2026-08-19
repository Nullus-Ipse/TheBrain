import traceback
from dotenv import load_dotenv
load_dotenv()

# ---- STEP 1: raw generateContent with the app's EXACT payload ----
import requests
from core.config import (
    GOOGLE_API_KEY, GEMINI_PRIMARY_MODEL, GEMINI_API_BASE,
    TEMPERATURE, MAX_OUTPUT_TOKENS,
)

url = f"{GEMINI_API_BASE}/models/{GEMINI_PRIMARY_MODEL}:generateContent"
payload = {
    "contents": [{"role": "user", "parts": [{"text": 'Return exactly this JSON: {"ok": true}'}]}],
    "generationConfig": {
        "temperature": TEMPERATURE,
        "maxOutputTokens": MAX_OUTPUT_TOKENS,
        "responseMimeType": "application/json",
    },
}
r = requests.post(url, params={"key": GOOGLE_API_KEY}, json=payload, timeout=30)
print("STEP1 STATUS:", r.status_code)
print(r.text[:600])
print()

# ---- STEP 2: the app's real pipeline, error visible ----
from core.prompt_selector import choose_cognitive_outcome
from core.prompts import build_prompt
from core.gemini_client import generate_json_from_gemini
from core.json_validator import validate_thought_json

outcome = choose_cognitive_outcome()
print("chosen outcome:", outcome)
try:
    prompt = build_prompt("Should I buy a new car?", outcome)
    raw = generate_json_from_gemini(prompt)
    print("STEP2 RAW GEMINI:", raw[:600])
    result = validate_thought_json(raw, expected_ending_type=outcome["ending_type"])
    print("STEP2 OK — validated ending:", result.ending.type)
except Exception:
    traceback.print_exc()