document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    // Speech recognition variables
    let recognition;
    let recognitionTimeout;
    let isAISpeaking = false;

    // Load welcome message + audio
    fetch('/get_initial_message')
        .then(result => result.json())
        .then(data => {
            if (data.message){
                appendMessage("Sao", data.message);
                if (data.audio_url){
                    // Stop previous recognition
                    if (recognition) {
                        recognition.abort();
                    }
                
                    const audio = new Audio(data.audio_url);
                    isAISpeaking = true;
                    audio.play();
                    audio.onended = () =>{
                        isAISpeaking = false;
                        startSpeechRecognition();
                    };
                } else {
                    startSpeechRecognition();
                }
            }
        });

    // Voice recognition with auto-restart
    function startSpeechRecognition() {
        if (isAISpeaking) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Speech recognition not supported in this browser.");
            return;
        }

        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            console.log("Listening...");
            // Set a manual timeout to stop listening after 5 seconds
            recognitionTimeout = setTimeout(() => {
                recognition.stop();
            }, 6000);
        };

        recognition.onresult = (event) => {
            // Stop timeout if speech is detected
            clearTimeout(recognitionTimeout);
            const transcript = event.results[0][0].transcript.trim();
            // Send message to AI
            sendMessage(transcript);
            console.log("You said:", transcript);
            // Add message to GUI
            appendMessage("You", transcript);
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
        };

        recognition.start();
    }

    // 2 Get response (FLASK))
    function sendMessage(message) {
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
        // 3 Append response data to frontend
        .then(data => {
            // 3.1 Append the message to GUI 
            appendMessage('Sao', data.response);
            // 3.2 Play the audio from received path
            if (recognition) {
                recognition.abort(); // stop listening before TTS
            }
            const audio = new Audio(data.audio_url);
            isAISpeaking = true;
            audio.play();
            audio.onended = () => {
                isAISpeaking = false;
                startSpeechRecognition();  // Restart after TTS
            };
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.textContent = `${sender}: ${message}`;
        chatBox.appendChild(messageElement);
        // Scroll to the bottom to see the newest message
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Send typed message (optional fallback if user types)
    chatForm.addEventListener('submit', function (event) {
        event.preventDefault();
        // 1 Get message
        const message = userInput.value.trim();
        if (message) {
            // 1.1 Append message to GUI
            appendMessage('You', message);
            userInput.value = '';
            sendMessage(message);
        }
    });
});

