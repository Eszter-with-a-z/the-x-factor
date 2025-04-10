document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // Send message and get response
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();
        // 1 Get message
        const message = userInput.value.trim();
        if (message) {
            appendMessage('You', message);
            userInput.value = '';
            // 2 Get response (FLASK))
            fetch('/chat', {
                method: 'POST',
                // 2.1 Turn message into JSON
                body: JSON.stringify({ message: message }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            // 2.2 Turn the response into JSON
            .then(response => response.json())
            // 3 Append response data to GUI
            .then(data => {
                appendMessage('Gemma 3', data.response);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.textContent = `${sender}: ${message}`;
        chatBox.appendChild(messageElement);
        // Scroll to the bottom to see the newest message
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
