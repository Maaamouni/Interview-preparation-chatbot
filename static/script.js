async function sendMessage() {

    const input = document.getElementById("message");
    const text = input.value;

    if (!text) return;

    const chatBox = document.getElementById("chat-box");

    chatBox.innerHTML += `
        <div class="user-message">
            <div class="bubble-user">${text}</div>
        </div>
    `;

    input.value = "";

    const response = await fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: text
        })
    });

    const data = await response.json();

    const sourcesHtml = data.sources
        .map(
            s => `${s.file} (page ${s.page})`
        )
        .join("<br>");

    chatBox.innerHTML += `
        <div class="bot-message">
            <div class="bubble-bot">
                ${data.answer}
            </div>
            <div class="sources">
                ${sourcesHtml}
            </div>
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;
}