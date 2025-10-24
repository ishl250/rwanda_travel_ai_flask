
from flask import Flask, render_template, request, jsonify, session
from pathlib import Path
import json, os, re
from datetime import datetime
from uuid import uuid4

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

DATA_PATH = Path(__file__).parent / "data" / "knowledge.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
    KB = json.load(f)

SYSTEM_PROMPT = (
    "You are a friendly and knowledgeable Rwanda travel assistant. "
    "Be concise, accurate, and warm. Include cultural insights, practical tips, and options. "
    "If you're uncertain about prices or policies, say you'll need to check official sources."
)

# Optional: lightweight NLP using transformers if available (falls back to rule-based answers)
def nlp_fallback_response(message: str) -> str:
    # Very small heuristic engine tailored to Rwanda travel
    msg = message.lower()

    # FAQs
    for key, answer in KB["faqs"].items():
        if key in msg or any(w in msg for w in {
            "visa", "e-visa", "evisa"
        }) and key == "visa":
            return f"{answer}"
        if any(w in msg for w in {"money", "currency", "cash", "exchange", "atm"}) and key == "currency":
            return f"{answer}"
        if any(w in msg for w in {"best time", "season", "weather", "rain"}) and key == "best_time":
            return f"{answer}"
        if "safety" in msg or "safe" in msg:
            return f"{KB['faqs']['safety']}"
        if "health" in msg or "vaccine" in msg or "malaria" in msg:
            return f"{KB['faqs']['health']}"
        if "sim" in msg or "mtn" in msg or "airtel" in msg or "internet" in msg:
            return f"{KB['faqs']['sim']}"
        if "transport" in msg or "bus" in msg or "drive" in msg or "car" in msg or "taxi" in msg:
            return f"{KB['faqs']['transport']}"
        if "permit" in msg or "gorilla" in msg:
            return f"{KB['faqs']['permits']}"

    # Itinerary requests
    if any(w in msg for w in ["1 day", "one day", "day trip", "kigali"]):
        return "Here’s a compact 1-day Kigali plan:\n- " + "\n- ".join(KB["itineraries"]["1_day_kigali"])
    if any(w in msg for w in ["3 day", "three day", "weekend", "adventure"]):
        return "A 3-day adventure idea:\n- " + "\n- ".join(KB["itineraries"]["3_days_adventure"])
    if any(w in msg for w in ["7 day", "seven day", "week long", "full week"]):
        return "A 7-day grand tour:\n- " + "\n- ".join(KB["itineraries"]["7_days_grand"])

    # Highlights
    if any(place in msg for place in ["volcano", "gorilla", "musanze"]):
        h = next(h for h in KB["highlights"] if "Volcanoes" in h["title"])
        return f"{h['title']}: {h['desc']} Tips: " + "; ".join(h["tips"])
    if any(place in msg for place in ["akagera", "safari", "big five"]):
        h = next(h for h in KB["highlights"] if "Akagera" in h["title"])
        return f"{h['title']}: {h['desc']} Tips: " + "; ".join(h["tips"])
    if any(place in msg for place in ["nyungwe", "canopy", "chimp"]):
        h = next(h for h in KB["highlights"] if "Nyungwe" in h["title"])
        return f"{h['title']}: {h['desc']} Tips: " + "; ".join(h["tips"])
    if any(place in msg for place in ["kivu", "rubavu", "karongi", "lake"]):
        h = next(h for h in KB["highlights"] if "Kivu" in h["title"])
        return f"{h['title']}: {h['desc']} Tips: " + "; ".join(h["tips"])
    if any(place in msg for place in ["memorial", "genocide", "kigali memorial"]):
        h = next(h for h in KB["highlights"] if "Genocide" in h["title"])
        return f"{h['title']}: {h['desc']} Tips: " + "; ".join(h["tips"])

    # Default
    return (
        "Rwanda offers gorilla trekking, serene lakes, lush rainforests, and vibrant city life in Kigali. "
        "Tell me your travel dates, budget range, and interests (wildlife, culture, relaxation, hiking), and I'll craft a tailored plan."
    )

# Attempt to use transformers if available
USE_TRANSFORMERS = False
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    MODEL_NAME = os.environ.get("CHAT_MODEL", "microsoft/DialoGPT-small")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    USE_TRANSFORMERS = True
except Exception:
    tokenizer = None
    model = None

def model_generate(prompt: str, user_input: str) -> str:
    if USE_TRANSFORMERS and tokenizer and model:
        inputs = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")
        reply_ids = model.generate(inputs, max_length=180, pad_token_id=tokenizer.eos_token_id)
        reply = tokenizer.decode(reply_ids[:, inputs.shape[-1]:][0], skip_special_tokens=True)
        # Add a tiny post-process to align to persona
        return reply.strip()
    else:
        return nlp_fallback_response(user_input)

@app.before_request
def ensure_session():
    if "sid" not in session:
        session["sid"] = str(uuid4())
        session["history"] = []

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", highlights=KB["highlights"])

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"ok": False, "response": "Please type a message."}), 400

    history = session.get("history", [])
    # You can prepend system prompt if you extend to full LLMs
    reply = model_generate(SYSTEM_PROMPT, message)

    # Save to history
    history.append({"role": "user", "content": message, "ts": datetime.utcnow().isoformat()})
    history.append({"role": "assistant", "content": reply, "ts": datetime.utcnow().isoformat()})
    session["history"] = history

    return jsonify({"ok": True, "response": reply, "history": history[-10:]})

@app.route("/reset", methods=["POST"])
def reset():
    session["history"] = []
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
