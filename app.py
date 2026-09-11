# import os
# import time
# from dotenv import load_dotenv
# from google import genai

# # Load environment variables
# load_dotenv()

# # Get API key
# api_key = os.getenv("api_key")

# if not api_key:
#     print("ERROR: GEMINI_API_KEY not found!")
#     exit()

# # Create Gemini client
# client = genai.Client(api_key=api_key)

# # Models to try
# models = [
#     "gemini-3.7-flash",
#     "gemini-3.6-flash"
# ]

# print("=" * 50)
# print("        Gemini Interactive Chat")
# print("=" * 50)
# print("Type 'exit' to quit.")
# print("=" * 50)

# while True:

#     user_message = input("\nYou: ")

#     if user_message.lower() == "exit":
#         print("Gemini: Goodbye! 👋")
#         break

#     if not user_message.strip():
#         continue

#     success = False

#     for model in models:

#         try:
#             print(f"Gemini is thinking...")

#             response = client.models.generate_content(
#                 model=model,
#                 contents=user_message
#             )

#             print("\nGemini:", response.text)

#             success = True
#             break

#         except Exception as e:

#             error = str(e)

#             if "503" in error or "UNAVAILABLE" in error:
#                 print(f"Model {model} is busy. Trying another model...")
#                 time.sleep(2)
#                 continue

#             print("\nError:", error)
#             break

#     if not success:
#         print("\nGemini is currently unavailable.")
#         print("Please try again in a few seconds.")








from flask import Flask, request, jsonify
from flask_cors import CORS

from services.ai_services import analyze_message

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return jsonify({
        "message": "CyberShield AI API is running"
    })


@app.route("/api/analyze", methods=["POST"])
def analyze():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({
            "error": "Message is required"
        }), 400

    message = data["message"].strip()

    if not message:
        return jsonify({
            "error": "Message cannot be empty"
        }), 400

    try:

        result = analyze_message(message)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": "AI analysis failed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )