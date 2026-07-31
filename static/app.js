let username = "";

const login = document.getElementById("login");
const chat = document.getElementById("chat");
const messages = document.getElementById("messages");
const input = document.getElementById("message");

function startChat() {

    username = document.getElementById("username").value.trim();

    if (username === "") {
        alert("Enter your name");
        return;
    }

    login.style.display = "none";
    chat.style.display = "flex";

    addAIMessage("Hello " + username + " 👋 Welcome to PENDO AI.");
}

function addUserMessage(text) {

    messages.innerHTML += `
        <div class="me">${text}</div>
    `;

    messages.scrollTop = messages.scrollHeight;
}

function addAIMessage(text) {

    messages.innerHTML += `
        <div class="ai">${text}</div>
    `;

    speechSynthesis.speak(
        new SpeechSynthesisUtterance(text)
    );

    messages.scrollTop = messages.scrollHeight;
}

async function sendMessage() {

    const text = input.value.trim();

    if (text === "") return;

    addUserMessage(text);

    input.value = "";

    const res = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: text
        })
    });

    const data = await res.json();

    setTimeout(() => {
        addAIMessage(data.reply);
    }, 500);
}

function voiceInput() {

    if (!("webkitSpeechRecognition" in window)) {
        alert("Voice recognition is not supported on this browser.");
        return;
    }

    const recognition = new webkitSpeechRecognition();

    recognition.lang = "en-US";

    recognition.onresult = function(event) {
        input.value = event.results[0][0].transcript;
    };

    recognition.start();
}

function pickImage() {
    document.getElementById("image").click();
}

document.getElementById("image").addEventListener("change", function () {

    const file = this.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function () {

        messages.innerHTML += `
            <div class="me">
                <img src="${reader.result}">
            </div>
        `;

        messages.scrollTop = messages.scrollHeight;
    };

    reader.readAsDataURL(file);
});

input.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
