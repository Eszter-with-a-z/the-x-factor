document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const statusElement = document.getElementById('recognition-status');

    // Speech recognition variables
    let recognition;
    let isAIGeneratingResponse = false;
    let isRecognitionActive = false;
    let manuallyStopped = false;
    let transcript = '';
    let transcriptBuffer = '';

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
                    isAIGeneratingResponse = true;
                    audio.play();
                    audio.onended = () =>{
                        isAIGeneratingResponse = false;
                        manuallyStopped = false;  // Ensure reset
                        startSpeechRecognition();
                    };
                } else {
                    startSpeechRecognition();
                }
            }
        });

    // Voice recognition with auto-restart
    function startSpeechRecognition() {
        if (isAIGeneratingResponse || isRecognitionActive) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert("Speech recognition not supported in this browser.");
            return;
        }

        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;


        // When voice recognition starts
        recognition.onstart = () => {
            transcript = '';
            isRecognitionActive = true;
            toggleRecognitionStatus();
        };

        recognition.onresult = (event) => {
            transcript = event.results[0][0].transcript.trim();
            transcriptBuffer += ' ' + transcript;
            console.log("Transcript received:", transcript);
        };

        recognition.onend = () => {
            isRecognitionActive = false;
            toggleRecognitionStatus();
             // Unless manually stopped, restart speechrecognition
            if (!manuallyStopped && !isAIGeneratingResponse) {
                startSpeechRecognition()
            }
        };

        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
        };

        recognition.start();
    }

    function toggleRecognitionStatus() {
        statusElement.textContent = `Speech Recognition: ${isRecognitionActive ? "ON" : "OFF"}`;
        statusElement.style.color = isRecognitionActive ? "green" : "red";
    }

    // Get response from FLASK
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
            isAIGeneratingResponse = true;
            audio.play();
            
            audio.onended = () => {
                isAIGeneratingResponse = false;
                manuallyStopped = false;  // Reset manual state
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
        console.log("TranscriptBuffer before sending:", transcriptBuffer);

        if (message) {
            // 1.1 Append message to GUI
            appendMessage('You', message);
            userInput.value = '';
            sendMessage(message);
        }
    });

    // Stop recognition manually with spacebar
    document.addEventListener('keydown', function (event) {
        if (event.code === 'Space' && isRecognitionActive && recognition) {
            manuallyStopped = true;
            isAIGeneratingResponse = true; 
            recognition.stop();

            toggleRecognitionStatus();

            const message = transcriptBuffer;
            console.log("TranscriptBuffer before sending:", message);
            if (message){
                // Send message to AI
                sendMessage(message);
                // Add message to GUI
                appendMessage("You", message);
            }
            transcriptBuffer ='';
        }
    });
});

