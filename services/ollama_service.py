import requests

def analyze_with_ollama(message):

    prompt = f"""
You are a cybersecurity assistant.

Analyze this message for phishing or scam indicators.

MESSAGE:
{message}

Give:
- Risk score from 0 to 100
- Risk level: Safe, Suspicious, or Dangerous
- Threat type
- Short explanation
- Red flags
- Recommended actions
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    response.raise_for_status()

    return response.json()["response"]