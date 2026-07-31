from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data["message"].lower()

    if "hello" in message or "hi" in message:
        reply = "Hello 👋 How are you?"

    elif "how are you" in message:
        reply = "I'm fine 😊 What can I help you with?"

    elif "your name" in message:
        reply = "My name is PENDO AI."

    elif "who made you" in message:
        reply = "Engineer Pelumi created me. 😎"

    elif "bye" in message:
        reply = "Goodbye 👋 Have a great day."

    else:
        reply = "Interesting 🤔. Tell me more."

    return jsonify({
        "reply": reply
    })


if __name__ == "__main__":
    app.run(debug=True)
