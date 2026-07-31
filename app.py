import sqlite3
import uuid
import os
from datetime import date
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

BUILDER_PASSCODE = os.environ.get("BUILDER_PASSCODE")
PUBLIC_PASSCODE = os.environ.get("PUBLIC_PASSCODE")

DAILY_LIMIT = 500
MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct" 
DB_PATH = "/data/chatbot.db" if os.path.exists("/data") else "chatbot.db"

BUILDER_SYSTEM_PROMPT = "You are talking to your creator, the brilliant engineer who built you. Be warm, respectful, and slightly more personal. Keep answers concise."
PUBLIC_SYSTEM_PROMPT = "You are a friendly assistant talking to a member of the public. Keep answers concise, welcoming, and helpful."

app = Flask(__name__)
CORS(app)
executor = ThreadPoolExecutor(max_workers=1)

print("Loading AI Model into CPU memory...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, torch_dtype=torch.float32)
print("Model Ready!")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            visitor_id TEXT NOT NULL,
            day        TEXT NOT NULL,
            count      INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (visitor_id, day)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            visitor_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            reply TEXT NOT NULL
        )
    """)
    return conn

def log_conversation(visitor_id: str, role: str, message: str, reply: str):
    conn = get_db()
    conn.execute("""
        INSERT INTO chat_logs (visitor_id, role, message, reply)
        VALUES (?, ?, ?, ?)
    """, (visitor_id, role, message, reply))
    conn.commit()
    conn.close()

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    passcode = data.get("passcode") or ""
    visitor_id = data.get("visitor_id") or str(uuid.uuid4())

    if passcode == BUILDER_PASSCODE:
        role = "builder"
    elif passcode == PUBLIC_PASSCODE:
        role = "public"
    else:
        return jsonify({"error": "Invalid passcode. Access denied."}), 401

    if not message:
        return jsonify({"error": "Message is required."}), 400

    conn = get_db()
    today = date.today().isoformat()
    
    if role == "public":
        row = conn.execute("SELECT count FROM usage WHERE visitor_id = ? AND day = ?", (visitor_id, today)).fetchone()
        used = row if row else 0
        if used >= DAILY_LIMIT:
            conn.close()
            return jsonify({"reply": "You've reached today's limit. Come back tomorrow!"})

    prompt = BUILDER_SYSTEM_PROMPT if role == "builder" else PUBLIC_SYSTEM_PROMPT
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": message}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt")
    
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=150, pad_token_id=tokenizer.eos_token_id)
    
    reply = tokenizer.decode(output[inputs["input_ids"].shape:], skip_special_tokens=True).strip()

    log_conversation(visitor_id, role, message, reply)
    
    if role == "public":
        conn = get_db()
        conn.execute("""
            INSERT INTO usage (visitor_id, day, count) VALUES (?, ?, 1)
            ON CONFLICT(visitor_id, day) DO UPDATE SET count = count + 1
        """, (visitor_id, today))
        conn.commit()
        
    conn.close()
    return jsonify({"reply": reply})

@app.route("/logs", methods=["POST"])
def get_logs():
    data = request.get_json(force=True) or {}
    if data.get("passcode") != BUILDER_PASSCODE:
        return jsonify({"error": "Unauthorized."}), 401
        
    conn = get_db()
    rows = conn.execute("SELECT timestamp, visitor_id, role, message, reply FROM chat_logs ORDER BY id DESC").fetchall()
    conn.close()
    
    logs = []
    for r in rows:
        logs.append({
            "time": r,
            "id": r[:8],
            "role": r,
            "msg": r,
            "rep": r
        })
    return jsonify({"logs": logs})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
