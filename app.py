from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

USERS_FOLDER = "users"


if not os.path.exists(USERS_FOLDER):
    os.makedirs(USERS_FOLDER)


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/chat")
def chat():
    username = request.args.get("username")
    return render_template("chat.html", username=username)


@app.route("/save_message", methods=["POST"])
def save_message():
    data = request.json
    username = data["username"]
    message = data["message"]

    file_path = os.path.join(USERS_FOLDER, f"{username}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            chats = json.load(f)
    else:
        chats = []

    chats.append(message)

    with open(file_path, "w") as f:
        json.dump(chats, f, indent=4)

    return jsonify({"status": "saved"})


@app.route("/get_messages/<username>")
def get_messages(username):
    file_path = os.path.join(USERS_FOLDER, f"{username}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            chats = json.load(f)
    else:
        chats = []

    return jsonify(chats)


if __name__ == "__main__":
    app.run(debug=True)
