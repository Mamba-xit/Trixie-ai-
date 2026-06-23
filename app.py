from flask import Flask, request, render_template, jsonify, session
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "trixie-secret-key")

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="You are Trixie AI 🦊, a friendly, helpful, and slightly playful assistant. Be concise and clear."
)

@app.route("/")
def home():
    if "history" not in session:
        session["history"] = []
    return render_template("index.html", history=session["history"])

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_msg = data.get("message", "")

    if not os.environ.get("GEMINI_API_KEY"):
        return jsonify({"reply": "Error: GEMINI_API_KEY not set"}), 500

    if "history" not in session:
        session["history"] = []

    history = session["history"]
    history.append({"role": "user", "parts": [user_msg]})

    try:
        response = model.generate_content(history)
        ai_reply = response.text
        history.append({"role": "model", "parts": [ai_reply]})
        session["history"] = history[-20:]
        return jsonify({"reply": ai_reply})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"}), 500

@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    return jsonify({"status": "cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))