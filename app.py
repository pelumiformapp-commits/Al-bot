import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Robot Chat</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f0f2f5; text-align: center; }
        .chat-box { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        input, button { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; }
        button { background: #28a745; color: white; cursor: pointer; border: none; font-weight: bold;}
        #response { background: #e9ecef; padding: 10px; border-radius: 5px; margin-top: 10px; text-align: left; min-height: 50px; }
    </style>
</head>
<body>
    <div class="chat-box">
        <h2>🤖 Data-Powered Robot Brain</h2>
        <p>Type a message or upload your question image!</p>
        <input type="text" id="textMsg" placeholder="Type your question here...">
        <input type="file" id="imageFile" accept="image/*">
        <button onclick="sendMessage()">Send to Robot</button>
        <h3>Robot Answer:</h3>
        <div id="response">Waiting for your message...</div>
    </div>

    <script>
        async function sendMessage() {
            const text = document.getElementById('textMsg').value;
            const fileInput = document.getElementById('imageFile');
            const responseDiv = document.getElementById('response');
            responseDiv.innerText = "Robot is analyzing your question...";

            const formData = new FormData();
            formData.append('message', text);
            if(fileInput.files[0]) {
                formData.append('image', fileInput.files[0]);
            }

            try {
                const res = await fetch('/chat', { method: 'POST', body: formData });
                const data = await res.json();
                responseDiv.innerText = data.reply;
            } catch (err) {
                responseDiv.innerText = "Error connecting to the robot server!";
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form.get('message', '')
    image_present = 'image' in request.files
    
    # Base response logic
    if image_present and user_message:
        bot_reply = f"I received your image and your text: '{user_message}'. I am processing this question for you!"
    elif image_present:
        bot_reply = "I received your image! Let me look at the question details."
    elif user_message:
        bot_reply = f"Hello! You asked: '{user_message}'. Here is your answer!"
    else:
        bot_reply = "Please type a message or upload an image so I can help you."

    return jsonify({"reply": bot_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

