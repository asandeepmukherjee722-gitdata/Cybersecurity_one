import os
import json
import requests

from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=api_key)


def create_prompt(message):
    return f"""
You are CyberShield AI, a cybersecurity threat analysis assistant.

Analyze the following message for phishing, scams, fraud, social engineering,
malicious links, impersonation, or other cybersecurity threats.

MESSAGE:
{message}

Return ONLY valid JSON using exactly this structure:

{{
    "risk_score": 0,
    "risk_level": "Safe",
    "threat_type": "None",
    "summary": "Short explanation",
    "red_flags": [
        "reason 1",
        "reason 2",
        "reason 3"
    ],
    "recommended_actions": [
        "action 1",
        "action 2",
        "action 3"
    ]
}}

Rules:
- risk_score must be between 0 and 100.
- risk_level must be exactly Safe, Suspicious, or Dangerous.
- Do not claim certainty when evidence is insufficient.
- Explain why the message appears suspicious or safe.
- Never request passwords, OTPs, banking details, or other secrets.
- Focus on cybersecurity awareness.
"""


def clean_json(text):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    return json.loads(text)


def analyze_with_gemini(message):

    print("Trying Gemini...")

    prompt = create_prompt(message)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    result = clean_json(response.text)

    print("Gemini analysis successful.")

    return result


def analyze_with_ollama(message):

    print("Gemini unavailable. Switching to Ollama...")

    prompt = create_prompt(message)

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    result = clean_json(data["response"])

    print("Ollama analysis successful.")

    return result


def analyze_message(message):

    # PRIMARY: Gemini
    try:
        return analyze_with_gemini(message)

    except Exception as gemini_error:

        print(f"Gemini failed: {gemini_error}")

        # FALLBACK: Ollama
        try:
            return analyze_with_ollama(message)

        except Exception as ollama_error:

            print(f"Ollama failed: {ollama_error}")

            raise Exception(
                f"Both AI systems failed. "
                f"Gemini: {gemini_error} | "
                f"Ollama: {ollama_error}"
            )