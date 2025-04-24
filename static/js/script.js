document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const startButton = document.getElementById('stop-voice');
    const stopButton = document.getElementById('start-voice')
    // Speech recognition variables
    let recognition;
    let isAISpeaking = false;
    let manualStop = false;
    let isListening = false;

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

        function startSpeechRecognition() {
            if (isAISpeaking|| isListening || manualStop) return;
        
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                alert("Speech recognition not supported in this browser.");
                return;
            }
        
            recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.interimResults = false; // you can set this to true if you want live text
            recognition.maxAlternatives = 1;
        
            let transcript = '';
            isListening = true;
            
            // Add detected speech to transcript
            recognition.onresult = (event) => {
                transcript += ' ' + event.results[0][0].transcript.trim();
            };
            
            // When speech detectionends
            recognition.onend = () => {
                isListening = false;
                // Return if manual stop OR AI still speaking
                // because of manual stop, stop voice recognition, just return
                if (manualStop || isAISpeaking) {
                    return; 
                }
                // Append detected speech and send
                if (transcript.trim()) {
                    sendMessage(transcript.trim());
                    appendMessage("You", transcript.trim());
                    // Clear transcript
                    transcript = '';
                }
                // If not manual stop, resume recognition 
                // NOTE: WebAPI would stop it unless restarted
                startSpeechRecognition(); // auto-restart if not manually stopped
            };
        
            recognition.onerror = (event) => {
                console.error("Speech recognition error:", event.error);
                isListening = false;
                if (!manualStop && !isAISpeaking) {
                    // try again unless user stopped it
                    startSpeechRecognition(); 
                }
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
            if (message !== "__continue_post__") {
                appendMessage('Sao', data.response);
            }
            // 3.2 Play the audio from received path
            if (recognition) {
                recognition.abort(); // stop listening before TTS
            }
            isAISpeaking = true;
            const audio = new Audio(data.audio_url);
            audio.play();
            audio.onended = () => {
                isAISpeaking = false;
                // Handle auto-continue
                if (data.auto_continue) {
                    setTimeout(() => {
                        sendMessage("__continue_post__");
                    }, 800); // small pause so it feels natural
                } else {
                    startSpeechRecognition(); // normal case
                }
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

    stopButton.addEventListener('click', () => {
        manualStop = true;
        if (recognition && isListening) {
            recognition.abort();
            isListening = false;
            console.log("Manual stop triggered.");
        }
    });

    startButton.addEventListener('click', () => {
        if (!isListening) {
            manualStop = false;
            startSpeechRecognition();
            console.log("Manual start triggered.");
        }
    });
});




