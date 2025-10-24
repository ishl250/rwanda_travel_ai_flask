
# Rwanda Travel Guide AI (Flask + Tailwind)

A complete starter app for a Rwanda tourism assistant with:
- Flask backend
- Interactive chat UI (TailwindCSS via CDN)
- Icons (inline SVG) and local placeholder images (SVG)
- Lightweight rule-based AI with optional Transformers fallback

## Quick Start

1) Create & activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Run the app
```bash
python app.py
```

4) Open http://127.0.0.1:5000 in your browser.

> Note: The app works out of the box using the built-in rule-based responder.
> If `transformers` + `torch` are installed and a model can be downloaded, it will use DialoGPT-small automatically.
> Set `CHAT_MODEL` env var to switch models. For production, also set `FLASK_SECRET_KEY`.

## Customize

- Edit `data/knowledge.json` for highlights, FAQs, and itineraries.
- Modify `templates/index.html` and `static/js/app.js` for UI changes.
- Extend `app.py` to integrate a hosted LLM API (e.g., OpenAI, together, or local models).
