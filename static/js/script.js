document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // Load welcome message + audio
    fetch('/get_initial_message')
        .then(result => result.json())
        .then(data => {
            if (data.message){
                appendMessage("Gemma 3", data.message);
                if (data.audio_url){
                    const audio = new Audio(data.audio_url);
                    audio.play();
                }
            }
        })

    // Send message and get response
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();
        // 1 Get message
        const message = userInput.value.trim();
        if (message) {
            // 1.1 Append message to GUI
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
                // 3.1 Play the audio from received path
                const audio = new Audio(data.audio_url);
                audio.play();
                // 3.2 Append the message to GUI
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
