"""Flask-palvelin: tarjoaa index.html:n ja POST /api/chat -rajapinnan."""

import os
import secrets
import uuid
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, session

from chat_core import SYSTEM_PROMPT, chat

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
# Allekirjoittaa istuntoevästeen; uusi joka käynnistyksellä, ei tallenneta mihinkään.
app.secret_key = secrets.token_bytes(32)

# Keskusteluhistoriat muistissa, avaimena istunnon tunniste.
CONVERSATIONS: dict[str, list[dict]] = {}


def get_history() -> list[dict]:
    """Palauttaa tämän selainistunnon keskusteluhistorian (luo tarvittaessa)."""
    sid = session.get("sid")
    if sid is None or sid not in CONVERSATIONS:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        CONVERSATIONS[sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return CONVERSATIONS[sid]


@app.get("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.get("/style.css")
def stylesheet():
    return send_from_directory(BASE_DIR, "style.css")


@app.post("/api/chat")
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Viesti puuttuu."}), 400

    history = get_history()
    history_len = len(history)
    history.append({"role": "user", "content": message})
    searches: list[dict] = []
    try:
        reply = chat(history, searches)
    except Exception as e:  # esim. OpenRouterin verkko- tai kiintiövirhe
        del history[history_len:]  # perutaan epäonnistunut vuoro historiasta
        app.logger.exception("Mallikutsu epäonnistui")
        return jsonify({"error": f"Mallikutsu epäonnistui: {e}"}), 502

    return jsonify({"reply": reply, "searches": searches})


@app.post("/api/reset")
def api_reset():
    CONVERSATIONS.pop(session.pop("sid", None), None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    # Vain 127.0.0.1: muut verkon koneet eivät pääse käyttämään API-avainta.
    # Debug-tila (Werkzeug-debugger sallii koodin suorituksen) vain FLASK_DEBUG=1:llä.
    app.run(
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
