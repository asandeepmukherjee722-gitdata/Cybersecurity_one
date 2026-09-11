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


# def analyze_message(message):

#     # PRIMARY: Gemini
#     try:
#         return analyze_with_gemini(message)

#     except Exception as gemini_error:

#         print(f"Gemini failed: {gemini_error}")

#         # FALLBACK: Ollama
#         try:
#             return analyze_with_ollama(message)

#         except Exception as ollama_error:

#             print(f"Ollama failed: {ollama_error}")

#             raise Exception(
#                 f"Both AI systems failed. "
#                 f"Gemini: {gemini_error} | "
#                 f"Ollama: {ollama_error}"
#             )

def analyze_message(message):

    # 1. PRIMARY: Gemini
    try:
        return analyze_with_gemini(message)

    except Exception as gemini_error:

        print(f"Gemini failed: {gemini_error}")

    # 2. SECONDARY: Ollama
    # Works when running locally, but usually unavailable on Render
    try:
        return analyze_with_ollama(message)

    except Exception as ollama_error:

        print(f"Ollama failed: {ollama_error}")

    # 3. FINAL FALLBACK: Deterministic cybersecurity analysis
    print("Using rule-based cybersecurity fallback...")

    text = message.lower()

    score = 0
    red_flags = []

    # Urgency
    urgency_words = [
        "urgent",
        "immediately",
        "now",
        "as soon as possible",
        "within 24 hours",
        "act now"
    ]

    if any(word in text for word in urgency_words):
        score += 25
        red_flags.append(
            "Urgent or pressure-based language"
        )

    # Threats
    threat_words = [
        "blocked",
        "suspended",
        "closed",
        "terminated",
        "deactivated",
        "will be blocked"
    ]

    if any(word in text for word in threat_words):
        score += 25
        red_flags.append(
            "Threat of account suspension or negative consequences"
        )

    # Links
    if "http://" in text or "https://" in text or "click" in text or "link" in text:
        score += 25
        red_flags.append(
            "Requests the user to click or interact with a link"
        )

    # Financial/account related
    financial_words = [
        "bank",
        "account",
        "payment",
        "credit card",
        "debit card",
        "upi",
        "money",
        "transaction"
    ]

    if any(word in text for word in financial_words):
        score += 15
        red_flags.append(
            "Financial or account-related context"
        )

    # Prize/scam language
    scam_words = [
        "won",
        "winner",
        "prize",
        "reward",
        "lottery",
        "claim"
    ]

    if any(word in text for word in scam_words):
        score += 20
        red_flags.append(
            "Unexpected prize or reward claim"
        )

    score = min(score, 100)

    # Determine level
    if score >= 70:
        risk_level = "Dangerous"
    elif score >= 35:
        risk_level = "Suspicious"
    else:
        risk_level = "Safe"

    # Determine threat type
    if score >= 70:
        threat_type = "Phishing / Scam"
    elif score >= 35:
        threat_type = "Potential Social Engineering"
    else:
        threat_type = "None"

    # Ensure we always have useful red flags
    if not red_flags:
        red_flags = [
            "No major phishing indicators detected"
        ]

    if risk_level == "Dangerous":
        summary = (
            "This message contains multiple indicators commonly "
            "associated with phishing or social engineering. "
            "The combination of urgency, suspicious requests, "
            "or threats should be treated with caution."
        )
    elif risk_level == "Suspicious":
        summary = (
            "This message contains some characteristics that "
            "may indicate a phishing or social engineering attempt. "
            "Verify the message through an official source before acting."
        )
    else:
        summary = (
            "No strong phishing indicators were detected in this message. "
            "However, users should still verify unexpected requests "
            "through official channels."
        )

    recommended_actions = [
        "Do not click suspicious links or interact with unexpected requests.",
        "Verify the message using the organization's official website or app.",
        "Never share passwords, OTPs, banking details, or other sensitive information."
    ]

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "threat_type": threat_type,
        "summary": summary,
        "red_flags": red_flags[:5],
        "recommended_actions": recommended_actions
    }