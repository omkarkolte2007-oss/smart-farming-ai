"""
SmartFarm AI — Flask Backend
Serves the frontend static files AND provides a REST API that
accepts farmer details and returns AI-generated farming advice
using the Groq LLM API.

Run:  python app.py
Then open:  http://127.0.0.1:5000
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq

# Load .env file (GROQ_API_KEY lives there — never hard-code secrets)
load_dotenv()

# ──────────────────────────────────────────────
# Paths — works both locally and on Render
# ──────────────────────────────────────────────
# Local:  project root is smart-farming/  → frontend is ../frontend  relative to backend/
# Render: rootDir is backend/             → frontend is ../frontend  relative to backend/
#         BUT Render clones the whole repo, so parent.parent still resolves correctly.
# We check both locations and use whichever exists.
_here = Path(__file__).resolve().parent          # .../backend/
_candidate_up   = _here.parent / "frontend"      # .../smart-farming/frontend  (local + Render)
_candidate_same = _here / "frontend"             # .../backend/frontend  (fallback)
FRONTEND_DIR = _candidate_up if _candidate_up.exists() else _candidate_same

# ──────────────────────────────────────────────
# App setup — serve static files from frontend/
# ──────────────────────────────────────────────
app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)  # kept for dev flexibility

# Groq API key — read from .env (see .env.example for setup instructions)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set. Copy .env.example to .env and add your key.")

# Raise timeout to 60 s — default is too short on some networks
client = Groq(api_key=GROQ_API_KEY, timeout=60.0)

# llama3-8b-8192 was decommissioned in 2025 — use the current recommended model
LLM_MODEL = "llama-3.1-8b-instant"


# ──────────────────────────────────────────────
# Helper: build the AI prompt
# ──────────────────────────────────────────────
def build_prompt(farmer_name: str, location: str, crop: str,
                 soil_type: str, season: str, question: str) -> str:
    """
    Constructs a detailed system + user prompt for the LLM so it
    behaves as a knowledgeable agricultural advisor.
    """
    system_prompt = (
        "You are an expert agricultural advisor with deep knowledge in agronomy, "
        "soil science, crop management, pest control, irrigation, and organic farming. "
        "Provide practical, actionable, and easy-to-understand farming advice. "
        "Structure your response clearly using sections like 'Possible Causes:', "
        "'Suggested Solutions:', 'Fertilizer Tips:', 'Irrigation Tips:', and "
        "'Organic Alternatives:' wherever relevant. "
        "Use bullet points (starting with '- ') for lists. "
        "Always recommend consulting a local agricultural expert for serious issues. "
        "End every response with: 'Happy Farming! 🌱'"
    )

    user_prompt = (
        f"Farmer Name : {farmer_name}\n"
        f"Location    : {location}\n"
        f"Crop        : {crop}\n"
        f"Soil Type   : {soil_type}\n"
        f"Season      : {season}\n\n"
        f"Question    : {question}\n\n"
        "Please provide detailed, practical farming advice based on the above information."
    )

    return system_prompt, user_prompt


# Print resolved path at startup so Render logs show it clearly
import sys
print(f"[SmartFarm] FRONTEND_DIR = {FRONTEND_DIR}", flush=True)
print(f"[SmartFarm] index.html exists = {(FRONTEND_DIR / 'index.html').exists()}", flush=True)


# ──────────────────────────────────────────────
# Route: GET /  → serve the frontend
# ──────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    """Serve the frontend index.html from the ../frontend directory."""
    if not (FRONTEND_DIR / "index.html").exists():
        return f"ERROR: index.html not found at {FRONTEND_DIR}", 500
    return send_from_directory(str(FRONTEND_DIR), "index.html")


# ──────────────────────────────────────────────
# Route: GET /status  → JSON health-check
# ──────────────────────────────────────────────
@app.route("/status", methods=["GET"])
def status():
    """JSON health-check — returns application status."""
    return jsonify({
        "status" : "running",
        "app"    : "SmartFarm AI API",
        "version": "1.0.0"
    })


# ──────────────────────────────────────────────
# Route: POST /advice
# ──────────────────────────────────────────────
@app.route("/advice", methods=["POST"])
def get_advice():
    """
    Accepts farmer details + question and returns AI-generated farming advice.

    Expected JSON body:
    {
        "farmerName": "...",
        "location"  : "...",
        "crop"      : "...",
        "soilType"  : "...",
        "season"    : "...",
        "question"  : "..."
    }

    Returns:
    {
        "success": true,
        "advice" : "..."
    }
    """

    # ── Parse & validate request body ──────────
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body."}), 400

    required_fields = ["farmerName", "location", "crop", "soilType", "season", "question"]
    missing = [f for f in required_fields if not data.get(f, "").strip()]
    if missing:
        return jsonify({
            "success": False,
            "error"  : f"Missing required fields: {', '.join(missing)}"
        }), 422

    farmer_name = data["farmerName"].strip()
    location    = data["location"].strip()
    crop        = data["crop"].strip()
    soil_type   = data["soilType"].strip()
    season      = data["season"].strip()
    question    = data["question"].strip()

    # ── Build prompts ───────────────────────────
    system_prompt, user_prompt = build_prompt(
        farmer_name, location, crop, soil_type, season, question
    )

    # ── Call Groq LLM (with one retry on timeout) ──
    last_error = None
    for attempt in range(2):                          # try at most twice
        try:
            completion = client.chat.completions.create(
                model    = LLM_MODEL,
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                temperature = 0.7,
                max_tokens  = 1024,
            )
            advice = completion.choices[0].message.content.strip()
            last_error = None
            break                                     # success — exit retry loop
        except Exception as e:
            last_error = e
            app.logger.warning(f"Groq attempt {attempt+1} failed: {type(e).__name__}: {e}")

    if last_error is not None:
        app.logger.error(f"Groq API final error: {last_error}")
        return jsonify({
            "success": False,
            "error"  : f"AI service error: {type(last_error).__name__} — {last_error}"
        }), 502

    return jsonify({"success": True, "advice": advice})


# ──────────────────────────────────────────────
# Run the server
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
