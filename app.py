"""IBM BlenderBot web exercise, with isolated local-demo sessions."""
import os
import secrets
import threading
import time
from flask import Flask, jsonify, render_template, request, session
from conversation import fit_prompt

app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
                  MAX_CONTENT_LENGTH=16_384, SESSION_COOKIE_HTTPONLY=True,
                  SESSION_COOKIE_SAMESITE="Strict")
# Local, single-process demo storage. A restart clears conversations.
_histories = {}
_lock = threading.Lock()
_model = _tokenizer = None

def load_model():
    global _model, _tokenizer
    if _model is None:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        name = "facebook/blenderbot-400M-distill"
        tokenizer = AutoTokenizer.from_pretrained(name)
        model = AutoModelForSeq2SeqLM.from_pretrained(name)
        model.eval()
        _tokenizer, _model = tokenizer, model
    return _model, _tokenizer

def identity():
    if "conversation" not in session:
        session["conversation"] = secrets.token_urlsafe(24)
    return session["conversation"]

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'"
    return response

@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="Message is too large."), 413

@app.get("/")
def home():
    identity()
    return render_template("index.html")

@app.post("/chatbot")
def chat():
    data = request.get_json(silent=True)
    text = data.get("prompt") if isinstance(data, dict) else None
    if not isinstance(text, str) or not text.strip() or len(text) > 2000:
        return jsonify(error="Enter a message of 1–2000 characters."), 400
    sid = identity()
    with _lock:
        now = time.monotonic()
        for key in list(_histories):
            if now - _histories[key][0] > 3600:
                del _histories[key]
        if sid not in _histories and len(_histories) >= 100:
            return jsonify(error="Local demo capacity reached. Try again later."), 503
        history = _histories.get(sid, (now, []))[1]
        try:
            model, tokenizer = load_model()
            limit = min(int(model.config.max_position_embeddings), 512)
            prompt = fit_prompt(tokenizer, history, text.strip(), limit)
            import torch
            with torch.inference_mode():
                output = model.generate(**tokenizer(prompt, return_tensors="pt"),
                    max_new_tokens=60, do_sample=True, temperature=.6, top_p=.85,
                    repetition_penalty=1.3, no_repeat_ngram_size=3)
            reply = tokenizer.decode(output[0], skip_special_tokens=True).strip()
            if not reply:
                return jsonify(error="No response was generated. Please retry."), 502
        except ValueError:
            return jsonify(error="Message exceeds model limits or configuration is invalid. Shorten it and retry."), 422
        except Exception:
            return jsonify(error="The local model could not load or respond. Check setup and retry."), 503
        _histories[sid] = (now, (history + [f"User: {text.strip()}\nBot: {reply}"])[-3:])
    return app.response_class(reply, mimetype="text/plain")

@app.post("/reset")
def reset():
    sid = identity()
    with _lock:
        _histories.pop(sid, None)
    return "ok"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
